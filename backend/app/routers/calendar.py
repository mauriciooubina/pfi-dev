from fastapi import APIRouter, Query
from app.schemas.calendar import CalendarResponse
from app.services.calendar_service import get_calendar_data

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])

@router.get("", response_model=CalendarResponse)
def get_calendar(
    shop_id: str = Query(..., description="ID del comercio: 'hellfish' o 'hooligans'"),
    date: str = Query(None, description="Fecha en formato YYYY-MM-DD. Si no se especifica, toma la primera fecha disponible.")
):
    """
    Returns appointments for a specific date and shop, attaching simulated absenteeism risk flags.
    """
    return get_calendar_data(shop_id=shop_id, date=date)
