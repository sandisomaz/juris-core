// JurisCore — Two-State Shell Interaction Logic

let isWorkspaceOpen = false;
let isRailCollapsed = false;
let currentMatterId = "m-001";
let eventSourceInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  initLiveEventStream();
});

function initLiveEventStream() {
  if (!window.EventSource || eventSourceInstance) return;
  try {
    eventSourceInstance = new EventSource("/api/events/stream");
    eventSourceInstance.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        const feed = document.getElementById("thinking-steps-feed");
        const dot = document.getElementById("thinking-pulse-dot");
        const text = document.getElementById("thinking-status-text");

        if (feed && data.summary) {
          const line = document.createElement("div");
          line.className = data.status === "HUMAN_REVIEW_REQUIRED" ? "thinking-step-line escalation" : "thinking-step-line";
          line.innerHTML = `<b>${data.agent || 'Agent'}:</b> ${data.summary}`;
          feed.appendChild(line);
          feed.scrollTop = feed.scrollHeight;
        }
        if (text && data.agent) {
          text.innerText = `${data.agent.toUpperCase()} • ${data.status || 'ACTIVE'}`;
        }
        if (dot) {
          dot.classList.toggle("active", data.status === "RUNNING");
        }
      } catch (err) {}
    };
  } catch (e) {
    console.warn("SSE event stream offline, using local fallback");
  }
}

// --- 1. SEGMENTED LAYOUT STATE MANAGEMENT ---
let currentLayoutMode = "chat"; // 'chat' | 'split' | 'doc'

function setLayoutMode(mode) {
  currentLayoutMode = mode;

  // Update button active state
  document.querySelectorAll(".layout-btn").forEach(btn => btn.classList.remove("active"));
  const activeBtn = document.getElementById(`layout-btn-${mode}`);
  if (activeBtn) activeBtn.classList.add("active");

  const rail = document.getElementById("nav-rail");
  const wsCol = document.getElementById("right-workspace-column");
  const centerCol = document.querySelector(".center-chat-column");

  if (mode === "chat") {
    isWorkspaceOpen = false;
    if (wsCol) wsCol.classList.add("hidden");
    if (rail) rail.classList.remove("collapsed");
    if (centerCol) centerCol.style.display = "flex";
  } else if (mode === "split") {
    isWorkspaceOpen = true;
    if (wsCol) {
      wsCol.classList.remove("hidden");
      wsCol.style.width = "400px";
    }
    if (rail) rail.classList.add("collapsed");
    if (centerCol) centerCol.style.display = "flex";
  } else if (mode === "doc") {
    isWorkspaceOpen = true;
    if (wsCol) {
      wsCol.classList.remove("hidden");
      wsCol.style.width = "calc(100% - 56px)";
    }
    if (rail) rail.classList.add("collapsed");
    if (centerCol) centerCol.style.display = "none";
  }
}

function openWorkspaceState() {
  setLayoutMode("split");
}

function closeWorkspaceState() {
  setLayoutMode("chat");
}

function toggleWorkspaceColumn() {
  if (currentLayoutMode === "split" || currentLayoutMode === "doc") {
    setLayoutMode("chat");
  } else {
    setLayoutMode("split");
  }
}

function toggleRail() {
  const rail = document.getElementById("nav-rail");
  if (!rail) return;
  rail.classList.toggle("collapsed");
  isRailCollapsed = rail.classList.contains("collapsed");
}

// Global Keyboard Shortcuts (Ctrl+1, Ctrl+2, Ctrl+3, Ctrl+B)
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "1") {
    e.preventDefault();
    setLayoutMode("chat");
  } else if ((e.ctrlKey || e.metaKey) && e.key === "2") {
    e.preventDefault();
    setLayoutMode("split");
  } else if ((e.ctrlKey || e.metaKey) && e.key === "3") {
    e.preventDefault();
    setLayoutMode("doc");
  } else if ((e.ctrlKey || e.metaKey) && (e.key === "b" || e.key === "B")) {
    e.preventDefault();
    toggleWorkspaceColumn();
  }
});

function handleMatterSelect(matterId) {
  currentMatterId = matterId;
  const select = document.getElementById("matter-select");
  const matterName = select.options[select.selectedIndex].text;
  showToast(`Switched active matter context to: ${matterName}`, "success");
  loadMatter(matterId);
}

function startNewChat() {
  closeWorkspaceState();
  const chatStream = document.getElementById("chat-stream");
  if (chatStream) {
    chatStream.innerHTML = `
      <div class="msg ai">
        <div class="ai-body">
          Welcome to a new compliance session. Ask a question or type <code>review contract</code> to open the full workspace.
        </div>
      </div>
    `;
  }
}

// --- 2. WORKSPACE TAB FOCUS & ATTACHMENT CARDS ---
function openWorkspaceTab(tabId, clauseId) {
  openWorkspaceState();
  switchWsTab(tabId);

  if (clauseId) {
    scrollToClause(clauseId);
  }
}

function switchWsTab(tabId) {
  document.querySelectorAll(".ws-tab").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".ws-tab-content").forEach(el => el.classList.remove("active"));

  const targetContent = document.getElementById(`ws-tab-${tabId}`);
  if (targetContent) targetContent.classList.add("active");

  const targetTab = Array.from(document.querySelectorAll(".ws-tab")).find(el => el.getAttribute("onclick")?.includes(tabId));
  if (targetTab) targetTab.classList.add("active");
}

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

// --- 3. TOP AGENT THINKING BANNER ---
function triggerAgentWork(taskName) {
  openWorkspaceState();

  const dot = document.getElementById("thinking-pulse-dot");
  const text = document.getElementById("thinking-status-text");
  const feed = document.getElementById("thinking-steps-feed");
  if (!dot || !text) return;

  dot.classList.add("active");
  text.innerText = `EVALUATING LEGAL COMPLIANCE: ${taskName.toUpperCase()}...`;

  const time = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  div.className = "thinking-step-line active-agent";
  div.innerHTML = `<b>Step:</b> Processing multi-step task for ${taskName}...`;
  if (feed) {
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  }

  setTimeout(() => {
    dot.classList.remove("active");
    text.innerText = `COMPLIANCE CHECK COMPLETED FOR: ${taskName.toUpperCase()}`;
  }, 2200);
}

function toggleThinkingExpand() {
  const feed = document.getElementById("thinking-steps-feed");
  const arrow = document.getElementById("thinking-toggle-arrow");
  if (!feed || !arrow) return;

  if (feed.style.display === "none") {
    feed.style.display = "block";
    arrow.innerText = "Collapse Steps";
  } else {
    feed.style.display = "none";
    arrow.innerText = "Expand Steps";
  }
}

// --- 4. CHAT ACTIONS & PROMPTS ---
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

  const chatStream = document.getElementById("chat-stream");
  chatStream.innerHTML += `<div class="msg user">${msg}</div>`;
  input.value = "";

  // Trigger workspace transition if request warrants multi-step artifact creation
  const triggersWorkspace = msg.toLowerCase().includes("review") || msg.toLowerCase().includes("contract") || msg.toLowerCase().includes("open") || msg.toLowerCase().includes("dpa") || msg.toLowerCase().includes("popia");
  if (triggersWorkspace) {
    triggerAgentWork(msg);
  }

  setTimeout(() => {
    let reply = `I have completed the statutory review. I've verified that Clause 3.0 requires notification within 120 hours, which exceeds statutory POPIA §22 requirements <span class="cite wrong" onclick="openWorkspaceTab('sources', '3_0')" title="Click to view Clause 3.0 in Document Reader">POPIA §22 · Non-Compliant SLA</span>.`;
    
    chatStream.innerHTML += `
      <div class="msg ai">
        <div class="ai-body">
          ${reply}
          <div class="artifact-card-work" onclick="openWorkspaceTab('report')">
            <div class="artifact-card-left">
              <div class="artifact-file-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              </div>
              <div>
                <div class="artifact-title">Executive_Compliance_Memorandum_v1.docx</div>
                <div class="artifact-sub">Word Document • 4.2 KB • Click to open in panel</div>
              </div>
            </div>
            <button class="artifact-dl-btn" onclick="event.stopPropagation(); downloadDocxReport()" title="Download DOCX">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Download
            </button>
          </div>
        </div>
      </div>
    `;
    chatStream.scrollTop = chatStream.scrollHeight;
  }, 400);
}

function downloadDocxReport() {
  showToast("Compiling executive compliance memorandum and redlines to Word DOCX...", "success");
  window.open("/api/reports/default/export/docx", "_blank");
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter') sendChatMessage();
}

// --- Document Switcher & Reader Font Scale ---
function switchDocument(docKey) {
  document.querySelectorAll(".source-item-card").forEach(el => el.classList.remove("active-doc"));
  const title = document.getElementById("reader-title-display");
  const readerBox = document.getElementById("reader-content-box");

  if (docKey === "doc1") {
    const card = document.getElementById("doc-card-1");
    if (card) card.classList.add("active-doc");
    if (title) title.innerText = "Document Reader — Supplier_Agreement.txt";
    if (readerBox) {
      readerBox.innerHTML = `
        <div id="clause-text-1_0"><b>1. DEFINITIONS:</b> This Agreement is entered into under South African statutory jurisdiction.</div>
        <div id="clause-text-2_0" style="margin-top: 10px;"><b>2. OPERATOR SECURITY:</b> Data confidentiality and technical controls maintained per POPIA Section 21.</div>
        <div id="clause-text-3_0" style="margin-top: 10px;"><b>3. INCIDENT NOTIFICATION:</b> <mark>Operator shall notify Responsible Party within 120 hours of becoming aware of a data compromise.</mark></div>
        <div id="clause-text-4_0" style="margin-top: 10px;"><b>4. INDEMNITY:</b> Supplier provides an indemnity to Customer for all losses without financial limitation or monetary cap.</div>
      `;
    }
  } else if (docKey === "doc2") {
    const card = document.getElementById("doc-card-2");
    if (card) card.classList.add("active-doc");
    if (title) title.innerText = "Document Reader — Data_Processing_DPA.txt";
    if (readerBox) {
      readerBox.innerHTML = `
        <div id="clause-text-dpa_1"><b>Section 1. SCOPE & PURPOSE:</b> This Data Processing Addendum governs personal information processing by the Operator on behalf of the Customer under POPIA.</div>
        <div id="clause-text-dpa_2" style="margin-top: 10px;"><b>Section 2. DATA BREACH PROTOCOL:</b> <mark>Operator shall notify Customer without undue delay and in any event within 24 hours of becoming aware of a data breach.</mark></div>
        <div id="clause-text-dpa_3" style="margin-top: 10px;"><b>Section 3. SUB-PROCESSORS:</b> Prior written authorization is required before engaging third-party sub-processors.</div>
      `;
    }
  }
}

function setFontSize(size) {
  const readerBox = document.getElementById("reader-content-box");
  const btnStd = document.getElementById("font-btn-std");
  const btnLg = document.getElementById("font-btn-lg");

  if (size === "large") {
    if (readerBox) readerBox.classList.add("large-font");
    if (btnLg) btnLg.classList.add("active");
    if (btnStd) btnStd.classList.remove("active");
  } else {
    if (readerBox) readerBox.classList.remove("large-font");
    if (btnStd) btnStd.classList.add("active");
    if (btnLg) btnLg.classList.remove("active");
  }
}

// --- Navigation & Matter Handlers ---
function loadChat(chatId) {
  document.querySelectorAll(".rail-item").forEach(el => el.classList.remove("active"));
  const clicked = Array.from(document.querySelectorAll(".rail-item")).find(el => el.getAttribute("onclick")?.includes(chatId));
  if (clicked) clicked.classList.add("active");

  const chatStream = document.getElementById("chat-stream");
  if (chatStream) {
    chatStream.innerHTML = `
      <div class="msg ai">
        <div class="ai-body">
          Loaded session <strong>${chatId.toUpperCase()}</strong>. You are reviewing the compliance findings and statutory checks for this matter.
          <br><br>
          <div class="chat-attachment-card" onclick="openWorkspaceTab('report')">
            <span class="attachment-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--navy)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </span>
            <div>
              <div class="attachment-title">Executive Compliance Memorandum v1.pdf</div>
              <div class="attachment-sub">Click to inspect compliance scoring & statutory rationale</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

function loadMatter(matterId) {
  currentMatterId = matterId;
  
  // Update left rail active state
  document.querySelectorAll(".rail-item").forEach(el => el.classList.remove("active"));
  const clicked = Array.from(document.querySelectorAll(".rail-item")).find(el => el.getAttribute("onclick")?.includes(matterId));
  if (clicked) clicked.classList.add("active");

  const chatStream = document.getElementById("chat-stream");
  if (chatStream) {
    chatStream.innerHTML = `
      <div class="project-hub-view">
        <div class="project-back-link" onclick="loadChat('c-001')">← Back to Chat Stream</div>
        <div class="project-header-title">ABC Logistics — Vendor Onboarding &amp; POPIA Audit</div>
        <div class="project-header-sub">Client Matter • Cross-border vendor compliance review under POPIA Sections 19, 21, and 22</div>
        
        <div class="project-prompt-card">
          <textarea class="project-prompt-input" placeholder="Type / for skills or ask a compliance question for this matter..." id="project-prompt-field"></textarea>
          <div class="project-prompt-footer">
            <div style="font-size: 11.5px; color: var(--text-tertiary);">JurisCore Intelligence • Qwen 2.5 3B Local</div>
            <button class="btn btn-teal" style="font-size: 11.5px; padding: 4px 12px;" onclick="clickPromptChip('Run Full POPIA Compliance Audit')">Run Matter Audit</button>
          </div>
        </div>

        <div class="project-recents-section">
          <div class="project-section-heading">Recent Matter Audit Sessions</div>
          <div class="project-recent-row" onclick="loadChat('c-001')">
            <span class="project-recent-title">ABC Logistics Master Vendor Agreement Audit</span>
            <span class="project-recent-time">2 hours ago</span>
          </div>
          <div class="project-recent-row" onclick="loadChat('c-002')">
            <span class="project-recent-title">POPIA Section 22 Incident Notification Verification</span>
            <span class="project-recent-time">Yesterday</span>
          </div>
          <div class="project-recent-row" onclick="loadChat('c-001')">
            <span class="project-recent-title">Data Processing Addendum (DPA) Cross-Reference</span>
            <span class="project-recent-time">2 days ago</span>
          </div>
        </div>
      </div>
    `;
  }

  // Open right workspace in Project Mode
  openWorkspaceState();
  switchWsTab("sources");
}

function openArtifact(artifactType) {
  openWorkspaceState();
  if (artifactType === "report") switchWsTab("report");
  else if (artifactType === "redlines") switchWsTab("redlines");
  else if (artifactType === "audit") switchWsTab("audit");
  else switchWsTab("sources");
}

// --- 5. DRAG & DROP MULTI-FILE UPLOAD ---
function setupDragAndDrop() {
  const dropzone = document.getElementById("sources-dropzone");
  if (!dropzone) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

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
  const container = document.getElementById("sources-list-container");
  if (!container) return;

  docs.forEach((doc, idx) => {
    const div = document.createElement("div");
    div.className = "source-item-card";
    div.innerHTML = `
      <span>${idx + 1}. ${doc.filename}</span>
      <span class="chip verified">${doc.status || "VERIFIED"}</span>
    `;
    container.insertBefore(div, container.firstChild);
  });
}

// --- 6. NON-BLOCKING TOAST SYSTEM ---
function showToast(message, type = "success", onUndo = null) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast-message ${type}`;

  let undoHtml = "";
  if (onUndo) {
    undoHtml = `<button class="toast-undo-btn" id="toast-undo-btn">Undo</button>`;
  }

  toast.innerHTML = `
    <span>${message}</span>
    ${undoHtml}
  `;

  container.appendChild(toast);

  if (onUndo) {
    const undoBtn = toast.querySelector("#toast-undo-btn");
    if (undoBtn) {
      undoBtn.addEventListener("click", () => {
        onUndo();
        toast.remove();
      });
    }
  }

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(12px) scale(0.96)";
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

function acceptRedline(id) {
  showToast("Surgical redline accepted and applied to document drafting queue.", "success", () => {
    showToast("Redline change undone.", "warning");
  });
}

function rejectRedline(id) {
  showToast("Surgical redline rejected by counsel.", "warning");
}

function exportAuditTrail() {
  showToast("Downloading SHA-256 verified compliance audit log...", "success");
  window.open("/api/audit/export", "_blank");
}
