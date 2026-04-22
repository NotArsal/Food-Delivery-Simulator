"""
ML Prediction utilities for delivery ETA.
"""
import os
import joblib
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MODEL_FILE = os.path.join(DATA_DIR, "eta_model.pkl")

_model = None


def load_model():
    """Load the trained model."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError(
                f"Model not found at {MODEL_FILE}. "
                "Run train_model.py first."
            )
        _model = joblib.load(MODEL_FILE)
        print(f"[ML] Model loaded from {MODEL_FILE}")
    return _model


def predict_eta(distance, traffic_level=1.0, num_stops=1, hour=12):
    """
    Predict delivery ETA.

    Args:
        distance: route distance in meters
        traffic_level: traffic multiplier (1.0, 1.3, 1.8)
        num_stops: number of delivery stops
        hour: hour of day (0-23)

    Returns:
        Predicted delivery time in minutes
    """
    model = load_model()
    features = pd.DataFrame([{
        "route_distance": distance,
        "traffic_level": traffic_level,
        "num_stops": num_stops,
        "hour_of_day": hour,
    }])
    prediction = model.predict(features)[0]
    return max(1.0, prediction)


def predict_batch(features_list):
    """Predict ETA for multiple deliveries."""
    model = load_model()
    df = pd.DataFrame(features_list)
    predictions = model.predict(df)
    return [max(1.0, p) for p in predictions]
