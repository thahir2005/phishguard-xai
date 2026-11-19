"""
PhishGuard-XAI Feature Extraction Engine
Implements the 20 base features from Dirchaoui et al. (Procedia CS 2026)
plus 5 novel multilingual and homograph security features.
"""

import math
import re
from urllib.parse import urlparse

# Common trusted top-level domains (including Arabic/regional ccTLDs noted in paper)
COMMON_TLDS = {
    "com", "org", "net", "edu", "gov", "mil", "int",
    "ma", "sa", "ae", "eg", "kw", "qa", "om", "bh", "jo", "lb", "tn", "dz",
    "io", "co", "uk", "de", "fr", "in"
}

# Known URL shortener services
SHORTENER_DOMAINS = {
    "bit.ly", "goo.gl", "tinyurl.com", "t.co", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "bit.do", "cutt.ly", "rb.gy", "shorturl.at"
}

# Suspicious words including English and Arabic transliterated phishing triggers
SUSPICIOUS_WORDS = [
    # English keywords
    "login", "verify", "banking", "lottery", "account", "update", "secure",
    "signin", "wallet", "confirm", "free", "gift", "bonus", "reward", "winner",
    "claim", "prize", "support", "service", "password", "security",
    # Arabic transliterated / regional keywords
    "nafath", "absher", "rajhi", "ahli", "fawz", "ribh", "tasjeel", "wazifa",
    "musada", "jaiza", "mal", "mabrouk", "aramex", "sadad"
]

# Targeted brands for impersonation detection
PROTECTED_BRANDS = [
    "alrajhibank", "alahli", "snb", "riyadbank", "alinma",
    "absher", "nafath", "stc", "mobily", "zain", "aramex",
    "noon", "amazon", "paypal", "meta", "facebook", "instagram",
    "whatsapp", "telegram", "apple", "microsoft", "google"
]

# Cyrillic lookalikes commonly used in IDN homograph attacks
HOMOGRAPH_MAP = {
    '\u0430': 'a', '\u0441': 'c', '\u0435': 'e', '\u043e': 'o',
    '\u0440': 'p', '\u0455': 's', '\u0445': 'x', '\u0443': 'y',
    '\u0456': 'i', '\u0458': 'j'
}


def calculate_shannon_entropy(text: str) -> float:
    """Calculates Shannon entropy: H(X) = - sum(p(x) * log2(p(x)))"""
    if not text:
        return 0.0
    entropy = 0.0
    text_len = len(text)
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    for count in freq.values():
        p = count / text_len
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 4)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes standard Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def extract_features(raw_url: str) -> dict:
    """
    Extracts all 20 base features (Dirchaoui et al. 2026)
    plus 5 novel cybersecurity extension features.
    """
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        parsed = urlparse(url)
    except Exception:
        parsed = urlparse("http://invalid-url.local")

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query
    fragment = parsed.fragment

    # Split host and port if present
    domain_part = netloc.split(":")[0]

    # --- BASE FEATURES (Dirchaoui et al. 2026) ---

    # 1. url_length
    url_length = len(raw_url)

    # 2. num_digits
    num_digits = sum(1 for c in raw_url if c.isdigit())

    # 3. num_special_chars (-_?&=./%#@+~)
    special_chars = set("-_?&=./%#@+~")
    num_special_chars = sum(1 for c in raw_url if c in special_chars)

    # 4. num_slashes
    num_slashes = raw_url.count("/")

    # 5. num_params
    num_params = len(query.split("&")) if query else 0

    # 6. num_fragments
    num_fragments = 1 if fragment else 0

    # Domain parts and TLD
    domain_tokens = domain_part.split(".")
    if len(domain_tokens) > 1:
        tld = domain_tokens[-1]
        domain_name = domain_tokens[-2]
        subdomain_tokens = domain_tokens[:-2]
        subdomain = ".".join(subdomain_tokens)
    else:
        tld = ""
        domain_name = domain_part
        subdomain_tokens = []
        subdomain = ""

    # 7. num_subdomains
    num_subdomains = len(subdomain_tokens)

    # 8. has_https
    has_https = 1 if scheme == "https" else 0

    # 9. is_shortened_url
    is_shortened_url = 1 if any(shortener in netloc for shortener in SHORTENER_DOMAINS) else 0

    # 10. has_suspicious_words & 11. suspicious_word_count
    url_lower = raw_url.lower()
    suspicious_count = 0
    for word in SUSPICIOUS_WORDS:
        suspicious_count += url_lower.count(word)
    has_suspicious_words = 1 if suspicious_count > 0 else 0
    suspicious_word_count = suspicious_count

    # 12. repeated_chars (max consecutive repeated character)
    max_repeated = 1
    current_rep = 1
    for i in range(1, len(raw_url)):
        if raw_url[i] == raw_url[i - 1]:
            current_rep += 1
            if current_rep > max_repeated:
                max_repeated = current_rep
        else:
            current_rep = 1
    repeated_chars = max_repeated

    # 13. has_hex (e.g. %20, %3d)
    has_hex = 1 if re.search(r"%[0-9a-fA-F]{2}", raw_url) else 0

    # 14. tld_length
    tld_length = len(tld)

    # 15. is_common_tld
    is_common_tld = 1 if tld in COMMON_TLDS else 0

    # 16. has_ip (IPv4 or IPv6 address instead of domain)
    ipv4_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    has_ip = 1 if re.match(ipv4_pattern, domain_part) else 0

    # 17. num_directories
    path_dirs = [d for d in path.split("/") if d]
    num_directories = len(path_dirs)

    # 18. path_length
    path_length = len(path)

    # 19. entropy (Shannon entropy of domain name)
    entropy = calculate_shannon_entropy(domain_name)

    # 20. letter_digit_ratio
    num_letters = sum(1 for c in raw_url if c.isalpha())
    letter_digit_ratio = round(num_letters / (num_digits + 1), 4)

    # --- NOVEL EXTENSION FEATURES (Paper Contributions) ---

    # 21. is_punycode (IDN homograph attack indicator)
    is_punycode = 1 if "xn--" in netloc else 0

    # 22. homograph_spoof_score (Cyrillic/Greek characters in Latin domain context)
    homograph_count = sum(1 for c in domain_part if c in HOMOGRAPH_MAP)
    homograph_spoof_score = homograph_count

    # 23. subdomain_entropy
    subdomain_entropy = calculate_shannon_entropy(subdomain) if subdomain else 0.0

    # 24. brand_impersonation_score (Min Levenshtein distance to known brands, normalized)
    # A score near 0 or 1 indicates close typo-squatting (e.g. "alrajhi-secure" or "sn-bank")
    brand_scores = []
    clean_domain = re.sub(r"[^a-z0-9]", "", domain_name)
    for brand in PROTECTED_BRANDS:
        if brand in clean_domain and clean_domain != brand:
            # Brand is contained as a substring inside an unverified domain
            brand_scores.append(1.0)
        else:
            dist = levenshtein_distance(clean_domain, brand)
            if dist <= 2 and clean_domain != brand:
                brand_scores.append(0.85)
            elif dist <= 3:
                brand_scores.append(0.5)
            else:
                brand_scores.append(0.0)
    brand_impersonation_score = max(brand_scores) if brand_scores else 0.0

    # 25. arabic_ad_scam_flag (Combines social prize tokens with redirection or unverified tld)
    is_scam_ad = 1 if (suspicious_count >= 2 and (not is_common_tld or num_subdomains > 1)) else 0

    features = {
        # Base Features
        "url_length": url_length,
        "num_digits": num_digits,
        "num_special_chars": num_special_chars,
        "num_slashes": num_slashes,
        "num_params": num_params,
        "num_fragments": num_fragments,
        "num_subdomains": num_subdomains,
        "has_https": has_https,
        "is_shortened_url": is_shortened_url,
        "has_suspicious_words": has_suspicious_words,
        "suspicious_word_count": suspicious_word_count,
        "repeated_chars": repeated_chars,
        "has_hex": has_hex,
        "tld_length": tld_length,
        "is_common_tld": is_common_tld,
        "has_ip": has_ip,
        "num_directories": num_directories,
        "path_length": path_length,
        "entropy": entropy,
        "letter_digit_ratio": letter_digit_ratio,
        # Novel Features
        "is_punycode": is_punycode,
        "homograph_spoof_score": homograph_spoof_score,
        "subdomain_entropy": subdomain_entropy,
        "brand_impersonation_score": brand_impersonation_score,
        "arabic_ad_scam_flag": is_scam_ad
    }

    return features


FEATURE_COLUMNS = [
    "url_length", "num_digits", "num_special_chars", "num_slashes",
    "num_params", "num_fragments", "num_subdomains", "has_https",
    "is_shortened_url", "has_suspicious_words", "suspicious_word_count",
    "repeated_chars", "has_hex", "tld_length", "is_common_tld",
    "has_ip", "num_directories", "path_length", "entropy", "letter_digit_ratio",
    "is_punycode", "homograph_spoof_score", "subdomain_entropy",
    "brand_impersonation_score", "arabic_ad_scam_flag"
]
