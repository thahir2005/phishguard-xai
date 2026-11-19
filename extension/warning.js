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
      if (confirm("WARNING: Visiting this site may compromise your personal passwords, banking details, or device security. Are you sure?")) {
        window.location.href = targetUrl;
      }
    });
  }
});
