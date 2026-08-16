import time
from src.agents.state import WorkflowState
from src.domain.audit import AgentStepTrace
from src.core.llm_bridge import llm_bridge


class RedlineAgent:
    """Redline Drafting Agent: Generates precise, surgical replacement language for legal findings."""

    def _draft_redline_with_llm(self, issue: str, explanation: str, clause_text: str) -> str:
        system_prompt = (
            "You are an expert contract lawyer. Draft a surgical, commercially reasonable redline "
            "clause that resolves the specified compliance issue while preserving the remaining "
            "commercial terms of the clause. Return ONLY a JSON object: "
            '{"redline": "The amended clause text here..."}'
        )
        user_prompt = (
            f"Compliance Issue: {issue}\n"
            f"Legal Analysis: {explanation}\n"
            f"Original Clause Text:\n{clause_text}"
        )
        result = llm_bridge.query(system_prompt, user_prompt, expect_json=True)
        if "error" not in result and "redline" in result:
            return result["redline"]
        return ""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        redline_count = 0

        clause_map = {c.clause_id: c.text for c in state.clauses}

        for finding in state.final_findings:
            # If finding already has a specific redline, keep it
            if finding.redline and len(finding.redline.strip()) > 0:
                redline_count += 1
            else:
                # Use LLM to generate custom surgical redline
                clause_text = clause_map.get(finding.clause_id or "", "")
                drafted = self._draft_redline_with_llm(
                    issue=finding.issue,
                    explanation=finding.explanation,
                    clause_text=clause_text
                )
                if drafted:
                    finding.redline = drafted
                    redline_count += 1

        state.current_step = "REDLINES_DRAFTED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="RedlineAgent",
            action_summary=f"Prepared {redline_count} surgical redline proposals preserving commercial intent.",
            duration_ms=round(duration, 2),
            details={"redline_count": redline_count}
        ))
        return state


redline_agent = RedlineAgent()
