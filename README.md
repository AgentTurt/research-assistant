# Research Assistant Agent

A production-ready, Coral-compatible research agent for the Coral Protocol ecosystem.

> **Note:** This agent is compatible with both the original Coral Server and [`coral-server-next`](https://github.com/Coral-Protocol/coral-server-next) (the newer Kotlin implementation). See [CORAL_SERVER_NEXT.md](CORAL_SERVER_NEXT.md) for specific configuration details.

## 🚀 Quick Start

### Option 1: Standalone Mode (No Coral Server)

```bash
cd agents/research-assistant

# Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key

# Run
python research_agent.py
```

### Option 2: Coralized Mode (With Coral Server)

```bash
# Setup environment
export CORAL_SSE_URL="http://localhost:5555/devmode/exampleApplication/privkey/session1/sse"
export CORAL_AGENT_ID="research_assistant"
export OPENAI_API_KEY="your-key"

# Run with Coral integration
python research_agent.py
```

### Option 3: Docker

```bash
# Build and run
docker-compose up -d

# Or manually
docker build -t coral-research-agent .
docker run -e CORAL_SSE_URL=... -e OPENAI_API_KEY=... coral-research-agent
```

## 🛠 Tools Provided

| Tool | Description | Use Case |
|------|-------------|----------|
| `web_search` | Search the web via DuckDuckGo | Quick research on any topic |
| `fetch_url` | Extract content from URLs | Deep dive into articles/papers |
| `track_competitor` | Log competitor activities | Track Google A2A, AGNTCY, etc. |
| `generate_report` | Create structured reports | Share findings with team |
| `summarize_paper` | Summarize technical papers | Quick paper analysis |
| `get_competitor_logs` | View tracked competitors | Monitor competition over time |

## 🔌 Coral Protocol Integration

When connected to a Coral Server, this agent can:

- **Collaborate** with other agents on research tasks
- **Receive** research assignments via messages
- **Publish** findings to threads for team access
- **Get paid** via $CORAL token for research services

### Multi-Agent Workflow Example

```
User: "Research the latest on Google A2A and share with the team"

Research Agent:
1. Uses web_search to find latest A2A news
2. Uses track_competitor to log findings
3. Uses create_thread to start a discussion
4. Uses add_participant to invite team agents
5. Uses send_message to share summary
```

## 📁 File Structure

```
research-assistant/
├── research_agent.py          # Full LangChain agent with Coral integration
├── research_mcp_server.py     # MCP server for Coralizer compatibility
├── coral.json                 # Coral metadata/configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── start.sh                  # Quick start script
├── Dockerfile                # Container build
├── docker-compose.yml        # Docker orchestration
├── test_tools.py             # Tool testing
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes* | OpenAI API key (or use GROQ/Anthropic) |
| `CORAL_SSE_URL` | No | Coral Server SSE endpoint |
| `CORAL_AGENT_ID` | No | Unique agent ID (default: research_assistant) |
| `CORAL_AGENT_DESCRIPTION` | No | Agent description for discovery |

*Or set GROQ_API_KEY or ANTHROPIC_API_KEY and update model in code

### Coral.json Fields

```json
{
  "coral": {
    "agentId": "research_assistant",
    "agentType": "service",
    "capabilities": ["web_search", "content_extraction", ...],
    "category": "research",
    "pricing": {
      "model": "per_task",
      "basePrice": 0.001  // in $CORAL
    }
  }
}
```

## 💡 Usage Examples

### Example 1: Competitor Research

```
📝 You: Track what Google A2A launched this week

🤖 Agent: I'll search for the latest Google A2A updates and log them.

[Uses web_search to find news]
[Uses track_competitor to log: "Google A2A - New SDK release v1.2"]

✓ Logged activity for Google A2A: New SDK release v1.2 with improved...
```

### Example 2: Generate Report

```
📝 You: Research multi-agent protocols and generate a markdown report

🤖 Agent: I'll research the multi-agent protocol landscape and create a report.

[Uses web_search for A2A, AGNTCY, ANP, Coral]
[Uses generate_report with format_type="markdown"]

✓ Report saved to report_multi_agent_protocols_20250215_1430.md
```

### Example 3: Multi-Agent Collaboration

When connected to Coral Server:

```
📝 You: Ask the content agent to help write about our A2A findings

🤖 Agent: 
1. [Uses list_agents] Found: content_writer_agent, seo_agent
2. [Uses create_thread] Created thread: "A2A Analysis"
3. [Uses add_participant] Added content_writer_agent
4. [Uses send_message] "@content_writer_agent - Please write a blog post 
   about Google A2A's new features based on this research: [summary]"
5. [Uses wait_for_mentions] Waiting for response...
```

## 🧪 Testing

```bash
# Test individual tools
python test_tools.py

# Test full agent (interactive)
python research_agent.py
```

## 🚢 Deployment

### To Coral Registry

1. Ensure `coral.json` is properly configured
2. Use Coralizer to package:
   ```bash
   coraliser package ./research-assistant
   ```
3. Publish to registry:
   ```bash
   coral publish research-assistant-v1.0.0.tar.gz
   ```

### As Remote Agent

Deploy to Coral Cloud as a Remote Agent for automatic scaling and monetization.

## 📄 License

MIT - See LICENSE file

## 🤝 Contributing

This is a reference implementation for Coral Protocol. Feel free to extend with:
- Additional research sources (ArXiv, Google Scholar)
- More output formats (PDF, DOCX)
- Integration with specific APIs (Crunchbase, LinkedIn)
- Advanced competitor analysis features
