import json
from app import create_app

app = create_app()

def test_healthz():
    client = app.test_client()
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"

def test_api_log():
    client = app.test_client()
    payload = {"message": "hello"}
    resp = client.post("/api/log", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["message"] == "hello"
