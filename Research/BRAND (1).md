# JurisCore — Brand Bible
*v1.0 · extends the Clear Path system · for the build agent and any human reading over its shoulder*

---

## 0. Why this isn't just "Clear Path with a new logo"

Clear Path was designed for one specific person: someone with no legal background — the brief literally named children and seniors as the accessibility floor — uploading one contract and needing it translated into plain language. Soft rounded cards, warm white, a friendly chat bubble mascot. That was the right call *for that user*.

JurisCore's actual user, per your own README, is a lawyer, compliance officer, GC, or ALSP analyst reviewing dozens of contracts at once, who wants density, precision, and proof — not onboarding warmth. That's a different job, so it gets its own visual register. But it's the *same brand* — this isn't two colour systems, it's one. JurisCore uses the exact Clear Path palette (Wayfinder navy, Trailhead teal, Paper, Blaze, Stop, Clear — see §5), with the professional workspace built as a **dark surface derived from Wayfinder navy itself**, not a separate unrelated graphite scale. Someone moving between a Clear Path screen and a JurisCore screen should feel one company, two rooms — not two companies.

What does change between the two: layout density, copy register (JurisCore doesn't explain what a DPA is — this audience already knows), and shape language (JurisCore's panels are square-cornered and tight; Clear Path's cards stay soft and rounded). Colour is the thread that stays constant.

If you ever build the citizen-facing / SME side of this product, Clear Path's system is sitting there ready — don't merge the two.

---

## 1. Positioning

**One-liner:** LLMs interpret and draft. Deterministic code verifies. Humans approve consequential decisions.

**Audience:** law firms, ALSPs, in-house legal/compliance teams, GCs — people who already know what a DPA is and want to know *which clause*, *which statute section*, *how confident*, and *who signed off*.

**Personality:** Precise. Unhurried authority. Shows its work instead of asking to be trusted. Never states a citation it hasn't verified.

**The one sentence a recruiter should think looking at this:** *this person understands both the law and how to build a system that doesn't lie to a lawyer.*

---

## 2. Naming

- **JurisCore** — the platform. Always the full word, never "Juris" or "JC" in UI copy.
- Internal agent names (Intake, Extraction, Research, Compliance, Verifier, Redline, Escalation) are proper nouns in the trace log — capitalize them, they're characters in the audit trail, not generic labels.

---

## 3. Mark

Same shield-and-speech-bubble mark as Clear Path (protection + resolution + "this talks back to you"), redrawn for dark, dense UI: thinner stroke, no fill, Paper for the outline, Trailhead teal for the check — the exact same two colours doing the exact same jobs as on the light Clear Path mark.

```svg
<svg width="40" height="40" viewBox="0 0 64 64" fill="none">
  <path d="M32 6 L52 14 V30 C52 44 43 53 32 58 C21 53 12 44 12 30 V14 L32 6Z"
        stroke="#FAF9FD" stroke-width="2" stroke-linejoin="round" fill="none"/>
  <path d="M23 31 L29 37 L41 24"
        stroke="#006A63" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>
```

Drop the speech-bubble tail entirely at product-icon scale — it reads as a shield-check, which is correct here. The tail is a Clear-Path-specific detail for a chat mascot; JurisCore isn't a chat mascot.

---

## 4. Typography

| Role | Face | Notes |
|---|---|---|
| Wordmark / section eyebrows only | Newsreader, italic, small sizes | The one warm touch left from Clear Path — used sparingly, never for UI copy or data |
| UI / body / everything the user reads to make a decision | Atkinson Hyperlegible Next | Kept from Clear Path — legibility is not audience-specific, and dense contract text benefits from it more than most content does |
| Citations, clause refs, statute sections, confidence scores, timestamps, agent trace | IBM Plex Mono | New for JurisCore. This is a data-dense tool; give data its own register so it's visually distinct from prose at a glance |

No new sizes — reuse Clear Path's scale (headline-lg 32/700, headline-md 24/700, body-md 18/400, label-lg 18/600) so the two systems stay compatible if screens are ever shared.

---

## 5. Colour System

Same six named colours as Clear Path, no new hues invented. Your README calls for an "Enterprise Dark-Mode SPA" — so instead of a second unrelated dark palette, the workspace's dark surfaces are **built by darkening Wayfinder navy itself**, the way you'd dim the lights in the same room rather than move to a different building.

**The six brand colours (identical hex values to Clear Path):**

| Name | Hex | Role |
|---|---|---|
| Wayfinder (navy) | `#002045` | Structure, chrome, headers — and now also the seed for every dark workspace surface below |
| Trailhead (teal) | `#006A63` | Every interactive element, every "verified" state, the assistant/agent identity colour — light mode or dark |
| Paper | `#FAF9FD` | Light-mode background, and text-on-dark in the workspace |
| Blaze | `#C6955E` | Pending / in-progress / `OUTDATED` |
| Stop | `#BA1A1A` | Violations, `WRONG_SECTION` — nothing else |
| Clear | `#146C2E` | All-clear findings, `VALID` |

**Workspace dark surfaces — derived from Wayfinder, not a new palette:**

| Token | Hex | Role |
|---|---|---|
| `workspace-bg` | `#041531` | Wayfinder, darkened — base surface of the dark workspace |
| `workspace-surface` | `#0B2A52` | Cards, panels — Wayfinder, lightened one step |
| `workspace-surface-raised` | `#123765` | Active/selected panel state |
| `workspace-border` | `#1F4270` | Hairlines |
| `workspace-text-secondary` | `#9FB0C8` | Labels/metadata — a desaturated tint of Wayfinder, not a generic grey |

**Citation validity states** — the states your README defines (`VALID`, `OUTDATED`, `WRONG_SECTION`, `UNKNOWN`) map directly onto the six brand colours, so a status never needs a colour Clear Path doesn't already use:

| State | Colour | Hex |
|---|---|---|
| `VALID` | Clear | `#146C2E` |
| `OUTDATED` | Blaze | `#C6955E` |
| `WRONG_SECTION` | Stop | `#BA1A1A` |
| `UNKNOWN` | Workspace text-secondary | `#9FB0C8` |

Note: `VALID` uses Clear rather than Trailhead teal — Trailhead stays reserved for interactive/identity so it never gets confused with a status. On the darkened workspace surfaces, Stop and Clear may need a touch more weight (bold text, not just colour) to hold WCAG contrast — don't shift the hex, add emphasis instead.

Same colour rule as Clear Path, unchanged: status colour always ships with an icon and a word, never colour alone.

---

## 6. Voice

Same discipline as Clear Path — translate jargon, cite the source, never bluff confidence — pitched at someone who already knows the field:

- **Don't** explain what a DPA is. **Do** say exactly which section is missing it and why this vendor relationship triggers the requirement.
- **Don't** say "compliance check passed." **Do** say "3 of 3 conditions verified against POPIA s.19–25, citations confirmed VALID."
- **Don't** hide uncertainty behind confident language. **Do** say "Citation confidence: 0.71 — recommend human review" when it's genuinely not sure. This audience will trust the tool *more* for admitting it, not less.

---

## 7. Motion

Clear Path's "trail" concept becomes JurisCore's **agent trace** — the same idea (show the steps, don't hide them behind a spinner), reframed as a live processing pipeline instead of a friendly journey:

- Each agent (Intake → Extraction → Research → Compliance → Verifier → Redline → Escalation) posts a line to the trace feed the moment it starts and finishes — never batch-reveal the whole trace at once, that reads as fake.
- No spinners. A step in progress gets a slow pulse on its status dot, same principle as Clear Path's "pin bobs, it doesn't spin."
- Citations resolve into the document reader with a brief highlight-and-settle, never a hard jump-scroll.
