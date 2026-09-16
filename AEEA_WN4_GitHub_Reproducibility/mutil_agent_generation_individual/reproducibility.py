"""Structured, append-only logging for LLM reproducibility."""

from __future__ import annotations

import atexit
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_default(value: Any):
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8",
    )


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=_json_default) + "\n")


def _package_versions() -> Dict[str, Optional[str]]:
    versions: Dict[str, Optional[str]] = {}
    for package in ("numpy", "matplotlib", "openai", "pandas", "requests"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ReproducibilityLogger:
    def __init__(
        self,
        run_dir: Path,
        run_metadata: Dict[str, Any],
        llm_config: Dict[str, Any],
        pricing_file: Path,
        schema_file: Path,
        source_files: list[Path],
    ) -> None:
        self.run_dir = run_dir.resolve()
        if self.run_dir.exists() and any(self.run_dir.iterdir()):
            raise FileExistsError(
                f"Run directory is not empty: {self.run_dir}. Use a unique --run-id."
            )
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir = self.run_dir / "prompts"
        self.raw_outputs_dir = self.run_dir / "raw_outputs"
        self.prompts_dir.mkdir(exist_ok=True)
        self.raw_outputs_dir.mkdir(exist_ok=True)
        self.calls_path = self.run_dir / "llm_calls.jsonl"
        self.validation_path = self.run_dir / "validation_events.jsonl"
        self.composition_path = self.run_dir / "population_composition.jsonl"
        self.summary_path = self.run_dir / "run_summary.json"
        self._attempt_records: list[Dict[str, Any]] = []
        self._validation_records: list[Dict[str, Any]] = []
        self._composition_records: list[Dict[str, Any]] = []
        self._finalized = False

        self.pricing = json.loads(pricing_file.read_text(encoding="utf-8"))
        self.schema = json.loads(schema_file.read_text(encoding="utf-8"))
        project_root = Path(__file__).resolve().parents[1]
        source_hashes = {
            str(path.resolve().relative_to(project_root)): _sha256(path)
            for path in source_files
            if path.exists()
        }
        self.manifest = {
            "run_id": self.run_dir.name,
            "access_started_utc": utc_now(),
            "provider": "DeepSeek",
            "llm": llm_config,
            "algorithm_and_instance": run_metadata,
            "output_schema": {
                "file": str(schema_file.resolve().relative_to(project_root)),
                "sha256": _sha256(schema_file),
                "schema": self.schema,
                "enforcement": "JSON-object API mode plus local structural validation and feasibility checking/repair",
            },
            "pricing": self.pricing,
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "packages": _package_versions(),
            },
            "source_file_sha256": source_hashes,
        }
        _write_json(self.run_dir / "run_manifest.json", self.manifest)

    def estimate_cost(self, usage: Dict[str, Any]) -> Optional[float]:
        if not self.pricing.get("verified_for_experiment_access_date", False):
            return None
        hit_price = self.pricing.get("input_cache_hit_usd_per_million")
        miss_price = self.pricing.get("input_cache_miss_usd_per_million")
        output_price = self.pricing.get("output_usd_per_million")
        if any(value is None for value in (hit_price, miss_price, output_price)):
            return None
        hit_tokens = usage.get("prompt_cache_hit_tokens", 0) or 0
        miss_tokens = usage.get("prompt_cache_miss_tokens")
        if miss_tokens is None:
            miss_tokens = max((usage.get("prompt_tokens", 0) or 0) - hit_tokens, 0)
        completion_tokens = usage.get("completion_tokens", 0) or 0
        return (
            hit_tokens * hit_price
            + miss_tokens * miss_price
            + completion_tokens * output_price
        ) / 1_000_000

    def log_api_attempt(
        self,
        record: Dict[str, Any],
        prompt: str,
        raw_output: str,
    ) -> None:
        call_id = record["call_id"]
        prompt_path = self.prompts_dir / f"{call_id}.txt"
        raw_path = self.raw_outputs_dir / f"{call_id}.txt"
        prompt_path.write_text(prompt, encoding="utf-8")
        raw_path.write_text(raw_output or "", encoding="utf-8")
        record["prompt_file"] = str(prompt_path.relative_to(self.run_dir))
        record["raw_output_file"] = str(raw_path.relative_to(self.run_dir))
        record["prompt_sha256"] = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        record["raw_output_sha256"] = hashlib.sha256((raw_output or "").encode("utf-8")).hexdigest()
        record["estimated_cost_usd"] = self.estimate_cost(record.get("usage", {}))
        _append_jsonl(self.calls_path, record)
        self._attempt_records.append(record)

    def log_validation(self, record: Dict[str, Any]) -> None:
        _append_jsonl(self.validation_path, record)
        self._validation_records.append(record)

    def log_population_composition(self, record: Dict[str, Any]) -> None:
        _append_jsonl(self.composition_path, record)
        self._composition_records.append(record)

    def finalize(self) -> None:
        if self._finalized:
            return
        self._finalized = True
        totals = defaultdict(float)
        returned_models = set()
        fingerprints = set()
        logical_calls = set()
        per_generation: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "logical_calls": set(),
                "api_attempts": 0,
                "accepted_candidates": 0,
                "population_composition": None,
            }
        )

        for record in self._attempt_records:
            usage = record.get("usage", {})
            for key in (
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "prompt_cache_hit_tokens",
                "prompt_cache_miss_tokens",
                "reasoning_tokens",
            ):
                totals[key] += usage.get(key, 0) or 0
            totals["latency_seconds"] += record.get("latency_seconds", 0) or 0
            if record.get("estimated_cost_usd") is not None:
                totals["estimated_cost_usd"] += record["estimated_cost_usd"]
            if record.get("response_model"):
                returned_models.add(record["response_model"])
            if record.get("system_fingerprint"):
                fingerprints.add(record["system_fingerprint"])
            logical_key = (record.get("generation"), record.get("logical_call_index"))
            logical_calls.add(logical_key)
            generation_key = str(record.get("generation"))
            per_generation[generation_key]["logical_calls"].add(logical_key)
            per_generation[generation_key]["api_attempts"] += 1

        for record in self._validation_records:
            if record.get("accepted"):
                generation_key = str(record.get("generation"))
                per_generation[generation_key]["accepted_candidates"] += record.get(
                    "accepted_candidates", 0
                )

        for record in self._composition_records:
            generation_key = str(record.get("generation"))
            per_generation[generation_key]["population_composition"] = record

        serializable_per_generation = {
            generation: {
                "logical_calls": len(values["logical_calls"]),
                "api_attempts": values["api_attempts"],
                "accepted_candidates": values["accepted_candidates"],
                "population_composition": values["population_composition"],
            }
            for generation, values in sorted(per_generation.items(), key=lambda item: int(item[0]))
        }
        cost_available = all(
            record.get("estimated_cost_usd") is not None for record in self._attempt_records
        ) and bool(self._attempt_records)
        summary = {
            "run_id": self.run_dir.name,
            "access_finished_utc": utc_now(),
            "logical_llm_calls": len(logical_calls),
            "api_attempts_including_retries": len(self._attempt_records),
            "retry_attempts": max(len(self._attempt_records) - len(logical_calls), 0),
            "successful_validations": sum(1 for item in self._validation_records if item.get("accepted")),
            "returned_models": sorted(returned_models),
            "system_fingerprints": sorted(fingerprints),
            "token_and_latency_totals": dict(totals),
            "estimated_api_cost_usd": totals.get("estimated_cost_usd") if cost_available else None,
            "cost_note": (
                "Computed from pricing.json"
                if cost_available
                else "Unavailable until pricing.json is completed and verified for the experiment access date"
            ),
            "per_generation": serializable_per_generation,
        }
        _write_json(self.summary_path, summary)


_LOGGER: Optional[ReproducibilityLogger] = None


def configure_reproducibility(
    run_dir: Path,
    run_metadata: Dict[str, Any],
    llm_config: Dict[str, Any],
    pricing_file: Path,
    schema_file: Path,
    source_files: list[Path],
) -> ReproducibilityLogger:
    global _LOGGER
    _LOGGER = ReproducibilityLogger(
        run_dir=run_dir,
        run_metadata=run_metadata,
        llm_config=llm_config,
        pricing_file=pricing_file,
        schema_file=schema_file,
        source_files=source_files,
    )
    atexit.register(_LOGGER.finalize)
    return _LOGGER


def get_reproducibility_logger() -> ReproducibilityLogger:
    if _LOGGER is None:
        raise RuntimeError("Reproducibility logging has not been configured by run_experiment.py")
    return _LOGGER


def finalize_reproducibility() -> None:
    if _LOGGER is not None:
        _LOGGER.finalize()
