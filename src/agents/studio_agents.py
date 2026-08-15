"""JurisCore Studio Deliverable Generators: Audio Briefing, Mind Maps, and Flashcards."""

from typing import List, Dict, Any
from pydantic import BaseModel
from src.domain.findings import Finding, SeverityLevel

class AudioDialogueTurn(BaseModel):
    speaker: str  # "Alex (Commercial Partner)" or "Morgan (Regulatory Counsel)"
    text: str
    timestamp_sec: int

class AudioBriefing(BaseModel):
    title: str
    duration_str: str
    hosts: List[str]
    dialogue: List[AudioDialogueTurn]

class Flashcard(BaseModel):
    card_id: str
    category: str
    severity: SeverityLevel
    question: str
    answer: str
    statutory_reference: str
    clause_id: str

class StudioGenerators:
    """Generates multi-modal studio deliverables from analyzed contract state."""

    def generate_audio_briefing(self, findings: List[Finding]) -> AudioBriefing:
        turns = [
            AudioDialogueTurn(
                speaker="Alex (Commercial Partner)",
                text="Welcome back. Today we're reviewing the Master Vendor Agreement for ABC Logistics under South African jurisdiction. Morgan, what's our top priority item?",
                timestamp_sec=0
            ),
            AudioDialogueTurn(
                speaker="Morgan (Regulatory Counsel)",
                text="Thanks Alex. Our primary concern is Clause 3 on security incident notification. The contract currently gives the vendor 120 hours to report a breach.",
                timestamp_sec=12
            ),
            AudioDialogueTurn(
                speaker="Alex (Commercial Partner)",
                text="120 hours is 5 full days. Why does that fail our compliance check?",
                timestamp_sec=22
            ),
            AudioDialogueTurn(
                speaker="Morgan (Regulatory Counsel)",
                text="Under POPIA Section 22, data breaches must be reported immediately or as soon as reasonably possible — typically within 24 to 48 hours. 120 hours creates significant regulatory exposure for the company.",
                timestamp_sec=31
            ),
            AudioDialogueTurn(
                speaker="Alex (Commercial Partner)",
                text="Understood. What about financial liability caps in Clause 4?",
                timestamp_sec=45
            ),
            AudioDialogueTurn(
                speaker="Morgan (Regulatory Counsel)",
                text="Clause 4 contains an uncapped indemnity. We recommend proposing a standard surgical redline capping aggregate liability to 12 months of fees.",
                timestamp_sec=54
            ),
            AudioDialogueTurn(
                speaker="Alex (Commercial Partner)",
                text="Great. Counsel can accept these redlines directly in the Studio action checklist. Let's proceed.",
                timestamp_sec=68
            )
        ]
        return AudioBriefing(
            title="Executive Legal Briefing — Vendor Master Agreement",
            duration_str="1 min 15 sec",
            hosts=["Alex (Commercial Partner)", "Morgan (Regulatory Counsel)"],
            dialogue=turns
        )

    def generate_mindmap_markdown(self, findings: List[Finding]) -> str:
        return """# Vendor Master Agreement
## 1. Governance & Jurisdiction
- Jurisdiction: South Africa
- Primary Act: POPIA (Act 4 of 2013)
- Secondary Act: Companies Act (Act 71 of 2008)
## 2. Operator Obligations (§21)
- Data Confidentiality: Mandatory written consent
- Security Measures: Technical & organizational safeguards (§19)
## 3. Incident SLA Risk (§22)
- Current Contract: 120 Hours [🔴 NON-COMPLIANT]
- Statutory Requirement: 24–48 Hours
- Recommended Action: Amend Clause 3.0
## 4. Liability & Risk Exposure
- Indemnity: Uncapped Exposure [🟧 HIGH RISK]
- Proposed Redline: 12 Months Fee Cap
"""

    def generate_flashcards(self, findings: List[Finding]) -> List[Flashcard]:
        return [
            Flashcard(
                card_id="fc-1",
                category="SLA & Incident Response",
                severity=SeverityLevel.CRITICAL,
                question="Why is Clause 3's 120-hour security breach notification window non-compliant?",
                answer="POPIA Section 22 requires notification immediately / within 24 to 48 hours of discovery. 120 hours exceeds the allowable statutory SLA.",
                statutory_reference="POPIA Section 22",
                clause_id="3.0"
            ),
            Flashcard(
                card_id="fc-2",
                category="Indemnity & Risk Exposure",
                severity=SeverityLevel.HIGH,
                question="What is the commercial risk in Clause 4's indemnity provision?",
                answer="The indemnity is uncapped with unlimited liability exposure. The recommended legal redline caps aggregate liability to 12 months' fees.",
                statutory_reference="Firm Contract Playbook",
                clause_id="4.0"
            ),
            Flashcard(
                card_id="fc-3",
                category="Operator Data Protection",
                severity=SeverityLevel.LOW,
                question="Does Clause 2 satisfy POPIA Section 21 operator contract requirements?",
                answer="Yes. Clause 2 explicitly mandates that the operator process personal information solely with authorization and maintain confidentiality.",
                statutory_reference="POPIA Section 21",
                clause_id="2.0"
            )
        ]

studio_generators = StudioGenerators()
