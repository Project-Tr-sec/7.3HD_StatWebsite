from __future__ import annotations

from flask import Blueprint, jsonify, request

bp = Blueprint("main", __name__)


@bp.get("/healthz")
def healthz():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200


@bp.post("/api/log")
def api_log():
    """
    Echo a simple payload to simulate logging.
    Tests typically just verify 200 + JSON shape.
    """
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "logged")
    return jsonify({"ok": True, "message": message}), 200
