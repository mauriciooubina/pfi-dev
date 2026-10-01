import pytest
import pandas as pd
from unittest.mock import patch
from app.services.ml_service import get_ml_model, predict_appointment_risk

def test_get_ml_model_success():
    model = get_ml_model()
    assert model is not None
    assert hasattr(model, "predict_proba")

def test_predict_inactive_barber():
    row = pd.Series({"barber_active": False})
    risk, color, prob = predict_appointment_risk(row)
    assert risk == "ALTO"
    assert color == "#ef4444"
    assert prob == 0.99

def test_predict_standard_appointment():
    row = pd.Series({
        "barber_active": True,
        "lead_time_hours": 24.0,
        "service_price": 8500.0,
        "duration": 30,
        "hour_of_day": 15,
        "shop_id": "hellfish",
        "is_self_booked": 1,
        "day_of_week": 3,
        "month": 4,
        "barber_id": "1",
        "client_hashed": "client_abc",
        "appointment_start": "2026-04-10 15:00:00"
    })
    risk, color, prob = predict_appointment_risk(row)
    assert risk in ["ALTO", "MEDIO", "BAJO"]
    assert color in ["#ef4444", "#f59e0b", "#10b981"]
    assert 0.0 <= prob <= 1.0

def test_predict_with_historical_context():
    historical_df = pd.DataFrame([
        {
            "client_hashed": "repeat_client",
            "appointment_start": "2026-03-01 10:00:00",
            "target": 1
        },
        {
            "client_hashed": "repeat_client",
            "appointment_start": "2026-03-15 10:00:00",
            "target": 1
        },
        {
            "client_hashed": "loyal_client",
            "appointment_start": "2026-03-01 10:00:00",
            "target": 0
        },
        {
            "client_hashed": "loyal_client",
            "appointment_start": "2026-03-15 10:00:00",
            "target": 0
        }
    ])
    
    # Test client with 100% past no-shows
    bad_row = pd.Series({
        "barber_active": True,
        "lead_time_hours": 120.0,
        "service_price": 12000.0,
        "duration": 45,
        "hour_of_day": 18,
        "shop_id": "hellfish",
        "is_self_booked": 1,
        "day_of_week": 5,
        "month": 3,
        "barber_id": "1",
        "client_hashed": "repeat_client",
        "appointment_start": "2026-03-20 10:00:00"
    })
    risk_bad, _, prob_bad = predict_appointment_risk(bad_row, all_appointments_df=historical_df)
    
    # Test loyal client with 0% past no-shows
    good_row = pd.Series({
        "barber_active": True,
        "lead_time_hours": 2.0,
        "service_price": 5000.0,
        "duration": 30,
        "hour_of_day": 11,
        "shop_id": "hellfish",
        "is_self_booked": 0,
        "day_of_week": 2,
        "month": 3,
        "barber_id": "1",
        "client_hashed": "loyal_client",
        "appointment_start": "2026-03-20 10:00:00"
    })
    risk_good, _, prob_good = predict_appointment_risk(good_row, all_appointments_df=historical_df)
    
    assert prob_bad > prob_good

def test_predict_fallback_when_model_is_none():
    with patch("app.services.ml_service.get_ml_model", return_value=None):
        # Case 1: High lead time & self booked
        row_high = pd.Series({"lead_time_hours": 100.0, "is_self_booked": 1, "barber_active": True})
        risk, color, prob = predict_appointment_risk(row_high)
        assert risk == "ALTO"
        assert color == "#ef4444"
        assert prob == 0.75
        
        # Case 2: Short lead time & self booked
        row_short = pd.Series({"lead_time_hours": 3.0, "is_self_booked": 1, "barber_active": True})
        risk, color, prob = predict_appointment_risk(row_short)
        assert risk == "MEDIO"
        assert color == "#f59e0b"
        assert prob == 0.35
        
        # Case 3: Other
        row_other = pd.Series({"lead_time_hours": 24.0, "is_self_booked": 0, "barber_active": True})
        risk, color, prob = predict_appointment_risk(row_other)
        assert risk == "BAJO"
        assert color == "#10b981"
        assert prob == 0.10

def test_predict_fallback_when_exception_in_prediction():
    mock_model = patch("app.services.ml_service.get_ml_model").start()
    mock_model.return_value.predict_proba.side_effect = RuntimeError("Inference failed")
    
    row = pd.Series({"lead_time_hours": 100.0, "is_self_booked": 1, "barber_active": True})
    risk, color, prob = predict_appointment_risk(row)
    assert risk == "ALTO"
    assert prob == 0.75
    patch.stopall()
