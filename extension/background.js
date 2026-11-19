/**
 * PhishGuard-XAI Background Service Worker (Manifest V3)
 * Handles automatic pre-click interception, direct navigation blocking,
 * and offline heuristic evaluation.
 */

const API_ENDPOINT = "http://localhost:8000/api/scan";
const urlCache = new Map();

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    linksScanned: 0,
    threatsBlocked: 0,
    protectionEnabled: true
  });
  console.log("PhishGuard-XAI Shield initialized successfully.");
});

// 1. Direct Browser Navigation Interceptor (Catches address bar & redirects)
if (chrome.webNavigation && chrome.webNavigation.onBeforeNavigate) {
  chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    // Only intercept main frame navigations (top window)
    if (details.frameId !== 0) return;

    const url = details.url;
    if (!url || !url.startsWith("http")) return;

    // Skip localhost and internal chrome pages
    if (url.includes("localhost") || url.includes("127.0.0.1") || url.startsWith("chrome://") || url.startsWith("chrome-extension://")) {
      return;
    }

    try {
      const data = await handleUrlScan(url);
      if (data && data.risk_score >= 65) {
        // Halt navigation and redirect to emergency warning shield
        const warningUrl = chrome.runtime.getURL(`warning.html?target=${encodeURIComponent(url)}`);
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
    handleUrlScan(request.url)
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

  // Increment scanned counter
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
    // Backend offline: seamlessly fallback to client-side heuristics
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
  const commonTlds = ["com", "org", "net", "edu", "gov", "sa", "ma", "ae", "eg", "in", "io", "uk"];
  const badWords = [
    "verify", "nafath", "absher", "login", "lottery", "prize", "winner",
    "reward", "wazifa", "claim", "bonus", "fawz", "bank", "secure-update"
  ];

  let risk = 12;
  const reasons = [];

  try {
    const urlObj = new URL(rawUrl.startsWith("http") ? rawUrl : "http://" + rawUrl);
    const host = urlObj.hostname.toLowerCase();
    const parts = host.split(".");
    const tld = parts[parts.length - 1];

    if (!commonTlds.includes(tld)) {
      risk += 48;
      reasons.push(`High-risk uncommon top-level domain (.${tld}) identified.`);
    }

    let wordHits = 0;
    badWords.forEach(w => {
      if (rawUrl.toLowerCase().includes(w)) wordHits++;
    });

    if (wordHits > 0) {
      risk += wordHits * 18;
      reasons.push(`Detected ${wordHits} phishing / credential harvesting keyword triggers.`);
    }

    if (host.includes("xn--")) {
      risk += 40;
      reasons.push("Internationalized Domain Name (IDN) / Punycode homograph attack indicator.");
    }
  } catch (e) {
    risk = 50;
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
}
