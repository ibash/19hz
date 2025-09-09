# 19hz MCP Server

MCP server for accessing electronic music events from [19hz.info](https://19hz.info).

## Installation

```bash
# Install dependencies
uv sync
```

## Usage

### HTTP Mode (default)

```bash
uv run python server.py
# Server runs at http://127.0.0.1:8000/mcp (or PORT env var if set)
```

### STDIO Mode

```bash
uv run python server.py --stdio
```

## Available Tools

### `get_events`
Fetch events for a specific region.

```json
{
  "region": "bayarea",
  "search": "techno"  // optional
}
```

### `list_regions`
List all available regions.

### `search_all_regions`
Search across all regions.

```json
{
  "search_term": "warehouse",
  "max_results": 10
}
```

### `check_for_new_regions`
Check if 19hz.info has added new regions.

## Supported Regions

- `bayarea` - San Francisco Bay Area / Northern California
- `la` - Los Angeles / Southern California
- `seattle` - Seattle
- `atlanta` - Atlanta
- `miami` - Miami
- `dc` - Washington, DC / Maryland / Virginia
- `texas` - Texas
- `philadelphia` - Philadelphia
- `toronto` - Toronto
- `iowa` - Iowa / Nebraska
- `denver` - Denver
- `chicago` - Chicago
- `detroit` - Detroit
- `massachusetts` - Massachusetts
- `lasvegas` - Las Vegas
- `phoenix` - Phoenix
- `oregon` - Portland / Oregon
- `bc` - Vancouver / British Columbia

## Testing with Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "19hz": {
      "command": "uv",
      "args": ["run", "python", "/path/to/19hz-mcp/server.py", "--stdio"]
    }
  }
}
```