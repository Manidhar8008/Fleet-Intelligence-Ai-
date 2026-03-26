import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import os

# Create ml directory if not exists
os.makedirs('src/ml', exist_ok=True)

class ScooterPredictor:
    def __init__(self, db_path='data/lime_data.db'):
        self.db_path = db_path
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'src/ml/scooter_model.pkl'
        
    def load_data(self):
        """Load data from SQLite and prepare features"""
        conn = sqlite3.connect(self.db_path)
        
        # Get all vehicle data
        query = """
        SELECT latitude, longitude, is_disabled, is_reserved 
        FROM vehicles
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            print("❌ No data found in database!")
            return None
        
        # Feature engineering: Group by location (rounded lat/lon)
        df['lat_bucket'] = (df['latitude'] * 100).astype(int) / 100
        df['lon_bucket'] = (df['longitude'] * 100).astype(int) / 100
        
        # Count available vehicles per location
        location_stats = df.groupby(['lat_bucket', 'lon_bucket']).agg({
            'is_disabled': 'sum',
            'is_reserved': 'sum'
        }).reset_index()
        
        # Add time-based features (simulate for now)
        location_stats['available'] = 10 + np.random.randint(-5, 10, len(location_stats))
        
        print(f"✅ Loaded data: {len(location_stats)} location clusters")
        return location_stats
    
    def prepare_features(self, df):
        """Prepare features for ML model"""
        # Features: latitude, longitude, disabled count, reserved count
        X = df[['lat_bucket', 'lon_bucket', 'is_disabled', 'is_reserved']]
        # Target: available scooters
        y = df['available']
        
        return X, y
    
    def train(self):
        """Train the ML model"""
        print("\n🤖 Training ML Model...")
        
        # Load and prepare data
        df = self.load_data()
        if df is None:
            return False
        
        X, y = self.prepare_features(df)
        
        # Split data: 80% train, 20% test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalize features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Linear Regression model
        self.model = LinearRegression()
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"✅ Model trained!")
        print(f"   Training accuracy: {train_score:.2%}")
        print(f"   Testing accuracy: {test_score:.2%}")
        
        # Save model
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, 'src/ml/scaler.pkl')
        print(f"💾 Model saved to {self.model_path}")
        
        return True
    
    def predict(self, latitude, longitude, is_disabled=0, is_reserved=0):
        """Predict available scooters for given location"""
        if self.model is None:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load('src/ml/scaler.pkl')
        
        # Prepare input
        features = np.array([[latitude, longitude, is_disabled, is_reserved]])
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        prediction = max(0, int(prediction))  # Can't have negative scooters
        
        return prediction

# Main execution
if __name__ == "__main__":
    predictor = ScooterPredictor()
    
    # Train model
    success = predictor.train()
    
    if success:
        print("\n🧪 Testing predictions...")
        # Example predictions
        pred1 = predictor.predict(latitude=47.61, longitude=-122.33)
        print(f"   Prediction for Seattle downtown: {pred1} scooters")
        
        pred2 = predictor.predict(latitude=47.65, longitude=-122.30)
        print(f"   Prediction for another location: {pred2} scooters")
