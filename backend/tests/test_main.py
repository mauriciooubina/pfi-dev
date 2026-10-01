def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "Backend running successfully." in data["message"]

def test_openapi_schema(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Sistema de Predicción de Ausentismo"
    assert "/api/calendar" in schema["paths"]
    assert "/api/queues" in schema["paths"]
