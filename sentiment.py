
from textblob import TextBlob


def analyze_sentiment(text):
    """
    Analyze customer feedback using TextBlob.

    Returns:
        sentiment, polarity, subjectivity and message.
    """

    if not isinstance(text, str) or not text.strip():
        return {
            "sentiment": "Neutral",
            "polarity": 0.0,
            "subjectivity": 0.0,
            "message": "No valid feedback provided."
        }

    cleaned_text = " ".join(text.strip().split())

    analysis = TextBlob(cleaned_text).sentiment

    polarity = round(analysis.polarity, 3)
    subjectivity = round(analysis.subjectivity, 3)

    if polarity > 0.10:
        sentiment = "Positive"

    elif polarity < -0.10:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "message": f"Feedback classified as {sentiment}."
    }


def analyze_multiple_feedback(feedback_list):
    """
    Analyze multiple customer feedback entries.
    """

    results = []

    for feedback in feedback_list:

        result = analyze_sentiment(feedback)

        results.append({
            "feedback": feedback,
            **result
        })

    return results


def get_sentiment_summary(feedback_list):
    """
    Generate an overall sentiment summary.
    """

    results = analyze_multiple_feedback(feedback_list)

    positive = sum(
        1 for item in results
        if item["sentiment"] == "Positive"
    )

    negative = sum(
        1 for item in results
        if item["sentiment"] == "Negative"
    )

    neutral = sum(
        1 for item in results
        if item["sentiment"] == "Neutral"
    )

    total = len(results)

    return {
        "total_feedback": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "positive_percentage": round(
            positive / total * 100, 2
        ) if total else 0,
        "negative_percentage": round(
            negative / total * 100, 2
        ) if total else 0,
        "neutral_percentage": round(
            neutral / total * 100, 2
        ) if total else 0,
        "results": results
    }
