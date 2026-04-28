"""
Arcy — News Connector
Fetches top headlines using NewsAPI's free tier.
Sign up free at: https://newsapi.org (500 requests/day free)
"""

import requests
from arcy.core.config import NEWS_API_KEY


def get_top_headlines(topic: str = None, count: int = 3) -> str:
    """
    Fetch top news headlines and return a natural language summary.

    Args:
        topic: Optional topic like "technology", "sports", "india"
        count: Number of headlines to return (max 3 for voice readability)

    Returns:
        Human-readable news string for Arcy to say
    """
    if not NEWS_API_KEY:
        return (
            "I'd love to brief you on the latest news, but I need a NewsAPI key. "
            "It's free at newsapi.org — add it to your .env as NEWS_API_KEY."
        )

    try:
        if topic:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": topic,
                "apiKey": NEWS_API_KEY,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": count,
            }
        else:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "country": "in",   # India headlines by default
                "apiKey": NEWS_API_KEY,
                "pageSize": count,
            }

        resp = requests.get(url, params=params, timeout=6)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])

        if not articles:
            return "I couldn't find any relevant news right now. Try again in a moment."

        headlines = [a["title"] for a in articles[:count] if a.get("title")]

        if len(headlines) == 1:
            return f"Here's the top story: {headlines[0]}"
        elif len(headlines) == 2:
            return f"Top two stories: First, {headlines[0]}. And second, {headlines[1]}."
        else:
            return (
                f"Here are the top {len(headlines)} stories. "
                f"One: {headlines[0]}. "
                f"Two: {headlines[1]}. "
                f"Three: {headlines[2]}."
            )

    except Exception as e:
        return f"I couldn't reach the news service right now: {e}"
