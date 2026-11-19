/**
 * PhishGuard-XAI Content Script (Automatic Link Interceptor)
 * Intercepts clicks on every webpage.
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

function handleLinkClick(e) {
  if (!protectionEnabled) return;

  const targetAnchor = e.target.closest("a");
  if (!targetAnchor || !targetAnchor.href) return;

  const href = targetAnchor.href;

  // Ignore page anchors, javascript, mailto
  if (href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:")) {
    return;
  }

  // Same page navigation
  try {
    const urlObj = new URL(href);
    if (urlObj.hostname === window.location.hostname && urlObj.pathname === window.location.pathname) {
      return;
    }
  } catch (err) {
    return;
  }

  // If user already clicked "proceed anyway" on this specific link
  if (targetAnchor.getAttribute("data-phishguard-allowed") === "true") {
    return;
  }

  // STOP THE CLICK IMMEDIATELY BEFORE CHROME LOADS THE LINK
  e.preventDefault();
  e.stopPropagation();

  // Show a mini non-intrusive checking indicator
  const originalCursor = document.body.style.cursor;
  document.body.style.cursor = "wait";

  chrome.runtime.sendMessage({ action: "scanUrl", url: href }, (response) => {
    document.body.style.cursor = originalCursor;

    if (response && response.success && response.data) {
      const result = response.data;

      if (result.risk_score >= 65) {
        // High Risk / Phishing: BLOCK PAGE AND ASK USER
        showWarningModal(href, result, targetAnchor);
      } else {
        // Safe: Show 1-second "Verified Safe" indicator, then open
        showSafeToastAndNavigate(href, result, targetAnchor);
      }
    } else {
      // Fallback: Proceed
      targetAnchor.setAttribute("data-phishguard-allowed", "true");
      window.location.href = href;
    }
  });
}

function showSafeToastAndNavigate(url, result, targetAnchor) {
  const existing = document.getElementById("pg-safe-toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.id = "pg-safe-toast";
  toast.className = "pg-safe-toast";
  toast.innerHTML = `
    <span class="pg-toast-shield">🛡️ ✓</span>
    <div class="pg-toast-text">
      <strong>Link Verified Safe (${result.risk_score}% Risk)</strong>
      <span>Authentic domain verified. Opening destination...</span>
    </div>
  `;
  document.body.appendChild(toast);

  // Display for 1 second, then navigate naturally
  setTimeout(() => {
    toast.remove();
    targetAnchor.setAttribute("data-phishguard-allowed", "true");
    window.location.href = url;
  }, 950);
}

function showWarningModal(url, result, originalAnchor) {
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
    originalAnchor.setAttribute("data-phishguard-allowed", "true");
    window.location.href = url;
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
