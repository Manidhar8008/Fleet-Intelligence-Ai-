import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

from src.battery_predict.data_extract import get_battery_data


# Load data
df = get_battery_data(limit=10000)

# One-hot encode vehicle_type
df = pd.get_dummies(df, columns=["vehicle_type"], drop_first=True)

# Feature columns: base numeric + one-hot vehicle types
feature_cols = ["latitude", "longitude", "is_disabled", "is_reserved"] + [
    col for col in df.columns if col.startswith("vehicle_type_")
]

X = df[feature_cols]
y = df["battery_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.2f}")
print(f"R^2 Score: {r2:.2f}")

# Save model and features
joblib.dump(model, "src/battery_predict/battery_model.pkl")
joblib.dump(feature_cols, "src/battery_predict/battery_features.pkl")
print("✅ Model + feature list saved to src/battery_predict/")
