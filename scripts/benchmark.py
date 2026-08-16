import os
import subprocess
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.llm_bridge import llm_bridge
from src.agents.compliance_agent import compliance_agent
from src.agents.state import WorkflowState
from src.domain.documents import Clause

MODELS_TO_TEST = [
    "qwen2.5:3b",
    "qwen2.5:1.5b",
    "qwen2.5-coder:3b",
    "qwen2.5-coder:1.5b",
    "qwen3.5:4b",
    "qwen3.5:2b",
    "qwen3.5:0.8b",
    "qwen3:4b",
    "qwen3:1.7b",
    "llama3.2:latest",
    "llama3.2:1b"
]

DEFAULT_BENCHMARK_SECONDS = int(os.getenv("BENCHMARK_DURATION_SECONDS", "600"))
BENCHMARK_PAUSE_SECONDS = float(os.getenv("BENCHMARK_PAUSE_SECONDS", "0.5"))


def run_ollama_command(args):
    try:
        result = subprocess.run(["ollama", *args], capture_output=True, text=True, timeout=60)
        return result
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_active_ollama_models():
    result = run_ollama_command(["ps"])
    if not result or result.returncode != 0:
        return []

    active_models = []
    lines = result.stdout.strip().splitlines()
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        model_name = stripped.split()[0]
        if model_name and model_name != "NAME":
            active_models.append(model_name)
    return active_models


def stop_model(model_name):
    if not model_name:
        return
    result = run_ollama_command(["stop", model_name])
    if result is not None and result.returncode != 0:
        print(f"  Warning: could not stop {model_name}: {result.stderr.strip() or result.stdout.strip()}")


def enforce_single_active_model(target_model: str):
    active_models = get_active_ollama_models()
    for model_name in active_models:
        if model_name != target_model:
            print(f"  Evicting active model {model_name} before testing {target_model}...")
            stop_model(model_name)


def summarize_latencies(latencies):
    if not latencies:
        return {
            "min": 0.0,
            "median": 0.0,
            "max": 0.0,
            "avg": 0.0,
        }

    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)
    midpoint = n // 2

    if n % 2 == 0:
        median = (sorted_latencies[midpoint - 1] + sorted_latencies[midpoint]) / 2
    else:
        median = sorted_latencies[midpoint]

    return {
        "min": min(sorted_latencies),
        "median": median,
        "max": max(sorted_latencies),
        "avg": sum(sorted_latencies) / n,
    }


def load_sample_document():
    doc_path = Path(__file__).parent.parent / "samples" / "sample_supplier_agreement.txt"
    if not doc_path.exists():
        print(f"Sample not found: {doc_path}")
        return None
    with open(doc_path, "r", encoding="utf-8") as f:
        return f.read()


def benchmark_model(model: str, text: str, test_clause: Clause, duration_seconds: int):
    llm_bridge.set_model(model)
    deadline = time.monotonic() + duration_seconds
    latencies = []
    statuses = []
    run_count = 0

    try:
        while time.monotonic() < deadline:
            run_count += 1
            state = WorkflowState(
                trace_id=f"tr-benchmark-{model}-{run_count}",
                document_id=f"doc-benchmark-{model}-{run_count}",
                matter_id=f"mat-benchmark-{model}-{run_count}",
                raw_content=text,
                filename="sample_supplier_agreement.txt",
                clauses=[test_clause],
                ai_findings=[]
            )

            t0 = time.monotonic()
            try:
                state = compliance_agent.execute(state)
                latency = time.monotonic() - t0
                found = any(f.issue == "Uncapped Liability Exposure" for f in state.ai_findings)
                status = "PASS" if found else "FAIL (No Finding)"
            except Exception as e:
                latency = time.monotonic() - t0
                status = f"ERROR ({str(e)[:50]})"

            latencies.append(latency)
            statuses.append(status)

            if time.monotonic() < deadline:
                time.sleep(BENCHMARK_PAUSE_SECONDS)
    finally:
        active_models = get_active_ollama_models()
        for active_model in active_models:
            if active_model != model:
                stop_model(active_model)
        stop_model(model)

    status_counts = {}
    for status in statuses:
        status_counts[status] = status_counts.get(status, 0) + 1

    primary_status = max(status_counts.items(), key=lambda item: item[1])[0]
    latency_summary = summarize_latencies(latencies)

    return {
        "model": model,
        "runs": run_count,
        "latency": latency_summary["avg"],
        "status": primary_status,
        "status_counts": status_counts,
        "latency_summary": latency_summary,
    }


def run_benchmark(duration_seconds: int = DEFAULT_BENCHMARK_SECONDS):
    print("Starting JurisCore Local LLM Benchmark\n" + "=" * 40)
    print(f"Each model runs for {duration_seconds} seconds (set BENCHMARK_DURATION_SECONDS to change this).\n")

    text = load_sample_document()
    if not text:
        return

    test_clause = Clause(
        clause_id="C1",
        title="Indemnity",
        text="The Supplier shall indemnify and hold harmless the Company against all losses, damages, and claims arising from a breach of this Agreement. This is an unlimited liability clause with no cap."
    )

    results = []
    for model in MODELS_TO_TEST:
        print(f"Testing model: {model} for up to {duration_seconds}s...")
        result = benchmark_model(model, text, test_clause, duration_seconds)
        results.append(result)

        print(f"  -> {result['status']} | avg latency {result['latency']:.2f}s | runs {result['runs']}")
        print("-" * 40)

    print("\nBENCHMARK RESULTS")
    print("========================================")
    print(f"{'Model Name':<20} | {'Status':<20} | {'Min':<8} | {'Median':<9} | {'Max':<8} | {'Avg':<8} | {'Runs':<5}")
    print("-" * 100)
    for res in results:
        summary = res["latency_summary"]
        print(
            f"{res['model']:<20} | {res['status']:<20} | {summary['min']:<8.2f} | {summary['median']:<9.2f} | {summary['max']:<8.2f} | {summary['avg']:<8.2f} | {res['runs']:<5}"
        )
    print("========================================")


if __name__ == "__main__":
    run_benchmark(DEFAULT_BENCHMARK_SECONDS)
