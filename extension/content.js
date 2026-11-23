/**
 * PhishGuard-XAI Content Script
 * 1. Automatic On-Page Load Verification:
 *    - SAFE: Displays sleek green badge for 1.0 second!
 *    - UNHOSTED / NOT FOUND: Displays slate-amber badge "URL Not Found (Not Hosted)" for 1.0 second!
 *    - UNSAFE: Immediately halts page and displays emergency warning shield!
 * 2. Pre-Click Link Interceptor:
 *    - Intercepts clicks on social media links (Instagram shims, Facebook shims, etc.)
 */

let protectionEnabled = true;

chrome.storage.local.get(["protectionEnabled"], (data) => {
  if (data.protectionEnabled !== undefined) {
    protectionEnabled = data.protectionEnabled;
  }
  initPageSecurityCheck();
});

// Listen for messages from background script (e.g. unhosted domain detected)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "showNotFound") {
    showOneSecondNotFoundBadge(request.domain || window.location.hostname);
  }
});

// ========================================================
// 1. AUTOMATIC ON-PAGE LOAD VERIFICATION (Address Bar / WhatsApp / Direct Visit)
// ========================================================
function initPageSecurityCheck() {
  if (!protectionEnabled) return;

  const currentUrl = window.location.href;

  // Detect browser error / unhosted / DNS failure pages
  if (document.title.includes("Site can't be reached") || 
      document.title.includes("Server Not Found") || 
      document.title.includes("404") ||
      document.body && (document.body.innerText.includes("ERR_NAME_NOT_RESOLVED") || document.body.innerText.includes("DNS_PROBE_FINISHED"))) {
    showOneSecondNotFoundBadge(window.location.hostname || "Target Domain");
    return;
  }

  // Skip internal browser and extension pages
  if (!currentUrl.startsWith("http://") && !currentUrl.startsWith("https://")) {
    return;
  }
  if (currentUrl.includes("localhost") || currentUrl.includes("127.0.0.1")) {
    return;
  }

  // Check if user already clicked "proceed anyway" on this domain in this session
  if (sessionStorage.getItem("pg_allowed_" + window.location.hostname) === "true") {
    return;
  }

  chrome.runtime.sendMessage({ action: "scanUrl", url: currentUrl }, (response) => {
    if (response && response.success && response.data) {
      const result = response.data;

      // If domain was whitelisted by user bypass, permit immediately
      if (result.classification === "USER_ALLOWED" || result.user_bypassed) {
        return;
      }

      if (result.classification === "URL_NOT_FOUND" || result.status === "unhosted") {
        showOneSecondNotFoundBadge(window.location.hostname);
      } else if (result.risk_score >= 65) {
        // High Risk / Phishing: IMMEDIATELY COVER PAGE WITH INTERSTITIAL WARNING
        showOnLoadWarningScreen(currentUrl, result);
      } else {
        // Safe: Show the 1.0-second Green "Verified Safe" Badge
        showOneSecondSafeBadge(result);
      }
    }
  });
}

function showOneSecondSafeBadge(result) {
  if (document.getElementById("pg-onpage-safe-badge")) return;

  const badge = document.createElement("div");
  badge.id = "pg-onpage-safe-badge";
  badge.className = "pg-safe-badge-pill";
  badge.innerHTML = `
    <span class="pg-badge-icon">🛡️ ✓</span>
    <div class="pg-badge-content">
      <strong>Verified Safe (${result.risk_score}% Risk)</strong>
      <span>${window.location.hostname} — Protected by PhishGuard</span>
    </div>
  `;
  document.documentElement.appendChild(badge);

  // Keep visible for exactly 1.0 second (1000ms), then smoothly fade out
  setTimeout(() => {
    badge.classList.add("pg-badge-fadeout");
    setTimeout(() => {
      badge.remove();
    }, 350);
  }, 1000);
}

function showOneSecondNotFoundBadge(domain) {
  if (document.getElementById("pg-onpage-notfound-badge")) return;

  const badge = document.createElement("div");
  badge.id = "pg-onpage-notfound-badge";
  badge.className = "pg-notfound-badge-pill";
  badge.innerHTML = `
    <span class="pg-badge-icon" style="color:#f59e0b;">⚠️</span>
    <div class="pg-badge-content">
      <strong style="color:#fbbf24;">URL Not Found</strong>
      <span>${escapeHtml(domain)} — Domain not active or unhosted</span>
    </div>
  `;
  document.documentElement.appendChild(badge);

  // Display for exactly 1.0 second
  setTimeout(() => {
    badge.classList.add("pg-badge-fadeout");
    setTimeout(() => {
      badge.remove();
    }, 350);
  }, 1000);
}

function showOnLoadWarningScreen(url, result) {
  window.stop();

  const overlay = document.createElement("div");
  overlay.id = "pg-onload-warning-overlay";
  overlay.className = "pg-modal-overlay";

  const reasons = (result.human_explanation && result.human_explanation.primary_risk_reasons)
    ? result.human_explanation.primary_risk_reasons
    : ["Critical domain anomalies detected by machine learning model."];

  const reasonsHtml = reasons.map(r => `<li>${escapeHtml(r)}</li>`).join("");

  overlay.innerHTML = `
    <div class="pg-modal-dialog">
      <div class="pg-modal-header">
        <div class="pg-shield-icon">🛑</div>
        <div class="pg-header-title">
          <h2>Dangerous Website Blocked</h2>
          <p>PhishGuard Shield blocked this page to protect your credentials and data.</p>
        </div>
      </div>

      <div class="pg-risk-banner">
        <div class="pg-risk-score">${result.risk_score}% Threat Risk</div>
        <div class="pg-risk-badge">${result.classification}</div>
      </div>

      <div class="pg-url-preview">
        <span>Blocked Destination:</span>
        <code>${escapeHtml(url)}</code>
      </div>

      <div class="pg-reasons-box">
        <h3>Why Was This Site Blocked? (TreeSHAP XAI)</h3>
        <ul>${reasonsHtml}</ul>
      </div>

      <div class="pg-action-buttons">
        <button id="pg-onload-btn-exit" class="pg-btn-primary">
          🛡️ Exit / Return to Safety (Recommended)
        </button>
        <button id="pg-onload-btn-proceed" class="pg-btn-secondary">
          ⚠️ Continue Anyway (Unsafe)
        </button>
      </div>

      <div class="pg-footer-note">
        PhishGuard-XAI Active Defense Shield (Procedia CS 2026 Model Architecture)
      </div>
    </div>
  `;

  document.documentElement.appendChild(overlay);

  document.getElementById("pg-onload-btn-exit").addEventListener("click", () => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = "https://google.com";
    }
  });

  document.getElementById("pg-onload-btn-proceed").addEventListener("click", () => {
    const domain = window.location.hostname.toLowerCase();
    sessionStorage.setItem("pg_allowed_" + domain, "true");
    chrome.runtime.sendMessage({ action: "allowDomain", domain: domain }, () => {
      overlay.remove();
    });
  });
}

// ========================================================
// 2. IN-PAGE CLICK INTERCEPTION (Links inside social media & web pages)
// ========================================================
document.addEventListener("click", handleLinkClick, true);

function extractTargetUrl(rawHref) {
  try {
    const urlObj = new URL(rawHref);
    if (urlObj.hostname.includes("instagram.com") || urlObj.hostname.includes("facebook.com")) {
      const u = urlObj.searchParams.get("u");
      if (u) return decodeURIComponent(u);
    }
    if (urlObj.hostname.includes("google.") && urlObj.searchParams.get("q")) {
      return decodeURIComponent(urlObj.searchParams.get("q"));
    }
    if (urlObj.hostname.includes("youtube.com") && urlObj.searchParams.get("q")) {
      return decodeURIComponent(urlObj.searchParams.get("q"));
    }
    for (const key of ["url", "target", "dest", "link", "redirect"]) {
      const val = urlObj.searchParams.get(key);
      if (val && val.startsWith("http")) return decodeURIComponent(val);
    }
  } catch (e) {}
  return rawHref;
}

function handleLinkClick(e) {
  if (!protectionEnabled) return;

  const targetAnchor = e.target.closest("a") || e.target.closest("[data-href]") || e.target.closest("[role='link']");
  if (!targetAnchor) return;

  let href = targetAnchor.href || targetAnchor.getAttribute("data-href") || targetAnchor.getAttribute("href");
  if (!href) return;

  if (href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:")) {
    return;
  }

  const targetUrl = extractTargetUrl(href);

  try {
    const urlObj = new URL(targetUrl);
    if (urlObj.hostname === window.location.hostname && urlObj.pathname === window.location.pathname) {
      return;
    }

    // Allow immediate, zero-latency navigation to trusted Identity Providers (Google, Microsoft, Apple, GitHub)
    // so synchronous OAuth user gestures and popups are never interrupted or blocked
    const host = urlObj.hostname.toLowerCase();
    const parts = host.split(".");
    let apex = parts.slice(-2).join(".");
    if (parts.length >= 3 && (parts.slice(-2).join(".") === "ac.in" || parts.slice(-2).join(".") === "co.uk" || parts.slice(-2).join(".") === "gov.in")) {
      apex = parts.slice(-3).join(".");
    }
    const trustedIdPs = ["google.com", "microsoftonline.com", "live.com", "apple.com", "github.com", "auth0.com", "okta.com", "firebaseapp.com", "atlassian.com"];
    if (trustedIdPs.includes(apex) && !host.includes("xn--")) {
      return; // Do not preventDefault; let native OAuth popup/redirect fire instantly!
    }
  } catch (err) {
    return;
  }

  if (targetAnchor.getAttribute("data-phishguard-allowed") === "true") {
    return;
  }

  e.preventDefault();
  e.stopPropagation();

  const originalCursor = document.body.style.cursor;
  document.body.style.cursor = "wait";

  chrome.runtime.sendMessage({ action: "scanUrl", url: targetUrl }, (response) => {
    document.body.style.cursor = originalCursor;

    if (response && response.success && response.data) {
      const result = response.data;

      if (result.classification === "URL_NOT_FOUND" || result.status === "unhosted") {
        showClickNotFoundToast(targetUrl);
      } else if (result.risk_score >= 65) {
        showClickWarningModal(targetUrl, result, targetAnchor, href);
      } else {
        showClickSafeToast(href, targetAnchor);
      }
    } else {
      allowNavigation(targetAnchor, href);
    }
  });
}

function allowNavigation(targetAnchor, href) {
  targetAnchor.setAttribute("data-phishguard-allowed", "true");
  if (targetAnchor.target === "_blank") {
    window.open(href, "_blank");
  } else {
    window.location.href = href;
  }
}

function showClickSafeToast(originalHref, targetAnchor) {
  const toast = document.createElement("div");
  toast.className = "pg-safe-badge-pill";
  toast.innerHTML = `
    <span class="pg-badge-icon">🛡️ ✓</span>
    <div class="pg-badge-content">
      <strong>Link Verified Safe</strong>
      <span>Authentic destination verified. Opening...</span>
    </div>
  `;
  document.documentElement.appendChild(toast);

  // 1-second display
  setTimeout(() => {
    toast.classList.add("pg-badge-fadeout");
    setTimeout(() => {
      toast.remove();
      allowNavigation(targetAnchor, originalHref);
    }, 250);
  }, 1000);
}

function showClickNotFoundToast(targetUrl) {
  const toast = document.createElement("div");
  toast.className = "pg-notfound-badge-pill";
  toast.innerHTML = `
    <span class="pg-badge-icon" style="color:#f59e0b;">⚠️</span>
    <div class="pg-badge-content">
      <strong style="color:#fbbf24;">URL Not Found</strong>
      <span>Destination link is inactive or unhosted on the internet.</span>
    </div>
  `;
  document.documentElement.appendChild(toast);

  // 1-second display
  setTimeout(() => {
    toast.classList.add("pg-badge-fadeout");
    setTimeout(() => {
      toast.remove();
    }, 250);
  }, 1000);
}

function showClickWarningModal(url, result, originalAnchor, originalHref) {
  const existing = document.getElementById("pg-click-warning-modal");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "pg-click-warning-modal";
  modal.className = "pg-modal-overlay";

  const reasons = (result.human_explanation && result.human_explanation.primary_risk_reasons)
    ? result.human_explanation.primary_risk_reasons
    : ["High-risk domain anomalies identified by machine learning model."];

  const reasonsHtml = reasons.map(r => `<li>${escapeHtml(r)}</li>`).join("");

  modal.innerHTML = `
    <div class="pg-modal-dialog">
      <div class="pg-modal-header">
        <div class="pg-shield-icon">🛑</div>
        <div class="pg-header-title">
          <h2>Dangerous Link Blocked</h2>
          <p>PhishGuard Shield stopped navigation to prevent information theft.</p>
        </div>
      </div>

      <div class="pg-risk-banner">
        <div class="pg-risk-score">${result.risk_score}% Threat Risk</div>
        <div class="pg-risk-badge">${result.classification}</div>
      </div>

      <div class="pg-url-preview">
        <span>Intercepted Destination URL:</span>
        <code>${escapeHtml(url)}</code>
      </div>

      <div class="pg-reasons-box">
        <h3>Why Was This Link Blocked? (TreeSHAP XAI)</h3>
        <ul>${reasonsHtml}</ul>
      </div>

      <div class="pg-action-buttons">
        <button id="pg-btn-safe" class="pg-btn-primary">
          🛡️ Exit / Return to Safety (Recommended)
        </button>
        <button id="pg-btn-proceed" class="pg-btn-secondary">
          ⚠️ Continue Anyway (Unsafe)
        </button>
      </div>

      <div class="pg-footer-note">
        PhishGuard-XAI Real-Time Interception Engine (Procedia CS 2026 Model)
      </div>
    </div>
  `;

  document.documentElement.appendChild(modal);

  document.getElementById("pg-btn-safe").addEventListener("click", () => {
    modal.remove();
  });

  document.getElementById("pg-btn-proceed").addEventListener("click", () => {
    modal.remove();
    try {
      const parsed = new URL(url.startsWith("http") ? url : "http://" + url);
      const domain = parsed.hostname.toLowerCase();
      sessionStorage.setItem("pg_allowed_" + domain, "true");
      chrome.runtime.sendMessage({ action: "allowDomain", domain: domain }, () => {
        allowNavigation(originalAnchor, originalHref);
      });
    } catch (e) {
      allowNavigation(originalAnchor, originalHref);
    }
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
