// PhishGuard-XAI Warning Page Logic (CSP Compliant - No inline scripts)
document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const targetUrl = params.get("target") || "Suspicious URL";
  
  const blockedEl = document.getElementById("blocked-url");
  if (blockedEl) {
    blockedEl.textContent = targetUrl;
  }

  const btnBack = document.getElementById("btn-back");
  if (btnBack) {
    btnBack.addEventListener("click", (e) => {
      e.preventDefault();
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = "https://google.com";
      }
    });
  }

  const btnBypass = document.getElementById("btn-bypass");
  if (btnBypass) {
    btnBypass.addEventListener("click", () => {
      if (confirm("WARNING: Visiting this site may compromise your personal passwords, banking details, or device security. Are you sure you want to proceed?")) {
        try {
          const parsed = new URL(targetUrl.startsWith("http") ? targetUrl : "http://" + targetUrl);
          const domain = parsed.hostname.toLowerCase();
          // Whitelist domain across background worker and session
          chrome.runtime.sendMessage({ action: "allowDomain", domain: domain }, () => {
            sessionStorage.setItem("pg_allowed_" + domain, "true");
            window.location.replace(targetUrl);
          });
        } catch (e) {
          window.location.replace(targetUrl);
        }
      }
    });
  }
});
