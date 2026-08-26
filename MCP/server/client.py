#unified MCP Client Library - MCP USE

#what mcp agent can do
'''
The agent can:

Understand the question.
Decide whether an MCP capability is required.
Call the appropriate MCP tool/resource through the client.
Receive the result.
Use the LLM to formulate the final response.
Store the conversation in memory.
'''
import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from mcp_use import MCPAgent, MCPClient
import os

async def run_memory_chat():
    """Run a chat using MCPAgent's built-in conversation memory."""
    # Load environment variables for API keys
    load_dotenv()
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

    # Config file path - change this to your config file
    config_file = "server/weather.json"

    print("Initializing chat...")

    # Create MCP client and agent with memory enabled
    client = MCPClient.from_config_file(config_file)
    llm = ChatGroq(model="qwen-qwq-32b")

    # Create agent with memory_enabled=True
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,  # Enable built-in conversation memory
    )

    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("==================================\n")

    try:
        # Main chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ")

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break

            # Check for clear history command
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            # Get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                # Run the agent with the user input (memory handling is automatic)
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        # Clean up
        if client and client.sessions:
            await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())

'''
# MCP Agent + Conversation Memory — Interview Notes

## 1. What this application does

This code creates an **MCP-based conversational agent** using:

* **MCPClient** → connects to MCP servers.
* **MCPAgent** → uses the MCP tools/resources through an LLM.
* **ChatGroq** → provides the LLM.
* **Built-in memory** → maintains conversation history.
* **AsyncIO** → handles asynchronous execution.

**Flow:**

`User → MCPAgent → LLM → MCP Tools → Result → Memory → Response`

---

# 2. Imports

```python id="y1zj8e"
import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient
import os
```

* `asyncio` → runs asynchronous Python code.
* `load_dotenv` → loads environment variables from `.env`.
* `ChatGroq` → Groq LLM integration.
* `MCPClient` → connects to MCP servers.
* `MCPAgent` → creates an agent capable of using MCP capabilities.
* `os` → accesses environment variables.

---

# 3. Async Main Function

```python id="9yp8tq"
async def run_memory_chat():
```

The entire application is asynchronous because MCP communication and agent execution can involve network I/O.

The function contains the interactive chat loop.

---

# 4. Load API Key

```python id="i4l7e6"
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
```

Loads the Groq API key from `.env`.

Example:

```text id="q9ryxf"
GROQ_API_KEY=your_api_key
```

**Interview point:** API keys should be stored in environment variables rather than hardcoded.

---

# 5. MCP Configuration File

```python id="4bq1rt"
config_file = "server/weather.json"
```

This points to the MCP configuration file.

The configuration tells `MCPClient` how to connect to the MCP server.

In this project, it is the **weather MCP server** created earlier.

---

# 6. Create MCP Client

```python id="8j7p1d"
client = MCPClient.from_config_file(config_file)
```

Creates an MCP client using the configuration file.

The client is responsible for connecting to the MCP server and accessing its available capabilities.

### Remember

**MCP Server**

→ exposes tools/resources.

**MCP Client**

→ connects to and uses those tools/resources.

---

# 7. Create Groq LLM

```python id="3a5n8d"
llm = ChatGroq(
    model="qwen-qwq-32b"
)
```

Creates the LLM used by the agent.

The LLM is responsible for understanding the user's request and deciding how to use the available MCP capabilities.

---

# 8. Create MCP Agent

```python id="q8a6re"
agent = MCPAgent(
    llm=llm,
    client=client,
    max_steps=15,
    memory_enabled=True
)
```

This is the **core component**.

### Parameters

**`llm=llm`**

→ LLM used for reasoning/generation.

**`client=client`**

→ MCP client through which the agent accesses MCP servers.

**`max_steps=15`**

→ Maximum number of agent execution steps.

This helps prevent an agent from running indefinitely.

**`memory_enabled=True`**

→ Enables built-in conversation memory.

---

# 9. Architecture

```text id="j3h3q1"
              User
                ↓
            MCPAgent
                ↓
             Groq LLM
                ↓
          MCPClient
                ↓
          MCP Server
                ↓
          Weather Tool
                ↓
          Weather API
                ↓
             Result
                ↓
          Conversation
             Memory
                ↓
             Response
```

---

# 10. Interactive Chat Loop

```python id="o4kqwj"
while True:
    user_input = input("\nYou: ")
```

Continuously waits for user input.

The user can keep asking multiple questions in the same conversation.

---

# 11. Exit Command

```python id="9k7x0w"
if user_input.lower() in ["exit", "quit"]:
    print("Ending conversation...")
    break
```

If the user types:

```text id="1j7c4p"
exit
```

or:

```text id="bfrx9k"
quit
```

the loop stops.

---

# 12. Clear Conversation Memory

```python id="f5a2j7"
if user_input.lower() == "clear":
    agent.clear_conversation_history()
    print("Conversation history cleared.")
    continue
```

If the user types:

```text id="36y5fo"
clear
```

the agent deletes its stored conversation history.

### Important

`memory_enabled=True`

→ enables memory.

`clear_conversation_history()`

→ explicitly removes that memory.

---

# 13. Run the Agent

```python id="7q0q7c"
response = await agent.run(user_input)
```

This sends the user's question to the MCP agent.

The agent can:

1. Understand the question.
2. Decide whether an MCP capability is required.
3. Call the appropriate MCP tool/resource through the client.
4. Receive the result.
5. Use the LLM to formulate the final response.
6. Store the conversation in memory.

---

# 14. Error Handling

```python id="9k0t8w"
try:
    response = await agent.run(user_input)
    print(response)

except Exception as e:
    print(f"\nError: {e}")
```

If agent execution fails, the exception is caught and displayed instead of crashing the entire chat loop.

---

# 15. Cleanup

```python id="y1k3c2"
finally:
    if client and client.sessions:
        await client.close_all_sessions()
```

When the application finishes, it closes all MCP client sessions.

**Why?**

To properly release network connections/resources.

### Interview point

> Always clean up asynchronous/network resources when the application terminates.

---

# 16. Start the Application

```python id="j9v4gq"
if __name__ == "__main__":
    asyncio.run(run_memory_chat())
```

`asyncio.run()` starts the asynchronous `run_memory_chat()` function.

So the execution is:

```text id="6a0y7z"
Python starts
    ↓
asyncio.run()
    ↓
run_memory_chat()
    ↓
Interactive loop
```

---

# What to Remember for Interview

## 7 Key Concepts

### 1. `MCPClient`

**Connects to MCP servers.**

### 2. `MCPAgent`

**Combines the LLM + MCP client and manages agent execution.**

### 3. `ChatGroq`

**Provides the LLM used by the agent.**

### 4. `memory_enabled=True`

**Maintains conversation history across turns.**

### 5. `max_steps`

**Limits how many agent steps can execute.**

### 6. `async/await`

**Handles asynchronous agent/MCP operations.**

### 7. `close_all_sessions()`

**Cleans up MCP connections when finished.**

---

# Most Important Difference

### MCP Server

Provides capabilities.

```text id="q8g5w2"
MCP Server
   ↓
Tools / Resources
```

### MCP Client

Connects to the server.

```text id="8l6psr"
MCP Client → MCP Server
```

### MCP Agent

Uses the LLM + MCP Client to intelligently use those capabilities.

```text id="5h5h9v"
LLM
 ↓
MCPAgent
 ↓
MCPClient
 ↓
MCP Server
 ↓
Tool
```

---

# Memory Flow

```text id="9bq5xs"
User: "What is the weather in NY?"
             ↓
         MCP Agent
             ↓
        Store history
             ↓
User: "What about tomorrow?"
             ↓
      Agent can use previous
       conversation context
```

The second question can be understood in relation to the previous conversation because memory is enabled.

---

# Interview-Ready Explanation

> "This application builds a conversational MCP agent using `mcp-use`. The MCPClient connects to the configured weather MCP server, while MCPAgent combines that client with a Groq-hosted LLM. With `memory_enabled=True`, the agent maintains conversation history across multiple turns, and `max_steps` limits the agent's execution. The application runs asynchronously, accepts user input in an interactive loop, allows the user to clear conversation history, and closes all MCP sessions when the application exits."

## One-Line Memory Trick

**`MCPClient = Connect`**

**`MCPAgent = Reason + Use MCP`**

**`ChatGroq = LLM`**

**`memory_enabled = Remember`**

**`max_steps = Limit`**

**`close_all_sessions = Cleanup`**

### Final Architecture to Remember

```text id="v0g7kr"
                  User
                   ↓
                MCPAgent
              ↙         ↘
           Memory       Groq LLM
                          ↓
                     MCPClient
                          ↓
                     MCP Server
                          ↓
                    Weather Tool
                          ↓
                    External API
                          ↓
                       Result
                          ↓
                       Agent
                          ↓
                    Final Answer
```

'''