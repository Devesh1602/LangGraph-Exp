##You can find it in VSCode/Cursor IDEs in command palette

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp=FastMCP("weather")

#constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str)-> dict[str, Any] | None:
    '''Make a request to the NWS API with proper error handling'''
    header={
        "User-Agent":USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response=await client.get(url, header=header, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    '''Format an alert feature into readable string'''
    props=feature["properties"]
    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction', 'No specific instructions provided')}
        """

@mcp.tool()
async def get_alerts(state: str) -> str:
    '''Get weather alerts for US State
    Args:
    state: Two-letter US State code (eg. CA/MA)
    '''
    url=f"{NWS_API_BASE}/alerts/active/area/{state}"
    data=await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts sound!"

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

#Resources are how you expose data to LLMs
@mcp.resource("echo://{message}")
def echo_resource(message: str) ->str:
    '''Echo message as a resource'''
    return f"Resource echo: {message}"

'''
In the Model Context Protocol (MCP), context refers to the external data, tools, and systems that AI models access to enhance their responses and perform actions beyond their static training data.  It encompasses three primary primitives provided by MCP servers:

Resources: Structured data such as files, database rows, or API outputs that provide read-only information to the model. 
Tools: Executable functions that allow the AI to perform actions, such as querying a database, modifying files, or invoking external APIs. 
Prompts: Pre-defined templates or instructions that guide the language model’s interactions and workflows. 

'''
'''
# MCP Weather Server — Interview Notes

## 1. What this application does

This code creates an **MCP server using FastMCP** that exposes:

* **Tool:** `get_alerts()` → fetches active weather alerts for a U.S. state.
* **Resource:** `echo://{message}` → returns an echo message.

It uses the **National Weather Service (NWS) API** as the external data source.

**Flow:**

`MCP Client → MCP Server → get_alerts() → NWS API → Weather Data → Client`

---

# 2. Imports

```python
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
```

* `Any` → used for flexible type annotations.
* `httpx` → asynchronous HTTP client used to call the NWS API.
* `FastMCP` → simplifies creation of an MCP server and its tools/resources.

---

# 3. Initialize MCP Server

```python
mcp = FastMCP("weather")
```

Creates an MCP server named **weather**.

This server will expose capabilities such as tools and resources.

**Remember:**

> `FastMCP` provides a simple way to create an MCP server in Python.

---

# 4. API Constants

```python
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
```

* `NWS_API_BASE` → base URL for the National Weather Service API.
* `USER_AGENT` → identifies the application when making API requests.

---

# 5. Make NWS API Request

```python
async def make_nws_request(
    url: str
) -> dict[str, Any] | None:
```

This is an **async helper function** that communicates with the weather API.

### Why `async`?

The function performs network I/O.

Using asynchronous HTTP allows the application to avoid blocking while waiting for the API response.

---

## 6. HTTP Headers

```python
headers = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json"
}
```

The request sends:

* `User-Agent` → identifies the client.
* `Accept` → tells the API which response format the client expects.

---

# 7. Async HTTP Request

```python
async with httpx.AsyncClient() as client:
    try:
        response = await client.get(
            url,
            headers=headers,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
```

Important parts:

### `httpx.AsyncClient()`

Creates an asynchronous HTTP client.

### `await client.get(...)`

Makes the GET request asynchronously.

### `timeout=30.0`

The request can wait up to 30 seconds.

### `raise_for_status()`

Raises an exception if the HTTP response indicates an error.

### `response.json()`

Converts the API's JSON response into a Python object.

---

# 8. Error Handling

```python
except Exception:
    return None
```

If the API request fails, the function returns `None`.

So instead of crashing the MCP server, the caller can handle the failure.

**Interview point:**

> The helper function separates external API communication and error handling from the MCP tool logic.

---

# 9. Format Weather Alert

```python
def format_alert(feature: dict) -> str:
    props = feature["properties"]

    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction',
                                  'No specific instructions provided')}
    """
```

The NWS API returns alert information inside a `properties` object.

This function converts the raw API data into a **human-readable string**.

### Why `.get()`?

```python
props.get("severity", "Unknown")
```

If the field does not exist, it returns `"Unknown"` instead of causing a `KeyError`.

---

# 10. Create MCP Tool

```python
@mcp.tool()
async def get_alerts(state: str) -> str:
```

This is the **most important line**.

```python
@mcp.tool()
```

registers `get_alerts()` as an **MCP Tool**.

The AI client can discover and call this tool.

The tool accepts:

```text
state → two-letter U.S. state code
```

Example:

```text
CA
NY
TX
```

---

# 11. Build NWS API URL

```python
url = f"{NWS_API_BASE}/alerts/active/area/{state}"
```

For example:

```text
https://api.weather.gov/alerts/active/area/CA
```

This endpoint requests active alerts for the specified state.

---

# 12. Fetch Weather Data

```python
data = await make_nws_request(url)
```

Calls the helper function to retrieve the weather data.

Flow:

```text
get_alerts()
    ↓
make_nws_request()
    ↓
NWS API
    ↓
JSON response
```

---

# 13. Handle Failed/Invalid Response

```python
if not data or "features" not in data:
    return "Unable to fetch alerts or no alerts found."
```

Checks whether:

* API returned no data, or
* expected `"features"` field is missing.

If either occurs, the tool returns an error message.

---

# 14. Handle No Active Alerts

```python
if not data["features"]:
    return "No active alerts for this state."
```

If the API successfully responds but there are no active alerts, return a meaningful message.

---

# 15. Format All Alerts

```python
alerts = [
    format_alert(feature)
    for feature in data["features"]
]
```

Processes every weather alert.

Then:

```python
return "\n---\n".join(alerts)
```

combines multiple alerts into one readable response.

Example:

```text
Alert 1
-------
Alert 2
-------
Alert 3
```

---

# 16. Create MCP Resource

```python
@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"
```

This registers an MCP **Resource**.

Resource URI:

```text
echo://{message}
```

For example:

```text
echo://hello
```

returns:

```text
Resource echo: hello
```

---

# Tool vs Resource — VERY IMPORTANT

### `get_alerts()`

```python
@mcp.tool()
```

**Tool = performs an action**

It makes an API request to retrieve weather alerts.

```text
AI → Tool → NWS API → Result
```

### `echo_resource()`

```python
@mcp.resource(...)
```

**Resource = exposes data/context through a URI**

```text
AI Client → Resource URI → Data
```

### Interview answer

> **Tool is something the model can call to perform an operation; a resource exposes contextual data that can be retrieved using a URI.**

---

# Complete Architecture

```text
                 MCP Client
                     │
                     │ MCP
                     ↓
              ┌──────────────┐
              │  FastMCP     │
              │   Server     │
              └──────┬───────┘
                     │
             ┌───────┴────────┐
             ↓                ↓
       get_alerts()      echo://{message}
          Tool              Resource
             │
             ↓
        NWS Weather API
             │
             ↓
       Weather Alerts
             │
             ↓
         MCP Client
```

---

# What to Remember for Interview

### 6 Key Concepts

**1. `FastMCP`**

→ Simplifies creation of MCP servers.

**2. `@mcp.tool()`**

→ Registers a function as an MCP tool.

**3. `@mcp.resource()`**

→ Registers a resource accessible through a URI.

**4. `httpx.AsyncClient`**

→ Makes asynchronous HTTP requests.

**5. `async/await`**

→ Handles network I/O without blocking the application.

**6. NWS API**

→ External API providing the weather alert data.

---

# Interview-Ready Explanation

> "This is an MCP weather server built using FastMCP. It exposes a `get_alerts` tool that accepts a two-letter U.S. state code and asynchronously calls the National Weather Service API using httpx. The API response is validated and formatted into readable weather alerts. The server also exposes an `echo://{message}` resource as an example of an MCP resource. The main idea is that an MCP client can discover and use the weather tool through the standardized MCP interface without needing to know how the underlying NWS API is implemented."

## One-Line Memory Trick

**`FastMCP → Tool → External API → Result`**

and

**`FastMCP → Resource URI → Data`**

### The 4 things to memorize

**`@mcp.tool()` → Action**

**`@mcp.resource()` → Data/Context**

**`async/await` → Non-blocking I/O**

**`httpx` → HTTP/API calls**

'''