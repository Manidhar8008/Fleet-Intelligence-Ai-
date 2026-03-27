"""
Validation script to verify repository cleanup was successful
Run from /app directory: python validate_structure.py
"""

import sys
import os
from pathlib import Path

def check_file_exists(path: str, description: str) -> bool:
    """Check if file exists"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_file_not_exists(path: str, description: str) -> bool:
    """Check if file doesn't exist (should be deleted)"""
    exists = os.path.exists(path)
    status = "✅" if not exists else "❌ STILL EXISTS"
    print(f"{status} {description}: {path}")
    return not exists

def validate_imports() -> bool:
    """Verify all imports work"""
    print("\n📦 Checking imports...")
    
    try:
        print("   Importing utils.config...", end=" ")
        from utils.config import config
        print("✅")
        
        print("   Importing utils.logger...", end=" ")
        from utils.logger import app_logger
        print("✅")
        
        print("   Importing core.preprocessing...", end=" ")
        from core.preprocessing import clean_fleet_data
        print("✅")
        
        print("   Importing core.data_loader...", end=" ")
        from core.data_loader import generate_demo_data
        print("✅")
        
        print("   Importing core.feature_engineering...", end=" ")
        from core.feature_engineering import engineer_features
        print("✅")
        
        print("   Importing core.decision_engine...", end=" ")
        from core.decision_engine import decision_engine
        print("✅")
        
        print("   Importing core.insights_engine...", end=" ")
        from core.insights_engine import insights_engine
        print("✅")
        
        print("   Importing models.risk_model...", end=" ")
        from models.risk_model import risk_model
        print("✅")
        
        return True
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🔍 REPOSITORY STRUCTURE VALIDATION")
    print("="*70)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # CD to app/ dir
    
    all_checks_pass = True
    
    # Check required directories exist
    print("\n📁 Checking required directories...")
    all_checks_pass &= check_file_exists("core", "Core module directory")
    all_checks_pass &= check_file_exists("models", "Models directory")
    all_checks_pass &= check_file_exists("utils", "Utils directory")
    all_checks_pass &= check_file_exists("data", "Data directory")
    
    # Check required files exist
    print("\n📄 Checking required files...")
    all_checks_pass &= check_file_exists("main.py", "Main Streamlit app")
    all_checks_pass &= check_file_exists("requirements.txt", "Requirements")
    all_checks_pass &= check_file_exists("README.md", "README")
    all_checks_pass &= check_file_exists("core/data_loader.py", "Data loader module")
    all_checks_pass &= check_file_exists("core/preprocessing.py", "Preprocessing module")
    all_checks_pass &= check_file_exists("core/feature_engineering.py", "Feature engineering module")
    all_checks_pass &= check_file_exists("core/decision_engine.py", "Decision engine module")
    all_checks_pass &= check_file_exists("core/insights_engine.py", "Insights engine module")
    all_checks_pass &= check_file_exists("models/risk_model.py", "Risk model")
    all_checks_pass &= check_file_exists("utils/config.py", "Config module")
    all_checks_pass &= check_file_exists("utils/logger.py", "Logger module")
    
    # Check __init__ files
    print("\n🐍 Checking Python package __init__ files...")
    all_checks_pass &= check_file_exists("__init__.py", "App __init__")
    all_checks_pass &= check_file_exists("core/__init__.py", "Core __init__")
    all_checks_pass &= check_file_exists("models/__init__.py", "Models __init__")
    all_checks_pass &= check_file_exists("utils/__init__.py", "Utils __init__")
    
    # Check imports work
    sys.path.insert(0, ".")
    all_checks_pass &= validate_imports()
    
    # Summary
    print("\n" + "="*70)
    if all_checks_pass:
        print("✅ ALL CHECKS PASSED - Repository cleanup successful!")
        print("\nNext steps:")
        print("1. Delete old directories: /core, /models, /utils, /src")
        print("2. Delete old files: app.py, clear_db.py")
        print("3. Run Streamlit: streamlit run app/main.py")
        print("4. Deploy to production")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Review above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())
