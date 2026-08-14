from pydantic import BaseModel
from typing import Optional, List

class AppointmentResponse(BaseModel):
    id: int
    barber_id: int
    barber_name: str
    date: str
    start_time: str
    end_time: str
    service_name: str
    service_price: float
    service_duration: int
    client_hashed: str
    is_self_booked: int
    target: Optional[int]
    ausentismo_risk: str  # "ALTO" | "MEDIO" | "BAJO"
    color_code: str       # Hex or Tailwind color for risk

class CalendarResponse(BaseModel):
    shop_id: str
    date: str
    total_appointments: int
    appointments: List[AppointmentResponse]
