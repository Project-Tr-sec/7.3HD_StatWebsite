from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request

bp = Blueprint("main", __name__)

@bp.get("/healthz")
def healthz():
    return jsonify(status="ok")

@bp.get("/")
def index():
    # Renders the new templates/index.html we created
    return render_template("index.html")

@bp.route("/basic", methods=["GET", "POST"])
def basic_stats():
    if request.method == "POST":
        raw = request.form.get("numbers", "")
        # split on comma or whitespace
        parts = [p for chunk in raw.split(",") for p in chunk.strip().split()]
        nums = [float(p) for p in parts if p]
        if not nums:
            result = {"error": "No numbers parsed"}
        else:
            n = len(nums)
            s = sum(nums)
            mean = s / n
            # median
            xs = sorted(nums)
            mid = n // 2
            if n % 2 == 1:
                median = xs[mid]
            else:
                median = (xs[mid - 1] + xs[mid]) / 2
            result = {"count": n, "sum": s, "mean": mean, "median": median, "min": min(nums), "max": max(nums)}
        return render_template("basic_stats.html", result=result)
    return render_template("basic_stats.html", result=None)

@bp.route("/data", methods=["GET", "POST"])
def data_models():
    def suggest(goal: str, clues: str) -> dict:
        text = f"{goal} {clues}".lower()

        def has(*keys): return any(k in text for k in keys)

        # Very simple heuristic tree (average difficulty)
        if has("time", "timestamp", "daily", "weekly", "monthly", "season", "trend", "next month", "next week"):
            return {
                "task": "time-series forecasting",
                "models": ["ARIMA/Seasonal ARIMA", "Prophet", "Exponential Smoothing", "LightGBM with lag features"],
                "notes": "Create lag features, moving averages; check stationarity; consider holiday/seasonal effects.",
            }
        if has("class", "yes/no", "churn", "fraud", "spam", "default", "category", "labelled", "labeled", "classify"):
            return {
                "task": "classification",
                "models": ["Logistic Regression", "Random Forest", "XGBoost", "LightGBM", "SVM (linear/RBF)"],
                "notes": "Start with baseline logistic regression + proper CV; watch class imbalance; calibrate probabilities.",
            }
        if has("price", "amount", "score", "count", "rate", "continuous", "regression", "numeric"):
            return {
                "task": "regression",
                "models": ["Linear/Elastic Net", "Random Forest Regressor", "XGBoost/LightGBM Regressor", "CatBoost"],
                "notes": "Check feature scaling; try tree models if nonlinearity; use MAE/RMSE with CV.",
            }
        if has("text", "review", "nlp", "sentence", "document"):
            return {
                "task": "text classification / NLP",
                "models": ["Logistic on TF-IDF", "Linear SVM on TF-IDF", "DistilBERT fine-tune (if enough data)"],
                "notes": "Start with TF-IDF baselines; move to transformer fine-tuning for more accuracy.",
            }
        if has("image", "vision", "photo", "cnn", "picture"):
            return {
                "task": "image classification",
                "models": ["Transfer learning (ResNet/EfficientNet)", "Data augmentation"],
                "notes": "Start with transfer learning; freeze then unfreeze; early stopping.",
            }

        # Fallback: choose by keywords in features/target
        if has("binary", "0/1", "two classes"):
            kind = "classification"
        elif has("category", "multi-class", "multiclass"):
            kind = "multi-class classification"
        else:
            kind = "regression"

        base = {
            "classification": ["Logistic Regression", "Random Forest", "LightGBM"],
            "multi-class classification": ["Linear SVM / One-vs-Rest", "Random Forest", "LightGBM"],
            "regression": ["Elastic Net", "Random Forest Regressor", "LightGBM Regressor"],
        }
        return {"task": kind, "models": base[kind], "notes": "Use cross-validation and a hold-out test set."}

    if request.method == "POST":
        goal = request.form.get("goal", "")
        clues = request.form.get("clues", "")
        suggestion = suggest(goal, clues)
        return render_template("data_models.html", suggestion=suggestion)
    return render_template("data_models.html", suggestion=None)

# Optional: simple log API still supported
@bp.post("/api/log")
def api_log():
    payload = request.get_json(silent=True) or {}
    current_app.logger.info("api/log: %s", payload)
    return jsonify(ok=True, echo=payload)
