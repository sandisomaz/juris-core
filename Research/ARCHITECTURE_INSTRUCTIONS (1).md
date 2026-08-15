# JurisCore — Workspace Evolution Instructions
*For the build agent. Read BRAND.md first — every UI decision below should read as an application of that system, not a fresh set of choices.*

---

## 0. What we're building

JurisCore already has (per README): a supervised agentic graph (Intake → Extraction → Research → Compliance → Verifier → Redline → Escalation), a deterministic rules core with statutory citation validation, and a 3-column review workspace for a single document.

We're evolving the workspace from **"review one document"** to **"drop in a whole matter's worth of documents and work with all of them at once"** — the interaction model of NotebookLM/Gemini Notebook (source list → grounded chat → generated outputs), with the transparency of Claude Cowork (every autonomous action is visible, timestamped, and inspectable) applied to legal documents instead of general knowledge work.

**Reference implementations — study the patterns, don't copy code or UI wholesale:**
- **open-notebook** (github.com/lfnovo/open-notebook) — look at how it structures the source list → notebook → generated-note relationship, and its docs layout (`0-START-HERE` through `7-DEVELOPMENT`) as a model for how JurisCore's own `/docs` should be organized.
- **openwork** (github.com/different-ai/openwork) — look at how it exposes agent actions as an inspectable, permissioned trace (`VISION.md` / `PRINCIPLES.md` / `ARCHITECTURE.md` before any code) — that documentation discipline is worth adopting for JurisCore itself, separate from any UI pattern.

If you have local clones of these under `Research/`, read their actual source for the source-list data model and the trace/activity-feed component structure specifically — those two patterns are the highest-value things to borrow.

---

## 1. Layout — three panels, dark theme, per BRAND.md

```
┌─────────────┬───────────────────────────┬─────────────────┐
│   SOURCES    │        WORKSPACE          │      STUDIO     │
│  (left,      │  (center, primary focus)  │  (right,        │
│   ~280px)    │                           │   ~360px)       │
├─────────────┼───────────────────────────┼─────────────────┤
│ Uploaded     │ Chat, grounded in the     │ Generated        │
│ documents,   │ selected source set, with │ artifacts:       │
│ each with a  │ a document reader below   │ Compliance       │
│ processing   │ or beside it showing      │ Report ·         │
│ status chip  │ clause highlights that    │ Redlines ·       │
│ (queued /    │ citations resolve into    │ Relationship     │
│ processing / │                           │ Map · Audit      │
│ done /       │                           │ Trail            │
│ needs review)│                           │                  │
└─────────────┴───────────────────────────┴─────────────────┘
```

All three panels collapsible/toggleable independently (matches the reference apps' "toggle each section" behavior the founder specifically called out) — a lawyer working through a redline wants Workspace full-width; someone triaging a new intake wants Sources + trace visible.

---

## 2. Sources panel

- **Drag-and-drop multi-file upload** onto the panel itself, not just a button — accept PDF/DOCX in a batch, target the same ballpark as the reference apps (tens of documents per matter, not just one).
- Each source gets a card: filename, doc type (once Intake Agent classifies it), a **status chip** that changes live: `Queued` → `Extracting` → `Researching` → `Checking` → `Needs Review` / `Verified`. This chip is driven by the same agent-trace events described in §4 — don't build a separate status system.
- Clicking a source scopes the Workspace chat to that document (or shift-click to scope to a subset) — this is the "which sources is the AI grounded in" control from the reference pattern.
- Selecting a source shows its extracted clause hierarchy (this already exists per README's Column 1 — reuse it here, don't rebuild).

## 3. Workspace panel

- Chat is always grounded: every claim in a response carries a citation back to `{source_id, clause_id}`. Render citations as small inline mono-styled chips (per BRAND.md §4) that, on click, scroll the reader to and highlight that exact clause.
- Cross-document questions ("does the DPA match what the vendor agreement says about data flows?") need the Research/Compliance agents to reason across multiple sources in one pass — this is new relative to the current single-document flow, and is the main backend lift (§5).
- Never let the chat state an unverified statutory citation as fact. If the Verifier Agent hasn't confirmed it, the response must show the citation with its actual validity state (`VALID`/`OUTDATED`/`WRONG_SECTION`/`UNKNOWN`) inline, colored per BRAND.md §5 — this is the single most important trust signal in the whole product, don't let it get lost in a UI refactor.

## 4. Agent trace (the transparency layer)

- A persistent, filterable activity feed — this can live docked to the Workspace panel or as a slide-out, but it must always be one click away, not buried in a settings page.
- Every agent (Intake, Extraction, Research, Compliance, Verifier, Redline, Escalation) posts a line the moment it starts and the moment it finishes, with duration and a one-line summary ("Verifier: checked 4 citations against POPIA — 3 VALID, 1 WRONG_SECTION"). Stream this via SSE or websocket — don't batch-reveal after the fact, per BRAND.md §7.
- Escalation Agent events should visually interrupt the feed (not just another line) — that's the human-in-the-loop checkpoint and it needs to read as different in kind from routine progress.

## 5. Backend additions

- **Bulk ingestion endpoint** — accept a batch upload, queue each doc independently, expose per-doc job status (this feeds the Sources panel chips).
- **Cross-document reasoning** — Research and Compliance agents need a way to be invoked with a *set* of source IDs instead of one, and to produce findings that reference more than one source (`finding.related_sources: [id, id]`). This is the biggest schema change: findings currently likely assume a single parent document.
- **Citation resolution API** — given `{source_id, clause_id}`, return the exact text span and its position in the reader, so chat citations can click through reliably.
- **Studio artifact generators**, one per output type:
  - *Compliance Report* — already exists in some form per README's `reporting/` module; extend it to span multiple sources.
  - *Redlines* — already exists (Redline Agent); expose as a Studio tab, diff view.
  - *Relationship Map* — new. A JSON graph (`nodes`: clauses/obligations/entities, `edges`: references/dependencies/conflicts between them) that the frontend renders — this is the "mind map for contracts" the founder wants. Keep graph generation on the backend (deterministic, inspectable) and rendering on the frontend (so the graph library can change without touching agent logic).
  - *Audit Trail export* — the existing immutable audit log (README already claims this), exposed as a downloadable, timestamped record — this is a genuine differentiator for a legal audience, don't undersell it in the UI.

## 6. Non-goals for this pass

- Don't build user accounts/multi-tenant billing yet — this is still a portfolio-stage system.
- Don't try to match NotebookLM's exact 50-document ceiling as a hard target — match the *pattern* (bulk upload, per-doc status, grounded chat across many sources), let the real ceiling be whatever the extraction pipeline can actually handle reliably, and surface that limit honestly in the UI rather than silently failing past it.
- Don't reskin Clear Path's soft rounded chat UI into this workspace — BRAND.md §0 explains why that's a deliberate choice, not an oversight.

---

## 7. Suggested build order

1. Sources panel + bulk ingestion + status chips (visible progress first — this alone is a big perceived-quality jump)
2. Agent trace feed wired to real event stream (makes the "autonomous but supervised" claim in the README actually demonstrable)
3. Grounded chat with citation click-through (the core trust mechanic)
4. Cross-document reasoning in Research/Compliance agents
5. Studio panel: Report and Redlines first (already exist, just need to be exposed per-matter instead of per-document), Relationship Map and Audit Trail export after
