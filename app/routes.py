from __future__ import annotations

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from .math_core import log_e, mean, sqrt, variance
from .suggestor import suggest_models

bp = Blueprint("main", __name__)


@bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


@bp.post("/api/log")
def api_log():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "logged")
    return jsonify({"ok": True, "message": message}), 200


@bp.get("/")
def index():
    # Landing page with two options
    return render_template("index.html")


# ---------- Basic Statistics flow ----------

@bp.get("/basic")
def basic_get():
    return render_template("basic.html", result=None, error=None)


@bp.post("/basic")
def basic_post():
    op = request.form.get("operation", "")
    numbers = (request.form.get("numbers") or "").strip()

    try:
        if op in {"sqrt", "log"}:
            x = float(numbers)
            result = sqrt(x) if op == "sqrt" else log_e(x)
        elif op in {"mean", "var_pop", "var_sample"}:
            vals = [float(v) for v in numbers.replace(",", " ").split()]
            if not vals:
                raise ValueError("Please enter at least one number.")
            if op == "mean":
                result = mean(vals)
            elif op == "var_pop":
                result = variance(vals, sample=False)
            else:
                result = variance(vals, sample=True)
        else:
            return render_template("basic.html", result=None, error="Unknown operation.")
        return render_template("basic.html", result=result, error=None)
    except Exception as e:
        return render_template("basic.html", result=None, error=str(e)), 400


# ---------- Data Study flow (text → model suggestions) ----------

@bp.get("/data")
def data_get():
    return render_template("data.html", suggestions=None, text="")


@bp.post("/data")
def data_post():
    text = (request.form.get("description") or "").strip()
    if not text:
        return render_template("data.html", suggestions=None, text="", error="Please enter a description."), 400
    out = suggest_models(text)
    return render_template("data.html", suggestions=out["suggestions"], text=text, error=None)
