"""
MCP Server for Research Assistant

This exposes the research tools as an MCP server that can be Coralized
via the Coralizer tool.
"""

import os
import json
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

# MCP server imports
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent
import mcp.server.stdio

# Load env
from dotenv import load_dotenv
load_dotenv()

# Create MCP server
app = Server("research-assistant")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available research tools."""
    return [
        Tool(
            name="web_search",
            description="Search the web for information on any topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="fetch_url",
            description="Fetch and extract content from a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="track_competitor",
            description="Log a competitor activity for tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor_name": {
                        "type": "string",
                        "description": "Competitor name (e.g., Google A2A, AGNTCY)"
                    },
                    "activity": {
                        "type": "string",
                        "description": "Description of activity"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source URL",
                        "default": ""
                    }
                },
                "required": ["competitor_name", "activity"]
            }
        ),
        Tool(
            name="generate_report",
            description="Generate a structured research report",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Research topic"
                    },
                    "findings": {
                        "type": "string",
                        "description": "Research findings"
                    },
                    "format_type": {
                        "type": "string",
                        "enum": ["markdown", "json", "text"],
                        "default": "markdown"
                    }
                },
                "required": ["topic", "findings"]
            }
        ),
        Tool(
            name="get_competitor_logs",
            description="Get logged competitor activities",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitor": {
                        "type": "string",
                        "description": "Filter by competitor name (optional)",
                        "default": ""
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max entries to return",
                        "default": 50
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute a tool."""
    
    if name == "web_search":
        return await handle_web_search(arguments)
    
    elif name == "fetch_url":
        return await handle_fetch_url(arguments)
    
    elif name == "track_competitor":
        return await handle_track_competitor(arguments)
    
    elif name == "generate_report":
        return await handle_generate_report(arguments)
    
    elif name == "get_competitor_logs":
        return await handle_get_logs(arguments)
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_web_search(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle web search requests."""
    try:
        from duckduckgo_search import DDGS
        
        query = arguments.get("query", "")
        num_results = arguments.get("num_results", 5)
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
        
        if not results:
            return [TextContent(type="text", text="No results found.")]
        
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"{i}. **{r['title']}**\n   URL: {r['href']}\n   {r['body'][:300]}...")
        
        return [TextContent(type="text", text="\n\n".join(formatted))]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Search error: {str(e)}")]


async def handle_fetch_url(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle URL fetching."""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = arguments.get("url", "")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for elem in soup(["script", "style", "nav", "footer", "header"]):
            elem.decompose()
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        content = '\n'.join(lines[:150])
        
        return [TextContent(
            type="text", 
            text=f"Content from {url}:\n\n{content[:8000]}"
        )]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_track_competitor(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle competitor tracking."""
    try:
        competitor = arguments.get("competitor_name", "")
        activity = arguments.get("activity", "")
        source = arguments.get("source", "")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "competitor": competitor,
            "activity": activity,
            "source": source
        }
        
        log_file = "competitor_tracking.json"
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return [TextContent(
            type="text",
            text=f"✓ Logged activity for {competitor}: {activity[:60]}..."
        )]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_generate_report(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle report generation."""
    try:
        topic = arguments.get("topic", "")
        findings = arguments.get("findings", "")
        format_type = arguments.get("format_type", "markdown")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if format_type == "markdown":
            report = f"""# Research Report: {topic}

**Generated:** {timestamp}  
**Agent:** Research Assistant (Coral Protocol)

---

## Findings

{findings}

---

*Report generated by Coral Protocol Research Agent*
"""
        
        elif format_type == "json":
            report = json.dumps({
                "topic": topic,
                "timestamp": timestamp,
                "findings": findings
            }, indent=2)
        
        else:
            report = f"RESEARCH REPORT: {topic}\nGenerated: {timestamp}\n\n{findings}"
        
        return [TextContent(type="text", text=report)]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_get_logs(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle getting competitor logs."""
    try:
        competitor_filter = arguments.get("competitor", "")
        limit = arguments.get("limit", 50)
        
        log_file = "competitor_tracking.json"
        
        if not os.path.exists(log_file):
            return [TextContent(type="text", text="No logs found.")]
        
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        if competitor_filter:
            logs = [l for l in logs if competitor_filter.lower() in l.get("competitor", "").lower()]
        
        logs = logs[-limit:]  # Get most recent
        
        if not logs:
            return [TextContent(type="text", text="No matching logs found.")]
        
        formatted = []
        for log in logs:
            formatted.append(f"[{log['timestamp'][:10]}] {log['competitor']}: {log['activity'][:80]}...")
        
        return [TextContent(type="text", text="\n".join(formatted))]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
