from fastapi import APIRouter, Query
from app.schemas.calendar import CalendarResponse, AppointmentResponse, SimulateAppointmentRequest
from app.services.calendar_service import get_calendar_data, simulate_appointment_service

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])

@router.get("", response_model=CalendarResponse)
def get_calendar(
    shop_id: str = Query(..., description="ID del comercio: 'hellfish' o 'hooligans'"),
    date: str = Query(None, description="Fecha en formato YYYY-MM-DD. Si no se especifica, toma la primera fecha disponible.")
):
    """
    Devuelve los turnos para un comercio y fecha, evaluando el riesgo de ausentismo en tiempo real.
    """
    return get_calendar_data(shop_id=shop_id, date=date)

@router.post("/simulate", response_model=AppointmentResponse)
def simulate_appointment(payload: SimulateAppointmentRequest):
    """
    Simula en caliente la inyección de un nuevo turno para la defensa en vivo,
    evaluándolo inmediatamente con el clasificador Gradient Boosting.
    """
    return simulate_appointment_service(payload)
