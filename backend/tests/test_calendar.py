import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.services.calendar_service import get_calendar_data

def test_get_calendar_api_hellfish(client):
    response = client.get("/api/calendar?shop_id=hellfish")
    assert response.status_code == 200
    data = response.json()
    assert data["shop_id"] == "hellfish"
    assert "date" in data
    assert "total_appointments" in data
    assert isinstance(data["appointments"], list)
    if len(data["appointments"]) > 0:
        first_app = data["appointments"][0]
        assert "ausentismo_risk" in first_app
        assert first_app["ausentismo_risk"] in ["ALTO", "MEDIO", "BAJO"]
        assert "color_code" in first_app
        assert first_app["color_code"] in ["#ef4444", "#f59e0b", "#10b981"]

def test_get_calendar_api_hooligans(client):
    response = client.get("/api/calendar?shop_id=hooligans")
    assert response.status_code == 200
    data = response.json()
    assert data["shop_id"] == "hooligans"
    assert isinstance(data["appointments"], list)

def test_get_calendar_missing_param(client):
    response = client.get("/api/calendar")
    assert response.status_code == 422

def test_get_calendar_nonexistent_shop(client):
    response = client.get("/api/calendar?shop_id=nonexistent_shop_xyz")
    assert response.status_code in [404, 500]

def test_calendar_service_fallback_on_db_error():
    with patch("app.services.calendar_service.fetch_appointments_from_db", side_effect=Exception("DB Connection Refused")):
        result = get_calendar_data(shop_id="hellfish")
        assert result.shop_id == "hellfish"
        assert result.total_appointments >= 0

def test_calendar_service_file_not_found():
    with patch("app.services.calendar_service.DATA_SOURCE", "CSV"):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                get_calendar_data(shop_id="hellfish")
            assert exc_info.value.status_code == 404

def test_simulate_appointment_fiel(client):
    payload = {
        "shop_id": "hooligans",
        "barber_id": 1,
        "barber_name": "Sebastian Fraga",
        "service_name": "Corte Clásico",
        "service_price": 19000.0,
        "service_duration": 45,
        "date": "2026-01-21",
        "start_time": "15:00:00",
        "lead_time_hours": 2.0,
        "client_profile": "fiel",
        "is_self_booked": 0
    }
    response = client.post("/api/calendar/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ausentismo_risk"] == "BAJO"
    assert data["color_code"] == "#10b981"

def test_simulate_appointment_riesgo(client):
    payload = {
        "shop_id": "hooligans",
        "barber_id": 5,
        "barber_name": "Valentin",
        "service_name": "Corte + Barba",
        "service_price": 13000.0,
        "service_duration": 30,
        "date": "2026-01-21",
        "start_time": "18:00:00",
        "lead_time_hours": 72.0,
        "client_profile": "riesgo",
        "is_self_booked": 1
    }
    response = client.post("/api/calendar/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ausentismo_risk"] == "ALTO"
    assert data["color_code"] == "#ef4444"


