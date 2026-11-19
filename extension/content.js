/**
 * PhishGuard-XAI Content Script
 * Scans page links in real-time, displays security badges,
 * and intercepts malicious phishing clicks before page navigation.
 */

let protectionEnabled = true;

// Check configuration
chrome.storage.local.get(["protectionEnabled"], (data) => {
  if (data.protectionEnabled !== undefined) {
    protectionEnabled = data.protectionEnabled;
  }
});

// Listen for link clicks across the entire DOM
document.addEventListener("click", handleLinkClick, true);

function handleLinkClick(e) {
  if (!protectionEnabled) return;

  const targetAnchor = e.target.closest("a");
  if (!targetAnchor || !targetAnchor.href) return;

  const href = targetAnchor.href;

  // Ignore internal hashes and javascript voids
  if (href.startsWith("#") || href.startsWith("javascript:") || href.startsWith("mailto:")) {
    return;
  }

  // Check if link is external or belongs to a different hostname
  try {
    const urlObj = new URL(href);
    if (urlObj.hostname === window.location.hostname) {
      return; // Internal page navigation
    }
  } catch (err) {
    return;
  }

  // If user has already confirmed proceeding for this URL in this session
  if (targetAnchor.getAttribute("data-phishguard-allowed") === "true") {
    return;
  }

  // Intercept and scan immediately
  e.preventDefault();
  e.stopPropagation();

  chrome.runtime.sendMessage({ action: "scanUrl", url: href }, (response) => {
    if (response && response.success && response.data) {
      const result = response.data;

      if (result.risk_score >= 65) {
        // High Risk / Critical Phishing detected -> Trigger Interstitial Modal
        showWarningModal(href, result, targetAnchor);
      } else {
        // Safe or Low Risk -> Proceed with normal navigation
        targetAnchor.setAttribute("data-phishguard-allowed", "true");
        window.location.href = href;
      }
    } else {
      // Fallback on error: allow navigation
      targetAnchor.setAttribute("data-phishguard-allowed", "true");
      window.location.href = href;
    }
  });
}

function showWarningModal(url, result, originalAnchor) {
  // Remove any existing modal
  const existing = document.getElementById("phishguard-interstitial");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "phishguard-interstitial";
  modal.className = "pg-modal-overlay";

  const reasonsHtml = result.human_explanation.primary_risk_reasons
    .map(r => `<li>${r}</li>`)
    .join("");

  modal.innerHTML = `
    <div class="pg-modal-dialog">
      <div class="pg-modal-header">
        <div class="pg-shield-icon">⚠️</div>
        <div class="pg-header-title">
          <h2>PhishGuard Shield: Deceptive Site Blocked</h2>
          <p>Real-Time Explainable Threat Interception</p>
        </div>
      </div>

      <div class="pg-risk-banner">
        <div class="pg-risk-score">${result.risk_score}% Threat Risk</div>
        <div class="pg-risk-badge">${result.classification}</div>
      </div>

      <div class="pg-url-preview">
        <span>Target URL:</span>
        <code>${escapeHtml(url)}</code>
      </div>

      <div class="pg-reasons-box">
        <h3>Why Was This Link Blocked? (TreeSHAP Analysis)</h3>
        <ul>${reasonsHtml}</ul>
      </div>

      <div class="pg-action-buttons">
        <button id="pg-btn-safe" class="pg-btn-primary">
          🛡️ Return to Safety (Recommended)
        </button>
        <button id="pg-btn-proceed" class="pg-btn-secondary">
          I understand the risks, proceed anyway
        </button>
      </div>

      <div class="pg-footer-note">
        Powered by PhishGuard-XAI (Based on Dirchaoui et al. 2026 Phishing Model)
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Button actions
  document.getElementById("pg-btn-safe").addEventListener("click", () => {
    modal.remove();
  });

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
