from flask import Blueprint, jsonify, render_template, request
from .math_core import log_e_is_one, sqrt_four_is_two
from .suggestor import suggest_models

bp = Blueprint("main", __name__)

# ---------- Pages ----------
@bp.get("/")
def index():
    return render_template("index.html")  # in app/templates/

@bp.get("/basic")
def page_basic():
    return render_template("basic.html")

@bp.get("/data")
def page_data():
    return render_template("data.html")

# ---------- APIs ----------
@bp.get("/healthz")
def healthz():
    return jsonify(status="ok")

@bp.post("/api/log")
def api_log():
    data = request.get_json(silent=True) or {}
    msg = data.get("message")
    return jsonify(ok=True, message=msg), 200

@bp.post("/api/stats/mean")
def api_stats_mean():
    data = request.get_json(silent=True) or {}
    nums = data.get("numbers", [])
    try:
        nums = [float(x) for x in nums]
    except Exception:
        return jsonify(error="Invalid numbers"), 400
    if not nums:
        return jsonify(error="Empty list"), 400
    return jsonify(mean=sum(nums) / len(nums))

@bp.post("/api/suggest")
def api_suggest():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify(error="prompt is required"), 400
    return jsonify(models=suggest_models(prompt))

@bp.get("/api/math")
def api_math():
    return jsonify(log_e_is_one=log_e_is_one(), sqrt_four_is_two=sqrt_four_is_two())
