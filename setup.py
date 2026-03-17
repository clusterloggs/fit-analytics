"""
Setup and utilities for Fitness Analytics project
"""
import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def verify_credentials():
    """Verify Google Fit credentials exist"""
    credentials_file = Path(__file__).parent / "credentials.json"
    
    if not credentials_file.exists():
        print("\nGoogle Fit Credentials Missing!")
        print("\nTo set up Google Fit integration:")
        print("=" * 50)
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project (or use existing)")
        print("3. Enable Google Fit API")
        print("4. Create OAuth 2.0 Desktop credentials")
        print("5. Download credentials.json")
        print("6. Place in: " + str(credentials_file))
        print("=" * 50)
        return False
    else:
        print(" Google Fit credentials found")
        return True


def verify_dependencies():
    """Verify all required packages are installed"""
    required_packages = [
        'google_auth_oauthlib',
        'googleapiclient',
        'pandas',
        'numpy',
        'sklearn',
        'streamlit',
        'plotly'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"  Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print(" All required packages found")
        return True


def create_directories():
    """Create required directories"""
    base_path = Path(__file__).parent
    directories = [
        base_path / 'data' / 'raw',
        base_path / 'data' / 'processed',
        base_path / 'src',
        base_path / 'notebooks'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("All directories created/verified")


def main():
    """Run setup checks"""
    print("\nFitness Analytics Setup Checker")
    print("=" * 50)
    
    create_directories()
    
    deps_ok = verify_dependencies()
    creds_ok = verify_credentials()
    
    print("\n" + "=" * 50)
    if deps_ok and creds_ok:
        print("Setup complete! Ready to start.")
        print("\nNext steps:")
        print("1. Run pipeline: python pipeline.py")
        print("2. Launch dashboard: streamlit run dashboard.py")
    else:
        print("Please fix the issues above before proceeding")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    main()
