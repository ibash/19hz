"""Constants for 19hz MCP server."""

from models import Region

# All available regions with their configuration
REGIONS = {
    "bayarea": Region(
        key="bayarea",
        name="San Francisco Bay Area / Northern California",
        filename="eventlisting_BayArea.php",
    ),
    "la": Region(
        key="la",
        name="Los Angeles / Southern California",
        filename="eventlisting_LosAngeles.php",
    ),
    "seattle": Region(
        key="seattle", name="Seattle", filename="eventlisting_Seattle.php"
    ),
    "atlanta": Region(
        key="atlanta", name="Atlanta", filename="eventlisting_Atlanta.php"
    ),
    "miami": Region(key="miami", name="Miami", filename="eventlisting_Miami.php"),
    "dc": Region(
        key="dc",
        name="Washington, DC / Maryland / Virginia",
        filename="eventlisting_DC.php",
    ),
    "texas": Region(key="texas", name="Texas", filename="eventlisting_Texas.php"),
    "philadelphia": Region(
        key="philadelphia", name="Philadelphia", filename="eventlisting_PHL.php"
    ),
    "toronto": Region(
        key="toronto", name="Toronto", filename="eventlisting_Toronto.php"
    ),
    "iowa": Region(
        key="iowa", name="Iowa / Nebraska", filename="eventlisting_Iowa.php"
    ),
    "denver": Region(key="denver", name="Denver", filename="eventlisting_Denver.php"),
    "chicago": Region(key="chicago", name="Chicago", filename="eventlisting_CHI.php"),
    "detroit": Region(
        key="detroit", name="Detroit", filename="eventlisting_Detroit.php"
    ),
    "massachusetts": Region(
        key="massachusetts",
        name="Massachusetts",
        filename="eventlisting_Massachusetts.php",
    ),
    "lasvegas": Region(
        key="lasvegas", name="Las Vegas", filename="eventlisting_LasVegas.php"
    ),
    "phoenix": Region(
        key="phoenix", name="Phoenix", filename="eventlisting_Phoenix.php"
    ),
    "oregon": Region(
        key="oregon", name="Portland / Oregon", filename="eventlisting_ORE.php"
    ),
    "bc": Region(
        key="bc", name="Vancouver / British Columbia", filename="eventlisting_BC.php"
    ),
}
