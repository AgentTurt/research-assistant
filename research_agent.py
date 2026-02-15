"""
Research Assistant Agent - Coralized for Coral Protocol

This agent connects to the Coral Server via MCP and provides research capabilities
to the multi-agent ecosystem.
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# MCP imports for Coral integration
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

# Load environment variables
load_dotenv()

# ============================================================================
# NATIVE TOOLS (Agent's own capabilities)
# ============================================================================

@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for information on a given topic.
    
    Args:
        query: The search query string
        num_results: Number of results to return (default 5)
    
    Returns:
        A summary of search results
    """
    try:
        # Using DuckDuckGo for search (no API key needed)
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
        
        if not results:
            return "No results found for the query."
        
        formatted_results = []
        for i, r in enumerate(results, 1):
            formatted_results.append(f"{i}. {r['title']}\n   {r['href']}\n   {r['body'][:200]}...")
        
        return "\n\n".join(formatted_results)
    
    except ImportError:
        return "Error: duckduckgo-search not installed. Run: pip install duckduckgo-search"
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def fetch_url(url: str) -> str:
    """
    Fetch and extract content from a URL.
    
    Args:
        url: The URL to fetch
    
    Returns:
        Extracted text content from the page
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines[:100])  # Limit to first 100 lines
        
        return f"Content from {url}:\n\n{text[:5000]}"
    
    except Exception as e:
        return f"Error fetching URL: {str(e)}"


@tool
def track_competitor(competitor_name: str, activity: str, source: str = "") -> str:
    """
    Track a competitor activity and log it to the database.
    
    Args:
        competitor_name: Name of the competitor (e.g., "Google A2A", "AGNTCY", "ANP")
        activity: Description of the activity/news
        source: URL or source of the information
    
    Returns:
        Confirmation that the activity was logged
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "competitor": competitor_name,
        "activity": activity,
        "source": source
    }
    
    # In production, this would write to a database
    # For now, we append to a local JSON file
    log_file = "competitor_tracking.json"
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return f"✓ Logged activity for {competitor_name}: {activity[:50]}..."
    
    except Exception as e:
        return f"Error logging activity: {str(e)}"


@tool
def generate_report(topic: str, findings: str, format_type: str = "markdown") -> str:
    """
    Generate a structured research report.
    
    Args:
        topic: The research topic
        findings: The research findings/content
        format_type: Output format (markdown, json, or text)
    
    Returns:
        Formatted report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if format_type == "markdown":
        report = f"""# Research Report: {topic}

**Generated:** {timestamp}  
**Agent:** Research Assistant (Coral Protocol)

---

## Summary

{findings[:500]}

## Detailed Findings

{findings}

---

*Report generated by Coral Protocol Research Agent*
"""
    
    elif format_type == "json":
        report = json.dumps({
            "topic": topic,
            "timestamp": timestamp,
            "summary": findings[:500],
            "findings": findings
        }, indent=2)
    
    else:  # text
        report = f"""RESEARCH REPORT: {topic}
Generated: {timestamp}

{findings}
"""
    
    # Save to file
    filename = f"report_{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.{format_type if format_type != 'markdown' else 'md'}"
    
    try:
        with open(filename, 'w') as f:
            f.write(report)
        return f"Report saved to {filename}\n\n{report[:1000]}..."
    except Exception as e:
        return f"Error saving report: {str(e)}\n\n{report[:1000]}..."


@tool
def summarize_paper(paper_text: str, max_length: int = 500) -> str:
    """
    Summarize a technical paper or long document.
    
    Args:
        paper_text: The full text of the paper
        max_length: Maximum length of summary in words
    
    Returns:
        A structured summary
    """
    # This is a placeholder - in production, this would use the LLM
    # to generate a proper summary
    return f"""Paper Summary (max {max_length} words):

Key Points:
- {paper_text[:200]}...

[Full summarization would be performed by the LLM using this tool]
"""


# ============================================================================
# CORAL INTEGRATION
# ============================================================================

def get_tools_description(tools: List[Any]) -> str:
    """Generate a description of available tools."""
    descriptions = []
    for tool in tools:
        descriptions.append(f"- {tool.name}: {tool.description}")
    return "\n".join(descriptions)


async def create_coralized_agent():
    """
    Create a Coralized agent that connects to the Coral Server.
    """
    
    # Get configuration from environment
    coral_url = os.getenv("CORAL_SSE_URL")
    agent_id = os.getenv("CORAL_AGENT_ID", "research_assistant")
    agent_description = os.getenv("CORAL_AGENT_DESCRIPTION", "Research assistant agent")
    
    # Build Coral Server URL with query parameters
    if coral_url:
        separator = "&" if "?" in coral_url else "?"
        coral_url = f"{coral_url}{separator}agentId={agent_id}&agentDescription={agent_description.replace(' ', '%20')}"
    
    # Initialize the model
    model = ChatOpenAI(
        model="gpt-4o-mini",  # Using mini model for efficiency
        temperature=0.3,
        max_tokens=4096
    )
    
    # Define native tools
    native_tools = [
        web_search,
        fetch_url,
        track_competitor,
        generate_report,
        summarize_paper
    ]
    
    # Connect to Coral Server if URL is provided
    all_tools = native_tools.copy()
    coral_client = None
    
    if coral_url:
        print(f"🔌 Connecting to Coral Server at {coral_url[:50]}...")
        
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                coral_client = MultiServerMCPClient(
                    {
                        "coral": {
                            "url": coral_url,
                            "transport": "sse",
                            "timeout": 600,
                            "sse_read_timeout": 600,
                        }
                    }
                )
                
                # Load Coral tools
                coral_tools = await coral_client.get_tools()
                all_tools.extend(coral_tools)
                
                print(f"✓ Connected to Coral Server with {len(coral_tools)} Coral tools")
                break
                
            except Exception as e:
                print(f"⚠ Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    print("⚠ Could not connect to Coral Server. Running with native tools only.")
    else:
        print("⚠ No CORAL_SSE_URL set. Running in standalone mode.")
    
    # Create the prompt template
    tools_description = get_tools_description(all_tools)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a Research Assistant Agent in the Coral Protocol ecosystem.

Your role is to perform research tasks, track competitors, and generate reports.

AVAILABLE TOOLS:
{tools_description}

CORAL SERVER TOOLS (if connected):
- list_agents: List all connected agents
- create_thread: Create a new conversation thread
- add_participant: Add an agent to a thread
- send_message: Send a message to a thread
- wait_for_mentions: Wait for responses from other agents

WORKFLOW FOR MULTI-AGENT COLLABORATION:
1. When given a research task, first check if other agents can help
2. Use list_agents to see who's available
3. Create a thread and add relevant agents
4. Send messages to collaborate
5. Wait for responses before proceeding
6. Synthesize findings and generate reports

IMPORTANT:
- You MUST NEVER finish the chain until the user explicitly says they're done
- Always ask if the user needs more research or has follow-up questions
- Be thorough but concise in your research
- Cite sources when possible
- Track competitor activities when relevant

Your agent ID is: {agent_id}
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_tool_calling_agent(model, all_tools, prompt)
    
    # Create the executor
    executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=20
    )
    
    return executor, coral_client


async def main():
    """
    Main entry point for the Research Assistant Agent.
    """
    print("=" * 60)
    print("🔬 Research Assistant Agent (Coral Protocol)")
    print("=" * 60)
    print()
    
    # Create the agent
    executor, coral_client = await create_coralized_agent()
    
    print("\n✓ Agent initialized and ready")
    print("\nCapabilities:")
    print("  • Web search")
    print("  • URL content extraction")
    print("  • Competitor tracking")
    print("  • Report generation")
    print("  • Paper summarization")
    print("  • Multi-agent collaboration (via Coral)")
    print()
    
    # Interactive loop
    chat_history = []
    
    print("Enter your research questions (type 'exit' to quit):\n")
    
    while True:
        try:
            user_input = input("\n📝 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🔍 Researching...\n")
            
            # Run the agent
            result = await executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            # Update chat history
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=result["output"]))
            
            # Keep history manageable
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]
            
            print(f"\n🤖 Agent: {result['output']}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    # Cleanup
    if coral_client:
        await coral_client.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(main())
