"""Data models for 19hz MCP server."""

from typing import Optional

from pydantic import BaseModel, Field


class Region(BaseModel):
    """Represents a geographic region for event listings."""

    key: str  # Short identifier like "bayarea"
    name: str  # Full name like "San Francisco Bay Area / Northern California"
    filename: str  # PHP filename like "eventlisting_BayArea.php"

    @property
    def url(self) -> str:
        """Full URL to the event listing page."""
        return f"https://19hz.info/{self.filename}"


class Event(BaseModel):
    """Represents an electronic music event."""

    date: str
    time: str
    title: str
    venue: str
    location: str
    genres: list[str] = Field(default_factory=list)
    price: Optional[str] = None
    age_restriction: Optional[str] = None
    organizers: list[str] = Field(default_factory=list)
    url: Optional[str] = None  # Primary URL (from title)
    additional_links: dict[str, str] = Field(default_factory=dict)  # Link text -> URL

    def format_markdown(self) -> str:
        """Format event as markdown."""
        lines = [
            f"## {self.title}",
            f"**Date:** {self.date}",
            f"**Time:** {self.time}",
            f"**Venue:** {self.venue}",
        ]

        if self.genres:
            lines.append(f"**Genres:** {', '.join(self.genres)}")
        if self.price:
            lines.append(f"**Price:** {self.price}")
        if self.age_restriction:
            lines.append(f"**Age:** {self.age_restriction}")
        if self.organizers:
            lines.append(f"**Organizers:** {', '.join(self.organizers)}")
        if self.url:
            lines.append(f"**Link:** {self.url}")
        if self.additional_links:
            lines.append("**Additional Links:**")
            for text, url in self.additional_links.items():
                lines.append(f"  - [{text}]({url})")

        lines.append("\n---\n")
        return "\n".join(lines)

    def matches_search(self, search_term: str) -> bool:
        """Check if event matches search term."""
        search_lower = search_term.lower()
        return (
            search_lower in self.title.lower()
            or search_lower in self.venue.lower()
            or any(search_lower in g.lower() for g in self.genres)
            or any(search_lower in o.lower() for o in self.organizers)
        )


class EventPage(BaseModel):
    """A page of events with pagination info."""

    events: list[Event]
    page: int
    page_size: int
    total_events: int
    has_more: bool

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return max(1, (self.total_events + self.page_size - 1) // self.page_size)

    def format_markdown(
        self, region_name: str, search_term: Optional[str] = None
    ) -> str:
        """Format page as markdown response."""
        lines = [f"# Electronic Music Events - {region_name}"]

        if search_term:
            lines.append(f"\nSearch: '{search_term}'")

        lines.append(
            f"\n**Page {self.page} of {self.total_pages}** ({self.total_events} total events)\n"
        )

        for event in self.events:
            lines.append(event.format_markdown())

        if self.has_more:
            lines.append(f"\n*Use page={self.page + 1} to see more events*")

        return "\n".join(lines)
