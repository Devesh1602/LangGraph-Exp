import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

nest_asyncio.apply()  # Needed to run interactive python

"""
Make sure:
1. The server is running before running this script.
2. The server is configured to use SSE transport.
3. The server is listening on port 8050.

To run the server:
uv run server.py
"""


async def main():
    # Connect to the server using SSE
    async with sse_client("http://localhost:8000/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our Weather tool
            result = await session.call_tool("get_alerts", arguments={"state":"CA"})
            print(f"The weather alerts are = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

'''
# MCP Client with SSE Transport — Interview Notes

## 1. What this application does

This code creates an **MCP client that connects to an already-running MCP server using SSE (Server-Sent Events)**.

Unlike the previous STDIO client, this client **does not start `server.py`**. The MCP server must already be running and listening on the configured SSE endpoint.

**Flow:**

`MCP Client → SSE → Running MCP Server → get_alerts("CA") → NWS API → Result`

---

# 2. Imports

```python
import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
```

* `asyncio` → runs asynchronous Python code.
* `nest_asyncio` → allows nested event loops, useful in interactive environments such as Jupyter.
* `ClientSession` → manages the MCP client-server session.
* `sse_client` → creates an SSE connection to the MCP server.

### Important difference from previous code

Previous:

```python
from mcp.client.stdio import stdio_client
```

Here:

```python
from mcp.client.sse import sse_client
```

So the **transport mechanism changes from STDIO → SSE**.

---

# 3. Apply `nest_asyncio`

```python
nest_asyncio.apply()
```

Allows an existing asyncio event loop to be reused/nested.

This is especially useful when running the code inside **Jupyter/IPython**, where an event loop may already be running.

**Interview point:**

> `nest_asyncio` is not an MCP requirement; it is mainly useful when running asynchronous code in an interactive environment.

---

# 4. Server Requirements

The comments specify that:

1. The MCP server must already be running.
2. The server must use **SSE transport**.
3. The server must expose the SSE endpoint at the specified URL.

The server is started separately, for example:

```bash
uv run server.py
```

Then this client connects to it.

### Important architecture difference

**STDIO client:**

```text
Client
  ↓
Starts server.py
  ↓
MCP Server
```

**SSE client:**

```text
MCP Server
  ↑
Already running
  ↑
SSE
  ↑
MCP Client
```

---

# 5. Create Async Main Function

```python
async def main():
```

The MCP communication is asynchronous, so the main function uses `async`.

---

# 6. Connect Using SSE

```python
async with sse_client(
    "http://localhost:8000/sse"
) as (read_stream, write_stream):
```

This is the most important line.

The client connects to:

```text
http://localhost:8000/sse
```

using **SSE transport**.

Two communication streams are provided:

* `read_stream` → receives messages from the server.
* `write_stream` → sends messages to the server.

Conceptually:

```text
Client ── request ──→ Server
Client ←── response ─ Server
          via SSE
```

---

# 7. Create MCP Session

```python
async with ClientSession(
    read_stream,
    write_stream
) as session:
```

Creates an MCP session using the streams created by `sse_client()`.

The `session` object provides MCP operations such as:

```text
initialize()
list_tools()
call_tool()
```

---

# 8. Initialize Connection

```python
await session.initialize()
```

Initializes the MCP session.

Before calling tools, the client and server need to complete the MCP initialization process.

**Remember:**

`Connect → Initialize → Use MCP`

---

# 9. Discover Available Tools

```python
tools_result = await session.list_tools()
```

Requests the tools exposed by the MCP server.

Then:

```python
for tool in tools_result.tools:
    print(
        f"  - {tool.name}: {tool.description}"
    )
```

prints each tool's name and description.

For the weather server, you may see:

```text
get_alerts
get_forecast
```

### Interview point

This demonstrates **dynamic tool discovery**.

The client can ask the MCP server:

> "What tools do you provide?"

---

# 10. Call the Weather Tool

```python
result = await session.call_tool(
    "get_alerts",
    arguments={"state": "CA"}
)
```

The client invokes the server's `get_alerts` tool.

It passes:

```text
state = CA
```

The server then executes:

```python
get_alerts("CA")
```

which calls the NWS API.

---

# 11. Read the Result

```python
print(
    f"The weather alerts are = "
    f"{result.content[0].text}"
)
```

The MCP server returns a result containing content.

```python
result.content[0].text
```

extracts the first text response.

---

# 12. Run the Client

```python
if __name__ == "__main__":
    asyncio.run(main())
```

Starts the asynchronous client.

Overall:

```text
Python
  ↓
asyncio.run()
  ↓
main()
  ↓
Connect to SSE
  ↓
Initialize MCP
  ↓
Discover tools
  ↓
Call get_alerts()
  ↓
Print result
```

---

# SSE Architecture

```text
              ┌──────────────────┐
              │    MCP Client    │
              │                  │
              │  ClientSession   │
              └────────┬─────────┘
                       │
                       │ SSE
                       │
                       ↓
              ┌──────────────────┐
              │   MCP Server     │
              │ localhost:8000   │
              │                  │
              │ get_alerts()     │
              │ get_forecast()   │
              └────────┬─────────┘
                       │
                       ↓
                 NWS Weather API
```

---

# STDIO vs SSE — VERY IMPORTANT

This is one of the most useful interview comparisons from these examples.

|               | STDIO                | SSE                         |
| ------------- | -------------------- | --------------------------- |
| Server        | Client starts server | Server already running      |
| Communication | stdin/stdout         | Network connection          |
| Typical use   | Local process        | Network/server connection   |
| Client code   | `stdio_client()`     | `sse_client()`              |
| Server launch | Managed by client    | Separate process            |
| Example       | `python server.py`   | `http://localhost:8000/sse` |

### Easy memory trick

**STDIO:**

> "Start the server and talk to its input/output."

**SSE:**

> "Connect to a server that is already running."

---

# What to Remember for Interview

### `sse_client()`

→ Creates the SSE connection to the MCP server.

### `ClientSession`

→ Manages MCP communication.

### `initialize()`

→ Initializes the MCP session.

### `list_tools()`

→ Discovers server tools.

### `call_tool()`

→ Executes a specific tool.

### `nest_asyncio.apply()`

→ Helps asynchronous code run inside an already-running event loop.

---

# Interview-Ready Explanation

> "This code implements an MCP client using SSE transport. Unlike the STDIO version, the client does not launch the MCP server; the server must already be running and expose an SSE endpoint. The client connects using `sse_client`, creates a `ClientSession`, initializes the MCP connection, discovers available tools using `list_tools()`, and invokes the `get_alerts` tool using `call_tool()`. The server executes the tool, retrieves weather data from the NWS API, and returns the result to the client."

## One-Line Memory Trick

**`SSE Client → Connect → Initialize → Discover → Call → Result`**

```text
sse_client()
     ↓
ClientSession
     ↓
initialize()
     ↓
list_tools()
     ↓
call_tool()
     ↓
Result
```

### Core interview distinction

**STDIO:**

`Client → Starts Server → stdin/stdout`

**SSE:**

`Client → Network/SSE → Already-running Server`

'''