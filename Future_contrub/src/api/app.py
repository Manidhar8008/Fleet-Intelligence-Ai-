from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

# Initialize Flask app
app = Flask(__name__)

# Global variables for model
model = None
scaler = None

def load_model():
    """Load the pre-trained ML model"""
    global model, scaler
    
    model_path = 'src/ml/scooter_model.pkl'
    scaler_path = 'src/ml/scaler.pkl'
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("✅ Model loaded successfully")
    else:
        print("⚠️ Model files not found. Train the model first.")
        return False
    
    return True

@app.route('/predict', methods=['POST'])
def predict():
    """
    API Endpoint: Predict scooter availability
    
    Expected JSON:
    {
        "latitude": 47.61,
        "longitude": -122.33,
        "is_disabled": 0,
        "is_reserved": 0
    }
    
    Returns:
    {
        "status": "success",
        "predicted_scooters": 12,
        "location": [47.61, -122.33]
    }
    """
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['latitude', 'longitude']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: latitude, longitude'
            }), 400
        
        # Extract features
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        is_disabled = int(data.get('is_disabled', 0))
        is_reserved = int(data.get('is_reserved', 0))
        
        # Prepare features
        features = np.array([[latitude, longitude, is_disabled, is_reserved]])
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        prediction = max(0, int(prediction))  # Ensure non-negative
        
        return jsonify({
            'status': 'success',
            'predicted_scooters': prediction,
            'location': [latitude, longitude],
            'confidence': 'medium'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Lime Scooter Predictor API',
        'version': '1.0'
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API info"""
    return jsonify({
        'message': 'Welcome to Lime Scooter Predictor API',
        'endpoints': {
            'GET /': 'This page',
            'GET /health': 'Health check',
            'POST /predict': 'Predict scooter availability',
            'GET /docs': 'API documentation'
        },
        'example_prediction': {
            'url': '/predict',
            'method': 'POST',
            'body': {
                'latitude': 47.61,
                'longitude': -122.33,
                'is_disabled': 0,
                'is_reserved': 0
            }
        }
    }), 200

if __name__ == '__main__':
    # Load model before starting server
    if load_model():
        print("\n" + "="*60)
        print("🚀 Starting Lime Scooter Predictor API")
        print("="*60)
        print("📍 URL: http://localhost:5000")
        print("📚 Endpoints:")
        print("   GET  http://localhost:5000/")
        print("   GET  http://localhost:5000/health")
        print("   POST http://localhost:5000/predict")
        print("="*60 + "\n")
        
        # Run Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to start API - model not found")
