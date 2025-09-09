"""
19hz MCP Server - Electronic Music Event Calendar

This MCP server provides tools to fetch and search electronic music events
from 19hz.info, a comprehensive event calendar for electronic music across
North America.
"""

import os
import sys
from typing import Optional

from fastmcp import FastMCP
from pydantic import Field

from constants import REGIONS
from parser import EventParser

# Initialize MCP server
mcp = FastMCP(
    name="19hz Electronic Music Events",
    instructions="""Access electronic music event listings from 19hz.info.

Available regions: bayarea, la, seattle, atlanta, miami, dc, texas, 
philadelphia, toronto, iowa, denver, chicago, detroit, massachusetts, 
lasvegas, phoenix, oregon, bc

Use the 'get_events' tool to fetch current event listings for any region.""",
)

# Create parser instance
parser = EventParser(REGIONS)


@mcp.tool()
async def get_events(
    region: str = Field(
        description="Region to fetch events from (e.g., 'bayarea', 'la', 'seattle')"
    ),
    search: Optional[str] = Field(
        None, description="Optional search term to filter events"
    ),
    page: int = Field(1, description="Page number (default: 1)"),
    page_size: int = Field(50, description="Events per page (default: 50)"),
) -> str:
    """
    Fetch electronic music events for a specific region from 19hz.info.

    Returns a formatted list of upcoming events with dates, venues, and details.
    Supports pagination to browse through all events.
    """
    try:
        page_result = await parser.fetch_events(region, page, page_size, search)
        region_obj = REGIONS.get(region.lower())
        region_name = region_obj.name if region_obj else region.upper()
        return page_result.format_markdown(region_name, search)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error fetching events: {str(e)}"


@mcp.tool()
async def list_regions() -> str:
    """List all available regions for event listings."""
    result = "# Available Regions\n\n"

    for region in REGIONS.values():
        result += f"- **{region.key}** - {region.name}\n"

    return result


@mcp.tool()
async def search_all_regions(
    search_term: str = Field(description="Term to search for across all regions"),
    max_per_region: int = Field(5, description="Maximum results per region"),
) -> str:
    """
    Search for events across all regions.

    Returns matching events from all regions, limited to max_per_region per region.
    """
    output = f"# Search Results for '{search_term}'\n\n"
    total_found = 0

    for region in REGIONS.values():
        try:
            # Fetch first page with search
            page_result = await parser.fetch_events(
                region.key, page=1, page_size=max_per_region, search=search_term
            )

            if page_result.events:
                output += f"\n## {region.name} ({page_result.total_events} matches)\n"
                for event in page_result.events:
                    output += f"- **{event.date}** - {event.title} @ {event.venue}\n"
                    if event.url:
                        output += f"  [{event.url}]({event.url})\n"
                total_found += page_result.total_events

        except Exception as e:
            # Log error but continue with other regions
            output += f"\n## {region.name}\n"
            output += f"Error: {str(e)}\n"

    if total_found == 0:
        output += "No events found matching your search."
    else:
        output += f"\n**Total matches across all regions: {total_found}**"

    return output


@mcp.tool()
async def check_for_new_regions() -> str:
    """
    Check the main 19hz.info page for any new regions not in our list.

    This helps keep the server up to date with new regions added to 19hz.
    """
    try:
        found_regions, new_regions = await parser.check_for_new_regions()

        result = "# Region Check Results\n\n"
        result += f"**Known regions:** {len(REGIONS)}\n"
        result += f"**Found on site:** {len(found_regions)}\n\n"

        if new_regions:
            result += "## New regions found:\n"
            for region in new_regions:
                result += f"- {region}\n"
            result += "\nThese should be added to constants.py.\n"
        else:
            result += "✓ All regions are up to date.\n"

        return result
    except Exception as e:
        return f"Error checking for new regions: {str(e)}"


# HTTP app setup (only create if running as HTTP server)
if "--stdio" not in sys.argv:
    app = mcp.http_app()


def main():
    """Run the MCP server."""
    # Check for stdio mode
    if "--stdio" in sys.argv:
        mcp.run(transport="stdio")
    else:
        # Default to HTTP mode
        port = int(os.environ.get("PORT", "8000"))
        mcp.run(
            transport="http",
            host="127.0.0.1",
            port=port,
            path="/mcp",
        )


if __name__ == "__main__":
    main()
