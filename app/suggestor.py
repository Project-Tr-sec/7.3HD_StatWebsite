def suggest_models(prompt: str) -> list[str]:
    p = prompt.lower()
    suggestions: list[str] = []

    if any(k in p for k in ["price", "predict", "regression", "numeric", "continuous"]):
        suggestions += ["LinearRegression", "RandomForestRegressor"]

    if any(k in p for k in ["classify", "category", "spam", "fraud", "churn", "label"]):
        suggestions += ["LogisticRegression", "RandomForestClassifier", "NaiveBayes"]

    if any(k in p for k in ["text", "nlp", "review", "tweet", "document"]):
        suggestions += ["TFIDF+LogisticRegression", "NaiveBayes"]

    if any(k in p for k in ["image", "vision", "photo"]):
        suggestions += ["CNN (e.g., ResNet50 fine-tune)"]

    if any(k in p for k in ["time series", "timeseries", "temporal", "forecast"]):
        suggestions += ["ARIMA", "Prophet"]

    if any(k in p for k in ["cluster", "segment", "group"]):
        suggestions += ["KMeans", "DBSCAN"]

    if not suggestions:
        suggestions = ["Baseline (Mean/Mode)", "LogisticRegression", "RandomForest", "XGBoost (if allowed)"]

    out, seen = [], set()
    for m in suggestions:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out
