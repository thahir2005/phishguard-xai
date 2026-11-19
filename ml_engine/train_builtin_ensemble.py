"""
Pure-Python Ensemble GBDT Trainer & Weight Serializer
Trains a gradient-boosted decision tree ensemble on the dataset, evaluates metrics,
and serializes the model structure for real-time inference and exact TreeSHAP attribution.
Zero external library dependencies required.
"""

import csv
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml_engine.feature_extractor import FEATURE_COLUMNS

random.seed(42)


def sigmoid(x):
    if x < -30:
        return 0.0
    if x > 30:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


class DecisionStump:
    def __init__(self, feature_idx, threshold, value_left, value_right):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.value_left = value_left
        self.value_right = value_right

    def predict(self, x):
        if x[self.feature_idx] <= self.threshold:
            return self.value_left
        return self.value_right


def load_dataset(csv_path):
    rows = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            x = [float(r[col]) for col in FEATURE_COLUMNS]
            y = int(r["label"])
            rows.append((x, y))
    return rows


def evaluate_split(X, residuals, feature_idx, threshold):
    left_res = []
    right_res = []
    for i, x in enumerate(X):
        if x[feature_idx] <= threshold:
            left_res.append(residuals[i])
        else:
            right_res.append(residuals[i])

    if not left_res or not right_res:
        return float("inf"), 0.0, 0.0

    mean_left = sum(left_res) / len(left_res)
    mean_right = sum(right_res) / len(right_res)

    sse_left = sum((r - mean_left) ** 2 for r in left_res)
    sse_right = sum((r - mean_right) ** 2 for r in right_res)

    return sse_left + sse_right, mean_left, mean_right


def train_gbdt(X_train, y_train, n_estimators=60, learning_rate=0.15):
    n_samples = len(X_train)
    n_features = len(X_train[0])

    # Initial log-odds base value
    pos_count = sum(y_train)
    neg_count = n_samples - pos_count
    base_log_odds = math.log((pos_count + 1e-5) / (neg_count + 1e-5))

    current_preds = [base_log_odds] * n_samples
    trees = []

    print(f"Training Ensemble GBDT with {n_estimators} estimators on {n_samples} samples...")

    for est in range(n_estimators):
        # Calculate gradients (pseudo-residuals for binary log-loss)
        # residual = y - p
        residuals = []
        for i in range(n_samples):
            p = sigmoid(current_preds[i])
            residuals.append(y_train[i] - p)

        best_loss = float("inf")
        best_feat = 0
        best_thresh = 0.0
        best_val_left = 0.0
        best_val_right = 0.0

        # Sample features (feature subsampling like XGBoost colsample_bytree = 0.8)
        candidate_feats = random.sample(range(n_features), int(n_features * 0.85))

        for f_idx in candidate_feats:
            values = sorted(set(x[f_idx] for x in X_train))
            if len(values) <= 1:
                continue

            # Check candidate split percentiles
            step = max(1, len(values) // 15)
            for v_idx in range(0, len(values) - 1, step):
                thresh = (values[v_idx] + values[v_idx + 1]) / 2.0
                loss, val_l, val_r = evaluate_split(X_train, residuals, f_idx, thresh)
                if loss < best_loss:
                    best_loss = loss
                    best_feat = f_idx
                    best_thresh = thresh
                    best_val_left = val_l
                    best_val_right = val_r

        # Scale tree leaf values by learning rate
        val_left = best_val_left * learning_rate
        val_right = best_val_right * learning_rate

        tree = {
            "feature_idx": best_feat,
            "feature_name": FEATURE_COLUMNS[best_feat],
            "threshold": round(best_thresh, 4),
            "val_left": round(val_left, 5),
            "val_right": round(val_right, 5)
        }
        trees.append(tree)

        # Update predictions
        for i in range(n_samples):
            if X_train[i][best_feat] <= best_thresh:
                current_preds[i] += val_left
            else:
                current_preds[i] += val_right

        if (est + 1) % 15 == 0 or est == n_estimators - 1:
            # Current train accuracy
            correct = sum(1 for i in range(n_samples) if (sigmoid(current_preds[i]) >= 0.5) == y_train[i])
            acc = correct / n_samples
            print(f"Estimator {est + 1}/{n_estimators} - Train Accuracy: {acc * 100:.2f}%")

    return {
        "base_log_odds": round(base_log_odds, 4),
        "learning_rate": learning_rate,
        "n_estimators": n_estimators,
        "feature_names": FEATURE_COLUMNS,
        "trees": trees
    }


def evaluate_model(model, X_test, y_test):
    base = model["base_log_odds"]
    trees = model["trees"]

    y_pred = []
    y_prob = []

    for x in X_test:
        score = base
        for tree in trees:
            if x[tree["feature_idx"]] <= tree["threshold"]:
                score += tree["val_left"]
            else:
                score += tree["val_right"]
        prob = sigmoid(score)
        y_prob.append(prob)
        y_pred.append(1 if prob >= 0.5 else 0)

    # Metrics
    tp = sum(1 for p, y in zip(y_pred, y_test) if p == 1 and y == 1)
    tn = sum(1 for p, y in zip(y_pred, y_test) if p == 0 and y == 0)
    fp = sum(1 for p, y in zip(y_pred, y_test) if p == 1 and y == 0)
    fn = sum(1 for p, y in zip(y_pred, y_test) if p == 0 and y == 1)

    acc = (tp + tn) / len(y_test)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "accuracy": round(acc * 100, 2),
        "precision": round(prec * 100, 2),
        "recall": round(rec * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "confusion_matrix": {"TP": tp, "TN": tn, "FP": fp, "FN": fn}
    }


def compute_feature_baselines(X_train):
    n_features = len(FEATURE_COLUMNS)
    baselines = {}
    for j in range(n_features):
        vals = [x[j] for x in X_train]
        mean_val = sum(vals) / len(vals)
        baselines[FEATURE_COLUMNS[j]] = round(mean_val, 4)
    return baselines


def main():
    dataset_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dataset", "arabic_social_phishing_dataset.csv")
    )
    data = load_dataset(dataset_path)
    random.shuffle(data)

    # 80% train / 20% test split exactly as Dirchaoui et al. Section 3.1
    split_idx = int(0.8 * len(data))
    train_data = data[:split_idx]
    test_data = data[split_idx:]

    X_train = [d[0] for d in train_data]
    y_train = [d[1] for d in train_data]
    X_test = [d[0] for d in test_data]
    y_test = [d[1] for d in test_data]

    print(f"Loaded {len(data)} total samples: {len(X_train)} train, {len(X_test)} test.")

    model = train_gbdt(X_train, y_train, n_estimators=65, learning_rate=0.18)
    metrics = evaluate_model(model, X_test, y_test)

    print("\n--- TEST SET EVALUATION RESULTS ---")
    print(f"Accuracy : {metrics['accuracy']}% (Base paper XGBoost: 96.57%)")
    print(f"Precision: {metrics['precision']}% (Base paper XGBoost: 97.46%)")
    print(f"Recall   : {metrics['recall']}% (Base paper XGBoost: 95.65%)")
    print(f"F1-Score : {metrics['f1_score']}% (Base paper XGBoost: 96.55%)")
    print(f"Confusion Matrix: {metrics['confusion_matrix']}")

    # Attach metadata, test metrics, and baseline feature values
    model["test_metrics"] = metrics
    model["feature_baselines"] = compute_feature_baselines(X_train)

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "trained_model_weights.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    print(f"\nModel weights and metadata successfully serialized to: {output_path}")


if __name__ == "__main__":
    main()
