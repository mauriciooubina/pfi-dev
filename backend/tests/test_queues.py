import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.services.queue_service import get_queue_metrics_data

def test_get_queues_api(client):
    response = client.get("/api/queues")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    for item in data:
        assert "shop_id" in item
        assert "lambda_rate" in item
        assert "mu_rate" in item
        assert "servers" in item
        assert "metrics" in item
        m = item["metrics"]
        assert "utilization" in m
        assert "p0" in m
        assert "Lq" in m
        assert "Wq_minutes" in m
        assert "stable" in m

def test_queues_service_fallback_on_db_error():
    with patch("app.services.queue_service.fetch_queue_metrics_from_db", side_effect=Exception("DB Down")):
        # Should fallback to JSON gracefully
        data = get_queue_metrics_data()
        assert isinstance(data, list)
        assert len(data) >= 1

def test_queues_service_file_not_found():
    with patch("app.services.queue_service.DATA_SOURCE", "CSV"):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                get_queue_metrics_data()
            assert exc_info.value.status_code == 404

def test_queues_service_generic_error():
    with patch("app.services.queue_service.DATA_SOURCE", "CSV"):
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=IOError("Disk error")):
                with pytest.raises(HTTPException) as exc_info:
                    get_queue_metrics_data()
                assert exc_info.value.status_code == 500
