from pydantic import BaseModel

class QueueMetricsResponse(BaseModel):
    utilization: float
    p0: float
    Lq: float
    Wq_hours: float
    Wq_minutes: float
    L: float
    W_hours: float
    W_minutes: float
    stable: bool

class ShopQueueData(BaseModel):
    shop_id: str
    lambda_rate: float
    mu_rate: float
    servers: int
    metrics: QueueMetricsResponse
