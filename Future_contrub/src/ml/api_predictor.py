from predictor import ScooterPredictor
import json

class PredictionAPI:
    def __init__(self):
        self.predictor = ScooterPredictor()
        # Load pre-trained model
        try:
            import joblib
            self.predictor.model = joblib.load('src/ml/scooter_model.pkl')
            self.predictor.scaler = joblib.load('src/ml/scaler.pkl')
        except:
            print("⚠️ Model not found. Please train first.")
    
    def predict_batch(self, locations):
        """Predict for multiple locations"""
        results = []
        for loc in locations:
            pred = self.predictor.predict(
                latitude=loc['lat'],
                longitude=loc['lon'],
                is_disabled=loc.get('disabled', 0),
                is_reserved=loc.get('reserved', 0)
            )
            results.append({
                'location': f"({loc['lat']}, {loc['lon']})",
                'predicted_scooters': pred
            })
        return results

if __name__ == "__main__":
    api = PredictionAPI()
    
    # Example batch prediction
    test_locations = [
        {'lat': 47.61, 'lon': -122.33, 'disabled': 1, 'reserved': 2},
        {'lat': 47.65, 'lon': -122.30, 'disabled': 0, 'reserved': 1},
        {'lat': 47.60, 'lon': -122.35, 'disabled': 2, 'reserved': 0},
    ]
    
    print("📊 Batch Predictions:")
    results = api.predict_batch(test_locations)
    for result in results:
        print(f"   {result['location']}: {result['predicted_scooters']} scooters")
