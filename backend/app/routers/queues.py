from fastapi import APIRouter
from typing import List
from app.schemas.queues import ShopQueueData
from app.services.queue_service import get_queue_metrics_data

router = APIRouter(prefix="/api/queues", tags=["Queues"])

@router.get("", response_model=List[ShopQueueData])
def get_queue_metrics():
    """
    Returns pre-computed M/M/s queuing model metrics from queue_metrics.json.
    """
    return get_queue_metrics_data()
