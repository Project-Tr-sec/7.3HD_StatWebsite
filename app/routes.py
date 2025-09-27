# app/routes.py
from flask import request, jsonify, render_template
from . import app


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.post("/api/log")
def api_log():
    data = request.get_json(silent=True) or {}
    msg = data.get("message")
    app.logger.info("api_log: %r", msg)
    return jsonify(ok=True, message=msg), 200
