
from pathlib import Path
import joblib

from ai_models.train_model import MODEL_PATH, train_campaign_model


def load_campaign_model():
    """
    Load the saved campaign model.
    If the model file is missing, train it first.
    """

    if not MODEL_PATH.exists():
        train_campaign_model()

    try:
        return joblib.load(MODEL_PATH)

    except (OSError, ValueError):
        # Re-train if the saved model cannot be loaded.
        train_campaign_model()
        return joblib.load(MODEL_PATH)


def predict_campaign_performance(
    impressions,
    clicks,
    conversions,
    budget,
    revenue
):
    """
    Predict campaign performance category.

    Categories:
    Poor, Average, Good, Excellent
    """

    values = [
        impressions,
        clicks,
        conversions,
        budget,
        revenue
    ]

    try:
        values = [float(value or 0) for value in values]

        if any(value < 0 for value in values):
            raise ValueError("Campaign values cannot be negative.")

        model = load_campaign_model()

        prediction = model.predict([values])[0]

        probabilities = model.predict_proba([values])[0]

        confidence = round(max(probabilities) * 100, 2)

        return {
            "prediction": str(prediction),
            "confidence": confidence,
            "message": (
                f"The model classifies this campaign as {prediction}."
            )
        }

    except (TypeError, ValueError) as error:
        return {
            "prediction": "Unavailable",
            "confidence": 0,
            "message": str(error)
        }


def predict_from_campaign(campaign):
    """
    Predict performance using a campaign database record.
    """

    return predict_campaign_performance(
        impressions=campaign["impressions"],
        clicks=campaign["clicks"],
        conversions=campaign["conversions"],
        budget=campaign["budget"],
        revenue=campaign["revenue"]
    )
