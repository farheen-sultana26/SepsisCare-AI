from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from xgboost import XGBClassifier


PROJECT_DIR = Path(__file__).resolve().parent
DATA_FIXED = PROJECT_DIR / "Data_after_Cleaning_fixed.csv"
MODEL_OUT = PROJECT_DIR / "final_xgboost_sepsis_model_v2.pkl"
REPORT_OUT = PROJECT_DIR / "model_report_v2.json"


def eval_binary(y_true, y_prob, threshold: float = 0.5) -> dict:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def main():
    if not DATA_FIXED.exists():
        raise FileNotFoundError(
            f"Missing {DATA_FIXED.name}. Run prepare_dataset.py first."
        )

    df = pd.read_csv(DATA_FIXED)
    if "hospital_expire_flag" not in df.columns:
        raise ValueError("Expected target column 'hospital_expire_flag' not found.")

    y = df["hospital_expire_flag"].astype(int).values
    X = df.drop(columns=["hospital_expire_flag"])

    # Train/test split for an honest final report
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Class imbalance handling
    pos = (y_train == 1).sum()
    neg = (y_train == 0).sum()
    scale_pos_weight = float(neg / max(pos, 1))

    # Light tuning via CV over a small grid (fast, reproducible)
    candidates = []
    for max_depth in [3, 4, 5]:
        for learning_rate in [0.03, 0.06, 0.10]:
            for subsample in [0.8, 1.0]:
                for colsample_bytree in [0.8, 1.0]:
                    candidates.append(
                        dict(
                            n_estimators=900,
                            max_depth=max_depth,
                            learning_rate=learning_rate,
                            subsample=subsample,
                            colsample_bytree=colsample_bytree,
                        )
                    )

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    best = None
    best_auc = -1.0

    X_train_np = X_train.values
    for params in candidates:
        aucs = []
        for tr_idx, va_idx in skf.split(X_train_np, y_train):
            m = XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                tree_method="hist",
                random_state=42,
                n_jobs=-1,
                reg_lambda=1.0,
                min_child_weight=1.0,
                gamma=0.0,
                scale_pos_weight=scale_pos_weight,
                **params,
            )
            m.fit(X_train_np[tr_idx], y_train[tr_idx])
            p = m.predict_proba(X_train_np[va_idx])[:, 1]
            aucs.append(roc_auc_score(y_train[va_idx], p))
        mean_auc = float(np.mean(aucs))
        if mean_auc > best_auc:
            best_auc = mean_auc
            best = params

    # Train final model
    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
        reg_lambda=1.0,
        min_child_weight=1.0,
        gamma=0.0,
        scale_pos_weight=scale_pos_weight,
        **(best or {}),
    )
    model.fit(X_train.values, y_train)

    # Evaluate
    p_train = model.predict_proba(X_train.values)[:, 1]
    p_test = model.predict_proba(X_test.values)[:, 1]

    report = {
        "data": {
            "rows": int(df.shape[0]),
            "cols": int(df.shape[1]),
            "positive_rate": float(np.mean(y)),
        },
        "best_cv_mean_auc": float(best_auc),
        "best_params": best,
        "train": eval_binary(y_train, p_train),
        "test": eval_binary(y_test, p_test),
        "threshold": 0.5,
        "features": list(X.columns),
    }

    joblib.dump(model, MODEL_OUT)
    REPORT_OUT.write_text(json.dumps(report, indent=2))

    print(f"Saved model: {MODEL_OUT}")
    print(f"Saved report: {REPORT_OUT}")
    print("TEST metrics:", report["test"])


if __name__ == "__main__":
    main()

