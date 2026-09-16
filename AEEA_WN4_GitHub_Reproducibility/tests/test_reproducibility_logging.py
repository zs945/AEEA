import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from mutil_agent_generation_individual import DeepSeek
from mutil_agent_generation_individual.reproducibility import (
    configure_reproducibility,
    finalize_reproducibility,
)


class FakeUsage:
    def model_dump(self):
        return {
            "prompt_tokens": 10,
            "prompt_cache_hit_tokens": 2,
            "prompt_cache_miss_tokens": 8,
            "completion_tokens": 5,
            "total_tokens": 15,
            "completion_tokens_details": {"reasoning_tokens": 3},
        }


class FakeCompletions:
    def create(self, **kwargs):
        payload = {
            "individuals": [
                {
                    "采购供应商选择": [],
                    "产品内部的部装工序顺序": [],
                    "部装工序顺序列表": [],
                    "部装机器选择列表": [],
                    "总装工序顺序列表": [],
                    "总装机器选择列表": [],
                }
            ]
        }
        message = SimpleNamespace(content=json.dumps(payload, ensure_ascii=False))
        choice = SimpleNamespace(message=message, finish_reason="stop")
        return SimpleNamespace(
            id="fake-response-id",
            created=1,
            model="deepseek-reasoner-test",
            system_fingerprint="fake-fingerprint",
            choices=[choice],
            usage=FakeUsage(),
        )


class FakeOpenAI:
    def __init__(self, **kwargs):
        self.chat = SimpleNamespace(completions=FakeCompletions())


class ReproducibilityLoggingTest(unittest.TestCase):
    def test_api_attempt_is_fully_logged(self):
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            run_dir = temporary_path / "fake_run"
            pricing_file = temporary_path / "pricing.json"
            pricing_file.write_text(
                json.dumps(
                    {
                        "verified_for_experiment_access_date": True,
                        "input_cache_hit_usd_per_million": 1.0,
                        "input_cache_miss_usd_per_million": 2.0,
                        "output_usd_per_million": 3.0,
                    }
                ),
                encoding="utf-8",
            )
            configure_reproducibility(
                run_dir=run_dir,
                run_metadata={"seed": 4},
                llm_config=DeepSeek.llm_configuration(),
                pricing_file=pricing_file,
                schema_file=project_root / "schemas" / "individuals.schema.json",
                source_files=[project_root / "run_experiment.py"],
            )
            previous_key = os.environ.get("DEEPSEEK_API_KEY")
            os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"
            original_client = DeepSeek.OpenAI
            DeepSeek.OpenAI = FakeOpenAI
            try:
                candidates, call_id = DeepSeek.call_deepseek(
                    "return JSON",
                    generation=1,
                    logical_call_index=1,
                    attempt=1,
                    requested_candidates=1,
                    elite_context_size=1,
                )
                self.assertEqual(len(candidates), 1)
                self.assertTrue(call_id.startswith("g001_c01_a01_"))
                finalize_reproducibility()
            finally:
                DeepSeek.OpenAI = original_client
                if previous_key is None:
                    os.environ.pop("DEEPSEEK_API_KEY", None)
                else:
                    os.environ["DEEPSEEK_API_KEY"] = previous_key

            record = json.loads((run_dir / "llm_calls.jsonl").read_text(encoding="utf-8"))
            summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(record["response_model"], "deepseek-reasoner-test")
            self.assertEqual(record["usage"]["reasoning_tokens"], 3)
            self.assertAlmostEqual(record["estimated_cost_usd"], 33 / 1_000_000)
            self.assertEqual(summary["logical_llm_calls"], 1)
            self.assertTrue((run_dir / record["prompt_file"]).exists())
            self.assertTrue((run_dir / record["raw_output_file"]).exists())


if __name__ == "__main__":
    unittest.main()
