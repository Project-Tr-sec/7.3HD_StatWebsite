from __future__ import annotations

import re
from typing import Dict, List


def suggest_models(description: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Very lightweight rule-based "what model should I use?" helper.
    Looks at the text for signals: regression/classification/time series/text/nlp, etc.
    Returns a structure easy to render in HTML.
    """
    text = description.lower()

    # signals
    is_time = any(k in text for k in ["time series", "temporal", "timestamp", "monthly", "daily", "weekly", "trend", "seasonal"])
    is_text = any(k in text for k in ["text", "nlp", "tweets", "reviews", "documents"])
    is_image = any(k in text for k in ["image", "picture", "photo", "cnn"])
    # target hints
    is_binary = any(k in text for k in ["yes/no", "binary", "churn", "fraud", "spam", "default", "win/loss", "0/1"])
    is_multiclass = any(k in text for k in ["multiclass", "3 classes", "three classes", "category", "categories"])
    is_regression = any(k in text for k in ["price", "amount", "dollars", "continuous", "regression", "quantity"])
    # data scale / features
    many_features = any(k in text for k in ["many features", "high dimensional", "100+", "hundreds of features"])
    n_small = any(k in text for k in ["small dataset", "few samples", "n<100", "n < 100"])
    n_large = any(k in text for k in ["large dataset", "big data", "millions", "100k", "n>10000", "n > 10000"])
    has_categorical = any(k in text for k in ["categorical", "one-hot", "ordinal", "category"])
    has_missing = any(k in text for k in ["missing", "na", "null", "impute"])

    suggestions: List[Dict[str, str]] = []

    if is_text:
        suggestions.append({
            "model": "TF-IDF + Logistic Regression (or Linear SVM)",
            "why": "Strong baseline for text classification; fast, interpretable, works well with sparse features.",
            "next": "Clean text → split train/test → TfidfVectorizer → LogisticRegression with class_weight='balanced' if needed."
        })
        suggestions.append({
            "model": "Naive Bayes (Multinomial)",
            "why": "Simple, effective for bag-of-words when features are counts.",
            "next": "CountVectorizer → MultinomialNB; compare F1 vs Logistic/SVM."
        })

    elif is_time:
        suggestions.append({
            "model": "SARIMA / Prophet",
            "why": "Handles trend and seasonality for univariate time series.",
            "next": "Decompose → pick seasonal period → grid small SARIMA search or use Prophet; evaluate on rolling forecast."
        })
        suggestions.append({
            "model": "Gradient Boosting (XGBoost/LightGBM) with lag features",
            "why": "If you’ve multiple regressors (exogenous vars), tree models with engineered lags often win.",
            "next": "Create lag/rolling stats features; time-aware split; train XGB/LGBM; check feature importance."
        })

    elif is_image:
        suggestions.append({
            "model": "Transfer Learning (ResNet/EfficientNet)",
            "why": "Leverage pretrained CNNs for strong accuracy with limited data.",
            "next": "Resize/augment images → freeze base → train top layers → unfreeze few blocks → fine-tune."
        })

    else:
        # tabular
        if is_regression and not (is_binary or is_multiclass):
            suggestions.append({
                "model": "Elastic Net (Linear Regression with L1+L2)",
                "why": "Good baseline for numeric targets; robust to multicollinearity; feature selection via L1.",
                "next": "Standardize numeric; one-hot categoricals; cross-validate alpha/l1_ratio."
            })
            suggestions.append({
                "model": "Gradient Boosting (XGBoost/LightGBM/CatBoost)",
                "why": "Strong default on heterogeneous tabular data; handles non-linearities & interactions.",
                "next": "Minimal preprocessing; tune n_estimators, learning_rate, max_depth; early stopping."
            })
        elif is_binary or ("classify" in text and not is_multiclass):
            suggestions.append({
                "model": "Logistic Regression",
                "why": "Interpretable baseline for binary targets; works well with standardized numeric + one-hot categoricals.",
                "next": "Scale numeric; one-hot categoricals; penalty='l2' with C tuned; consider class_weight."
            })
            suggestions.append({
                "model": "Random Forest / Gradient Boosting",
                "why": "Powerful on tabular; less sensitive to scaling; captures interactions.",
                "next": "Tune trees modestly; evaluate ROC-AUC, PR-AUC for imbalance."
            })
        elif is_multiclass:
            suggestions.append({
                "model": "Linear SVM / Logistic Regression (One-vs-Rest)",
                "why": "Strong linear baselines for multiclass tasks.",
                "next": "Standardize; one-hot; use OvR with balanced classes or class weights."
            })
            suggestions.append({
                "model": "CatBoost",
                "why": "Handles categorical features natively; often strong on multiclass tabular.",
                "next": "Label/cat features declared; early stopping; check confusion matrix."
            })
        else:
            # default fallback
            suggestions.append({
                "model": "Start with a Baseline: Linear/Logistic → Tree Ensemble",
                "why": "Covers most tabular problems; compare linear interpretability vs ensemble accuracy.",
                "next": "Build quick baseline; then try XGBoost/LightGBM; pick by cross-val metric."
            })

    # modifiers
    if many_features:
        suggestions.append({
            "model": "Dimensionality Reduction (PCA) or Feature Selection",
            "why": "High-dimensional data benefits from reducing noise/collinearity.",
            "next": "Try PCA to 95% variance or use model-based selection (Elastic Net, tree importances)."
        })
    if has_missing:
        suggestions.append({
            "model": "Imputation Strategy",
            "why": "Handle missingness before modeling to avoid biased training.",
            "next": "SimpleImputer (median/most_frequent) or iterative imputer; add missing flags if informative."
        })
    if has_categorical:
        suggestions.append({
            "model": "Encoding",
            "why": "Categorical features need encoders.",
            "next": "One-hot for low-cardinality; target or CatBoost encoding for high-cardinality."
        })
    if n_small:
        suggestions.append({
            "model": "Prefer simpler/regularized models",
            "why": "Small n risks overfit.",
            "next": "Bias toward Logistic/Linear with regularization; use repeated CV; avoid heavy tuning."
        })
    if n_large:
        suggestions.append({
            "model": "Efficient learners",
            "why": "Large n favors scalable algorithms.",
            "next": "LightGBM/XGBoost with early stopping; or linear solvers with SGD."
        })

    return {"suggestions": suggestions}
