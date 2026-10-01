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
