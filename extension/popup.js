document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("shield-toggle");
  const toggleLbl = document.getElementById("toggle-lbl");
  const statScanned = document.getElementById("stat-scanned");
  const statBlocked = document.getElementById("stat-blocked");
  const scanBtn = document.getElementById("popup-scan-btn");
  const urlInput = document.getElementById("popup-url");
  const resultArea = document.getElementById("popup-result");
  const openDashBtn = document.getElementById("open-dashboard-btn");

  // Load stats
  chrome.storage.local.get(["linksScanned", "threatsBlocked", "protectionEnabled"], (data) => {
    statScanned.textContent = data.linksScanned || 0;
    statBlocked.textContent = data.threatsBlocked || 0;
    const isEnabled = data.protectionEnabled !== undefined ? data.protectionEnabled : true;
    toggle.checked = isEnabled;
    toggleLbl.textContent = isEnabled ? "Active" : "Paused";
  });

  // Toggle switch
  toggle.addEventListener("change", () => {
    const enabled = toggle.checked;
    toggleLbl.textContent = enabled ? "Active" : "Paused";
    chrome.storage.local.set({ protectionEnabled: enabled });
  });

  // Quick scan
  scanBtn.addEventListener("click", () => {
    const url = urlInput.value.trim();
    if (!url) return;

    scanBtn.textContent = "...";
    chrome.runtime.sendMessage({ action: "scanUrl", url }, (res) => {
      scanBtn.textContent = "Scan";
      if (res && res.success && res.data) {
        const d = res.data;
        resultArea.style.display = "block";
        const isMalicious = d.risk_score >= 65;

        resultArea.className = `scan-res-area ${isMalicious ? 'res-danger' : 'res-safe'}`;
        resultArea.innerHTML = `
          <strong>${d.classification} (${d.risk_score}%)</strong><br>
          ${d.human_explanation.summary}
        `;
      } else {
        resultArea.style.display = "block";
        resultArea.className = "scan-res-area res-danger";
        resultArea.textContent = "Scan request failed.";
      }
    });
  });

  // Open full SOC dashboard (Works on all computers via GitHub Pages, or fallback to local)
  openDashBtn.addEventListener("click", () => {
    // Attempt local if available, else open live GitHub Pages deployment
    fetch("http://localhost:8000/api/health", { method: "GET", mode: "no-cors" })
      .then(() => {
        chrome.tabs.create({ url: "http://localhost:8000" });
      })
      .catch(() => {
        chrome.tabs.create({ url: "https://thahir2005.github.io/phishguard-xai/" });
      });
  });
});
