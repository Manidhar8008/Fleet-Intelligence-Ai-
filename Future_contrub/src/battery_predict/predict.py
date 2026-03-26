import joblib
import numpy as np
import pandas as pd

# Load
model = joblib.load('src/battery_predict/battery_model.pkl')
feature_cols = joblib.load('src/battery_predict/battery_features.pkl')

def predict_battery(latitude, longitude, is_disabled, is_reserved, vehicle_type):
    # Handle one-hot encoding
    data = {col: 0 for col in feature_cols}
    data.update({
        'latitude': latitude,
        'longitude': longitude,
        'is_disabled': is_disabled,
        'is_reserved': is_reserved,
        f'vehicle_type_{vehicle_type}': 1
    })
    df = pd.DataFrame([data])
    pred = model.predict(df)[0]
    return max(0, min(100, round(pred)))

if __name__ == "__main__":
    val = predict_battery(47.61, -122.33, 0, 0, 'scooter')
    print(f"Predicted battery level: {val}%")
