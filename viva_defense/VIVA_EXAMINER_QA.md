# 25+ Toughest Viva & External Examiner Questions with Winning Answers

### Q1: Why did you choose XGBoost / Tree Ensembles instead of Deep Learning (LSTM, CNN, BERT)?
**Winning Answer:**  
*"As empirically proven in our base paper (Dirchaoui et al. 2026, Table 1) and in landmark machine learning studies such as Grinsztajn et al. (NeurIPS 2022) and Shwartz-Ziv & Armon (Information Fusion 2022), tree-based architectures consistently outperform deep neural networks on tabular cybersecurity datasets. In the base paper, a Deep Neural Network (DNN) achieved only 94.08% accuracy, whereas XGBoost reached 96.57%. Furthermore, tabular URL features are heterogeneous and non-smooth; decision trees provide axis-aligned decision partitions without requiring complex normalization. Lastly, tree ensembles execute in sub-millisecond time, allowing our Chrome Extension to scan links in under 15 milliseconds without GPU acceleration."*

---

### Q2: What is your exact novelty over the base paper by Dirchaoui et al. (2026)?
**Winning Answer:**  
*"The base paper had 4 major gaps which we solved:
1. **Deployment Gap:** The base paper was an offline proof-of-concept Jupyter notebook on 1,600 URLs. We built an end-to-end operational software product: a REST API, an enterprise Security Operations Center (SOC) dashboard, and a Manifest V3 Chrome Extension.
2. **Feature Set Gap:** The base paper only used 20 basic lexical features. We engineered 5 novel cybersecurity features: Punycode (`xn--`), Cyrillic-Arabic cross-script homograph detection, subdomain Shannon entropy, and normalized Levenshtein brand distance.
3. **Performance Gap:** Our model increased test precision to **98.28%** (compared to 97.46% in the base paper), drastically minimizing false alarms on critical government portals.
4. **Explainability Gap:** The base paper presented raw SHAP plots for researchers. We engineered a Human-Centered XAI layer that translates Shapley game-theoretic vectors into actionable English risk warnings for non-technical users."*

---

### Q3: How does SHAP work mathematically, and why did you use it over LIME?
**Winning Answer:**  
*"SHAP is grounded in cooperative game theory (Shapley values, Lundberg & Lee 2017). It measures the marginal contribution of each feature across all possible feature permutations $S \subseteq F \setminus \{i\}$:
$$\phi_i = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|! (|F| - |S| - 1)!}{|F|!} [f(S \cup \{i\}) - f(S)]$$
We chose TreeSHAP over LIME because:
1. **Mathematical Axioms:** SHAP uniquely satisfies three indispensable axioms: Local Accuracy (contributions sum to the model output), Missingness (missing features receive zero contribution), and Consistency.
2. **Deterministic & Exact:** LIME fits a local surrogate model using stochastic sampling, producing different explanations across runs. TreeSHAP computes exact, deterministic Shapley values in polynomial time $O(T L D^2)$ directly from tree structures."*

---

### Q4: If an attacker uses HTTPS, does your system fail to detect it?
**Winning Answer:**  
*"No, absolutely not. In fact, that was one of the core findings in Section 3.2 of Dirchaoui et al. (2026) and confirmed in our dataset: the feature `has_https` has a SHAP value near zero. Over 76% of modern phishing pages now use valid HTTPS certificates via Let's Encrypt or Cloudflare. Our system evaluates the entire 25-feature vector—specifically uncommon TLDs (`.top`, `.xyz`), domain Shannon entropy, subdomain nesting, and brand spoofing distance—which exposes the fraud regardless of whether HTTPS is present."*

---

### Q5: What is an IDN Homograph attack, and how does your system detect it?
**Winning Answer:**  
*"An Internationalized Domain Name (IDN) homograph attack occurs when an attacker registers a domain name using visually identical characters from different alphabets. For example, substituting the Latin letter 'a' with the Cyrillic letter 'а' (Unicode U+0430). To a human, `apple.com` and `аpple.com` look identical. In our feature extractor, we compute `is_punycode` (detecting the browser's `xn--` encoding) and `homograph_spoof_score` (checking for mixed scripts in Latin-oriented domains). If present, the model flags it with high severity."*

---

### Q6: How does your Chrome extension intercept links without slowing down the browser?
**Winning Answer:**  
*"We implemented a three-tier optimization architecture:
1. **Client-Side In-Memory Cache:** URLs that have already been evaluated are cached in memory in `background.js`, providing an immediate 0-millisecond response on repeated clicks.
2. **Event Delegation:** We attach a single capture listener to `document.addEventListener('click', ..., true)` rather than attaching listeners to thousands of individual DOM elements.
3. **Asynchronous Pre-Click Interception:** When a user clicks a link, `e.preventDefault()` halts browser navigation, the API or offline heuristic evaluates the URL in under 15ms, and only triggers the interstitial modal if the threat score is $\ge 65\%$."*

---

### Q7: What if the backend server is offline or unreachable? Does the extension stop working?
**Winning Answer:**  
*"No. We engineered an offline heuristic fallback inside `background.js`. If the backend API does not respond within 1.5 seconds, the extension seamlessly falls back to evaluating critical rules (uncommon TLD verification, high-risk bait words, Punycode detection, and entropy estimation) directly inside the browser, ensuring user protection is never interrupted."*

---

### Q8: How did you handle class imbalance in your dataset?
**Winning Answer:**  
*"We maintained an exact 50:50 balanced dataset consisting of 2,400 samples (1,200 verified benign URLs and 1,200 verified malicious URLs). During model evaluation, we utilized stratified 80/20 train/test splitting to preserve equal class proportions in both training (1,920 samples) and testing (480 samples). We also evaluated the model using Precision, Recall, and F1-Score rather than relying on raw accuracy alone."*

---

### Q9: What is Shannon Entropy in the context of URLs, and why is it important?
**Winning Answer:**  
*"Shannon entropy measures the uncertainty or unpredictability of characters in a string:
$$H(X) = -\sum p(x) \log_2 p(x)$$
Legitimate corporate and government domains are chosen for human readability and brand identity (e.g., `alrajhibank.com.sa` has an entropy around 2.7 to 3.0). Phishers and malware authors frequently employ Domain Generation Algorithms (DGA) or random string permutations (e.g., `x7k9p2-auth-verify.top` has an entropy > 3.8). Our TreeSHAP analysis shows that domain entropy is among the top 3 strongest predictors pushing the model toward a malicious verdict."*

---

### Q10: How do you protect against brand impersonation or typosquatting?
**Winning Answer:**  
*"We introduced a normalized Levenshtein edit distance metric (`brand_impersonation_score`) computed against a curated repository of protected regional and global entities (including Al Rajhi, Nafath, Absher, Aramco, STC, Noon, Amazon, PayPal, Meta). If a domain name contains a brand name as a substring inside an unverified domain (e.g., `alrajhi-portal-update.top`), or has an edit distance $\le 2$ from a legitimate brand, the brand impersonation score triggers an immediate surge in the phishing risk attribution."*

---

### Q11: What is the difference between Precision and Recall in phishing detection, and which is more important?
**Winning Answer:**  
*"Precision is $\frac{TP}{TP + FP}$ (out of all links we flagged as phishing, how many were actually phishing). Recall is $\frac{TP}{TP + FN}$ (out of all actual phishing links out there, how many did we catch).  
While high recall is necessary to catch threats, in a real-world enterprise or browser extension, **Precision is the most critical operational metric**. A low precision means high False Positives—blocking legitimate government services or banking portals—which causes users to disable the security extension out of frustration. Our system achieved **98.28% Precision**, which is higher than the base paper's 97.46%."*

---

### Q12: Can this model detect zero-day phishing attacks?
**Winning Answer:**  
*"Yes. Blacklists fail on zero-day phishing because they rely on previously reported domain signatures. Our system is a feature-based machine learning model that evaluates structural, lexical, and behavioral patterns of the URL itself. Even if a domain was registered 5 minutes ago and has never been seen by Google Safe Browsing or VirusTotal, its uncommon TLD, high entropy, multi-level subdomains, and suspicious query structures allow PhishGuard-XAI to detect it on its very first click."*
