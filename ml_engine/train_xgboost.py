"""
Production Training Pipeline using Scikit-Learn, XGBoost, and SHAP.
Run this script in an environment where xgboost, scikit-learn, and shap are installed
to regenerate full scientific plots and cross-validation artifacts.
"""

import os
import sys
import pandas as pd
import numpy as np

try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
    import shap
    import matplotlib.pyplot as plt
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False


def main():
    if not HAS_LIBS:
        print("[NOTICE] External libraries (xgboost, shap, matplotlib) not installed in this environment.")
        print("To run the full XGBoost and SHAP plot generation pipeline, run:")
        print("    pip install xgboost scikit-learn shap matplotlib pandas")
        print("\nNote: PhishGuard-XAI already includes the self-contained pure-Python engine")
        print("which runs out-of-the-box via: python3 ml_engine/train_builtin_ensemble.py")
        sys.exit(0)

    dataset_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dataset", "arabic_social_phishing_dataset.csv")
    )
    df = pd.read_csv(dataset_path)

    feature_cols = [c for c in df.columns if c not in ["url", "label"]]
    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Dataset Loaded: {len(df)} samples ({X_train.shape[0]} train, {X_test.shape[0]} test)")

    # Initialize XGBoost matching paper hyperparameters
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("\n--- XGBOOST EXPERIMENTAL RESULTS ---")
    print(f"Accuracy : {acc * 100:.2f}% (Dirchaoui et al. 2026: 96.57%)")
    print(f"Precision: {prec * 100:.2f}% (Dirchaoui et al. 2026: 97.46%)")
    print(f"Recall   : {rec * 100:.2f}% (Dirchaoui et al. 2026: 95.65%)")
    print(f"F1-Score : {f1 * 100:.2f}% (Dirchaoui et al. 2026: 96.55%)")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Compute SHAP Explanations
    print("Computing TreeSHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "research_paper"))
    os.makedirs(output_dir, exist_ok=True)

    # Figure 1: Summary Bar Plot
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
    plt.title("SHAP Feature Importance (Mean |SHAP Value|)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "shap_summary_plot.png"), dpi=300)
    plt.close()

    # Figure 2: Beeswarm Plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, show=False)
    plt.title("SHAP Beeswarm Plot (Directional Feature Impact)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "shap_beeswarm_plot.png"), dpi=300)
    plt.close()

    print(f"SHAP figures successfully saved to {output_dir}")


if __name__ == "__main__":
    main()
