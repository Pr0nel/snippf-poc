# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search():
    response = client.get("/api/v1/search?q=paracetamol")
    assert response.status_code == 200
    assert response.json() == {"total": 10, "items": [...]}

def test_ingest():
    response = client.post("/api/v1/ingest")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "inserted": 1000}