"""
First API Test - Connect to Real Lime Data
Tests connection to Lime GBFS API and analyzes sample data
Run this to verify your setup works!
"""

import requests
import json
from datetime import datetime

# Configuration
LIME_BASE_URL = "https://data.lime.bike/api/partners/v1/gbfs/seattle"
VEHICLE_STATUS_URL = f"{LIME_BASE_URL}/free_bike_status.json"

def test_api_connection():
    """Test connection to Lime API"""
    print("=" * 70)
    print("🚀 LIME API CONNECTION TEST")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: API Connectivity
    print("📡 TEST 1: Checking API connectivity...")
    print("-" * 50)
    
    try:
        response = requests.get(VEHICLE_STATUS_URL, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ API responded with status: {response.status_code}")
            print(f"✅ Response received successfully")
            data = response.json()
            
        else:
            print(f"❌ API returned error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - API took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Data Structure
    print("\n📊 TEST 2: Analyzing data structure...")
    print("-" * 50)
    
    try:
        last_updated = data.get('last_updated', 'Unknown')
        bikes = data.get('data', {}).get('bikes', [])
        
        print(f"✅ Data last updated: {datetime.fromtimestamp(last_updated)}")
        print(f"✅ Total vehicles found: {len(bikes)}")
        
        if len(bikes) == 0:
            print("⚠️  Warning: No vehicles in response")
            return False
            
    except Exception as e:
        print(f"❌ Data parsing error: {e}")
        return False
    
    # Test 3: Sample Data Analysis
    print("\n📈 TEST 3: Analyzing sample vehicle data...")
    print("-" * 50)
    
    try:
        sample = bikes[0]
        print(f"✅ Sample vehicle fields:")
        for key, value in sample.items():
            print(f"   • {key}: {value}")
        
        # Analyze all vehicles
        available_count = sum(1 for v in bikes if not v.get('is_disabled', False))
        
        battery_levels = []
        for vehicle in bikes:
            battery_str = vehicle.get('jump_ebike_battery_level', '0%')
            if battery_str and '%' in battery_str:
                try:
                    battery_pct = float(battery_str.replace('%', ''))
                    battery_levels.append(battery_pct)
                except:
                    pass
        
        print(f"\n✅ Analytics Summary:")
        print(f"   • Available vehicles: {available_count}/{len(bikes)}")
        print(f"   • Availability rate: {(available_count/len(bikes)*100):.1f}%")
        
        if battery_levels:
            avg_battery = sum(battery_levels) / len(battery_levels)
            print(f"   • Average battery: {avg_battery:.1f}%")
            print(f"   • Min battery: {min(battery_levels):.1f}%")
            print(f"   • Max battery: {max(battery_levels):.1f}%")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False
    
    # Test 4: Data Types
    print("\n🔬 TEST 4: Validating data types...")
    print("-" * 50)
    
    try:
        validation_checks = [
            ('bike_id', str, sample.get('bike_id')),
            ('lat', float, sample.get('lat')),
            ('lon', float, sample.get('lon')),
            ('is_reserved', bool, sample.get('is_reserved')),
            ('is_disabled', bool, sample.get('is_disabled'))
        ]
        
        all_valid = True
        for field_name, expected_type, value in validation_checks:
            if isinstance(value, expected_type):
                print(f"✅ {field_name}: {type(value).__name__} = {value}")
            else:
                print(f"❌ {field_name}: Expected {expected_type.__name__}, got {type(value).__name__}")
                all_valid = False
        
        if not all_valid:
            return False
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False
    
    return True

def save_sample_data():
    """Save sample data for analysis"""
    print("\n💾 TEST 5: Saving sample data...")
    print("-" * 50)
    
    try:
        response = requests.get(VEHICLE_STATUS_URL, timeout=10)
        
        if response.status_code == 200:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'sample_lime_data_{timestamp}.json'
            
            with open(filename, 'w') as f:
                json.dump(response.json(), f, indent=2)
            
            file_size = len(json.dumps(response.json()))
            print(f"✅ Sample data saved to: {filename}")
            print(f"✅ File size: {file_size:,} characters")
            return True
        else:
            print(f"❌ Failed to save: API error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

def main():
    """Run all tests"""
    api_test = test_api_connection()
    data_test = save_sample_data()
    
    print("\n" + "=" * 70)
    if api_test and data_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ API connection working")
        print("✅ Data structure valid")
        print("✅ Sample data saved")
        print("🚀 Ready for production data collection!")
    else:
        print("❌ Some tests failed")
        print("💡 Check internet connection and API availability")
    print("=" * 70)

if __name__ == "__main__":
    main()
