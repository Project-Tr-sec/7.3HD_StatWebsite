import json
from app import create_app

def test_healthz():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        r = c.get("/healthz")
        assert r.status_code == 200
        assert r.get_json()["status"] == "ok"

def test_api_log():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        payload = {"op": "log", "x": "2.718281828"}
        r = c.post("/api/calc", data=json.dumps(payload), content_type="application/json")
        assert r.status_code == 200
        assert abs(r.get_json()["result"] - 1.0) < 1e-6