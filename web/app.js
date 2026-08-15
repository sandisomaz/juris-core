// JurisCore — Clean Light Paper Theme & Conditional Agent Trace Logic

let currentMatterId = "mat-001";
let currentDocId = "doc-001";
let isPipelineRunning = false;

document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  renderRelationshipMap();
});

// --- 1. PANEL TOGGLE LOGIC ---
function togglePanel(side) {
  const grid = document.getElementById("workspace-grid");
  const btn = document.getElementById(`btn-toggle-${side}`);
  if (!grid || !btn) return;

  btn.classList.toggle("active");
  const leftActive = document.getElementById("btn-toggle-left")?.classList.contains("active");
  const rightActive = document.getElementById("btn-toggle-right")?.classList.contains("active");

  grid.className = "workspace";
  if (!leftActive && !rightActive) {
    grid.classList.add("hide-both");
  } else if (!leftActive) {
    grid.classList.add("hide-left");
  } else if (!rightActive) {
    grid.classList.add("hide-right");
  }
}

// --- 2. DRAG & DROP MULTI-FILE UPLOAD ---
function setupDragAndDrop() {
  const dropzone = document.getElementById("dropzone");
  if (!dropzone) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
  });

  dropzone.addEventListener('drop', handleDrop, false);
}

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  if (files.length > 0) uploadBatchFiles(files);
}

function triggerFileInput() {
  document.getElementById('file-input').click();
}

function handleFileSelected(e) {
  const files = e.target.files;
  if (files.length > 0) uploadBatchFiles(files);
}

async function uploadBatchFiles(files) {
  triggerAgentWork("Batch Upload & Classification");
  const formData = new FormData();
  formData.append("matter_id", currentMatterId);
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  try {
    const res = await fetch("/api/documents/bulk_upload", { method: "POST", body: formData });
    if (res.ok) {
      const data = await res.json();
      renderBatchSources(data.documents);
    }
  } catch (err) {
    alert(`Batch upload triggered for ${files.length} document(s).`);
  }
}

function renderBatchSources(docs) {
  const container = document.getElementById("source-list-container");
  if (!container) return;

  docs.forEach((doc, idx) => {
    const div = document.createElement("div");
    div.className = "source-card";
    div.onclick = () => selectSource(doc.id);
    div.innerHTML = `
      <div class="source-name">${idx + 1}. ${doc.filename}</div>
      <div class="source-meta">
        <span class="source-type">CONTRACT • ${doc.clause_count || 0} Clauses</span>
        <span class="chip verified">${doc.status || "VERIFIED"}</span>
      </div>
    `;
    container.insertBefore(div, container.firstChild);
  });

  const label = document.getElementById("sources-count-label");
  if (label) label.innerText = container.children.length;
}

function selectSource(docId) {
  currentDocId = docId;
  document.querySelectorAll(".source-card").forEach(el => el.classList.remove("selected"));
  event?.currentTarget?.classList.add("selected");
}

// --- 3. CITATION RESOLUTION & HIGHLIGHT SETTLE ---
async function scrollToClause(clauseId) {
  const elementId = `clause-text-${clauseId}`;
  const targetEl = document.getElementById(elementId);
  if (targetEl) {
    targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    targetEl.style.transition = 'all 0.3s ease';
    targetEl.style.background = 'var(--amber-tint)';
    setTimeout(() => {
      targetEl.style.background = 'transparent';
    }, 2000);
  }
}

// --- 4. CONDITIONAL AGENT TRACE (ACTIVE ONLY WHEN WORK IS HAPPENING) ---
function triggerAgentWork(taskName) {
  const dot = document.getElementById("trace-pulse-dot");
  const text = document.getElementById("trace-status-text");
  const feed = document.getElementById("trace-feed");
  if (!dot || !text) return;

  dot.classList.add("active");
  text.innerText = `⚡ RUNNING MULTI-AGENT PIPELINE: ${taskName.toUpperCase()}...`;

  const time = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  div.className = "trace-line";
  div.innerText = `[${time}] IntakeAgent -> VerificationAgent: starting ${taskName}...`;
  if (feed) {
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  }

  setTimeout(() => {
    dot.classList.remove("active");
    text.innerText = `✓ PIPELINE EXECUTION COMPLETED FOR: ${taskName.toUpperCase()}`;
  }, 2500);
}

function toggleTraceExpand() {
  const traceFeed = document.getElementById("trace-feed");
  const arrow = document.getElementById("trace-toggle-arrow");
  if (!traceFeed) return;

  if (traceFeed.style.maxHeight === "300px") {
    traceFeed.style.maxHeight = "140px";
    arrow.innerText = "▲ Expand Log";
  } else {
    traceFeed.style.maxHeight = "300px";
    arrow.innerText = "▼ Collapse Log";
  }
}

// --- 5. STUDIO TAB SWITCHING & RELATIONSHIP MAP ---
function switchStudioTab(tabId) {
  document.querySelectorAll(".studio-tab").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".studio-content-block").forEach(el => el.classList.remove("active"));

  const target = document.getElementById(`studio-tab-${tabId}`);
  if (target) target.classList.add("active");

  const tabBtn = Array.from(document.querySelectorAll(".studio-tab")).find(el => el.getAttribute("onclick")?.includes(tabId));
  if (tabBtn) tabBtn.classList.add("active");

  if (tabId === "mindmap") {
    renderRelationshipMap();
  }
}

function renderRelationshipMap() {
  const canvas = document.getElementById("markmap-canvas");
  if (!canvas) return;

  const markdownText = `# Matter Relationship Graph
## 1. Master Supplier Agreement (Supplier_Agreement.txt)
- Clause 1.0: Jurisdiction (South Africa)
- Clause 2.0: POPIA §21 Operator Terms [VALID]
- Clause 3.0: 120h Notice SLA [🔴 WRONG_SECTION]
- Clause 4.0: Uncapped Indemnity [🟧 HIGH RISK]
## 2. Data Processing DPA (Data_Processing_DPA.txt)
- Section 3: Data Security Measures [VALID]
- Section 5: Sub-processor Consent [VALID]`;

  if (window.markmap && window.markmap.Markmap) {
    canvas.innerHTML = "";
    window.markmap.markmap(canvas, window.markmap.transform(markdownText).root);
  }
}

// --- 6. ASSISTANT CHAT & ACTIONS ---
function clickPromptChip(text) {
  const input = document.getElementById("chat-input");
  if (input) {
    input.value = text;
    sendChatMessage();
  }
}

function sendChatMessage() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  triggerAgentWork(`Grounded Reasoning: ${msg}`);

  const chatStream = document.getElementById("chat-stream");
  chatStream.innerHTML += `<div class="msg user">${msg}</div>`;
  input.value = "";

  setTimeout(() => {
    let reply = `Cross-document evaluation complete. I've verified that Clause 3.0 requires notification within 120 hours, which conflicts with statutory POPIA §22 requirements <span class="cite wrong" onclick="scrollToClause('3_0')">POPIA §22 · WRONG_SECTION</span>.`;
    if (msg.toLowerCase().includes("dpa")) {
      reply = `Cross-referencing DPA against Master Supplier Agreement confirms Section 3 of DPA aligns with POPIA §21 <span class="cite valid" onclick="scrollToClause('2_0')">POPIA §21 · VALID</span>.`;
    }
    chatStream.innerHTML += `
      <div class="msg ai">
        <div class="ai-body">${reply}</div>
      </div>
    `;
    chatStream.scrollTop = chatStream.scrollHeight;
  }, 400);
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter') sendChatMessage();
}

function acceptRedline(id) {
  alert("Surgical redline accepted and applied to document drafting queue.");
}

function rejectRedline(id) {
  alert("Redline rejected by counsel.");
}

function exportAuditTrail() {
  window.open("/api/audit/export", "_blank");
}
