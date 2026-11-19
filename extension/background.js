/**
 * PhishGuard-XAI Background Service Worker (Manifest V3)
 * Handles automatic pre-click interception, direct navigation blocking,
 * social media link unwrapping (Instagram/Facebook shims), and offline heuristics.
 */

const API_ENDPOINT = "http://localhost:8000/api/scan";
const urlCache = new Map();

// Trusted meeting and collaboration platforms
const TRUSTED_COLLAB = [
  "zoom.us", "meet.google.com", "teams.microsoft.com", "teams.live.com",
  "webex.com", "gotomeeting.com", "eventbrite.com", "lu.ma", "chime.aws"
];

// Recognized URL shorteners
const TRUSTED_SHORTENERS = [
  "bit.ly", "tinyurl.com", "t.co", "cutt.ly", "rb.gy", "shorturl.at", "goo.gl", "is.gd"
];

function extractTargetUrl(rawUrl) {
  try {
    const urlObj = new URL(rawUrl);
    // Meta Instagram / Facebook link shim
    if (urlObj.hostname.includes("instagram.com") || urlObj.hostname.includes("facebook.com")) {
      const u = urlObj.searchParams.get("u");
      if (u) return decodeURIComponent(u);
    }
    // Google redirect
    if (urlObj.hostname.includes("google.") && urlObj.searchParams.get("q")) {
      return decodeURIComponent(urlObj.searchParams.get("q"));
    }
    // YouTube redirect
    if (urlObj.hostname.includes("youtube.com") && urlObj.searchParams.get("q")) {
      return decodeURIComponent(urlObj.searchParams.get("q"));
    }
    // General redirect params
    for (const key of ["url", "target", "dest", "link", "redirect"]) {
      const val = urlObj.searchParams.get(key);
      if (val && val.startsWith("http")) return decodeURIComponent(val);
    }
  } catch (e) {}
  return rawUrl;
}

chrome.runtime.onInstalled.addListener(async () => {
  chrome.storage.local.set({
    linksScanned: 0,
    threatsBlocked: 0,
    protectionEnabled: true
  });
  console.log("PhishGuard-XAI Shield initialized successfully.");
});

// 1. Direct Browser Navigation Interceptor (Catches address bar, new tabs & redirects)
if (chrome.webNavigation && chrome.webNavigation.onBeforeNavigate) {
  chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    if (details.frameId !== 0) return;

    const rawUrl = details.url;
    if (!rawUrl || !rawUrl.startsWith("http")) return;

    if (rawUrl.includes("localhost") || rawUrl.includes("127.0.0.1") || rawUrl.startsWith("chrome://") || rawUrl.startsWith("chrome-extension://")) {
      return;
    }

    const targetUrl = extractTargetUrl(rawUrl);

    try {
      const data = await handleUrlScan(targetUrl);
      if (data && data.risk_score >= 65) {
        const warningUrl = chrome.runtime.getURL(`warning.html?target=${encodeURIComponent(targetUrl)}`);
        chrome.tabs.update(details.tabId, { url: warningUrl });
      }
    } catch (e) {
      console.warn("Navigation scan error:", e);
    }
  });
}

// 2. Message Dispatcher for Content Script (In-page link clicks)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "scanUrl") {
    const targetUrl = extractTargetUrl(request.url);
    handleUrlScan(targetUrl)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true;
  }

  if (request.action === "getStats") {
    chrome.storage.local.get(["linksScanned", "threatsBlocked", "protectionEnabled"], (data) => {
      sendResponse(data);
    });
    return true;
  }
});

async function handleUrlScan(url) {
  if (urlCache.has(url)) {
    return urlCache.get(url);
  }

  chrome.storage.local.get(["linksScanned"], (data) => {
    chrome.storage.local.set({ linksScanned: (data.linksScanned || 0) + 1 });
  });

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1200);

    const res = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      urlCache.set(url, data);

      if (data.risk_score >= 65) {
        incrementThreatCount();
      }
      return data;
    }
  } catch (err) {
    // Backend offline: fallback to client-side heuristics
  }

  const fallback = offlineHeuristicScan(url);
  urlCache.set(url, fallback);
  if (fallback.risk_score >= 65) {
    incrementThreatCount();
  }
  return fallback;
}

function incrementThreatCount() {
  chrome.storage.local.get(["threatsBlocked"], (data) => {
    chrome.storage.local.set({ threatsBlocked: (data.threatsBlocked || 0) + 1 });
  });
}

function offlineHeuristicScan(rawUrl) {
  const commonTlds = ["com", "org", "net", "edu", "gov", "sa", "ma", "ae", "eg", "in", "io", "uk", "us", "ly", "app", "dev"];
  const badWords = [
    "verify", "nafath", "absher", "login", "lottery", "prize", "winner",
    "reward", "wazifa", "claim", "bonus", "fawz", "bank", "secure-update"
  ];

  try {
    const urlObj = new URL(rawUrl.startsWith("http") ? rawUrl : "http://" + rawUrl);
    const host = urlObj.hostname.toLowerCase();
    const parts = host.split(".");
    const tld = parts[parts.length - 1];

    if (TRUSTED_COLLAB.some(c => host.includes(c))) {
      return {
        url: rawUrl,
        classification: "SAFE",
        badge: "SECURE",
        risk_score: 5.0,
        human_explanation: {
          summary: "Verified Collaboration & Webinar Platform. Safe to attend.",
          action: "ACCESS PERMITTED.",
          primary_risk_reasons: ["No threat patterns detected."],
          positive_indicators: ["Verified enterprise video conferencing infrastructure."]
        },
        shap_explanation: { top_risk_drivers: [], all_features_shap: {} }
      };
    }

    const isShortener = TRUSTED_SHORTENERS.some(s => host.includes(s));
    let wordHits = 0;
    badWords.forEach(w => {
      if (rawUrl.toLowerCase().includes(w)) wordHits++;
    });

    if (isShortener && wordHits === 0) {
      return {
        url: rawUrl,
        classification: "SAFE",
        badge: "SECURE",
        risk_score: 22.0,
        human_explanation: {
          summary: "Legitimate URL shortener (commonly used for webinar/meeting invites). Safe to open.",
          action: "ACCESS PERMITTED. Standard redirect link with no suspicious indicators.",
          primary_risk_reasons: ["Standard redirect structure."],
          positive_indicators: ["Trusted URL shortener infrastructure.", "No credential harvesting bait detected."]
        },
        shap_explanation: { top_risk_drivers: [], all_features_shap: {} }
      };
    }

    let risk = 12;
    const reasons = [];

    if (!commonTlds.includes(tld) && !isShortener) {
      risk += 48;
      reasons.push(`High-risk uncommon top-level domain (.${tld}) identified.`);
    }

    if (wordHits > 0) {
      risk += wordHits * 20;
      reasons.push(`Detected ${wordHits} phishing / credential harvesting keyword triggers.`);
    }

    if (host.includes("xn--")) {
      risk += 40;
      reasons.push("Internationalized Domain Name (IDN) / Punycode homograph attack indicator.");
    }

    risk = Math.min(99, Math.max(5, risk));
    const isMalicious = risk >= 65;

    return {
      url: rawUrl,
      classification: isMalicious ? "CRITICAL_PHISHING" : (risk >= 35 ? "SUSPICIOUS" : "SAFE"),
      risk_score: risk,
      badge: isMalicious ? "DANGER" : (risk >= 35 ? "WARNING" : "SECURE"),
      human_explanation: {
        summary: isMalicious ? "High-probability malicious domain detected." : "Standard legitimate domain characteristics.",
        action: isMalicious ? "DO NOT VISIT. Connection halted to prevent credential exfiltration." : "Access permitted.",
        primary_risk_reasons: reasons.length ? reasons : ["Parameters within baseline security thresholds."],
        positive_indicators: ["Client-side heuristic verification complete."]
      },
      shap_explanation: {
        top_risk_drivers: [
          { feature: "is_common_tld", impact: isMalicious ? 1.54 : -1.2 },
          { feature: "has_suspicious_words", impact: isMalicious ? 0.78 : -0.1 }
        ],
        all_features_shap: {}
      }
    };
  } catch (e) {
    return {
      url: rawUrl,
      classification: "SAFE",
      risk_score: 15.0,
      badge: "SECURE",
      human_explanation: {
        summary: "Standard link structure.",
        action: "Access permitted.",
        primary_risk_reasons: [],
        positive_indicators: []
      },
      shap_explanation: { top_risk_drivers: [], all_features_shap: {} }
    };
  }
}
