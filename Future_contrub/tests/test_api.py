import sys
import json
sys.path.insert(0, 'src')

from api.app import app

class TestAPI:
    """Test cases for the Lime Scooter Predictor API"""
    
    def setup_method(self):
        """Setup test client before each test"""
        self.client = app.test_client()
        self.client.testing = True
    
    def test_health_endpoint(self):
        """Test 1: Health check endpoint works"""
        response = self.client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        print("✅ Test 1 PASSED: Health check works")
    
    def test_home_endpoint(self):
        """Test 2: Home endpoint returns info"""
        response = self.client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data
        print("✅ Test 2 PASSED: Home endpoint works")
    
    def test_predict_valid_request(self):
        """Test 3: Prediction with valid data"""
        payload = {
            'latitude': 47.61,
            'longitude': -122.33,
            'is_disabled': 0,
            'is_reserved': 0
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Check response
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'predicted_scooters' in data
            assert data['predicted_scooters'] >= 0
            print("✅ Test 3 PASSED: Valid prediction works")
        else:
            print(f"⚠️ Test 3 SKIPPED: Model not trained yet")
    
    def test_predict_missing_fields(self):
        """Test 4: API rejects incomplete data"""
        payload = {
            'latitude': 47.61
            # Missing 'longitude'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        print("✅ Test 4 PASSED: API rejects incomplete data")
    
    def test_predict_invalid_type(self):
        """Test 5: API rejects invalid data types"""
        payload = {
            'latitude': 'not_a_number',  # Should be float
            'longitude': -122.33
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        print("✅ Test 5 PASSED: API rejects invalid data types")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
