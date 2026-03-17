"""
Google Fit API Client (Enhanced)
- Historical ingestion from 2019
- Metrics + Activity Sessions
- Chunked, robust, production-ready
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import (
    GOOGLE_FIT_SCOPES,
    GOOGLE_FIT_API_NAME,
    GOOGLE_FIT_API_VERSION,
    CREDENTIALS_FILE,
    TOKEN_FILE,
)

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= CONSTANTS =================

CHUNK_SIZES = {
    "com.google.step_count.delta": 30,
    "com.google.distance.delta": 30,
    "com.google.active_minutes": 30,
    "com.google.calories.expended": 30,
    "com.google.heart_rate.bpm": 7
}

ACTIVITY_MAP = {
    7: "walking",
    8: "running",
    9: "cycling",
    108: "swimming",
}


# ================= CLIENT =================
class GoogleFitClient:
    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self.service = None
        self._authenticate()

    # ---------- AUTH ----------
    def _authenticate(self):
        if os.path.exists(TOKEN_FILE):
            self.credentials = Credentials.from_authorized_user_file(
                TOKEN_FILE, GOOGLE_FIT_SCOPES
            )

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, GOOGLE_FIT_SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "w") as f:
                f.write(self.credentials.to_json())

        self.service = build(
            GOOGLE_FIT_API_NAME,
            GOOGLE_FIT_API_VERSION,
            credentials=self.credentials,
        )

    # ---------- PUBLIC METHODS ----------
    def get_all_metrics(self, start_time: datetime) -> Dict[str, List[Dict]]:
        """Fetch all quantitative metrics from a given start time."""
        results = {}

        for data_type in CHUNK_SIZES.keys():
            logger.info(f"Fetching {data_type}...")
            results[data_type] = self._get_data(data_type, start_time)

        return results

    def get_activity_sessions(self, start_time: datetime) -> List[Dict]:
        """Fetch workout/activity sessions from a given start time."""
        end_time = datetime.utcnow()

        try:
            response = self.service.users().sessions().list(
                userId="me",
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000),
            ).execute()

            sessions = response.get("session", [])

            parsed = []
            for s in sessions:
                activity_code = s.get("activityType")

                parsed.append({
                    "name": s.get("name"),
                    "activity": ACTIVITY_MAP.get(activity_code, f"unknown_{activity_code}"),
                    "start_time": int(s.get("startTimeMillis")),
                    "end_time": int(s.get("endTimeMillis")),
                })

            return parsed

        except Exception as e:
            logger.exception("Failed to fetch activity sessions")
            return []

    # ---------- CORE ENGINE ----------
    def _get_data(self, data_type: str, start_time: datetime) -> List[Dict]:
        end_time = datetime.utcnow()

        chunk_days = CHUNK_SIZES.get(data_type, 30)

        all_points = []
        current_start = start_time

        while current_start < end_time:
            current_end = min(current_start + timedelta(days=chunk_days), end_time)

            for attempt in range(3):
                try:
                    body = {
                        "aggregateBy": [{"dataTypeName": data_type}],
                        "bucketByTime": {"durationMillis": 86400000},
                        "startTimeMillis": int(current_start.timestamp() * 1000),
                        "endTimeMillis": int(current_end.timestamp() * 1000),
                    }

                    response = (
                        self.service.users()
                        .dataset()
                        .aggregate(userId="me", body=body)
                        .execute()
                    )

                    parsed = self._parse_response(response, data_type)
                    all_points.extend(parsed)

                    logger.info(
                        f"{data_type} | {current_start.date()} → {current_end.date()} | {len(parsed)}"
                    )

                    break

                except Exception as e:
                    logger.warning(f"{data_type} retry {attempt+1} failed: {e}")
                    time.sleep(2 ** attempt)

            else:
                logger.error(f"{data_type} failed for {current_start} → {current_end}")

            current_start = current_end
            time.sleep(0.5)

        return all_points

    # ---------- PARSER ----------
    def _parse_response(self, response: Dict, data_type: str) -> List[Dict]:
        records = []

        for bucket in response.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    value = point.get("value", [{}])[0]

                    if "intVal" in value:
                        val = value["intVal"]
                    elif "fpVal" in value:
                        val = value["fpVal"]
                    else:
                        val = None

                    records.append({
                        "data_type": data_type,
                        "timestamp": int(point.get("endTimeNanos", 0)) // 1_000_000,
                        "value": val,
                    })

        return records


# ================= USAGE =================
if __name__ == "__main__":
    client = GoogleFitClient()

    metrics = client.get_all_metrics()
    sessions = client.get_activity_sessions()

    print("Metrics collected:")
    for k, v in metrics.items():
        print(f"{k}: {len(v)}")

    print(f"\nActivity sessions: {len(sessions)}")