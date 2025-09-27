def suggest_models(prompt: str) -> list[str]:
    """
    A very light heuristic suggestor for demo purposes.
    Looks at keywords in the prompt and returns typical "average" choices.
    """
    p = prompt.lower()
    suggestions: list[str] = []

    if any(k in p for k in ["predict", "forecast", "regression"]):
        suggestions += ["LinearRegression", "RandomForestRegressor", "XGBoostRegressor (if allowed)"]

    if any(k in p for k in ["classify", "classification", "label"]):
        suggestions += ["LogisticRegression", "RandomForestClassifier", "XGBoostClassifier (if allowed)"]

    if any(k in p for k in ["time series", "timeseries", "seasonal"]):
        suggestions += ["SARIMA", "Prophet (if allowed)"]

    if any(k in p for k in ["cluster", "segment", "group"]):
        suggestions += ["KMeans", "DBSCAN"]

    if not suggestions:
        suggestions = [
            "Baseline (Mean/Mode)",
            "LogisticRegression",
            "RandomForest",
            "XGBoost (if allowed)"
        ]

    out, seen = [], set()
    for m in suggestions:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out
