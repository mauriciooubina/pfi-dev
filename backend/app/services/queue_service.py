import os
import json
from fastapi import HTTPException
from app.config import QUEUE_METRICS_JSON, DATA_SOURCE
from app.services.db_service import fetch_queue_metrics_from_db

def get_queue_metrics_data():
    """
    Loads M/M/s queuing model metrics from PostgreSQL when DATA_SOURCE='POSTGRES' (with automatic fallback to JSON if DB is down).
    """
    try:
        if DATA_SOURCE == "POSTGRES":
            try:
                return fetch_queue_metrics_from_db()
            except Exception as db_err:
                print(f"[Warning] PostgreSQL connection failed: {db_err}. Falling back to JSON mode.")
        
        if not os.path.exists(QUEUE_METRICS_JSON):
            raise HTTPException(
                status_code=404, 
                detail="Queue metrics JSON not found. Run queuing_theory.py first."
            )
        with open(QUEUE_METRICS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading queue metrics ({DATA_SOURCE}): {str(e)}"
        )


