/**
 * PhishGuard-XAI Web Dashboard Client Logic
 * Handles interactive tabs, live URL scans, TreeSHAP bar renders,
 * benchmark reproduction (Table 1), and batch scanning.
 */

const API_BASE = window.location.origin;

// Global ranked feature list from Dirchaoui et al. (Fig 1)
const GLOBAL_SHAP_FEATURES = [
  { name: "is_common_tld", mean_shap: 2.18, desc: "Common vs Uncommon Top-Level Domain (.com vs .top/.xyz)" },
  { name: "tld_length", mean_shap: 1.30, desc: "Length of the Top-Level Domain" },
  { name: "entropy", mean_shap: 1.28, desc: "Shannon Entropy of the Domain Name (Randomness)" },
  { name: "letter_digit_ratio", mean_shap: 1.18, desc: "Ratio of alphabetic characters to numerical digits" },
  { name: "num_slashes", mean_shap: 0.86, desc: "Count of forward slashes in URL structure" },
  { name: "num_subdomains", mean_shap: 0.77, desc: "Number of nested subdomains" },
  { name: "path_length", mean_shap: 0.65, desc: "Character length of the URL path" },
  { name: "url_length", mean_shap: 0.46, desc: "Total length of the Uniform Resource Locator" },
  { name: "num_digits", mean_shap: 0.45, desc: "Total count of digits within the URL" },
  { name: "num_special_chars", mean_shap: 0.35, desc: "Count of special characters (-_?&=./%#@+~)" },
  { name: "num_directories", mean_shap: 0.26, desc: "Count of nested path directories" },
  { name: "has_suspicious_words", mean_shap: 0.16, desc: "Presence of phishing / social engineering trigger words" },
  { name: "num_fragments", mean_shap: 0.14, desc: "Fragment identifier count (#)" },
  { name: "has_https", mean_shap: 0.06, desc: "Presence of HTTPS protocol encryption" },
  { name: "has_hex", mean_shap: 0.05, desc: "Presence of hexadecimal URL encodings (%20, %2f)" },
  { name: "is_shortened_url", mean_shap: 0.05, desc: "Usage of public URL shortening services" },
  { name: "has_ip", mean_shap: 0.01, desc: "Direct IP address usage instead of domain" }
];

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initScanForm();
  initDemoChips();
  initBenchmarkTab();
  initShapTab();
  initBatchScanner();
});

/* ================= TAB NAVIGATION ================= */
function initTabs() {
  const buttons = document.querySelectorAll(".nav-btn");
  const panes = document.querySelectorAll(".tab-pane");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      buttons.forEach(b => b.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

/* ================= LIVE URL SCANNER ================= */
function initScanForm() {
  const form = document.getElementById("scan-form");
  const input = document.getElementById("url-input");
  const scanBtn = document.getElementById("scan-btn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = input.value.trim();
    if (!url) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      renderScanResults(data);
    } catch (err) {
      alert(`Scan failed: ${err.message}. Ensure the PhishGuard server is running on port 8000.`);
    } finally {
      setLoading(false);
    }
  });

  function setLoading(loading) {
    const btnText = scanBtn.querySelector(".btn-text");
    const loader = scanBtn.querySelector(".btn-loader");
    if (loading) {
      btnText.textContent = "Scanning...";
      scanBtn.disabled = true;
    } else {
      btnText.textContent = "Analyze Link";
      scanBtn.disabled = false;
    }
  }
}

/* ================= DEMO LINK CHIPS ================= */
function initDemoChips() {
  const chips = document.querySelectorAll(".demo-chip");
  const input = document.getElementById("url-input");
  const form = document.getElementById("scan-form");

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const url = chip.getAttribute("data-url");
      input.value = url;
      form.dispatchEvent(new Event("submit"));
    });
  });
}

/* ================= RENDER SCAN RESULTS ================= */
function renderScanResults(data) {
  const resultsView = document.getElementById("results-view");
  resultsView.style.display = "block";

  const verdictCard = document.getElementById("verdict-card");
  const gaugeCircle = document.getElementById("gauge-circle");
  const resScore = document.getElementById("res-score");
  const resBadge = document.getElementById("res-badge");
  const resClass = document.getElementById("res-class");
  const resUrl = document.getElementById("res-url-text");
  const resSummary = document.getElementById("res-summary-text");
  const resAction = document.getElementById("res-action-text");

  // Reset classes
  verdictCard.className = "verdict-banner";
  gaugeCircle.className = "gauge-ring";
  resBadge.className = "verdict-badge";

  const score = data.risk_score;
  resScore.textContent = `${score}%`;
  resUrl.textContent = data.url;
  resSummary.textContent = data.human_explanation.summary;
  resAction.textContent = data.human_explanation.action;

  if (score >= 65) {
    verdictCard.classList.add("banner-danger");
    gaugeCircle.classList.add("gauge-danger");
    resBadge.classList.add("badge-danger");
    resBadge.textContent = "CRITICAL PHISHING";
    resClass.textContent = "MALICIOUS CLASSIFICATION";
  } else if (score >= 35) {
    verdictCard.classList.add("banner-warning");
    gaugeCircle.classList.add("gauge-warning");
    resBadge.classList.add("badge-warning");
    resBadge.textContent = "SUSPICIOUS URL";
    resClass.textContent = "CAUTION ADVISED";
  } else {
    verdictCard.classList.add("banner-safe");
    gaugeCircle.classList.add("gauge-safe");
    resBadge.classList.add("badge-safe");
    resBadge.textContent = "SAFE & VERIFIED";
    resClass.textContent = "BENIGN CLASSIFICATION";
  }

  // Render SHAP Bars
  renderShapBars(data.shap_explanation);

  // Render Explanations
  const riskList = document.getElementById("res-risk-reasons");
  const safeList = document.getElementById("res-safe-reasons");

  riskList.innerHTML = data.human_explanation.primary_risk_reasons
    .map(r => `<li>${r}</li>`).join("");

  safeList.innerHTML = (data.human_explanation.positive_indicators.length > 0)
    ? data.human_explanation.positive_indicators.map(s => `<li>${s}</li>`).join("")
    : `<li>No strong positive legitimacy factors identified.</li>`;

  // Render Diagnostic Matrix
  renderDiagnosticMatrix(data.features);

  // Smooth scroll to results
  resultsView.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ================= RENDER SHAP BARS ================= */
function renderShapBars(shapData) {
  const container = document.getElementById("shap-bars-container");
  container.innerHTML = "";

  const allShap = shapData.all_features_shap;
  // Sort by absolute SHAP impact
  const sorted = Object.entries(allShap)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 7); // Show top 7 contributors

  const maxVal = Math.max(...sorted.map(s => Math.abs(s[1])), 0.1);

  sorted.forEach(([feat, val]) => {
    const isRisk = val > 0;
    const absPercent = Math.min(100, Math.round((Math.abs(val) / maxVal) * 100));

    const row = document.createElement("div");
    row.className = "shap-row";
    row.innerHTML = `
      <div class="shap-row-header">
        <span>${feat}</span>
        <span style="color: ${isRisk ? '#ef4444' : '#10b981'}">
          ${isRisk ? '+' : ''}${val.toFixed(3)} SHAP (${isRisk ? 'Risk' : 'Safe'})
        </span>
      </div>
      <div class="shap-bar-track">
        <div class="shap-bar-fill ${isRisk ? 'fill-danger' : 'fill-safe'}" style="width: ${absPercent}%"></div>
      </div>
    `;
    container.appendChild(row);
  });
}

/* ================= RENDER DIAGNOSTICS ================= */
function renderDiagnosticMatrix(f) {
  const grid = document.getElementById("diagnostic-grid");
  grid.innerHTML = "";

  const items = [
    { label: "Top-Level Domain (TLD)", value: f.is_common_tld ? "Common / Trusted" : "High-Risk Uncommon", danger: !f.is_common_tld },
    { label: "Domain Shannon Entropy", value: `${f.entropy} bits`, danger: f.entropy >= 3.6 },
    { label: "SSL / HTTPS Protocol", value: f.has_https ? "HTTPS (Present)" : "HTTP (Insecure)", danger: !f.has_https },
    { label: "Brand Impersonation Score", value: f.brand_impersonation_score > 0 ? `${(f.brand_impersonation_score*100).toFixed(0)}% Match` : "None Detected", danger: f.brand_impersonation_score >= 0.8 },
    { label: "Subdomain Nesting Level", value: `${f.num_subdomains} subdomains`, danger: f.num_subdomains >= 2 },
    { label: "IDN Homograph / Punycode", value: f.is_punycode || f.homograph_spoof_score ? "Detected Spoof" : "Standard Latin", danger: f.is_punycode || f.homograph_spoof_score },
    { label: "Suspicious Word Tokens", value: `${f.suspicious_word_count} tokens`, danger: f.suspicious_word_count > 0 },
    { label: "Letter to Digit Ratio", value: `${f.letter_digit_ratio}`, danger: f.letter_digit_ratio < 2.0 },
    { label: "URL Length", value: `${f.url_length} chars`, danger: f.url_length > 80 },
    { label: "URL Shortener Used", value: f.is_shortened_url ? "Yes (Obfuscated)" : "No (Direct)", danger: f.is_shortened_url }
  ];

  items.forEach(it => {
    const box = document.createElement("div");
    box.className = "diag-item";
    box.innerHTML = `
      <div class="diag-label">${it.label}</div>
      <div class="diag-value ${it.danger ? 'highlight-danger' : 'highlight-safe'}">${it.value}</div>
    `;
    grid.appendChild(box);
  });
}

/* ================= BENCHMARK TABLE (TABLE 1) ================= */
async function initBenchmarkTab() {
  const tbody = document.getElementById("benchmark-tbody");
  const refreshBtn = document.getElementById("refresh-benchmark-btn");

  async function loadBenchmark() {
    try {
      const res = await fetch(`${API_BASE}/api/benchmark`);
      const data = await res.json();
      const table = data.table_1_comparison;

      tbody.innerHTML = "";
      for (const [model, m] of Object.entries(table)) {
        const isProposed = model.includes("Proposed");
        const tr = document.createElement("tr");
        if (isProposed) tr.className = "highlight-row";

        tr.innerHTML = `
          <td><strong>${model}</strong></td>
          <td>${m.accuracy.toFixed(2)}%</td>
          <td>${m.precision.toFixed(2)}%</td>
          <td>${m.recall.toFixed(2)}%</td>
          <td>${m.f1_score.toFixed(2)}%</td>
          <td>${isProposed ? '<span class="badge-champion">★ Proposed (Ours)</span>' : 'Base Paper (2026)'}</td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      console.warn("Could not fetch benchmark API, rendering fallback benchmark.");
    }
  }

  refreshBtn.addEventListener("click", loadBenchmark);
  loadBenchmark();
}

/* ================= SHAP TAB ================= */
function initShapTab() {
  const listContainer = document.getElementById("global-shap-ranking");
  listContainer.innerHTML = "";

  GLOBAL_SHAP_FEATURES.forEach((item, idx) => {
    const el = document.createElement("div");
    el.className = "rank-item";
    el.innerHTML = `
      <div class="rank-title">
        <span class="rank-index">#${idx + 1}</span>
        <div>
          <strong>${item.name}</strong>
          <div style="font-size:0.75rem; color:var(--text-dim);">${item.desc}</div>
        </div>
      </div>
      <div class="rank-val">${item.mean_shap.toFixed(2)} SHAP</div>
    `;
    listContainer.appendChild(el);
  });
}

/* ================= BATCH SCANNER ================= */
function initBatchScanner() {
  const scanBtn = document.getElementById("batch-scan-btn");
  const clearBtn = document.getElementById("batch-clear-btn");
  const input = document.getElementById("batch-input");
  const container = document.getElementById("batch-results-container");
  const tbody = document.getElementById("batch-tbody");
  const statsBar = document.getElementById("batch-stats-bar");

  scanBtn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) return;

    const urls = text.split("\n").map(u => u.trim()).filter(u => u.length > 0);
    scanBtn.disabled = true;
    scanBtn.textContent = "Scanning Batch...";

    try {
      const res = await fetch(`${API_BASE}/api/batch-scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urls })
      });
      const data = await res.json();
      renderBatchResults(data.results);
    } catch (err) {
      alert(`Batch scan failed: ${err.message}`);
    } finally {
      scanBtn.disabled = false;
      scanBtn.textContent = "Scan All URLs";
    }
  });

  clearBtn.addEventListener("click", () => {
    input.value = "";
    container.style.display = "none";
  });

  function renderBatchResults(results) {
    container.style.display = "block";
    tbody.innerHTML = "";

    let dangerCount = 0;
    let safeCount = 0;

    results.forEach(r => {
      if (r.risk_score >= 65) dangerCount++;
      else safeCount++;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-size:0.8rem; word-break:break-all;">${r.url}</td>
        <td><span class="verdict-badge ${r.risk_score >= 65 ? 'badge-danger' : (r.risk_score >= 35 ? 'badge-warning' : 'badge-safe')}">${r.classification}</span></td>
        <td>${r.risk_score}%</td>
        <td style="font-size:0.8rem; color:var(--text-muted);">${r.human_explanation.primary_risk_reasons[0] || 'Standard'}</td>
      `;
      tbody.appendChild(tr);
    });

    statsBar.innerHTML = `
      <div class="stat-chip">Total Scanned: <strong>${results.length}</strong></div>
      <div class="stat-chip" style="color:var(--status-danger)">Threats Blocked: <strong>${dangerCount}</strong></div>
      <div class="stat-chip" style="color:var(--status-safe)">Safe Verified: <strong>${safeCount}</strong></div>
    `;
  }
}
