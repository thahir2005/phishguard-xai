/**
 * PhishGuard-XAI Background Service Worker (Manifest V3)
 * Handles link scan requests, API caching, telemetry counters,
 * and offline heuristic fallback.
 */

const API_ENDPOINT = "http://localhost:8000/api/scan";
const urlCache = new Map();

// Initialize stats in storage
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    linksScanned: 0,
    threatsBlocked: 0,
    protectionEnabled: true
  });
  console.log("PhishGuard-XAI extension installed and initialized.");
});

// Message dispatcher
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "scanUrl") {
    handleUrlScan(request.url)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true; // Keep message channel open for async response
  }

  if (request.action === "getStats") {
    chrome.storage.local.get(["linksScanned", "threatsBlocked", "protectionEnabled"], (data) => {
      sendResponse(data);
    });
    return true;
  }
});

async function handleUrlScan(url) {
  // Check memory cache first
  if (urlCache.has(url)) {
    return urlCache.get(url);
  }

  // Update scanned counter
  chrome.storage.local.get(["linksScanned"], (data) => {
    chrome.storage.local.set({ linksScanned: (data.linksScanned || 0) + 1 });
  });

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1500); // 1.5s timeout

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
    console.warn("Backend API unavailable, using offline fallback heuristics:", err.message);
  }

  // Offline heuristic fallback based on Dirchaoui et al. features
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
  const commonTlds = ["com", "org", "net", "edu", "gov", "sa", "ma", "ae", "eg"];
  const badWords = ["verify", "nafath", "absher", "login", "lottery", "prize", "winner", "reward", "wazifa"];

  let risk = 15;
  const reasons = [];

  try {
    const urlObj = new URL(rawUrl.startsWith("http") ? rawUrl : "http://" + rawUrl);
    const host = urlObj.hostname.toLowerCase();
    const parts = host.split(".");
    const tld = parts[parts.length - 1];

    if (!commonTlds.includes(tld)) {
      risk += 45;
      reasons.push(`Uncommon top-level domain (.${tld}) frequently used in social ad scams.`);
    }

    let wordHits = 0;
    badWords.forEach(w => {
      if (rawUrl.toLowerCase().includes(w)) wordHits++;
    });

    if (wordHits > 0) {
      risk += wordHits * 18;
      reasons.push(`Suspicious credential or financial lure keywords detected (${wordHits} matches).`);
    }

    if (host.includes("xn--")) {
      risk += 35;
      reasons.push("Punycode Internationalized Domain Name (IDN) homograph indicator.");
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
      summary: isMalicious ? "High-probability malicious domain identified via heuristic analysis." : "No critical threats detected.",
      action: isMalicious ? "DO NOT VISIT. This link demonstrates attributes of fraud or phishing." : "Proceed normally.",
      primary_risk_reasons: reasons.length ? reasons : ["Heuristic indicators within normal thresholds."],
      positive_indicators: ["Client-side heuristic evaluation complete."]
    },
    shap_explanation: {
      top_risk_drivers: [
        { feature: "is_common_tld", impact: isMalicious ? 1.5 : -1.2 },
        { feature: "has_suspicious_words", impact: isMalicious ? 0.8 : -0.2 }
      ],
      all_features_shap: {}
    }
  };
}
