"""
Train Random Forest model for delivery time prediction.
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MODEL_FILE = os.path.join(DATA_DIR, "eta_model.pkl")
TRAINING_DATA = os.path.join(DATA_DIR, "training_data.csv")


def train_model():
    """Train a Random Forest Regressor for ETA prediction."""

    if not os.path.exists(TRAINING_DATA):
        print("Training data not found. Generating...")
        from generate_training_data import generate_training_data
        generate_training_data()

    print(f"Loading training data from {TRAINING_DATA}...")
    df = pd.read_csv(TRAINING_DATA)

    # Features and target
    feature_cols = ["route_distance", "traffic_level", "num_stops", "hour_of_day"]
    X = df[feature_cols]
    y = df["delivery_time_minutes"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # Train Random Forest
    print("\nTraining Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"\n{'='*50}")
    print(f"Model Evaluation Results")
    print(f"{'='*50}")
    print(f"MAE:  {mae:.2f} minutes")
    print(f"RMSE: {rmse:.2f} minutes")
    print(f"R²:   {r2:.4f}")
    print(f"{'='*50}")

    # Feature importances
    print(f"\nFeature Importances:")
    for feat, imp in sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    ):
        print(f"  {feat}: {imp:.4f}")

    # Save model
    os.makedirs(DATA_DIR, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print(f"\nModel saved to {MODEL_FILE}")

    # Sample predictions
    print(f"\nSample Predictions:")
    samples = [
        {"route_distance": 3000, "traffic_level": 1.0, "num_stops": 1, "hour_of_day": 14},
        {"route_distance": 8000, "traffic_level": 1.3, "num_stops": 2, "hour_of_day": 9},
        {"route_distance": 12000, "traffic_level": 1.8, "num_stops": 3, "hour_of_day": 18},
    ]
    for s in samples:
        pred = model.predict(pd.DataFrame([s]))[0]
        print(f"  Dist={s['route_distance']}m, Traffic={s['traffic_level']}, "
              f"Stops={s['num_stops']}, Hour={s['hour_of_day']} -> {pred:.1f} min")

    return model, {"mae": mae, "rmse": rmse, "r2": r2}


if __name__ == "__main__":
    train_model()
