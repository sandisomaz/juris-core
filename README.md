# ⚖️ JurisCore

> A human-in-the-loop legal and regulatory intelligence platform combining agentic AI, deterministic rules, retrieval, workflow automation, and continuous compliance monitoring.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Orchestration](https://img.shields.io/badge/Orchestration-Supervised_Agentic_Graph-orange.svg)
![Database](https://img.shields.io/badge/Database-SQLite%2FPostgreSQL-blue.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

---

## 📌 Core Principle
> **"LLMs interpret and draft. Deterministic code verifies. Humans approve consequential decisions."**

JurisCore is designed for law firms, enterprise in-house legal teams, compliance officers, and ALSPs. It ingests contracts, policies, and vendor onboarding packs; extracts relevant obligations; checks them against a deterministic legal rules engine; and produces structured compliance reports with statutory citations, confidence metrics, recommended actions, redlines, and human-review checkpoints.

---

## 🏗 System Architecture

```text
                         USER / CLIENT
                  Lawyer • Compliance • GC
                              │
                              ▼
                  ┌────────────────────────┐
                  │     WEB APPLICATION    │
                  │ Dashboard • Matters    │
                  │ Review Workspace       │
                  │ Trace Log • Analytics  │
                  └────────────┬───────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │       API GATEWAY      │
                  │ Auth • RBAC • Jobs     │
                  │ Validation • Audit     │
                  └────────────┬───────────┘
                               │
                               ▼
            ┌─────────────────────────────────────┐
            │        WORKFLOW ORCHESTRATOR        │
            │                                     │
            │              SUPERVISOR             │
            │                 │                   │
            │     ┌───────────┼───────────┐       │
            │     ▼           ▼           ▼       │
            │ EXTRACTOR    ANALYST     RESEARCHER │
            │     │           │           │       │
            │     └───────────┼───────────┘       │
            │                 ▼                   │
            │           RULES ENGINE              │
            │                 │                   │
            │                 ▼                   │
            │            VERIFICATION             │
            │                 │                   │
            │       ┌─────────┴─────────┐         │
            │       ▼                   ▼         │
            │  HUMAN REVIEW          FINALIZE     │
            └─────────────────────────────────────┘
                               │
                  ┌────────────┼────────────┐
                  ▼            ▼            ▼
             PostgreSQL    Vector DB    Object Store
```

---

## 🚀 Key Features

1. **3-Column Interactive Review Workspace**:
   - **Column 1**: Document Structure DOM & Clause Hierarchy.
   - **Column 2**: Interactive Document Reader with clause selection & highlights.
   - **Column 3**: AI Risk Findings with legal basis, statutory source verification, confidence score, and Human-in-the-Loop approval buttons.

2. **Deterministic Rules Core**:
   - Legal Source Registry (e.g. POPIA Act 4 of 2013, Companies Act 71 of 2008, GDPR).
   - Statutory Citation Validator (`VALID`, `OUTDATED`, `WRONG_SECTION`, `UNKNOWN`).
   - Hard business rule checks (breach notification SLA timelines, numeric thresholds, mandatory privacy clauses).

3. **Supervised Agentic Graph**:
   - **Intake Agent**: Document classification & jurisdiction detection.
   - **Extraction Agent**: Spatial clause boundary & DOM tree extraction.
   - **Research Agent**: Legislation & internal precedent retrieval.
   - **Compliance Agent**: Contractual obligation interpretation.
   - **Verifier Agent**: Statutory citation & rule verification node.
   - **Redline Agent**: Proposes surgical text redlines preserving commercial intent.
   - **Escalation Agent**: Detects ambiguity/uncertainty and routes to human review.

4. **Auditability & Observability**:
   - Full agent execution trace viewer displaying latency, step logs, and state transitions.
   - Immutable audit trail recording every human approval, rejection, or edit.

---

## 🛠 Quick Start

### 1. Prerequisites
- Python 3.11+

### 2. Installation
```bash
git clone https://github.com/your-org/juris-core.git
cd juris-core
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Running the Server
```bash
python -m uvicorn src.main:app --reload --port 8000
```
Open your browser at `http://localhost:8000/` to access the JurisCore Web Application and Workspace.

---

## 🧪 Testing

Run the automated test suite covering rules, citation validation, layout segmentation, and multi-agent graph workflows:

```bash
pytest tests/ -v
```

---

## 📁 Repository Structure

```text
juris-core/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py                 # FastAPI Web Server & Router Registry
│   ├── api/                    # REST API Endpoints
│   ├── core/                   # Security, Settings & Database configuration
│   ├── domain/                 # Domain Schemas (Pydantic v2)
│   ├── deterministic/          # Rules Engine, Citation Validator & Legal Source Registry
│   ├── documents/              # Document Parser, Validator & Segmenter
│   ├── retrieval/              # Hybrid Search & Source Provenance
│   ├── agents/                 # Supervised Multi-Agent Orchestrator
│   └── reporting/              # PDF, HTML, JSON & Redline Generators
├── web/                        # Enterprise Dark-Mode SPA & 3-Column Review Workspace
├── tests/                      # Pytest Test Suite
└── samples/                    # Benchmark Contract Corpus
```
