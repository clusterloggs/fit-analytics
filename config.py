"""
Configuration settings for Fitness Analytics Project
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SRC_DIR = PROJECT_ROOT / "src"

# Google Fit API Configuration
# These will be set from environment variables or credentials.json
GOOGLE_FIT_SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.location.read'
]

# API Configuration
GOOGLE_FIT_API_NAME = 'fitness'
GOOGLE_FIT_API_VERSION = 'v1'

# Data Processing Configuration
# Set a long retention period to fetch all historical data.
DATA_RETENTION_DAYS = 365 * 10  # ~10 years of data
BATCH_SIZE = 1000

# Analytics Configuration
PREDICTION_DAYS_AHEAD = 7  # Predict 7 days ahead
MOVING_AVERAGE_WINDOW = 7  # 7-day moving average

# File paths
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.pickle"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
SRC_DIR.mkdir(parents=True, exist_ok=True)
