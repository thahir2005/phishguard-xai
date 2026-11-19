/**
 * PhishGuard-XAI Content Script (Automatic Link Interceptor)
 * Intercepts clicks on every webpage including Instagram, Facebook, X, and WhatsApp Web.
 * Automatically unwraps social media link shims (e.g. l.instagram.com/?u=...).
 * - If SAFE: Displays a 1-second "Verified Safe" security confirmation before opening.
 * - If RISK: Blocks the link immediately and asks "Exit / Return to Safety" or "Continue Anyway".
 */

let protectionEnabled = true;

chrome.storage.local.get(["protectionEnabled"], (data) => {
  if (data.protectionEnabled !== undefined) {
    protectionEnabled = data.protectionEnabled;
  }
});

// Intercept all clicks across the entire webpage in the capture phase
document.addEventListener("click", handleLinkClick, true);

function extractTargetUrl(rawHref) {
  try {
    const urlObj = new URL(rawHref);
    // 1. Meta / Instagram shim: l.instagram.com/?u=...
    // 2. Meta / Facebook shim: lm.facebook.com/l.php?u=... or l.facebook.com/l.php?u=...
    if (urlObj.hostname.includes("instagram.com") || urlObj.hostname.includes("facebook.com")) {
      const u = urlObj.searchParams.get("u");
      if (u) return decodeURIComponent(u);
    }
    // 3. Google search redirect: google.com/url?q=...
    if (urlObj.hostname.includes("google.") && urlObj.searchParams.get("q")) {
      return decodeURIComponent(urlObj.searchParams.get("q"));
    }
    // 4. YouTube redirect: youtube.com/redirect?q=...
    if (urlObj.hostname.includes("youtube.com") && urlObj.searchParams.get("q")) {
      return decodeURIComponent(urlObj.searchParams.get("q"));
    }
    // 5. Generic redirect parameters
    for (const key of ["url", "target", "dest", "link", "redirect"]) {
      const val = urlObj.searchParams.get(key);
      if (val && val.startsWith("http")) return decodeURIComponent(val);
    }
  } catch (e) {}
  return rawHref;
}

function handleLinkClick(e) {
  if (!protectionEnabled) return;

  // Find clicked anchor or elements with role=link / data-href
  const targetAnchor = e.target.closest("a") || e.target.closest("[data-href]") || e.target.closest("[role='link']");
  if (!targetAnchor) return;

  let href = targetAnchor.href || targetAnchor.getAttribute("data-href") || targetAnchor.getAttribute("href");
  if (!href) return;

  // Ignore page anchors, javascript, mailto
  if (href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:")) {
    return;
  }

  // Extract the true destination if wrapped inside an Instagram or Facebook shim
  const targetUrl = extractTargetUrl(href);

  // If internal same-page navigation
  try {
    const urlObj = new URL(targetUrl);
    if (urlObj.hostname === window.location.hostname && urlObj.pathname === window.location.pathname) {
      return;
    }
  } catch (err) {
    return;
  }

  // If user already clicked "proceed anyway" on this link
  if (targetAnchor.getAttribute("data-phishguard-allowed") === "true") {
    return;
  }

  // STOP THE CLICK IMMEDIATELY BEFORE NAVIGATION
  e.preventDefault();
  e.stopPropagation();

  const originalCursor = document.body.style.cursor;
  document.body.style.cursor = "wait";

  chrome.runtime.sendMessage({ action: "scanUrl", url: targetUrl }, (response) => {
    document.body.style.cursor = originalCursor;

    if (response && response.success && response.data) {
      const result = response.data;

      if (result.risk_score >= 65) {
        // High Risk / Phishing: BLOCK PAGE AND ASK USER
        showWarningModal(targetUrl, result, targetAnchor, href);
      } else {
        // Safe: Show 1-second "Verified Safe" indicator, then open
        showSafeToastAndNavigate(href, targetUrl, result, targetAnchor);
      }
    } else {
      // Fallback
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

function showSafeToastAndNavigate(originalHref, targetUrl, result, targetAnchor) {
  const existing = document.getElementById("pg-safe-toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.id = "pg-safe-toast";
  toast.className = "pg-safe-toast";
  toast.innerHTML = `
    <span class="pg-toast-shield">🛡️ ✓</span>
    <div class="pg-toast-text">
      <strong>Link Verified Safe (${result.risk_score}% Risk)</strong>
      <span>Authentic destination verified. Opening...</span>
    </div>
  `;
  document.body.appendChild(toast);

  // Display for 1 second, then open
  setTimeout(() => {
    toast.remove();
    allowNavigation(targetAnchor, originalHref);
  }, 950);
}

function showWarningModal(url, result, originalAnchor, originalHref) {
  const existing = document.getElementById("phishguard-interstitial");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "phishguard-interstitial";
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

  document.body.appendChild(modal);

  // Option 1: Exit / Return to Safety
  document.getElementById("pg-btn-safe").addEventListener("click", () => {
    modal.remove();
  });

  // Option 2: Continue Anyway
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
