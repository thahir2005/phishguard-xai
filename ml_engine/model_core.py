"""
PhishGuard-XAI Inference & Explainability Core
Evaluates any URL, extracts 25 multi-dimensional features, executes the GBDT ensemble,
computes TreeSHAP attributions, and provides human-readable diagnostic explanations.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml_engine.feature_extractor import extract_features, FEATURE_COLUMNS


def sigmoid(x: float) -> float:
    if x < -35.0:
        return 0.0
    if x > 35.0:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


class PhishGuardEngine:
    _instance = None

    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "trained_model_weights.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please run train_builtin_ensemble.py first.")

        with open(model_path, "r", encoding="utf-8") as f:
            self.model = json.load(f)

        self.base_log_odds = self.model["base_log_odds"]
        self.trees = self.model["trees"]
        self.feature_baselines = self.model.get("feature_baselines", {})
        self.test_metrics = self.model.get("test_metrics", {})

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PhishGuardEngine()
        return cls._instance

    def scan_url(self, raw_url: str) -> dict:
        features = extract_features(raw_url)
        feature_vector = [features[col] for col in FEATURE_COLUMNS]

        # Calculate prediction score & per-feature SHAP contributions
        score = self.base_log_odds
        shap_values = {col: 0.0 for col in FEATURE_COLUMNS}

        for tree in self.trees:
            f_idx = tree["feature_idx"]
            f_name = tree["feature_name"]
            thresh = tree["threshold"]

            val = feature_vector[f_idx]
            if val <= thresh:
                delta = tree["val_left"]
            else:
                delta = tree["val_right"]

            score += delta
            shap_values[f_name] += delta

        # Round SHAP values
        shap_values = {k: round(v, 4) for k, v in shap_values.items()}

        # Probability
        probability = sigmoid(score)
        risk_score = round(probability * 100, 1)

        # Classification label
        if risk_score >= 65.0:
            classification = "CRITICAL_PHISHING"
            badge = "DANGER"
        elif risk_score >= 35.0:
            classification = "SUSPICIOUS"
            badge = "WARNING"
        else:
            classification = "SAFE"
            badge = "SECURE"

        # Generate human explanations based on top SHAP contributors
        human_explanation = self._build_human_explanation(raw_url, features, shap_values, risk_score)

        # Top positive contributors (pushing towards phishing)
        top_risk_features = sorted(
            [(k, v) for k, v in shap_values.items() if v > 0],
            key=lambda item: item[1],
            reverse=True
        )[:5]

        # Top negative contributors (pushing towards safe)
        top_safe_features = sorted(
            [(k, v) for k, v in shap_values.items() if v < 0],
            key=lambda item: item[1]
        )[:5]

        return {
            "url": raw_url,
            "classification": classification,
            "badge": badge,
            "risk_score": risk_score,
            "phishing_probability": round(probability, 4),
            "human_explanation": human_explanation,
            "shap_explanation": {
                "base_value": round(self.base_log_odds, 4),
                "model_output": round(score, 4),
                "top_risk_drivers": [{"feature": f, "impact": v} for f, v in top_risk_features],
                "top_safe_drivers": [{"feature": f, "impact": v} for f, v in top_safe_features],
                "all_features_shap": shap_values
            },
            "features": features
        }

    def _build_human_explanation(self, url: str, features: dict, shap: dict, risk_score: float) -> dict:
        reasons = []
        positive_factors = []

        # TLD Check (Top factor in paper)
        if features["is_common_tld"] == 0:
            reasons.append("Uncommon or high-risk top-level domain (TLD) frequently observed in disposable cyber-fraud.")
        else:
            positive_factors.append("Legitimate, widely recognized top-level domain (.com, .gov, or approved ccTLD).")

        # Shannon Entropy
        if features["entropy"] >= 3.6:
            reasons.append(f"High domain randomness (Entropy: {features['entropy']:.2f}) indicates an automated or algorithmically generated URL.")
        elif features["entropy"] <= 2.8:
            positive_factors.append(f"Standard linguistic domain structure with natural character entropy ({features['entropy']:.2f}).")

        # Suspicious Words & Social Scams
        if features["suspicious_word_count"] > 0:
            reasons.append(f"Contains {features['suspicious_word_count']} high-risk keywords associated with credential harvesting, banking, or social ads.")

        # Punycode / Homograph Spoofing
        if features["is_punycode"] == 1 or features["homograph_spoof_score"] > 0:
            reasons.append("CRITICAL: Internationalized Domain Name (IDN) or Cyrillic homograph character spoofing detected.")

        # Brand Impersonation
        if features["brand_impersonation_score"] >= 0.8:
            reasons.append("High similarity to protected banking or government brand (potential typosquatting / brand spoofing).")

        # Subdomains & Structural Depth
        if features["num_subdomains"] >= 2:
            reasons.append(f"Excessive subdomain nesting ({features['num_subdomains']} levels) masking the true destination.")

        if features["has_ip"] == 1:
            reasons.append("Uses a raw IP address instead of a registered domain name.")

        if features["is_shortened_url"] == 1:
            reasons.append("Obfuscated using a public URL shortening service.")

        # HTTPS factor
        if features["has_https"] == 1:
            positive_factors.append("Encrypted HTTPS protocol present (Note: Modern phishers also use free SSL certificates).")
        else:
            reasons.append("Insecure plain HTTP connection with no cryptographic transit security.")

        if risk_score >= 65.0:
            action = "DO NOT VISIT. This link demonstrates characteristics of phishing, credential harvesting, or online financial scam."
            summary = "High probability of malicious intent. Do not enter credentials, OTPs, or financial details."
        elif risk_score >= 35.0:
            action = "PROCEED WITH CAUTION. Verify the domain identity and check the address bar before entering any information."
            summary = "Suspicious attributes detected that diverge from standard legitimate portals."
        else:
            action = "SAFE TO ACCESS. Structural and lexical attributes match verified benign portals."
            summary = "No anomalous or fraudulent patterns detected."

        return {
            "summary": summary,
            "action": action,
            "primary_risk_reasons": reasons if reasons else ["No specific risk anomalies found."],
            "positive_indicators": positive_factors
        }


# Quick test when executed directly
if __name__ == "__main__":
    engine = PhishGuardEngine.get_instance()
    test_urls = [
        "https://alrajhibank.com.sa/ar/personal-banking",
        "http://secure.login.nafath-verify.top/claim?token=89432",
        "https://absher.sa/portal/services",
        "http://noon-clearance-sale.xyz/iphone17/otp_submit?id=3829"
    ]
    for u in test_urls:
        res = engine.scan_url(u)
        print(f"\nURL: {res['url']}")
        print(f"Risk Score: {res['risk_score']}% | Class: {res['classification']}")
        print(f"Summary: {res['human_explanation']['summary']}")
        print(f"Top Risk Drivers: {res['shap_explanation']['top_risk_drivers']}")
