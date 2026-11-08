
from pathlib import Path
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "campaign_model.pkl"


def get_training_data():
    """
    Sample campaign dataset for model demonstration.
    Features:
    1. Impressions
    2. Clicks
    3. Conversions
    4. Budget
    5. Revenue
    """

    X = [
        [1000, 50, 5, 500, 700],
        [2000, 150, 20, 800, 1500],
        [5000, 400, 60, 1200, 3000],
        [800, 10, 1, 600, 200],
        [3000, 250, 35, 1000, 2500],
        [1500, 30, 2, 700, 400],
        [6000, 500, 80, 1500, 4000],
        [900, 15, 1, 500, 150],
        [4000, 300, 45, 1100, 2800],
        [2500, 80, 8, 900, 1000],
        [7000, 650, 100, 2000, 5500],
        [1200, 20, 2, 800, 300],
        [3500, 280, 40, 1000, 2600],
        [1800, 40, 4, 750, 600],
        [5500, 450, 70, 1400, 3800],
        [1000, 12, 0, 650, 100],
        [4500, 380, 55, 1300, 3200],
        [2200, 60, 5, 850, 750],
        [6500, 580, 90, 1800, 4800],
        [750, 8, 0, 450, 50]
    ]

    y = [
        "Good", "Good", "Excellent", "Poor",
        "Excellent", "Poor", "Excellent", "Poor",
        "Excellent", "Average", "Excellent", "Poor",
        "Excellent", "Average", "Excellent", "Poor",
        "Excellent", "Average", "Excellent", "Poor"
    ]

    return X, y


def train_campaign_model():
    """
    Train and save the campaign performance classifier.
    """

    X, y = get_training_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    # Save the trained model
    joblib.dump(model, MODEL_PATH)

    print("====================================")
    print(" MARKETMIND AI MODEL TRAINING")
    print("====================================")
    print("Model: Random Forest Classifier")
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print(f"Accuracy on sample test split: {accuracy * 100:.2f}%")
    print(f"Saved model: {MODEL_PATH}")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        zero_division=0
    ))

    return model


if __name__ == "__main__":
    train_campaign_model()
