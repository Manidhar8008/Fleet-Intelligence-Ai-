"""
Lime IoT ML Platform Configuration
Settings and environment variables for the project
"""

import os
from pathlib import Path

# ============ PROJECT PATHS ============
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============ API CONFIGURATION ============
LIME_BASE_URL = "https://data.lime.bike/api/partners/v1/gbfs"
DEFAULT_CITY = "seattle"
API_TIMEOUT = 10  # seconds
COLLECTION_INTERVAL = 300  # 5 minutes

# ============ DATABASE CONFIGURATION ============
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/lime_iot")
DB_TIMEOUT = 30

# ============ LOGGING CONFIGURATION ============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============ DISPLAY ============
if __name__ == "__main__":
    print("🚀 Lime IoT ML Platform - Configuration Loaded!")
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"📊 Data Directory: {DATA_DIR}")
    print(f"🌐 API Base URL: {LIME_BASE_URL}")
