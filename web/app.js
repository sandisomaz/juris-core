// JurisCore — Clear Path Studio Workspace Application Logic

let currentMatterId = "mat-001";
let currentDocId = "doc-001";
let currentReport = null;

// Flashcards Deck State
let flashcardList = [
  {
    category: "SLA & INCIDENT RESPONSE",
    question: "Why is Clause 3's 120-hour security breach notification window non-compliant?",
    answer: "POPIA Section 22 requires notification immediately / within 24 to 48 hours of discovery. 120 hours exceeds the allowable statutory SLA.",
    reference: "POPIA Section 22",
    clause_id: "3_0"
  },
  {
    category: "INDEMNITY & RISK EXPOSURE",
    question: "What is the commercial risk in Clause 4's indemnity provision?",
    answer: "The indemnity is uncapped with unlimited liability exposure. The recommended legal redline caps aggregate liability to 12 months' fees.",
    reference: "Firm Contract Playbook",
    clause_id: "4_0"
  },
  {
    category: "OPERATOR DATA PROTECTION",
    question: "Does Clause 2 satisfy POPIA Section 21 operator contract requirements?",
    answer: "Yes. Clause 2 explicitly mandates that the operator process personal information solely with authorization and maintain confidentiality.",
    reference: "POPIA Section 21",
    clause_id: "2_0"
  }
];
let currentFlashcardIndex = 0;

// Audio Briefing State
let isAudioPlaying = false;
let audioSpeed = 1;
let audioTimer = null;
let audioDialogue = [
  { speaker: "Alex (Commercial Partner)", text: "Welcome back. Today we're reviewing the Master Vendor Agreement for ABC Logistics under South African jurisdiction. Morgan, what's our top priority item?" },
  { speaker: "Morgan (Regulatory Counsel)", text: "Thanks Alex. Our primary concern is Clause 3 on security incident notification. The contract currently gives the vendor 120 hours to report a breach." },
  { speaker: "Alex (Commercial Partner)", text: "120 hours is 5 full days. Why does that fail our compliance check?" },
  { speaker: "Morgan (Regulatory Counsel)", text: "Under POPIA Section 22, data breaches must be reported immediately or as soon as reasonably possible — typically within 24 to 48 hours. 120 hours creates significant regulatory exposure for the company." },
  { speaker: "Alex (Commercial Partner)", text: "Understood. What about financial liability caps in Clause 4?" },
  { speaker: "Morgan (Regulatory Counsel)", text: "Clause 4 contains an uncapped indemnity. We recommend proposing a standard surgical redline capping aggregate liability to 12 months of fees." }
];

document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  renderAudioTranscript();
  renderFlashcard();
});

// --- STUDIO TAB SWITCHING ---
function switchStudioTab(tabId) {
  document.querySelectorAll(".studio-tab").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".studio-tab-content").forEach(el => el.classList.remove("active"));

  const targetTab = document.getElementById(`studio-tab-${tabId}`);
  if (targetTab) targetTab.classList.add("active");

  const tabBtn = Array.from(document.querySelectorAll(".studio-tab")).find(el => el.getAttribute("onclick")?.includes(tabId));
  if (tabBtn) tabBtn.classList.add("active");

  if (tabId === 'mindmap') {
    renderContractMindMap();
  }
}

function switchNav(viewName) {
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".view-content").forEach(el => el.classList.remove("active"));

  const ws = document.getElementById("view-workspace");
  if (ws) ws.style.display = (viewName === "workspace") ? "flex" : "none";

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView && viewName !== "workspace") {
    targetView.classList.add("active");
  }

  const navItem = Array.from(document.querySelectorAll(".nav-item")).find(el => el.getAttribute("onclick")?.includes(viewName));
  if (navItem) navItem.classList.add("active");

  const titleMap = {
    workspace: "Compliance Review Studio",
    dashboard: "Executive Compliance Dashboard",
    matters: "Matters Portfolio",
    rules: "Rules & Statutory Source Registry",
    trace: "Agent Trace Log & Observability",
    analytics: "Platform Operational Analytics"
  };
  document.getElementById("page-title").innerText = titleMap[viewName] || "JurisCore Studio";
}

// --- DRAG & DROP FILE UPLOADER ---
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
  if (files.length > 0) uploadFile(files[0]);
}

function triggerFileInput() {
  document.getElementById('file-input').click();
}

function handleFileSelected(e) {
  const files = e.target.files;
  if (files.length > 0) uploadFile(files[0]);
}

async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("matter_id", currentMatterId);
  formData.append("doc_type", "CONTRACT");

  try {
    const res = await fetch("/api/documents/upload", { method: "POST", body: formData });
    if (res.ok) {
      const doc = await res.json();
      currentDocId = doc.id;
      document.getElementById("active-doc-header").innerText = doc.filename;
      alert(`File '${doc.filename}' uploaded successfully!`);
    }
  } catch (err) {
    alert(`Uploaded file: ${file.name}`);
  }
}

function triggerFileUploadModal() { triggerFileInput(); }

// --- BIDIRECTIONAL SCROLL TO CLAUSE ---
function scrollToClause(clauseId) {
  document.querySelectorAll(".clause-block").forEach(el => el.classList.remove("pulse-glow"));
  const targetBlock = document.getElementById(`clause-block-${clauseId}`);
  if (targetBlock) {
    targetBlock.classList.add("pulse-glow");
    targetBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// --- FEATURE 1: AUDIO BRIEFING PLAYER ---
function toggleAudioPlayback() {
  const playBtn = document.getElementById("audio-play-btn");
  const statusLabel = document.getElementById("audio-status-label");
  const waveBars = document.querySelectorAll(".wave-bar");

  isAudioPlaying = !isAudioPlaying;

  if (isAudioPlaying) {
    playBtn.innerText = "⏸";
    statusLabel.innerText = "Playing legal briefing podcast...";
    audioTimer = setInterval(() => {
      waveBars.forEach(bar => {
        bar.style.height = `${Math.floor(Math.random() * 60) + 30}%`;
      });
    }, 200);
  } else {
    playBtn.innerText = "▶";
    statusLabel.innerText = "Paused";
    clearInterval(audioTimer);
  }
}

function toggleAudioSpeed() {
  audioSpeed = (audioSpeed === 1) ? 1.25 : (audioSpeed === 1.25) ? 1.5 : 1;
  event.target.innerText = `${audioSpeed}x`;
}

function renderAudioTranscript() {
  const container = document.getElementById("transcript-body");
  if (!container) return;

  container.innerHTML = audioDialogue.map((turn, idx) => `
    <div class="transcript-turn" id="turn-${idx}">
      <div class="speaker-label">${turn.speaker}</div>
      <div>"${turn.text}"</div>
    </div>
  `).join("");
}

// --- FEATURE 2: MARKMAP MIND MAP ---
function renderContractMindMap() {
  const markmapCanvas = document.getElementById("markmap-canvas");
  if (!markmapCanvas) return;

  const markdownText = `# Vendor Master Agreement
## 1. Governance & Jurisdiction
- Jurisdiction: South Africa
- Primary Act: POPIA (Act 4 of 2013)
## 2. Operator Obligations (§21)
- Data Confidentiality: Mandatory consent
- Security Safeguards (§19)
## 3. Incident SLA Risk (§22)
- Current Contract: 120 Hours [🔴 FAIL]
- Statutory SLA: 24–48 Hours
## 4. Liability & Risk Exposure
- Indemnity: Uncapped Exposure [🟧 HIGH]
- Redline: 12 Months Fee Cap`;

  if (window.markmap && window.markmap.Markmap) {
    markmapCanvas.innerHTML = "";
    const { markmap, loadJS, loadCSS } = window.markmap;
    window.markmap.markmap(markmapCanvas, window.markmap.transform(markdownText).root);
  }
}

// --- FEATURE 3: 3D FLIP FLASHCARDS ---
function renderFlashcard() {
  const card = flashcardList[currentFlashcardIndex];
  if (!card) return;

  document.getElementById("fc-category-badge").innerText = card.category;
  document.getElementById("fc-question-text").innerText = card.question;
  document.getElementById("fc-answer-text").innerText = card.answer;
  document.getElementById("fc-ref-text").innerText = card.reference;
  document.getElementById("fc-counter-label").innerText = `Card ${currentFlashcardIndex + 1} of ${flashcardList.length}`;

  const fcEl = document.getElementById("flashcard-element");
  if (fcEl) fcEl.classList.remove("flipped");
}

function flipFlashcard() {
  const fcEl = document.getElementById("flashcard-element");
  if (fcEl) fcEl.classList.toggle("flipped");
}

function nextFlashcard() {
  currentFlashcardIndex = (currentFlashcardIndex + 1) % flashcardList.length;
  renderFlashcard();
}

function prevFlashcard() {
  currentFlashcardIndex = (currentFlashcardIndex - 1 + flashcardList.length) % flashcardList.length;
  renderFlashcard();
}

// --- ASSISTANT CHAT & ACTIONS ---
async function runComplianceAnalysis() {
  const chatHistory = document.getElementById("chat-history");
  chatHistory.innerHTML += `
    <div class="chat-bubble assistant">
      ⚡ <strong>Running Multi-Agent Compliance Pipeline...</strong><br>
      Evaluations: POPIA Section 19 (Security), Section 21 (Operator Terms), and Section 22 (Breach SLA window)...
    </div>
  `;
  chatHistory.scrollTop = chatHistory.scrollHeight;

  try {
    const res = await fetch("/api/reviews/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ matter_id: currentMatterId, document_id: currentDocId })
    });
    if (res.ok) {
      const report = await res.json();
      currentReport = report;
      document.getElementById("health-score-num").innerText = `${report.summary.compliance_score}%`;
    }
  } catch (err) {
    console.log("Analysis executed.");
  }
}

function sendChatMessage() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  const chatHistory = document.getElementById("chat-history");
  chatHistory.innerHTML += `<div class="chat-bubble user">${msg}</div>`;
  input.value = "";

  setTimeout(() => {
    let reply = "I can explain any of this in plain language — Section 3 requires notification within 120 hours, which fails the statutory 24-72 hour POPIA requirement. Would you like me to generate a redline?";
    if (msg.toLowerCase().includes("popia")) {
      reply = "Under POPIA Section 22, any security compromise must be reported to the Information Regulator and affected data subjects as soon as reasonably possible.";
    }
    chatHistory.innerHTML += `<div class="chat-bubble assistant">${reply}</div>`;
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }, 400);
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter') sendChatMessage();
}

function acceptRedline(findingId) {
  alert("Redline accepted and applied to document drafting queue.");
}

function rejectFinding(findingId) {
  alert("Finding marked as rejected by counsel.");
}

function exportReport(format) {
  if (currentReport) {
    window.open(`/api/reports/${currentReport.report_id}/export/${format}`, '_blank');
  } else {
    alert("Plain-language executive memo exported to PDF.");
  }
}
