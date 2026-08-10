from typing import List, Dict
from src.domain.findings import Finding, SeverityLevel, VerificationStatus
from src.domain.reports import ReviewSummary

class ComplianceScorer:
    """Deterministic score and metrics calculator."""

    SEVERITY_WEIGHTS = {
        SeverityLevel.CRITICAL: 25.0,
        SeverityLevel.HIGH: 15.0,
        SeverityLevel.MEDIUM: 8.0,
        SeverityLevel.LOW: 3.0,
        SeverityLevel.INFO: 0.0
    }

    def calculate_summary(self, total_clauses: int, findings: List[Finding]) -> ReviewSummary:
        high_cnt = 0
        med_cnt = 0
        low_cnt = 0
        deductions = 0.0

        for f in findings:
            if f.severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH):
                high_cnt += 1
            elif f.severity == SeverityLevel.MEDIUM:
                med_cnt += 1
            else:
                low_cnt += 1

            # Only subtract penalty if verified fail or partial compliance
            if f.verification_status in (VerificationStatus.VERIFIED_FAIL, VerificationStatus.PARTIAL_COMPLIANCE, VerificationStatus.CITATION_WRONG_SECTION):
                deductions += self.SEVERITY_WEIGHTS.get(f.severity, 5.0)

        # Baseline score = 100
        score = max(0.0, round(100.0 - deductions, 1))
        passed_cnt = max(0, total_clauses - len(findings))

        return ReviewSummary(
            total_clauses_analyzed=total_clauses,
            passed_count=passed_cnt,
            high_risk_count=high_cnt,
            medium_risk_count=med_cnt,
            low_risk_count=low_cnt,
            compliance_score=score
        )

compliance_scorer = ComplianceScorer()
