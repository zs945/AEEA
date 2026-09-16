"""DeepSeek Chat Completions client with complete reproducibility logging."""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from openai import OpenAI

from mutil_agent_generation_individual.reproducibility import (
    get_reproducibility_logger,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PROMPT_FILE = PROJECT_ROOT / "prompts" / "system_prompt.txt"
SYSTEM_PROMPT = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()
API_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
REQUESTED_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", "8192"))
RESPONSE_FORMAT = {"type": "json_object"}

# The original experiment uses a reasoning/thinking model. DeepSeek documents that
# temperature and top_p have no effect in thinking mode, so they are deliberately
# omitted from the API request and recorded as not applicable.
TEMPERATURE = None
TOP_P = None
LLM_RANDOM_SEED = None


def llm_configuration() -> Dict[str, Any]:
    configured_context_window = os.getenv("DEEPSEEK_CONTEXT_WINDOW_TOKENS", "").strip()
    return {
        "provider": "DeepSeek",
        "api_base_url": API_BASE_URL,
        "requested_model": REQUESTED_MODEL,
        "returned_model": "recorded separately for every API response",
        "system_prompt": SYSTEM_PROMPT,
        "system_prompt_file": "prompts/system_prompt.txt",
        "thinking_mode": "enabled by the deepseek-reasoner model alias",
        "temperature": TEMPERATURE,
        "temperature_note": "not sent; unsupported/no effect in thinking mode",
        "top_p": TOP_P,
        "top_p_note": "not sent; unsupported/no effect in thinking mode",
        "max_tokens": MAX_TOKENS,
        "llm_random_seed": LLM_RANDOM_SEED,
        "llm_random_seed_note": "the DeepSeek Chat Completions API does not expose a seed parameter",
        "response_format": RESPONSE_FORMAT,
        "stream": False,
        "context_window_tokens": int(configured_context_window) if configured_context_window else None,
        "context_size_note": "actual prompt tokens and elite examples are logged for each call",
    }


def _model_dump(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    return {}


def _usage_dict(response: Any) -> Dict[str, Any]:
    usage = _model_dump(getattr(response, "usage", None))
    details = usage.get("completion_tokens_details") or {}
    if hasattr(details, "model_dump"):
        details = details.model_dump()
    usage["reasoning_tokens"] = details.get("reasoning_tokens", 0) if isinstance(details, dict) else 0
    return usage


def _extract_candidates(parsed: Any) -> Tuple[List[Dict[str, Any]], str | None]:
    if not isinstance(parsed, dict):
        return [], "top-level JSON value must be an object"
    candidates = parsed.get("individuals")
    if not isinstance(candidates, list):
        return [], "top-level object must contain an 'individuals' array"
    if not all(isinstance(candidate, dict) for candidate in candidates):
        return [], "every item in 'individuals' must be an object"
    return candidates, None


def call_deepseek(
    prompt: str,
    *,
    generation: int,
    logical_call_index: int,
    attempt: int,
    requested_candidates: int,
    elite_context_size: int,
) -> Tuple[List[Dict[str, Any]], str]:
    """Call DeepSeek once and return parsed candidate objects plus a traceable call id."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is not set. Set it in the environment; never commit the key."
        )

    call_id = (
        f"g{generation:03d}_c{logical_call_index:02d}_a{attempt:02d}_"
        f"{uuid.uuid4().hex[:8]}"
    )
    timestamp_utc = datetime.now(timezone.utc).isoformat()
    client = OpenAI(api_key=api_key, base_url=API_BASE_URL)
    request_parameters = {
        "model": REQUESTED_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "response_format": RESPONSE_FORMAT,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }
    start = time.perf_counter()
    raw_text = ""
    record: Dict[str, Any] = {
        "call_id": call_id,
        "timestamp_utc": timestamp_utc,
        "generation": generation,
        "logical_call_index": logical_call_index,
        "attempt": attempt,
        "requested_candidates": requested_candidates,
        "elite_context_size": elite_context_size,
        "prompt_characters": len(prompt),
        "request": {
            "provider": "DeepSeek",
            "api_base_url": API_BASE_URL,
            "model": REQUESTED_MODEL,
            "system_prompt": SYSTEM_PROMPT,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "max_tokens": MAX_TOKENS,
            "llm_random_seed": LLM_RANDOM_SEED,
            "response_format": RESPONSE_FORMAT,
            "stream": False,
        },
    }

    try:
        response = client.chat.completions.create(**request_parameters)
        latency_seconds = time.perf_counter() - start
        choice = response.choices[0]
        raw_text = choice.message.content or ""
        parse_error = None
        try:
            parsed = json.loads(raw_text)
            candidates, structure_error = _extract_candidates(parsed)
            if structure_error:
                parse_error = structure_error
        except Exception as exc:
            candidates = []
            parse_error = f"{type(exc).__name__}: {exc}"

        record.update(
            {
                "latency_seconds": latency_seconds,
                "response_id": getattr(response, "id", None),
                "response_created": getattr(response, "created", None),
                "response_model": getattr(response, "model", None),
                "system_fingerprint": getattr(response, "system_fingerprint", None),
                "finish_reason": getattr(choice, "finish_reason", None),
                "usage": _usage_dict(response),
                "json_parse_success": parse_error is None,
                "parse_or_structure_error": parse_error,
                "parsed_candidate_count": len(candidates),
                "api_error": None,
            }
        )
        get_reproducibility_logger().log_api_attempt(record, prompt, raw_text)
        return candidates, call_id
    except Exception as exc:
        record.update(
            {
                "latency_seconds": time.perf_counter() - start,
                "response_id": None,
                "response_created": None,
                "response_model": None,
                "system_fingerprint": None,
                "finish_reason": None,
                "usage": {},
                "json_parse_success": False,
                "parse_or_structure_error": None,
                "parsed_candidate_count": 0,
                "api_error": f"{type(exc).__name__}: {exc}",
            }
        )
        get_reproducibility_logger().log_api_attempt(record, prompt, raw_text)
        return [], call_id
