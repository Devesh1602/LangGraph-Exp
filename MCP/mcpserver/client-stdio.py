import asyncio
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",  # The command to run your server
        args=["server.py"],  # Arguments to the command
    )

    # Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

              # Call our Weather Tool
            result = await session.call_tool("get_alerts", arguments={"state":"CA"})
            print(f"The weather alerts are = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

'''
# MCP Client with STDIO Transport — Interview Notes

## 1. What this application does

This code creates a **Python MCP client** that connects to an MCP server using **STDIO transport**.

It:

1. Starts `server.py` as a subprocess.
2. Establishes STDIO communication with the server.
3. Initializes an MCP session.
4. Discovers available tools.
5. Calls the `get_alerts` tool with `CA`.
6. Prints the weather-alert response.

**Flow:**

`MCP Client → STDIO → MCP Server → get_alerts("CA") → NWS API → Result`

---

# 2. Imports

```python id="w8k2m5"
import asyncio
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
```

* `asyncio` → runs asynchronous Python code.
* `nest_asyncio` → allows nested asyncio event loops; **it is imported here but not actually used**.
* `ClientSession` → manages the MCP client-server session.
* `StdioServerParameters` → specifies how to start the MCP server.
* `stdio_client` → creates the STDIO communication connection.

---

# 3. Define Async Main Function

```python id="p4x7n2"
async def main():
```

The MCP client uses asynchronous communication, so the main function is defined with `async`.

---

# 4. Define Server Parameters

```python id="k6m3q8"
server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)
```

This tells the MCP client **how to start the server**.

It effectively runs:

```bash
python server.py
```

### Important

The client is not connecting to an already-running HTTP server here.

Instead:

```text id="r3v8m1"
MCP Client
    ↓
Starts subprocess
    ↓
python server.py
    ↓
MCP Server
```

This is the key characteristic of **STDIO transport**.

---

# 5. Connect Using STDIO

```python id="t9c4x6"
async with stdio_client(server_params) as (
    read_stream,
    write_stream
):
```

Creates the communication channel between the client and server.

Two streams are created:

* `read_stream` → client receives data from server.
* `write_stream` → client sends data to server.

Think:

```text id="f7m2q9"
Client ──write──→ Server
Client ←─read──── Server
```

---

# 6. Create MCP Client Session

```python id="v2k8p4"
async with ClientSession(
    read_stream,
    write_stream
) as session:
```

Creates an MCP session using the communication streams.

The `session` object provides methods such as:

```text id="h4m9s2"
session.initialize()
session.list_tools()
session.call_tool()
```

These are used to communicate with the MCP server.

---

# 7. Initialize the Connection

```python id="q8x3m6"
await session.initialize()
```

Initializes the MCP session.

This allows the client and server to establish the MCP connection and exchange the necessary initialization information/capabilities.

**Interview point:**

> `initialize()` establishes the MCP session before normal operations such as listing or calling tools.

---

# 8. Discover Available Tools

```python id="n5r2k7"
tools_result = await session.list_tools()
```

Requests the list of tools exposed by the MCP server.

Then:

```python id="c9v4x1"
for tool in tools_result.tools:
    print(
        f"  - {tool.name}: {tool.description}"
    )
```

prints each tool's:

* Name
* Description

For the weather server, you might see:

```text
get_alerts
get_forecast
```

### Important MCP concept

This demonstrates **tool discovery**.

The client doesn't need to hardcode the complete implementation of the tools. It can ask the server what tools are available.

---

# 9. Call the Weather Tool

```python id="j7m3p8"
result = await session.call_tool(
    "get_alerts",
    arguments={"state": "CA"}
)
```

This is where the MCP client actually invokes the server-side tool.

It requests:

```text id="x5q8n2"
Tool: get_alerts
Argument:
    state = CA
```

The MCP server then executes its `get_alerts()` function.

Remember the previous weather server:

```text id="m4v7c9"
MCP Client
     ↓
call_tool("get_alerts", {"state": "CA"})
     ↓
MCP Server
     ↓
get_alerts("CA")
     ↓
NWS API
     ↓
Weather Alerts
     ↓
MCP Client
```

---

# 10. Read the Tool Result

```python id="k2f6m9"
print(
    f"The weather alerts are = "
    f"{result.content[0].text}"
)
```

The tool result contains content returned by the MCP server.

Here:

```python id="q3n8v5"
result.content[0].text
```

extracts the first text content item.

---

# 11. Run the Client

```python id="s6m2x9"
if __name__ == "__main__":
    asyncio.run(main())
```

`asyncio.run()` starts the asynchronous `main()` function.

Overall:

```text id="w4p8k2"
Python
 ↓
asyncio.run()
 ↓
main()
 ↓
Start server.py
 ↓
Initialize MCP session
 ↓
Discover tools
 ↓
Call get_alerts()
 ↓
Print result
```

---

# STDIO Architecture

```text id="d7m4q9"
┌──────────────────┐
│    MCP Client    │
│                  │
│  ClientSession   │
└────────┬─────────┘
         │
         │ STDIO
         │
         ↓
┌──────────────────┐
│   server.py      │
│   MCP Server     │
│                  │
│  get_alerts()    │
│  get_forecast()  │
└────────┬─────────┘
         │
         ↓
    NWS Weather API
```

---

# What to Remember for Interview

### `StdioServerParameters`

Defines **how to launch the MCP server**.

```text
command = python
args = server.py
```

### `stdio_client()`

Creates the STDIO communication channel.

### `ClientSession`

Manages communication with the MCP server.

### `initialize()`

Starts/initializes the MCP session.

### `list_tools()`

Discovers tools exposed by the server.

### `call_tool()`

Invokes a specific MCP tool.

---

# Most Important Interview Concept

### STDIO MCP

With STDIO:

> **The client starts the MCP server as a local subprocess and communicates with it through standard input/output streams.**

```text id="v8m2k6"
Client
  │
  ├── stdin ───→ Server
  │
  └── stdout ←── Server
```

This is different from the **SSE server** you saw earlier.

### STDIO

```text
Client → Local Process → MCP Server
```

### SSE

```text
Client → Network/SSE → MCP Server
```

---

# Interview-Ready Explanation

> "This code implements an MCP client using STDIO transport. `StdioServerParameters` specifies that the client should start `server.py` using Python. `stdio_client` establishes read and write streams, and `ClientSession` manages the MCP session. After initialization, the client discovers the server's available tools using `list_tools()` and invokes the `get_alerts` tool using `call_tool()`. The server executes the tool and returns the weather alert result to the client."

## One-Line Memory Trick

**`Parameters → Connect → Initialize → Discover → Call → Result`**

```text id="a3m7q1"
StdioServerParameters
        ↓
  stdio_client()
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

### The 6 things to memorize

**`StdioServerParameters` → How to start server**

**`stdio_client` → STDIO connection**

**`ClientSession` → MCP communication**

**`initialize()` → Start session**

**`list_tools()` → Discover tools**

**`call_tool()` → Execute tool**

'''