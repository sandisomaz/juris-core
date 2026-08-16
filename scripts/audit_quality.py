import os
import sys
import json
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.llm_bridge import llm_bridge

MODELS = [
    "qwen2.5:1.5b",
    "qwen2.5:3b",
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:3b",
    "llama3.2:latest"
]

TEST_SCENARIOS = [
    {
        "name": "Scenario 1: Uncapped Liability",
        "rule": "The indemnity obligation must contain a monetary cap or limitation of liability.",
        "clause": "The Service Provider shall indemnify, defend, and hold harmless the Client against any and all claims, demands, liabilities, losses, costs, and expenses arising out of any breach of warranty or willful misconduct under this Agreement."
    },
    {
        "name": "Scenario 2: Cross-Border Data Transfer (POPIA s72)",
        "rule": "Personal information transfer outside South Africa requires data subject consent or adequate legal protection in recipient jurisdiction under POPIA s72.",
        "clause": "The Vendor may at its discretion transfer, store, and process Personal Data in servers located in third countries outside the Republic of South Africa without prior notice to the Customer."
    }
]

def run_quality_audit():
    print("=" * 80)
    print("JURISCORE LEGAL LLM QUALITY AUDIT")
    print("=" * 80)

    system_prompt = (
        "You are an expert legal AI compliance agent. You must review the provided clause and determine if it violates the specified rule. "
        "Return ONLY a JSON object with keys: 'violation_found' (boolean), 'reasoning' (string), and 'suggested_redline' (string)."
    )

    for scenario in TEST_SCENARIOS:
        print(f"\n\n### {scenario['name']} ###")
        print(f"Rule: {scenario['rule']}")
        print(f"Clause: \"{scenario['clause']}\"\n")
        print("-" * 80)

        for model_name in MODELS:
            llm_bridge.model = model_name
            user_prompt = f"Rule: {scenario['rule']}\nClause Text: {scenario['clause']}"
            
            try:
                resp = llm_bridge.query(system_prompt, user_prompt, expect_json=True)
                print(f"\n[MODEL: {model_name}]")
                print(f"  * Violation Found : {resp.get('violation_found')}")
                print(f"  * Reasoning        : {resp.get('reasoning')}")
                print(f"  * Suggested Redline: {resp.get('suggested_redline')}")
            except Exception as e:
                print(f"\n[MODEL: {model_name}] - ERROR: {e}")
            print("-" * 40)

if __name__ == "__main__":
    run_quality_audit()
