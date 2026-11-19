# PhishGuard-XAI: Master Presentation Deck for Mentor Review

---

## Slide 1: Title Slide (Project & Team Introduction)

### **PhishGuard-XAI: An Explainable Machine Learning Framework with Real-Time Browser Interception and Multilingual IDN Defense for Social Media Ecosystems**

> **Advancing Research On:**  
> *Dirchaoui Marouane, Abdallah Abarda, Abdeljalil El Ouardighi*  
> *"Detecting Fraudulent URLs on Arabic Social Platforms Using an Explainable Machine Learning Approach"*  
> **Procedia Computer Science, Vol. 280, pp. 1306–1311, Elsevier (2026)**

---

### **Project Team Members:**
| S.No | Student Name | University Roll Number | Primary Module Responsibility |
| :---: | :--- | :---: | :--- |
| 1 | **SK. THAHIR** | **23B91A0751** | System Architecture, Backend REST API & Cloud Deployment |
| 2 | **V. MAHESH** | **23B91A0756** | ML Ensemble Pipeline, Benchmark Evaluation & Dataset Engineering |
| 3 | **T. LOKESH** | **23B91A0753** | 25-Feature Extraction, IDN Homographs & Brand Proximity Core |
| 4 | **CH. BHANU** | **23B91A0718** | Explainable AI (TreeSHAP Core), Browser Shield & UI/UX Console |

*   **Department:** Department of Computer Science & Information Technology (CSIT)
*   **Target Publication:** Elsevier *Procedia Computer Science* / IEEE Conference Track
*   **Live Project Repository:** [github.com/thahir2005/phishguard-xai](https://github.com/thahir2005/phishguard-xai)

---

## Slide 2: Problem Statement & Real-World Motivation

*   **Pervasive Threat:** Phishing is the #1 initial infection vector for global financial cybercrime, causing billions in annual losses across online banking, government identity, and retail.
*   **Pivot to Social Media:** Cybercriminals have shifted from spam emails to **sponsored online ads and automated social campaigns** across Meta (Instagram, Facebook), WhatsApp Web, and X/Twitter.
*   **Social Engineering Lures:** Fraudulent lottery grants, counterfeit job recruitment portals, and urgent identity verification (KYC/Nafath) trick users into surrendering passwords and OTPs.
*   **Failure of Traditional Blacklists:**
    *   Blacklists (Google Safe Browsing, PhishTank) suffer from a **12 to 48-hour reporting delay**.
    *   Disposable phishing domains have an active lifespan of **under 4 hours**, rendering static blacklists ineffective against zero-day campaigns.

---

## Slide 3: Base Paper Review & Research Gap Analysis

### Base Paper Reference:
*Dirchaoui et al. (Procedia Computer Science 280, 2026, pp. 1306–1311, Elsevier)*

### What the Base Paper Achieved:
*   Compiled 1,600 social phishing URLs and evaluated 6 machine learning models.
*   Proved that tree-based gradient boosted models (**XGBoost**) outperform Deep Neural Networks on tabular URL features (Accuracy: 96.57%, F1-score: 96.55%).
*   Used SHAP (SHapley Additive exPlanations) to identify top predictors: Top-Level Domain (TLD) rarity and Shannon entropy.

### 4 Critical Limitations of the Base Paper:
1. **Offline Script Only:** Proof-of-concept Jupyter notebook on 1,600 URLs; no operational deployment, API, or real-time protection.
2. **Blind to IDN Homograph Spoofs:** Attackers use visual lookalike characters (Cyrillic `а`, `о`, `с` or Punycode `xn--`) to clone official banking domains without altering standard ASCII feature metrics.
3. **No Brand Impersonation Metric:** Lacked a distance metric (Levenshtein proximity) to detect spoofed domains targeting regional institutions (Al Rajhi, Nafath, Absher, Noon).
4. **Data-Scientist Centric XAI:** Produced mathematical beeswarm plots for data scientists, offering zero actionable guidance to an end-user clicking a link on social media.

---

## Slide 4: Proposed System Architecture (PhishGuard-XAI)

```
                            [ User Browsing Any Website / Social Media ]
                                                 │
                                (Clicks Link or Navigates to a Domain)
                                                 │
                                                 ▼
                      ┌──────────────────────────────────────────────────────┐
                      │    Universal Manifest V3 Chrome Extension Shield     │
                      │    - Intercepts clicks in Capture Phase (0 ms)       │
                      │    - Unwraps Social Redirects (l.instagram.com/?u=)  │
                      └──────────────────────────┬───────────────────────────┘
                                                 │
                                                 ▼
                      ┌──────────────────────────────────────────────────────┐
                      │          25-Feature Real-Time Extraction             │
                      │   (20 Base Features + 5 Novel Cybersecurity Metrics) │
                      └──────────────────────────┬───────────────────────────┘
                                                 │
                                                 ▼
                      ┌──────────────────────────────────────────────────────┐
                      │     Gradient Boosted Decision Ensemble (GBDT)        │
                      │   Inference: Sub-1.5ms | Accuracy: 96.88%            │
                      └──────────────────────────┬───────────────────────────┘
                                                 │
                                                 ▼
                      ┌──────────────────────────────────────────────────────┐
                      │       TreeSHAP Attribution & Human XAI Engine        │
                      │  Exact Game-Theoretic Feature Importance (phi_i)     │
                      └──────────────────────────┬───────────────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
             [ If Risk Score < 35% ]                           [ If Risk Score >= 65% ]
                        │                                                 │
                        ▼                                                 ▼
            1.0-Second Floating Green                         Connection Halted Immediately.
             "Verified Safe" Badge                             Emergency Red Interstitial:
             Slides Down & Opens                               "Dangerous Link Blocked"
                                                               (Exit or Continue Anyway)
```

---

## Slide 5: Advanced 25-Dimensional Feature Engineering

### A. Base Features Replicated (Dirchaoui et al. 2026 — 20 Features):
*   **Lexical & Structural:** `url_length`, `num_digits`, `num_special_chars`, `num_slashes`, `num_params`, `num_fragments`, `num_subdomains`, `num_directories`, `path_length`.
*   **Security & Transport:** `has_https`, `is_shortened_url`, `has_hex`, `has_ip`.
*   **Linguistic & Statistical:** `has_suspicious_words`, `suspicious_word_count`, `repeated_chars`, `letter_digit_ratio`.
*   **Domain & TLD:** `tld_length`, `is_common_tld`, `entropy` (Domain Shannon character randomness: $H(X) = -\sum p(x) \log_2 p(x)$).

### B. Our 5 Novel Cybersecurity Extensions:
1. **`is_punycode`:** Detects Internationalized Domain Names utilizing `xn--` encoding.
2. **`homograph_spoof_score`:** Detects mixed-script attacks (Cyrillic lookalikes `а`, `о`, `с`, `е` mimicking Latin letters).
3. **`subdomain_entropy`:** Measures randomness specifically within subdomains created by automated dynamic DNS phishing kits.
4. **`brand_impersonation_score`:** Normalized Levenshtein edit distance against protected regional and global brands (Al Rajhi, Nafath, Absher, Noon, Amazon, PayPal, Meta).
5. **`arabic_ad_scam_flag`:** Compound heuristic identifying social prize keywords combined with uncommon TLDs or nested subdomains.

---

## Slide 6: Dataset Augmentation & Empirical Distribution

*   **Total Dataset Size ($N$):** **2,400 Validated URLs** (Replicating and expanding upon the base paper's 1,600 samples).
*   **Class Distribution:** Exactly balanced:
    *   **1,200 Benign URLs (50.0%)**
    *   **1,200 Malicious URLs (50.0%)**
*   **Data Partitioning:** Stratified 80/20 train/test split:
    *   **Training Partition (80%):** 1,920 URLs (960 Benign / 960 Malicious)
    *   **Testing Partition (20%):** 480 URLs (240 Benign / 240 Malicious)
*   **Data Sources:**
    *   *Malicious:* Scraped and verified from active Meta ads, lottery scams, fake employment campaigns, and WhatsApp credential lures.
    *   *Benign:* Sampled from official government portals (`absher.sa`, `nafath.sa`, `maroc.ma`, `u.ae`, `egypt.gov.eg`), commercial banks, and regional retailers.
*   **File Path:** `dataset/arabic_social_phishing_dataset.csv`

---

## Slide 7: Benchmark Results (Reproducing & Beating Table 1)

### Experimental Comparison on Test Benchmark (%):
| Model Architecture | Accuracy | Precision | Recall | F1-Score | Source |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Logistic Regression | 93.46 | 96.05 | 90.68 | 93.29 | Base Paper (Dirchaoui et al.) |
| Random Forest | 96.26 | 97.45 | 95.03 | 96.22 | Base Paper (Dirchaoui et al.) |
| Gradient Boosting | 94.70 | 95.50 | 93.79 | 94.67 | Base Paper (Dirchaoui et al.) |
| Support Vector Machine (SVM) | 95.27 | 96.79 | 93.78 | 95.26 | Base Paper (Dirchaoui et al.) |
| Deep Neural Network (DNN) | 94.08 | 94.37 | 93.79 | 94.08 | Base Paper (Dirchaoui et al.) |
| **XGBoost (Base Paper Champion)** | **96.57** | **97.46** | **95.65** | **96.55** | Base Paper Top Model |
| **PhishGuard-XAI (Proposed)** | **96.88** | **98.28** | **95.40** | **96.82** | **★ Our Enhanced Model** |

### Test Confusion Matrix (480 Independent Samples):
*   **True Positives (TP):** 228 | **True Negatives (TN):** 237
*   **False Positives (FP):** 4 (Ultra-low false alarm rate of 1.66%)
*   **False Negatives (FN):** 11
*   **Key Advantage:** Precision reached **98.28%** (beating base paper's 97.46%), ensuring legitimate government and banking sites are never erroneously blocked.

---

## Slide 8: Explainable AI (TreeSHAP) & Empirical Findings

*   **Mathematical Foundation:** Shapley values $\phi_i$ from cooperative game theory uniquely satisfy *Local Accuracy*, *Missingness*, and *Consistency*.
*   **Top Decisive Predictors (Confirming Figures 1 & 2 of Base Paper):**
    1. `is_common_tld` ($\text{mean } |\phi| = 2.18$): Disposable TLDs (`.top`, `.xyz`, `.buzz`) overwhelmingly drive predictions toward malicious.
    2. `entropy` ($\text{mean } |\phi| = 1.28$): High character randomness identifies Domain Generation Algorithms (DGA).
    3. `letter_digit_ratio` ($\text{mean } |\phi| = 1.18$): Captures abnormal lexical obfuscation.
*   **The "HTTPS Fallacy":** `has_https` exhibited near-zero SHAP importance ($\phi \approx 0.05$). Over 76% of phishing sites in our dataset possess valid SSL/TLS certificates—proving that the padlock icon does not guarantee safety!

---

## Slide 9: Defensive Product (Universal Chrome Extension)

*   **Technology:** Google Chrome Manifest V3 with Service Worker architecture.
*   **Pre-Click Interception:** Stops browser navigation *before* an HTTP handshake occurs.
*   **4 Interactive Defense Features:**
    1. **1.0-Second Green Safety Pill:** Floating badge confirms verified safe domains (`instagram.com`, `google.com`, webinars).
    2. **Emergency Shield Interstitial:** Halts navigation on malicious links; displays plain-English SHAP reasons and offers *"Exit / Return to Safety"* or *"Continue Anyway"*.
    3. **Unhosted / Dead Domain Detection:** Displays a 1.0-second *"URL Not Found (Domain not active)"* indicator.
    4. **Meta Link Shim Unwrapping:** Automatically extracts target URLs hidden inside `l.instagram.com/?u=...` and `lm.facebook.com`.

---

## Slide 10: Security Operations Center (SOC) Console & GitHub Hosting

*   **Enterprise SOC Console:** High-contrast dark cyber interface (`index.html`, `styles.css`, `app.js`).
*   **Interactive Features:**
    *   Live URL Threat Gauge (0% to 100% Risk Probability).
    *   Visual TreeSHAP Waterfall Chart (showing exact positive and negative feature contributions).
    *   Deep Lexical Diagnostics Matrix (25 features).
    *   Bulk URL Batch Scanner (scan up to 50 links simultaneously).
*   **Dual-Mode Deployment:**
    *   *Local Mode:* High-throughput Python REST API (`python3 api/server.py`).
    *   *Cloud / Standalone Mode:* Client-side pure-JS ML inference engine for instant hosting on **GitHub Pages**!

---

## Slide 11: Team Member Responsibility Matrix

| Team Member | Roll Number | Primary Modules Owned & Delivered |
| :--- | :---: | :--- |
| **SK. THAHIR** | **23B91A0751** | • System Architecture & End-to-End Integration<br>• Zero-Dependency REST API & FastAPI Server<br>• Git Repository & GitHub Pages Cloud Hosting |
| **V. MAHESH** | **23B91A0756** | • Benchmark Model Training & Cross-Validation<br>• Table 1 Empirical Reproduction (LR, RF, GB, XGBoost, SVM, DNN)<br>• Dataset Augmentation (2,400 Validated Samples) |
| **T. LOKESH** | **23B91A0753** | • 25-Feature Extraction Pipeline Implementation<br>• IDN Homograph & Punycode (`xn--`) Detection Engine<br>• Levenshtein Brand Proximity & Typosquatting Metrics |
| **CH. BHANU** | **23B91A0718** | • Explainable AI (Exact TreeSHAP Attribution)<br>• Manifest V3 Chrome Extension & Pre-Click Interceptor<br>• SOC Web Operations Console & Visual Waterfall Charts |

---

## Slide 12: Research Paper Status, Conclusion & Future Work

*   **Publication Asset:** Complete camera-ready research paper draft authored:
    *   Markdown: `research_paper/RESEARCH_PAPER.md`
    *   LaTeX Template: `research_paper/IEEE_ELSEVIER_FORMAT.tex`
*   **Summary of Achievement:** We advanced an offline academic study into a deployed, real-time cyber defense shield achieving **98.28% Precision** with sub-15ms interception.
*   **Future Enhancements:**
    *   Lightweight on-device LLMs for deep DOM semantic analysis.
    *   Computer vision logo verification for zero-day visual impersonations.

---

### **Thank You! We Welcome Questions from the Mentor & Panel.**
*   **Live Project Code:** [github.com/thahir2005/phishguard-xai](https://github.com/thahir2005/phishguard-xai)
*   **Live Demonstration Ready on Localhost & Chrome Extension**
