import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

def get_search_tool():
    """
    Returns a configured Tavily search tool.
    Requires TAVILY_API_KEY in the .env file.
    """
    return TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True
    )

def format_search_results(results: list) -> str:
    """Helper to format search tool output for the LLM."""
    formatted = ""
    for res in results:
        formatted += f"Title: {res['title']}\nURL: {res['url']}\nContent: {res['content']}\n---\n"
    return formatted
