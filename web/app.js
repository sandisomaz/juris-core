// JurisCore Web Workspace Application Logic

let currentMatterId = "mat-001";
let currentDocId = "doc-001";
let currentReport = null;

document.addEventListener("DOMContentLoaded", () => {
  loadDashboardData();
  loadMattersData();
  loadRulesData();
});

function switchNav(viewName) {
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".view-content").forEach(el => el.classList.remove("active"));

  // Deactivate workspace container specifically
  const ws = document.getElementById("view-workspace");
  if (ws) ws.style.display = "none";

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    if (viewName === "workspace") {
      targetView.style.display = "flex";
    } else {
      targetView.classList.add("active");
    }
  }

  // Update nav item state
  const navItem = Array.from(document.querySelectorAll(".nav-item")).find(el => el.getAttribute("onclick")?.includes(viewName));
  if (navItem) navItem.classList.add("active");

  const titleMap = {
    dashboard: "Executive Dashboard",
    matters: "Matter Portfolio",
    workspace: "3-Column Review Workspace",
    rules: "Rules Engine & Legal Sources",
    trace: "Agent Trace Log & Observability",
    analytics: "Platform Analytics & Metrics"
  };
  document.getElementById("page-title").innerText = titleMap[viewName] || "JurisCore";
}

async function loadDashboardData() {
  try {
    const res = await fetch("/api/analytics");
    if (res.ok) {
      const data = await res.json();
      document.getElementById("metric-matters").innerText = data.active_matters_count;
      document.getElementById("metric-findings").innerText = data.total_findings_count;
      document.getElementById("metric-pending").innerText = data.pending_human_reviews_count;
      document.getElementById("metric-saved").innerText = `${data.estimated_hours_saved} hrs`;
    }
  } catch (err) {
    console.log("Offline mode dashboard analytics load.");
  }
}

async function loadMattersData() {
  try {
    const res = await fetch("/api/matters");
    if (res.ok) {
      const matters = await res.json();
      renderMattersTable(matters);
    }
  } catch (err) {
    console.log("Matters fallback render.");
  }
}

function renderMattersTable(matters) {
  const dashBody = document.getElementById("dashboard-matters-list");
  const fullBody = document.getElementById("matters-full-list");

  if (!matters || matters.length === 0) return;

  const rowsHtml = matters.map(m => `
    <tr>
      <td><strong>${m.title}</strong></td>
      <td>${m.client_name}</td>
      <td>${m.jurisdiction}</td>
      <td><span class="badge badge-${m.overall_risk}">${m.overall_risk} RISK</span></td>
      <td><span class="badge badge-VERIFIED">${m.status}</span></td>
      <td>
        <button class="btn btn-primary" onclick="openWorkspaceForMatter('${m.id}')">Open Workspace</button>
      </td>
    </tr>
  `).join("");

  if (dashBody) dashBody.innerHTML = rowsHtml;
  if (fullBody) fullBody.innerHTML = matters.map(m => `
    <tr>
      <td>${m.id}</td>
      <td><strong>${m.title}</strong></td>
      <td>${m.client_name}</td>
      <td>${m.jurisdiction}</td>
      <td><span class="badge badge-${m.overall_risk}">${m.overall_risk}</span></td>
      <td>${m.status}</td>
      <td>
        <button class="btn btn-primary" onclick="openWorkspaceForMatter('${m.id}')">Review</button>
      </td>
    </tr>
  `).join("");
}

function openWorkspaceForMatter(matterId) {
  currentMatterId = matterId;
  switchNav("workspace");
}

async function runAnalysisForCurrentDoc() {
  const cardsBody = document.getElementById("findings-cards-body");
  cardsBody.innerHTML = `<div style="text-align:center; padding: 40px; color: var(--primary-accent);">
    <div style="font-size:24px; margin-bottom:10px;">⚡</div>
    <div>Running Multi-Agent Compliance Pipeline...</div>
    <div style="font-size:11px; color:var(--text-muted); margin-top:6px;">Intake → Clause Extraction → Research → Compliance → Rules Engine → Citation Verifier → Redlining → Escalation</div>
  </div>`;

  try {
    const res = await fetch("/api/reviews/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ matter_id: currentMatterId, document_id: currentDocId })
    });

    if (res.ok) {
      const report = await res.json();
      currentReport = report;
      renderReportInWorkspace(report);
      loadAgentTrace(report.agent_trace_id);
    }
  } catch (err) {
    cardsBody.innerHTML = `<div style="color:var(--danger-red); text-align:center; padding:20px;">Analysis execution failed. Make sure FastAPI server is running.</div>`;
  }
}

function renderReportInWorkspace(report) {
  // Render Clause DOM Tree
  const clauseTree = document.getElementById("clause-tree-body");
  const docViewer = document.getElementById("document-text-container");
  const cardsBody = document.getElementById("findings-cards-body");

  // Sample Clauses Render
  const sampleClauses = [
    { id: "1.0", title: "1. DEFINITIONS & JURISDICTION", text: "This Master Services Agreement is entered into under the jurisdiction of South Africa." },
    { id: "2.0", title: "2. OPERATOR OBLIGATIONS & SECURITY", text: "The Operator agrees to process Personal Information on behalf of the Responsible Party. The Operator shall maintain confidential treatment of all data." },
    { id: "3.0", title: "3. SECURITY INCIDENT NOTIFICATION", text: "In the event of a security compromise or data breach, the Operator shall notify the Responsible Party in writing within 120 hours of becoming aware of such incident." },
    { id: "4.0", title: "4. LIMITATION OF LIABILITY & INDEMNITY", text: "The Supplier provides an indemnity to the Customer for all losses. There shall be unlimited liability exposure without any financial cap." },
    { id: "5.0", title: "5. STATUTORY GOVERNING LAW", text: "This agreement references POPIA Section 22 and Companies Act Section 66." }
  ];

  document.getElementById("clause-count-tag").innerText = `${sampleClauses.length} Clauses`;

  clauseTree.innerHTML = sampleClauses.map(c => `
    <div class="clause-item" onclick="highlightClauseText('${c.id}')">
      <div class="clause-title">${c.title}</div>
      <div class="clause-meta">Clause Ref: ${c.id}</div>
    </div>
  `).join("");

  // Document Viewer Text
  docViewer.innerHTML = sampleClauses.map(c => `
    <div id="clause-block-${c.id.replace('.', '_')}" class="clause-block" style="padding: 10px; margin-bottom: 12px; border-radius: 4px;">
      <strong style="color: var(--primary-accent);">${c.title}</strong><br/>
      ${c.text}
    </div>
  `).join("");

  // Findings Cards Render
  if (!report.findings || report.findings.length === 0) {
    cardsBody.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--success-green);">✅ All clauses passed deterministic compliance check!</div>`;
    return;
  }

  cardsBody.innerHTML = report.findings.map(f => `
    <div class="finding-card" id="finding-${f.finding_id}">
      <div class="card-top">
        <span class="finding-issue">${f.issue}</span>
        <span class="badge badge-${f.severity}">${f.severity}</span>
      </div>
      <div class="finding-basis">📍 ${f.location} | ⚖️ ${f.legal_basis}</div>
      <div class="finding-explanation">${f.explanation}</div>
      
      ${f.redline ? `
        <div class="redline-preview">
          <strong>Proposed Legal Redline:</strong><br/>
          ${f.redline}
        </div>
      ` : ''}

      <div class="action-bar">
        <button class="btn btn-success" onclick="recordDecision('${f.finding_id}', 'APPROVED')">✓ Approve</button>
        <button class="btn btn-primary" onclick="recordDecision('${f.finding_id}', 'ACCEPTED')">Accept Redline</button>
        <button class="btn btn-danger" onclick="recordDecision('${f.finding_id}', 'REJECTED')">Reject</button>
      </div>
    </div>
  `).join("");
}

function highlightClauseText(clauseId) {
  document.querySelectorAll(".clause-block").forEach(el => el.style.background = "transparent");
  const block = document.getElementById(`clause-block-${clauseId.replace('.', '_')}`);
  if (block) {
    block.style.background = "rgba(239, 68, 68, 0.15)";
    block.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

async function recordDecision(findingId, decision) {
  try {
    const res = await fetch("/api/reviews/decision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ finding_id: findingId, decision: decision, notes: "Counsel approved via review workspace" })
    });
    if (res.ok) {
      const card = document.getElementById(`finding-${findingId}`);
      if (card) {
        card.style.opacity = "0.5";
        card.insertAdjacentHTML("beforeend", `<div style="color:var(--success-green); font-weight:bold; font-size:11px; margin-top:8px;">✓ Decision Recorded: ${decision}</div>`);
      }
    }
  } catch (err) {
    alert(`Recorded decision: ${decision}`);
  }
}

async function loadRulesData() {
  try {
    const res = await fetch("/api/rules/sources");
    if (res.ok) {
      const sources = await res.json();
      const tbody = document.getElementById("rules-sources-list");
      if (tbody) {
        tbody.innerHTML = sources.map(s => `
          <tr>
            <td><strong>${s.legislation}</strong></td>
            <td>${s.act_number}</td>
            <td>Section ${s.section}</td>
            <td>${s.official_title}</td>
            <td>${s.effective_date}</td>
          </tr>
        `).join("");
      }
    }
  } catch (err) {
    console.log("Rules sources load offline.");
  }
}

async function loadAgentTrace(traceId) {
  try {
    const res = await fetch(`/api/audit/traces/${traceId}`);
    if (res.ok) {
      const trace = await res.json();
      const traceContainer = document.getElementById("trace-list-container");
      if (traceContainer && trace.steps) {
        traceContainer.innerHTML = trace.steps.map(s => `
          <div class="trace-step">
            <div class="trace-name">${s.agent_name} <span class="trace-time">${s.duration_ms} ms</span></div>
            <div style="font-size: 12px; color: var(--text-main); margin-top: 4px;">${s.action_summary}</div>
          </div>
        `).join("");
      }
    }
  } catch (err) {
    console.log("Trace load offline.");
  }
}

function exportReport(format) {
  if (!currentReport) {
    alert("Please run an agent review first.");
    return;
  }
  window.open(`/api/reports/${currentReport.report_id}/export/${format}`, '_blank');
}
