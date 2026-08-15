// JurisCore — Two-State Shell Interaction Logic

let isWorkspaceOpen = false;
let isRailCollapsed = false;
let currentMatterId = "m-001";

document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  renderRelationshipMap();
});

// --- 1. TWO LAYOUT STATES LOGIC ---
function openWorkspaceState() {
  if (isWorkspaceOpen) return;
  isWorkspaceOpen = true;

  // Auto-collapse Left Rail to icon-only (~56px) to free width for Workspace
  const rail = document.getElementById("nav-rail");
  if (rail) rail.classList.add("collapsed");
  isRailCollapsed = true;

  // Slide open 3rd Workspace Column
  const wsCol = document.getElementById("right-workspace-column");
  if (wsCol) wsCol.classList.remove("hidden");

  // Update Top Badge
  const badge = document.getElementById("layout-state-badge");
  if (badge) badge.innerText = "WORKSPACE STATE (3 COLUMNS)";

  renderRelationshipMap();
}

function closeWorkspaceState() {
  isWorkspaceOpen = false;
  const wsCol = document.getElementById("right-workspace-column");
  if (wsCol) wsCol.classList.add("hidden");

  const badge = document.getElementById("layout-state-badge");
  if (badge) badge.innerText = "CONVERSATION STATE (2 COLUMNS)";
}

function toggleWorkspaceColumn() {
  if (isWorkspaceOpen) {
    closeWorkspaceState();
  } else {
    openWorkspaceState();
  }
}

function toggleRail() {
  const rail = document.getElementById("nav-rail");
  if (!rail) return;
  rail.classList.toggle("collapsed");
  isRailCollapsed = rail.classList.contains("collapsed");
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

  if (tabId === "mindmap") {
    renderRelationshipMap();
  }
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
  text.innerText = `🧠 EVALUATING LEGAL COMPLIANCE: ${taskName.toUpperCase()}...`;

  const time = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  div.className = "thinking-step-line active-agent";
  div.innerHTML = `📁 <b>Step:</b> Processing multi-step task for ${taskName}...`;
  if (feed) {
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  }

  setTimeout(() => {
    dot.classList.remove("active");
    text.innerText = `✓ COMPLIANCE CHECK COMPLETED FOR: ${taskName.toUpperCase()}`;
  }, 2200);
}

function toggleThinkingExpand() {
  const feed = document.getElementById("thinking-steps-feed");
  const arrow = document.getElementById("thinking-toggle-arrow");
  if (!feed || !arrow) return;

  if (feed.style.display === "none") {
    feed.style.display = "block";
    arrow.innerText = "▲ Collapse Steps";
  } else {
    feed.style.display = "none";
    arrow.innerText = "▼ Expand Steps";
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
    let reply = `I have processed your query. I've verified that Clause 3.0 requires notification within 120 hours, which exceeds statutory POPIA §22 requirements <span class="cite wrong" onclick="openWorkspaceTab('sources', '3_0')">POPIA §22 · WRONG_SECTION</span>.`;
    
    chatStream.innerHTML += `
      <div class="msg ai">
        <div class="ai-body">
          ${reply}
          <div class="chat-attachment-card" onclick="openWorkspaceTab('report')">
            <span class="attachment-icon">📄</span>
            <div>
              <div class="attachment-title">Executive Compliance Memorandum v1.pdf</div>
              <div class="attachment-sub">Click to inspect matter compliance report & findings</div>
            </div>
          </div>
        </div>
      </div>
    `;
    chatStream.scrollTop = chatStream.scrollHeight;
  }, 400);
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter') sendChatMessage();
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

function acceptRedline(id) {
  alert("Surgical redline accepted and applied to document drafting queue.");
}

function rejectRedline(id) {
  alert("Redline rejected by counsel.");
}

function exportAuditTrail() {
  window.open("/api/audit/export", "_blank");
}
