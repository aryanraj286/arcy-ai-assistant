"""
WebSearch Connector — Arcy's Internet Brain
Uses DuckDuckGo for free, key-less real-time information.
"""

from duckduckgo_search import DDGS
from typing import List, Dict

def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for a given query and return a structured snippet.
    """
    print(f"[WebSearch] Querying: {query}")
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- {r['title']}: {r['body']} ({r['href']})")
        
        if not results:
            return "Sir, I searched the web but found no relevant information for that query."
        
        output = "Sir, here is what I found on the web:\n\n" + "\n".join(results)
        return output
    except Exception as e:
        print(f"[WebSearch] Error: {str(e)}")
        return f"Sir, I encountered an error while searching the web: {str(e)}"

def get_search_results_raw(query: str, max_results: int = 3) -> List[Dict]:
    """
    Returns raw results for AI to process.
    """
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except:
        return []
