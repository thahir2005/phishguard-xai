"""
Dataset Generator & Preprocessor for Arabic Social Media Phishing URLs
Reproduces and augments the dataset methodology of Dirchaoui et al. (Procedia CS 2026).
Generates 2,400 labeled samples (1,200 Benign, 1,200 Malicious) with all 25 extracted features.
"""

import csv
import os
import random
import sys

# Add ml_engine to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml_engine.feature_extractor import extract_features, FEATURE_COLUMNS

random.seed(42)

# --- BENIGN URL GENERATION TEMPLATES ---
BENIGN_DOMAINS = [
    # Government & Public Portals (Saudi, Morocco, UAE, Egypt)
    "absher.sa", "nafath.sa", "my.gov.sa", "zatca.gov.sa", "spa.gov.sa",
    "maroc.ma", "service-public.ma", "justice.gov.ma", "dgst.ma",
    "u.ae", "mofaic.gov.ae", "dubaipolice.gov.ae", "tam.abudhabi",
    "egypt.gov.eg", "cbe.org.eg", "idsc.gov.eg",

    # Regional Banking Institutions
    "alrajhibank.com.sa", "alahli.com", "riyadbank.com", "alinma.com", "bankalbilad.com",
    "attijariwafabank.com", "banquepopulaire.ma", "bmcebank.ma", "cihbank.ma",
    "emiratesnbd.com", "fab.com", "adcb.com", "mashreqbank.com",
    "nbe.com.eg", "banquemisr.com", "cibeg.com",

    # E-Commerce & Retail
    "noon.com", "amazon.sa", "amazon.ae", "amazon.eg", "jarir.com",
    "extra.com", "jumia.ma", "jumia.com.eg", "namshi.com", "boutiqaat.com",

    # Energy, Telecom, Media
    "aramco.com", "sabic.com", "adnoc.ae", "stc.com.sa", "mobily.com.sa",
    "maroctelecom.ma", "orange.ma", "etisalat.ae", "vodafone.com.eg",
    "aljazeera.net", "alarabiya.net", "hespress.com", "youm7.com", "skynewsarabia.com",

    # Global Trusted Services commonly visited
    "google.com", "microsoft.com", "apple.com", "linkedin.com", "wikipedia.org",
    "github.com", "stackoverflow.com", "cloudflare.com"
]

BENIGN_PATHS = [
    "",
    "ar/about-us",
    "en/services/personal-banking",
    "ar/portal/services/citizens",
    "en/products/electronics/laptops",
    "ar/news/local/economy-update-2026",
    "ar/careers/opportunities",
    "ar/help/security-tips",
    "ar/customer-service/faq",
    "ar/apply/verified-user",
    "ar/contact/locations",
    "en/investor-relations/reports",
    "ar/press/releases/annual-summary"
]

BENIGN_QUERIES = [
    "",
    "lang=ar",
    "region=mena&lang=ar",
    "page=1&limit=20&filter=official",
    "category=banking&type=personal",
    "utm_source=portal&utm_medium=organic"
]

# --- MALICIOUS URL PATTERNS (Based on Meta Phishing Ads & Findings in Paper) ---
UNCOMMON_TLDS = [
    "top", "xyz", "click", "buzz", "club", "live", "work", "bid", "rest", "surf",
    "shop", "site", "online", "vip", "cfd", "monster", "icu", "cam", "fit"
]

PHISHING_THEMES = {
    "lottery_prize": [
        "alwaleed-foundation-prize", "mbc-dream-prize2026", "ramadan-reward-bonus",
        "jawiza-fawz-kheir", "sheikh-mohammed-grant", "tasjeel-musada-maliya",
        "royal-court-gift", "qatar-charity-aid", "al-fawz-al-kabeer-win"
    ],
    "fake_jobs": [
        "aramco-recruitment-portal", "stc-remote-jobs-apply", "alrajhi-careers-hiring",
        "wazifa-hukumia-fawriya", "qatar-airways-jobs-online", "noon-warehouse-employment",
        "gulf-visa-work-apply", "ministry-labor-jobs-portal"
    ],
    "fake_banking_credential_harvesting": [
        "alrajhi-nafath-verify", "alahli-online-update", "riyad-secure-login",
        "absher-identity-confirm", "snb-quick-pay-auth", "cih-net-connexion-urgent",
        "attijari-mobile-reactivate", "emiratesnbd-kyc-update", "cib-egypt-token-auth"
    ],
    "fake_ecommerce_scams": [
        "iphone17-pro-free-giveaway", "noon-flash-sale-90off", "amazon-sa-special-voucher",
        "shein-luxury-coupons-win", "dyson-clearance-riyadh", "gold-jewellery-dubai-scam"
    ]
}

SUSPICIOUS_SUBDOMAINS = [
    "secure.login.portal",
    "verify.account.update",
    "online.auth.service",
    "kyc.validation.system",
    "claim.reward.portal",
    "support.helpdesk.check",
    "mobile.access.gateway"
]


def generate_benign_urls(count: int = 1200) -> list:
    urls = []
    for _ in range(count):
        domain = random.choice(BENIGN_DOMAINS)
        path = random.choice(BENIGN_PATHS)
        query = random.choice(BENIGN_QUERIES)

        # 95% HTTPS in legitimate sites
        scheme = "https" if random.random() > 0.05 else "http"

        full_url = f"{scheme}://{domain}"
        if path:
            full_url += f"/{path}"
        if query:
            full_url += f"?{query}"

        urls.append((full_url, 0))  # 0 = Benign
    return urls


def generate_malicious_urls(count: int = 1200) -> list:
    urls = []
    categories = list(PHISHING_THEMES.keys())

    for _ in range(count):
        cat = random.choice(categories)
        theme_token = random.choice(PHISHING_THEMES[cat])
        tld = random.choice(UNCOMMON_TLDS)

        # Style of URL:
        style = random.random()

        # Attackers use HTTPS ~70-80% now as noted in Section 3.2 / 4 of paper
        scheme = "https" if random.random() > 0.25 else "http"

        if style < 0.35:
            # Subdomain impersonation on cheap TLD
            sub = random.choice(SUSPICIOUS_SUBDOMAINS)
            rand_id = random.randint(100, 9999)
            domain = f"{sub}.{theme_token}{rand_id}.{tld}"
            path = f"verify/{random.choice(['login', 'auth', 'claim', 'step1'])}"
            query = f"token={random.randint(100000, 999999)}&ref=fb_ad"
        elif style < 0.65:
            # Typo-squatting or direct phishing keyword
            rand_hex = "%20%2f" if random.random() < 0.2 else ""
            domain = f"{theme_token}-{random.randint(10, 999)}.{tld}"
            path = f"ar/lottery/{rand_hex}action/{random.choice(['winner', 'bank_details', 'otp_submit'])}"
            query = f"session={random.randint(10000, 99999)}&amount=50000"
        elif style < 0.85:
            # IP address or IDN lookalike
            if random.random() < 0.15:
                # Raw IP address
                ip = f"{random.randint(45, 195)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
                domain = ip
                path = f"login/{random.choice(['nafath', 'alrajhi', 'absher', 'secure'])}"
                query = "redirect=index.php"
            elif random.random() < 0.3:
                # Punycode / IDN homograph
                domain = f"xn--{theme_token[:6]}-9za.{tld}"
                path = "verify-credentials"
                query = "utm_source=instagram_ad"
            else:
                # Deeply nested directory structure
                domain = f"{theme_token}.{tld}"
                path = f"secure/banking/ar/login/session/auth/v2/{random.randint(1000, 9999)}"
                query = "client_id=meta_sponsored_campaign"
        else:
            # Shortener redirecting to fraudulent campaign
            shortener = random.choice(["bit.ly", "tinyurl.com", "cutt.ly", "rb.gy"])
            domain = shortener
            path = f"{theme_token[:8]}_{random.randint(10, 99)}"
            query = ""

        full_url = f"{scheme}://{domain}"
        if path:
            full_url += f"/{path}"
        if query:
            full_url += f"?{query}"

        urls.append((full_url, 1))  # 1 = Malicious / Phishing
    return urls


def create_dataset_file(filepath: str):
    print("Generating benign URLs...")
    benign = generate_benign_urls(1200)
    print("Generating malicious URLs...")
    malicious = generate_malicious_urls(1200)

    combined = benign + malicious
    random.shuffle(combined)

    print(f"Total samples: {len(combined)} (1200 Benign, 1200 Malicious)")
    print("Extracting features for all URLs...")

    header = ["url", "label"] + FEATURE_COLUMNS

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for i, (url, label) in enumerate(combined):
            features = extract_features(url)
            row = [url, label] + [features[col] for col in FEATURE_COLUMNS]
            writer.writerow(row)
            if (i + 1) % 400 == 0:
                print(f"Processed {i + 1}/{len(combined)} URLs...")

    print(f"Dataset successfully created at: {filepath}")


if __name__ == "__main__":
    target_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "arabic_social_phishing_dataset.csv"))
    create_dataset_file(target_path)
