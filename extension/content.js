/**
 * PhishGuard-XAI Content Script
 * 1. Automatic On-Page Load Verification:
 *    - When ANY page loads (whether typed in address bar, opened from WhatsApp, or clicked):
 *      - If SAFE: Shows a sleek green "🛡️ ✓ Verified Safe" badge at the top for 0.5 seconds!
 *      - If UNSAFE: Immediately halts page and displays emergency warning shield!
 * 2. Pre-Click Link Interceptor:
 *    - Intercepts clicks on social media links (Instagram shims, Facebook shims, etc.)
 */

let protectionEnabled = true;

chrome.storage.local.get(["protectionEnabled"], (data) => {
  if (data.protectionEnabled !== undefined) {
    protectionEnabled = data.protectionEnabled;
  }
  // Run automatic on-page load verification
  initPageSecurityCheck();
});

// ========================================================
// 1. AUTOMATIC ON-PAGE LOAD VERIFICATION (Address Bar / WhatsApp / Direct Visit)
// ========================================================
function initPageSecurityCheck() {
  if (!protectionEnabled) return;

  const currentUrl = window.location.href;

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

      if (result.risk_score >= 65) {
        // High Risk / Phishing: IMMEDIATELY COVER PAGE WITH INTERSTITIAL WARNING
        showOnLoadWarningScreen(currentUrl, result);
      } else {
        // Safe: Show the 0.5-second Green "Verified Safe" Badge
        showHalfSecondSafeBadge(result);
      }
    }
  });
}

function showHalfSecondSafeBadge(result) {
  // Prevent duplicate badges
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

  // Keep visible for exactly 0.5 seconds (500ms), then smoothly fade out
  setTimeout(() => {
    badge.classList.add("pg-badge-fadeout");
    setTimeout(() => {
      badge.remove();
    }, 300);
  }, 500);
}

function showOnLoadWarningScreen(url, result) {
  // Stop page scripts and cover entire viewport
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

  // Exit / Return to safety
  document.getElementById("pg-onload-btn-exit").addEventListener("click", () => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = "https://google.com";
    }
  });

  // Continue anyway
  document.getElementById("pg-onload-btn-proceed").addEventListener("click", () => {
    sessionStorage.setItem("pg_allowed_" + window.location.hostname, "true");
    overlay.remove();
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

      if (result.risk_score >= 65) {
        showClickWarningModal(targetUrl, result, targetAnchor, href);
      } else {
        // Show 0.5s safe indicator before navigating
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
      <span>Opening destination...</span>
    </div>
  `;
  document.documentElement.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("pg-badge-fadeout");
    setTimeout(() => {
      toast.remove();
      allowNavigation(targetAnchor, originalHref);
    }, 200);
  }, 500);
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
    allowNavigation(originalAnchor, originalHref);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
