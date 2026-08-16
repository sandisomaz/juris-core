import json
import re
import subprocess
import urllib.request
import urllib.error
from src.core.config import settings

class LLMBridge:
    def __init__(self):
        self.mode = settings.LLM_MODE
        self.model = settings.LLM_MODEL
        self.ollama_host = settings.OLLAMA_HOST
        self.request_timeout_seconds = settings.LLM_REQUEST_TIMEOUT_SECONDS
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

        if self.mode == "cloud":
            if not self.anthropic_key and not self.openai_key:
                raise RuntimeError(
                    "Cloud mode requested but no ANTHROPIC_API_KEY or OPENAI_API_KEY "
                    "found in environment."
                )

    def health_check(self):
        """Returns True if the configured backend is reachable."""
        if self.mode == "local":
            try:
                req = urllib.request.Request(f"{self.ollama_host}/api/tags")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    return resp.status == 200
            except Exception:
                return False
        else:
            return bool(self.anthropic_key or self.openai_key)

    def _run_ollama_command(self, args):
        try:
            return subprocess.run(["ollama", *args], capture_output=True, text=True, timeout=60)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

    def get_active_ollama_models(self):
        result = self._run_ollama_command(["ps"])
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

    def stop_model(self, model_name: str):
        if not model_name:
            return
        result = self._run_ollama_command(["stop", model_name])
        if result is not None and result.returncode != 0:
            raise RuntimeError(f"Could not stop model '{model_name}': {result.stderr.strip() or result.stdout.strip()}")

    def set_model(self, model_name: str):
        self.model = model_name
        active_models = self.get_active_ollama_models()
        for active_model in active_models:
            if active_model != model_name:
                self.stop_model(active_model)

    def _extract_json(self, content: str) -> dict:
        """Extracts JSON from text, robustly handling reasoning/thinking blocks."""
        # Remove <think>...</think> tags if present
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        
        # Look for markdown code blocks
        match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
        else:
            # Look for outermost curly braces
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                json_str = match.group(0).strip()
            else:
                json_str = content.strip()
                
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "non_json_response", "raw": content}

    def query(self, system_prompt: str, user_prompt: str, expect_json: bool = True) -> dict:
        """
        Sends a prompt to the configured backend. Returns a parsed dict if
        expect_json=True, otherwise returns {"text": "..."}.
        """
        if self.mode == "local":
            return self._query_ollama(system_prompt, user_prompt, expect_json)
        else:
            return self._query_cloud(system_prompt, user_prompt, expect_json)

    def _query_ollama(self, system_prompt, user_prompt, expect_json):
        # We don't force 'format': 'json' because reasoning models often fail to emit reasoning if forced into JSON schema mode
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.ollama_host}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                content = body.get("message", {}).get("content", "")
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Could not reach local Ollama at {self.ollama_host}. "
                f"Is Ollama running? ('ollama serve') Error: {e}"
            )

        if expect_json:
            return self._extract_json(content)
        return {"text": content}

    def _query_cloud(self, system_prompt, user_prompt, expect_json):
        if self.anthropic_key:
            payload = {
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.request_timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                content = "".join(
                    block.get("text", "") for block in body.get("content", [])
                    if block.get("type") == "text"
                )
        else:
            raise RuntimeError("OpenAI cloud path not yet implemented in this scaffold.")

        if expect_json:
            return self._extract_json(content)
        return {"text": content}

llm_bridge = LLMBridge()
