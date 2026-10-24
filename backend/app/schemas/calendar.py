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
    target: Optional[int] = None
    ausentismo_risk: str
    color_code: str
    diagnostic: Optional[str] = None

class CalendarResponse(BaseModel):
    shop_id: str
    date: str
    total_appointments: int
    appointments: List[AppointmentResponse]

class SimulateAppointmentRequest(BaseModel):
    shop_id: str = "hooligans"
    barber_id: int = 1
    barber_name: Optional[str] = "Sebastian Fraga"
    service_name: str = "Corte de Pelo"
    service_price: float = 18000.0
    service_duration: int = 30
    date: str = "2026-10-25"
    start_time: str = "16:00:00"
    lead_time_hours: Optional[float] = None
    client_profile: str = "franco"  # "franco" | "matias" | "tomas" | "gonzalo" (or legacy: "fiel" | "nuevo" | "riesgo")
    client_name: Optional[str] = None
    is_self_booked: int = 1

