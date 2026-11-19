# PhishGuard-XAI: 4-Member Team Role Distribution & Presentation Guide

## Project Title
**PhishGuard-XAI: An Explainable Machine Learning Framework with Real-Time Browser Interception and Multilingual IDN Defense for Social Media Ecosystems**

*(Advancement over base paper: Dirchaoui Marouane et al., Procedia Computer Science 280 (2026) 1306–1311, Elsevier)*

---

## 1. Team Role Allocation (4 Members)

To impress project coordinators and external examiners, each member must present an independent, deep technical module while showing seamless collaboration.

```
+--------------------------------------------------------------------------+
|                       MEMBER 1: TEAM LEAD & ML RESEARCHER                |
|  - Literature Review & Base Paper Critique (Dirchaoui et al. 2026)        |
|  - Dataset Engineering (2,400 URLs, Meta Phishing Ads, Arabic Context)    |
|  - Benchmark Model Evaluation (LR, RF, GB, XGBoost, SVM, DNN vs Ours)    |
+------------------------------------+-------------------------------------+
                                     |
+------------------------------------+-------------------------------------+
|              MEMBER 2: FEATURE ENGINEERING & XAI SPECIALIST               |
|  - 25-Feature Extraction Pipeline (Lexical, Structural, Entropy)          |
|  - 5 Novel Features (Punycode, IDN Homographs, Levenshtein Brand Metric)  |
|  - Mathematics of TreeSHAP (Game-Theoretic Shapley Values phi_i)         |
|  - Natural Language Risk Explanation Generator (Human-Centered XAI)       |
+------------------------------------+-------------------------------------+
                                     |
+------------------------------------+-------------------------------------+
|             MEMBER 3: BACKEND ARCHITECT & SYSTEMS ENGINEER                |
|  - Zero-Dependency High-Throughput REST API Engine & FastAPI Backend     |
|  - Model Serialization & In-Memory Precomputed Tree Structures            |
|  - Sub-15ms Latency Profiling & Microservice Scalability                 |
|  - Batch Processing Engine (Bulk CSV / Security Operations SOC Pipeline) |
+------------------------------------+-------------------------------------+
                                     |
+------------------------------------+-------------------------------------+
|        MEMBER 4: CYBERSECURITY UI/UX & BROWSER SHIELD ENGINEER            |
|  - Manifest V3 Chrome Extension Architecture (Service Worker + DOM Script)|
|  - Pre-Click Link Interception & Anti-Phishing Interstitial Warning Modal |
|  - Modern SOC Operations Dashboard (Dark Theme, SHAP Waterfall Visuals)   |
|  - End-to-End Live Demonstration & Examiner Threat Simulation             |
+--------------------------------------------------------------------------+
```

---

## 2. 10-Minute Slide-by-Slide Presentation Script

### Slide 1: Introduction & Problem Statement (Speaker: Member 1)
> *"Respected panel and project guides, good morning. Phishing remains the #1 initial attack vector in cybercrime. In recent years, attackers have shifted heavily to online advertising on social platforms like Facebook, Instagram, and WhatsApp. Users are tricked by deceptive links promising monetary grants, government lottery prizes, or urgent KYC bank verifications. Our goal was to build a system that can detect, explain, and actively block these links in real time before a user becomes a victim."*

### Slide 2: The Base Paper & Its Limitations (Speaker: Member 1)
> *"Our project builds upon our base paper published in Elsevier Procedia Computer Science 2026 by Dirchaoui et al., titled 'Detecting Fraudulent URLs on Arabic Social Platforms Using an Explainable Machine Learning Approach'. The authors tested six algorithms and proved that XGBoost achieved 96.57% accuracy, outperforming Deep Neural Networks. However, we identified four critical limitations in the base paper: First, it was only an offline Jupyter experiment with no deployment. Second, it was blind to IDN homograph attacks where attackers use lookalike Russian or Arabic Unicode characters. Third, it had no brand impersonation distance metric. Fourth, its SHAP plots were meant for data scientists, not everyday users."*

### Slide 3: Dataset Augmentation & Model Benchmarks (Speaker: Member 1)
> *"To advance this research, we augmented the benchmark to 2,400 balanced URLs—1,200 benign from verified government and banking services, and 1,200 malicious URLs actively scraped from social media ads. We retrained and benchmarked the models: our proposed enhanced model achieved 96.88% Accuracy and 98.28% Precision, beating the base paper's 97.46% precision, drastically minimizing false alarms."*

---

### Slide 4: Advanced Feature Engineering (Speaker: Member 2)
> *"Moving to feature extraction, our base paper extracted 20 features such as URL length, digit counts, slashes, and TLD validity. To prevent sophisticated evasion, I introduced 5 novel cybersecurity features:
> 1. `is_punycode` detecting `xn--` domain encodings.
> 2. `homograph_spoof_score` identifying Cyrillic lookalikes mimicking Latin characters.
> 3. `subdomain_entropy` measuring algorithmic randomness in subdomains.
> 4. `brand_impersonation_score` using normalized Levenshtein distance against high-target institutions like Al Rajhi Bank, Nafath, and Absher.
> 5. `arabic_ad_scam_flag` capturing compound social engineering indicators."*

### Slide 5: Explainable AI with TreeSHAP (Speaker: Member 2)
> *"Why Explainable AI? Black-box security tools are distrusted by SOC analysts and users. We implemented exact TreeSHAP based on cooperative game theory. As seen in Figure 1 and 2 of our base paper, `is_common_tld` is the #1 deciding factor, followed by Shannon entropy. We took this further: our system converts raw SHAP mathematical vectors into plain-language diagnostic reasons, such as: 'Flagged because: Uncommon .top domain, high character entropy 3.84, and brand similarity to Nafath identity portal'."*

---

### Slide 6: Backend Architecture & High-Performance API (Speaker: Member 3)
> *"For real-world viability, an anti-phishing model must be ultra-fast. If a model takes 2 seconds to scan a link, user experience degrades. I engineered our backend inference engine in optimized Python, serializing the decision trees and baseline priors into a high-speed engine that executes in under 15 milliseconds. We designed a REST API with CORS compliance, providing endpoints for single scans, batch uploads for SOC teams, and live benchmark retrieval."*

---

### Slide 7: Chrome Extension & Real-Time Click Interception (Speaker: Member 4)
> *"Now let's examine the defensive product. A model is useless if it cannot protect users where they browse. I engineered a production Manifest V3 Chrome Extension. It quietly monitors links on social media feeds. When a user accidentally clicks an ad containing a fraudulent link, the extension intercepts the click event before navigation occurs, displaying an emergency warning modal with the exact SHAP reasons and threat score, giving the user the power to abort safely."*

### Slide 8: Live Demonstration (Speaker: Member 4)
> *"Let us demonstrate the system live. First, we test a legitimate link: `https://alrajhibank.com.sa` — our engine scores it at 9.9% Safe. Next, we test a real-world phishing ad link: `http://secure.login.nafath-verify.top/claim` — our engine instantly classifies it as CRITICAL PHISHING at 91.1%, highlighting the uncommon `.top` TLD and high entropy. When clicked in Chrome, the shield blocks it immediately."*

---

### Slide 9: Conclusion & Research Paper (Speaker: Member 1)
> *"In conclusion, we have transformed an offline academic study into a fully functioning, enterprise-grade cyber defense suite. We have authored our research paper draft formatted for Elsevier / IEEE conference submission, comparing our results with Dirchaoui et al. (2026). Thank you, and we welcome questions from the panel."*
