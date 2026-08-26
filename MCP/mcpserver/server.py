from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP(
    name="weather",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8000,  # only used for SSE transport (set this to any port)
)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
    Event: {props.get('event', 'Unknown')}
    Area: {props.get('areaDesc', 'Unknown')}
    Severity: {props.get('severity', 'Unknown')}
    Description: {props.get('description', 'No description available')}
    Instructions: {props.get('instruction', 'No specific instructions provided')}
    """

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
                {period['name']}:
                Temperature: {period['temperature']}°{period['temperatureUnit']}
                Wind: {period['windSpeed']} {period['windDirection']}
                Forecast: {period['detailedForecast']}
                """
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

# Run the server
if __name__ == "__main__":
    transport = "sse"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")


'''
# MCP Weather Server with Tools + SSE — Interview Notes

## 1. What this application does

This code creates a **remote MCP Weather Server** using `FastMCP`.

It exposes **two MCP tools**:

* `get_alerts(state)` → gets active weather alerts for a U.S. state.
* `get_forecast(latitude, longitude)` → gets a weather forecast for a location.

It also demonstrates **MCP transport**, specifically **SSE (Server-Sent Events)**.

**Flow:**

`MCP Client → SSE → MCP Server → Weather Tool → NWS API → Result`

---

# 2. Initialize FastMCP Server

```python id="h5y3r8"
mcp = FastMCP(
    name="weather",
    host="0.0.0.0",
    port=8000,
)
```

Creates an MCP server named `weather`.

### `host="0.0.0.0"`

Makes the server listen on all network interfaces.

### `port=8000`

The server uses port `8000` for the SSE transport in this code.

**Interview point:**

> `host` and `port` configure where the MCP server listens when using a network transport such as SSE.

---

# 3. NWS API Constants

```python id="e9f2k7"
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
```

* `NWS_API_BASE` → National Weather Service API.
* `USER_AGENT` → identifies the application making the request.

---

# 4. API Request Helper

```python id="r7a4m2"
async def make_nws_request(
    url: str
) -> dict[str, Any] | None:
```

This asynchronous helper function communicates with the NWS API.

```python id="y6n2pw"
async with httpx.AsyncClient() as client:
    try:
        response = await client.get(
            url,
            headers=headers,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None
```

### Important concepts

* `AsyncClient` → asynchronous HTTP client.
* `await client.get()` → performs async GET request.
* `raise_for_status()` → detects HTTP errors.
* `response.json()` → converts API response to Python data.
* `return None` → handles failed requests.

**Remember:**

`MCP Tool → HTTP Helper → NWS API`

---

# 5. Format Alert

```python id="e0r7f4"
def format_alert(feature: dict) -> str:
```

Converts raw NWS alert data into readable text.

It extracts:

* Event
* Area
* Severity
* Description
* Instructions

Using:

```python id="l4p9x2"
props.get("event", "Unknown")
```

provides a default value if a field is missing.

---

# 6. `get_alerts()` MCP Tool

```python id="x6s9v1"
@mcp.tool()
async def get_alerts(state: str) -> str:
```

The decorator:

```python id="8j4qz2"
@mcp.tool()
```

registers the function as an **MCP Tool**.

The AI client can discover and call it.

Example:

```text id="c3r1a9"
get_alerts("CA")
```

---

## 7. Alert Tool Flow

```python id="f5k2x8"
url = f"{NWS_API_BASE}/alerts/active/area/{state}"
data = await make_nws_request(url)
```

For `CA`:

```text id="7q3m5c"
https://api.weather.gov/alerts/active/area/CA
```

Then the code checks:

```python id="a2v8m1"
if not data or "features" not in data:
```

and:

```python id="n4b6q0"
if not data["features"]:
```

So it handles:

1. API failure.
2. Invalid response.
3. No active alerts.

Finally:

```python id="w9c3s6"
alerts = [format_alert(feature) for feature in data["features"]]
return "\n---\n".join(alerts)
```

formats all alerts into a readable response.

---

# 8. `get_forecast()` MCP Tool

```python id="q7f1k3"
@mcp.tool()
async def get_forecast(
    latitude: float,
    longitude: float
) -> str:
```

This is the second MCP tool.

It accepts:

* `latitude`
* `longitude`

Example:

```text id="s5j8r2"
latitude = 42.3736
longitude = -72.5199
```

---

# 9. Forecast Uses Two API Calls

This is an important interview point.

### Step 1 — Get Point Information

```python id="p8m4z6"
points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"

points_data = await make_nws_request(points_url)
```

The NWS API first converts the coordinates into information about that location.

---

### Step 2 — Get Forecast URL

```python id="r2c7v5"
forecast_url = points_data["properties"]["forecast"]
```

The first API response contains the actual forecast endpoint.

Then:

```python id="u6k1s9"
forecast_data = await make_nws_request(forecast_url)
```

fetches the detailed forecast.

### Remember this flow

```text id="h3m7q1"
Latitude + Longitude
        ↓
   /points API
        ↓
 Forecast URL
        ↓
 Forecast API
        ↓
 Detailed Forecast
```

---

# 10. Format Forecast

```python id="b5n8r3"
periods = forecast_data["properties"]["periods"]
```

Gets the forecast periods.

Then:

```python id="v2x6m4"
for period in periods[:5]:
```

only returns the **next 5 forecast periods**.

For each period, it extracts:

* Name
* Temperature
* Temperature unit
* Wind speed
* Wind direction
* Detailed forecast

Then:

```python id="k8s1p5"
return "\n---\n".join(forecasts)
```

combines them into a readable response.

---

# 11. Run the MCP Server

```python id="c6r9w2"
if __name__ == "__main__":
    transport = "sse"
```

The selected transport is:

```text id="f4m7q1"
sse
```

Then:

```python id="n3x8v5"
mcp.run(transport="sse")
```

starts the MCP server using SSE transport.

---

# 12. STDIO vs SSE

The code supports two transport options:

```python id="z1k5m8"
if transport == "stdio":
    mcp.run(transport="stdio")

elif transport == "sse":
    mcp.run(transport="sse")
```

### STDIO

Communication happens through **standard input/output**.

Common for:

* Local MCP servers
* Desktop applications
* Local development

### SSE

**Server-Sent Events** provides a network-based connection.

Useful when the MCP server is running as a network service.

### Interview answer

> **STDIO is commonly used for local process-based MCP communication, while SSE provides a network-based transport for connecting to a running MCP server.**

---

# Complete Architecture

```text id="p8w3n6"
                  MCP Client
                      │
                      │ SSE
                      ↓
              ┌──────────────┐
              │   FastMCP    │
              │    Server    │
              └──────┬───────┘
                     │
             ┌───────┴────────┐
             ↓                ↓
       get_alerts()      get_forecast()
             │                │
             ↓                ↓
        NWS Alerts API    NWS Points API
                              │
                              ↓
                        Forecast API
             │                │
             └───────┬────────┘
                     ↓
                 MCP Result
                     ↓
                 MCP Client
```

---

# What to Remember for Interview

### MCP

**FastMCP** → creates MCP server.

### Tools

```text id="b2r8x5"
@mcp.tool()
```

→ exposes a callable capability to the MCP client.

### Transport

```text id="y5k1c9"
stdio
```

→ local process communication.

```text id="n7m4p2"
sse
```

→ network-based communication.

### HTTP Client

```text id="q4x8s1"
httpx.AsyncClient
```

→ communicates with the external NWS API asynchronously.

### Two Weather Tools

**`get_alerts(state)`**

→ active alerts for a state.

**`get_forecast(latitude, longitude)`**

→ forecast for coordinates.

---

# Most Important Interview Distinction

### MCP Tool vs External API

The MCP tool is **not the weather API**.

```text id="x3k8v6"
MCP Tool
   ↓
Python Function
   ↓
NWS REST API
   ↓
Weather Data
```

The MCP tool acts as a **standardized interface/wrapper around the external API**.

---

# Interview-Ready Explanation

> "This is a network-enabled MCP weather server built using FastMCP. It exposes two tools: `get_alerts`, which retrieves active alerts for a U.S. state, and `get_forecast`, which retrieves a forecast using latitude and longitude. Both tools asynchronously call the National Weather Service API using httpx. The forecast tool first calls the NWS points endpoint to obtain the appropriate forecast URL and then makes a second request for the detailed forecast. The server is configured to run using SSE transport, allowing an MCP client to communicate with the server over the network."

## One-Line Memory Trick

**`MCP Server → SSE → Tools → NWS API → Result`**

### 5 things to memorize

**`FastMCP` → MCP Server**

**`@mcp.tool()` → Expose function as Tool**

**`httpx.AsyncClient` → Call external API**

**`SSE` → Network transport**

**`stdio` → Local process transport**

'''