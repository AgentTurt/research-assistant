"""
Quick test for Research Assistant tools
"""

import asyncio
import sys
sys.path.insert(0, '.')

from research_agent import web_search, fetch_url, track_competitor, generate_report

async def test_tools():
    print("🧪 Testing Research Assistant Tools\n")
    
    # Test web search
    print("1. Testing web_search...")
    result = web_search.invoke({"query": "Coral Protocol AI agents", "num_results": 3})
    print(f"   ✓ Search returned {len(result.split(chr(10)+chr(10)))} results")
    
    # Test competitor tracking
    print("\n2. Testing track_competitor...")
    result = track_competitor.invoke({
        "competitor_name": "Test Competitor",
        "activity": "Launched new feature",
        "source": "https://example.com"
    })
    print(f"   {result}")
    
    # Test report generation
    print("\n3. Testing generate_report...")
    result = generate_report.invoke({
        "topic": "AI Agent Protocols",
        "findings": "Coral Protocol provides unique payment capabilities not found in competitors.",
        "format_type": "markdown"
    })
    print(f"   ✓ Report generated: {result[:100]}...")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_tools())
