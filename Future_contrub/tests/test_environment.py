"""
Environment and dependency testing
Verifies that your development environment is set up correctly
"""

import sys

def test_python_version():
    """Test Python version is 3.9+"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK!")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} too old (need 3.9+)")
        return False

def test_basic_imports():
    """Test that all required packages can be imported"""
    print("\n📦 Testing package imports...")
    
    packages = {
        'pandas': 'Data processing',
        'numpy': 'Numerical computing',
        'scipy': 'Scientific computing',
        'sklearn': 'Machine learning',
        'tensorflow': 'Deep learning',
        'requests': 'HTTP requests',
        'matplotlib': 'Visualization'
    }
    
    all_ok = True
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package:15} - {description}")
        except ImportError:
            print(f"❌ {package:15} - NOT installed")
            all_ok = False
    
    return all_ok

def test_project_config():
    """Test project configuration"""
    print("\n⚙️  Testing project configuration...")
    try:
        from src.config.settings import PROJECT_ROOT, DATA_DIR, LIME_BASE_URL
        
        print(f"✅ Project configuration loaded")
        print(f"   📁 Project root: {PROJECT_ROOT}")
        print(f"   📊 Data directory: {DATA_DIR}")
        print(f"   🌐 API URL: {LIME_BASE_URL}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_data_science():
    """Test basic data science functionality"""
    print("\n📊 Testing data science functionality...")
    try:
        import pandas as pd
        import numpy as np
        
        # Create test data
        df = pd.DataFrame({
            'vehicle_id': ['bike_001', 'bike_002', 'bike_003'],
            'latitude': [47.6062, 47.6205, 47.6089],
            'longitude': [-122.3321, -122.3493, -122.3378],
            'battery': [0.85, 0.62, 0.91]
        })
        
        print(f"✅ Created test DataFrame with shape {df.shape}")
        print(f"   Average battery level: {df['battery'].mean():.2%}")
        print(f"   Columns: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"❌ Data science test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Lime IoT ML Platform - Environment Test")
    print("=" * 60)
    
    tests = [
        test_python_version(),
        test_basic_imports(),
        test_project_config(),
        test_data_science()
    ]
    
    print("\n" + "=" * 60)
    if all(tests):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your environment is ready for development!")
        print("🚀 Start building amazing ML models!")
    else:
        print("⚠️  Some tests failed - check errors above")
        print("💡 Install missing packages: pip install -r requirements.txt")
    print("=" * 60)
    
    return all(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

