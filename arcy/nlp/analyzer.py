"""
Arcy — Azure Language NLP Analyzer
Analyzes user text: sentiment, key phrases, named entities, language detection.
Returns a structured dict that the intent router uses.
"""

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from arcy.core.config import AZURE_LANGUAGE_ENDPOINT, AZURE_LANGUAGE_KEY


def _get_client() -> TextAnalyticsClient:
    """Create and return an Azure Language client."""
    return TextAnalyticsClient(
        endpoint=AZURE_LANGUAGE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_LANGUAGE_KEY)
    )


def analyze(text: str) -> dict:
    """
    Analyze a user message and return a rich understanding dict.

    Returns:
        {
            "sentiment": "positive" | "negative" | "neutral" | "mixed",
            "sentiment_scores": {"positive": 0.9, "neutral": 0.05, "negative": 0.05},
            "key_phrases": ["exam stress", "project deadline"],
            "entities": [{"text": "Monday", "category": "DateTime"}],
            "language": "English",
            "error": None  # or error string if something failed
        }
    """
    if not AZURE_LANGUAGE_KEY:
        # Fallback: return neutral defaults if no key configured yet
        return {
            "sentiment": "neutral",
            "sentiment_scores": {"positive": 0.33, "neutral": 0.34, "negative": 0.33},
            "key_phrases": [],
            "entities": [],
            "language": "English",
            "error": "No Azure Language key configured"
        }

    client = _get_client()
    documents = [text]

    result = {
        "sentiment": "neutral",
        "sentiment_scores": {},
        "key_phrases": [],
        "entities": [],
        "language": "English",
        "error": None
    }

    try:
        # ─── Sentiment Analysis ───────────────────────────────
        sentiment_result = client.analyze_sentiment(documents=documents)
        for doc in sentiment_result:
            if not doc.is_error:
                result["sentiment"] = doc.sentiment
                result["sentiment_scores"] = {
                    "positive": round(doc.confidence_scores.positive, 3),
                    "neutral": round(doc.confidence_scores.neutral, 3),
                    "negative": round(doc.confidence_scores.negative, 3),
                }

        # ─── Key Phrase Extraction ────────────────────────────
        phrase_result = client.extract_key_phrases(documents=documents)
        for doc in phrase_result:
            if not doc.is_error:
                result["key_phrases"] = list(doc.key_phrases)

        # ─── Named Entity Recognition ─────────────────────────
        ner_result = client.recognize_entities(documents=documents)
        for doc in ner_result:
            if not doc.is_error:
                result["entities"] = [
                    {"text": e.text, "category": e.category}
                    for e in doc.entities
                ]

        # ─── Language Detection ───────────────────────────────
        lang_result = client.detect_language(documents=documents)
        for doc in lang_result:
            if not doc.is_error:
                result["language"] = doc.primary_language.name

    except Exception as e:
        result["error"] = str(e)

    return result
