"""HTML parser for 19hz.info event listings."""

import re
from typing import Optional

import httpx
from selectolax.parser import HTMLParser

from models import Event, EventPage, Region


class EventParser:
    """Parses 19hz.info event listing pages."""

    BASE_URL = "https://19hz.info"
    DEFAULT_PAGE_SIZE = 50
    MIN_CELLS_FOR_EVENT = 6

    # Regex patterns
    DATE_PATTERN = re.compile(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[^\n]*")
    TIME_PATTERN = re.compile(r"\(([^)]+)\)")
    PRICE_PATTERN = re.compile(r"\$[\d\.]+|free|donation", re.IGNORECASE)
    AGE_PATTERN = re.compile(r"\b(21\+|18\+|All ages|\d+\+)", re.IGNORECASE)
    VENUE_LOCATION_PATTERN = re.compile(r"\([^)]+\)$")

    def __init__(self, regions: dict[str, Region]):
        """Initialize parser with region configuration."""
        self.regions = regions

    async def fetch_events(
        self,
        region_key: str,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: Optional[str] = None,
    ) -> EventPage:
        """Fetch and parse events for a specific region with pagination."""
        region = self._validate_region(region_key)
        html = await self._fetch_page_html(region.url)
        all_events = self._parse_events_html(html, region)

        # Apply search filter
        if search:
            all_events = [e for e in all_events if e.matches_search(search)]

        # Create paginated result
        return self._paginate_events(all_events, page, page_size)

    def _validate_region(self, region_key: str) -> Region:
        """Validate and return region object."""
        region_key_lower = region_key.lower()
        if region_key_lower not in self.regions:
            available = ", ".join(self.regions.keys())
            raise ValueError(f"Invalid region. Available regions: {available}")
        return self.regions[region_key_lower]

    async def _fetch_page_html(self, url: str) -> str:
        """Fetch HTML content from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text

    def _paginate_events(
        self, events: list[Event], page: int, page_size: int
    ) -> EventPage:
        """Create paginated event page."""
        total_events = len(events)

        # Validate page number
        page = max(1, page)  # Ensure page is at least 1

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        return EventPage(
            events=events[start_idx:end_idx],
            page=page,
            page_size=page_size,
            total_events=total_events,
            has_more=end_idx < total_events,
        )

    def _parse_events_html(self, html: str, region: Region) -> list[Event]:
        """Parse events from HTML table structure."""
        parser = HTMLParser(html)
        events = []

        for row in parser.css("tbody tr"):
            event = self._parse_event_row(row, region)
            if event:
                events.append(event)

        return events

    def _parse_event_row(self, row, region: Region) -> Optional[Event]:
        """Parse a single event from a table row."""
        cells = row.css("td")

        if len(cells) < self.MIN_CELLS_FOR_EVENT:
            return None

        # Extract data from each cell
        date, time = self._extract_datetime(cells[0])
        if not date:  # No valid date means not an event row
            return None

        title, url = self._extract_title_and_url(cells[1])
        venue = self._extract_venue(cells[1])
        genres = self._extract_genres(cells[2])
        price, age = self._extract_price_and_age(cells[3])
        organizers = self._extract_organizers(cells[4])
        additional_links = self._extract_additional_links(
            cells[5] if len(cells) > 5 else None
        )

        return Event(
            date=date,
            time=time,
            title=title,
            venue=venue,
            location=region.name,
            genres=genres,
            price=price,
            age_restriction=age,
            organizers=organizers,
            url=url,
            additional_links=additional_links,
        )

    def _extract_datetime(self, cell) -> tuple[Optional[str], str]:
        """Extract date and time from date/time cell."""
        text = cell.text(deep=True, strip=True)

        # Extract date
        date_match = self.DATE_PATTERN.search(text)
        if not date_match:
            return None, "TBA"

        date = date_match.group(0)

        # Extract time from parentheses
        time_match = self.TIME_PATTERN.search(text)
        time = time_match.group(1) if time_match else "TBA"

        return date, time

    def _extract_title_and_url(self, cell) -> tuple[str, Optional[str]]:
        """Extract event title and primary URL from title/venue cell."""
        # Try to get from link first
        link = cell.css_first("a")
        if link:
            title = link.text(strip=True)
            url = self._make_absolute_url(link.attributes.get("href", ""))
            return title, url

        # Fallback to text before @ symbol
        text = cell.text(deep=True, strip=True)
        title = text.split("@")[0].strip() if "@" in text else "Event"
        return title, None

    def _extract_venue(self, cell) -> str:
        """Extract venue from title/venue cell."""
        text = cell.text(deep=True, strip=True)
        if "@" not in text:
            return "TBA"

        venue = text.split("@", 1)[1].strip()
        # Remove location in parentheses (e.g., "(San Francisco)")
        venue = self.VENUE_LOCATION_PATTERN.sub("", venue).strip()
        return venue

    def _extract_genres(self, cell) -> list[str]:
        """Extract genres from genres cell."""
        text = cell.text(deep=True, strip=True)
        return [g.strip() for g in text.split(",") if g.strip()]

    def _extract_price_and_age(self, cell) -> tuple[Optional[str], Optional[str]]:
        """Extract price and age restriction from price/age cell."""
        text = cell.text(deep=True, strip=True)

        price_match = self.PRICE_PATTERN.search(text)
        price = price_match.group(0) if price_match else None

        age_match = self.AGE_PATTERN.search(text)
        age = age_match.group(0) if age_match else None

        return price, age

    def _extract_organizers(self, cell) -> list[str]:
        """Extract organizers from organizers cell."""
        text = cell.text(deep=True, strip=True)
        return [o.strip() for o in text.split(",") if o.strip()]

    def _extract_additional_links(self, cell) -> dict[str, str]:
        """Extract additional links from links cell."""
        if not cell:
            return {}

        links = {}
        for link in cell.css("a"):
            text = link.text(strip=True)
            url = self._make_absolute_url(link.attributes.get("href", ""))
            if text and url:
                links[text] = url

        return links

    def _make_absolute_url(self, url: str) -> Optional[str]:
        """Convert relative URL to absolute if needed."""
        if not url:
            return None
        if url.startswith("http"):
            return url
        if url.startswith("/"):
            return f"{self.BASE_URL}{url}"
        return url

    async def check_for_new_regions(self) -> tuple[list[str], list[str]]:
        """Check the main page for any new regions not in our list."""
        html = await self._fetch_page_html(self.BASE_URL)
        parser = HTMLParser(html)

        found_regions = []
        known_filenames = {r.filename for r in self.regions.values()}

        for link in parser.css("a[href*='eventlisting']"):
            href = link.attributes.get("href")
            if href and "eventlisting" in href:
                filename = href.split("/")[-1].split("?")[0]
                found_regions.append(filename)

        unique_found = list(set(found_regions))
        new_regions = [f for f in unique_found if f not in known_filenames]

        return unique_found, new_regions
