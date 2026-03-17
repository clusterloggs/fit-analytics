"""
Data Importer Module
Handles importing data from Google Fit and saving to CSV
"""
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
from typing import Dict

from config import RAW_DATA_DIR
from google_fit_client import GoogleFitClient

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitnessDataImporter:
    """Import fitness data from Google Fit API"""

    def __init__(self):
        self.client = GoogleFitClient()
        self.raw_data: Dict[str, pd.DataFrame] = {}

        # Ensure directory exists
        os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # ---------- MAIN IMPORT ----------
    def import_all_data(self, days_back: int) -> Dict[str, pd.DataFrame]:
        """
        Import fitness data for a given number of days.
        
        Args:
            days_back: Number of days of data to retrieve.
        """

        logger.info(f"Starting data import for the last {days_back} days from Google Fit...")
        start_time = datetime.now() - timedelta(days=days_back)
        data_frames = {}

        # ================= METRICS =================
        try:
            metrics = self.client.get_all_metrics(start_time=start_time)

            for data_type, records in metrics.items():
                if records:
                    name = self._map_data_type(data_type)
                    df = self._convert_to_dataframe(records)

                    data_frames[name] = df
                    logger.info(f"{name}: {len(df)} records")

        except Exception as e:
            logger.exception("Failed to import metrics")

        # ================= ACTIVITY SESSIONS =================
        try:
            sessions = self.client.get_activity_sessions(start_time=start_time)

            if sessions:
                df_sessions = pd.DataFrame(sessions)

                df_sessions["start_time"] = pd.to_datetime(
                    df_sessions["start_time"], unit="ms"
                )
                df_sessions["end_time"] = pd.to_datetime(
                    df_sessions["end_time"], unit="ms"
                )

                data_frames["activities"] = df_sessions
                logger.info(f"activities: {len(df_sessions)} records")

        except Exception as e:
            logger.exception("Failed to import activity sessions")

        self.raw_data = data_frames
        return data_frames

    # ---------- SAVE ----------
    def save_raw_data(self) -> Dict[str, str]:
        """Save raw data to CSV"""

        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for name, df in self.raw_data.items():
            filename = os.path.join(RAW_DATA_DIR, f"{name}_{timestamp}.csv")
            df.to_csv(filename, index=False)

            saved_files[name] = filename
            logger.info(f"Saved {name} → {filename}")

        return saved_files

    # ---------- HELPERS ----------
    @staticmethod
    def _convert_to_dataframe(data: list) -> pd.DataFrame:
        """Convert records to clean DataFrame"""

        df = pd.DataFrame(data)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
            df = df.dropna(subset=["timestamp"])

            df["date"] = df["timestamp"].dt.date
            df["time"] = df["timestamp"].dt.time

        return df

    @staticmethod
    def _map_data_type(data_type: str) -> str:
        """Map Google Fit data types to clean names"""

        mapping = {
            "com.google.step_count.delta": "steps",
            "com.google.distance.delta": "distance",
            "com.google.active_minutes": "move_minutes",
            "com.google.calories.expended": "calories",
            "com.google.heart_rate.bpm": "heart_rate",
            "com.google.sleep.segment": "sleep",
            "com.google.weight": "weight",
        }

        return mapping.get(data_type, data_type)


# ================= USAGE =================
if __name__ == "__main__":
    importer = FitnessDataImporter()

    data = importer.import_all_data()
    files = importer.save_raw_data()

    print("\nSaved files:")
    for k, v in files.items():
        print(f"{k}: {v}")