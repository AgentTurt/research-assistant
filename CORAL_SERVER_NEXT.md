# Research Assistant Agent for coral-server-next v1.1-beta

This version is specifically compatible with the Kotlin-based `coral-server-next` v1.1-beta implementation.

## coral-server-next v1.1-beta Compatibility

The `coral-server-next` (https://github.com/Coral-Protocol/coral-server-next) is the Kotlin implementation of the Coral Protocol. It provides MCP server tools for agent communication.

### API Discovery

When coral-server-next is running, the full API specification is available at:
```
http://localhost:5555/api_v1.json
```

This endpoint provides the complete API collection including all available endpoints.

### Key Features:

1. **Docker-based by default** - Agents run as Docker containers
2. **Registry-based** - Uses `registry.toml` for agent registration
3. **Thread-based messaging** - All communication happens through threads
4. **MCP-native** - Built from ground up as an MCP server
5. **API Documentation** - Auto-generated API spec at `/api_v1.json`

## Configuration for coral-server-next v1.1-beta

### 1. Registry Configuration

Add to your `registry.toml`:

```toml
[agents.research_assistant]
name = "Research Assistant"
description = "Research assistant that performs web searches and tracks competitors"
image = "research-assistant:latest"
capabilities = ["web_search", "competitor_tracking", "report_generation"]
```

### 2. Environment Variables

```bash
# Required
OPENAI_API_KEY=your_key

# For standalone mode (no Coral Server)
# (leave CORAL_SSE_URL unset)

# For Coral Server integration (v1.1-beta)
CORAL_SSE_URL=http://localhost:5555/sse
CORAL_AGENT_ID=research_assistant
CORAL_AGENT_DESCRIPTION="Research assistant agent"
```

### 3. Running with coral-server-next

#### Option A: As Docker Agent (Recommended)

```bash
# Build the Docker image
docker build -t research-assistant:latest .

# The Coral Server will manage the container
```

#### Option B: As External Agent via SSE

```bash
# Run the agent locally, connecting to Coral Server
export CORAL_SSE_URL="http://localhost:5555/sse"
python research_agent.py
```

#### Option C: As MCP Server

```bash
# Run as MCP server for Coralizer
python research_mcp_server.py
```

## Tool Compatibility

The agent dynamically discovers Coral Server tools. Expected tools from coral-server-next:

| Tool | Purpose |
|------|---------|
| `list_agents` | List registered agents |
| `create_thread` | Create a new thread |
| `add_participant` | Add agent to thread |
| `send_message` | Send message to thread |
| `wait_for_mentions` | Wait for responses |

## Testing with coral-server-next

1. Start coral-server-next:
```bash
docker run -p 5555:5555 \
  -v $(pwd)/registry.toml:/config/registry.toml \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/coral-protocol/coral-server
```

2. Verify the API is accessible:
```bash
curl http://localhost:5555/api_v1.json
```

3. Run the agent:
```bash
python research_agent.py
```

4. The agent will:
   - Connect to the Coral Server SSE endpoint
   - Discover available tools dynamically
   - Register itself (if configured in registry.toml)
   - Be available for multi-agent collaboration

## Troubleshooting

### Connection Issues

If the agent can't connect to coral-server-next:

1. Verify the API is accessible:
```bash
curl http://localhost:5555/api_v1.json
```

2. Check the SSE endpoint:
```bash
curl http://localhost:5555/sse
```

3. Check Docker networking (if using Docker):
```bash
docker network ls
docker network inspect <coral-network>
```

4. Ensure registry.toml is properly configured

### Tool Discovery

The agent logs discovered tools on startup. Check the output for:
```
✓ Connected to Coral Server with X tools
```

If tools aren't discovered, the agent will still work in standalone mode.

## Architecture

```
┌─────────────────────────────────────────┐
│  coral-server-next v1.1-beta (Kotlin)   │
│  - Port 5555                            │
│  - SSE endpoint: /sse                   │
│  - API docs: /api_v1.json               │
│  - Docker orchestration                 │
└──────────────┬──────────────────────────┘
               │ SSE/MCP
┌──────────────▼──────────────────────────┐
│  Research Assistant Agent               │
│  - LangChain agent                      │
│  - Native research tools                │
│  - Dynamic Coral tool discovery         │
└─────────────────────────────────────────┘
```
