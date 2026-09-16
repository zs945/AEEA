import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import run_experiment
from mutil_agent_generation_individual import DeepSeek
from mutil_agent_generation_individual.llm_agent import individualAgent
from mutil_agent_generation_individual.prompt_builder3 import (
    build_assembly_count_list,
    build_prompt_for_llm,
    get_purchase_ranges,
)
from mutil_agent_generation_individual.reproducibility import (
    configure_reproducibility,
    finalize_reproducibility,
)


class FakeUsage:
    def model_dump(self):
        return {
            "prompt_tokens": 100,
            "prompt_cache_hit_tokens": 0,
            "prompt_cache_miss_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "completion_tokens_details": {"reasoning_tokens": 20},
        }


class LlmPipelineTest(unittest.TestCase):
    def test_generated_json_reaches_feasibility_checker(self):
        project_root = Path(__file__).resolve().parents[1]
        orders = run_experiment.merge_orders(run_experiment.ordersss)
        candidate = run_experiment.generate_population(
            1, orders, run_experiment.Product_library
        )[0]
        payload = {"individuals": [copy.deepcopy(candidate)]}

        class FakeCompletions:
            def create(self, **kwargs):
                choice = SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(payload, ensure_ascii=False)
                    ),
                    finish_reason="stop",
                )
                return SimpleNamespace(
                    id="fake-pipeline-response",
                    created=1,
                    model="deepseek-reasoner-test",
                    system_fingerprint="fake-pipeline-fingerprint",
                    choices=[choice],
                    usage=FakeUsage(),
                )

        class FakeOpenAI:
            def __init__(self, **kwargs):
                self.chat = SimpleNamespace(completions=FakeCompletions())

        type_list = run_experiment.generate_product_mappings(run_experiment.ordersss)[1]
        purchase_ranges = get_purchase_ranges(type_list, run_experiment.Product_library)
        type_counts = build_assembly_count_list(run_experiment.Product_library, type_list)
        context = build_prompt_for_llm(
            [candidate], [[1.0, 2.0, 3.0]], 1, type_list, purchase_ranges, type_counts
        )

        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            pricing_file = temporary_path / "pricing.json"
            pricing_file.write_text(
                json.dumps({"verified_for_experiment_access_date": False}),
                encoding="utf-8",
            )
            configure_reproducibility(
                run_dir=temporary_path / "pipeline_run",
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
                accepted = individualAgent().generate(
                    context,
                    run_experiment.Product_library,
                    run_experiment.ordersss,
                    run_experiment.order_delay_costss,
                    run_experiment.product_Warehousing_Costss,
                    run_experiment.order_Deadliness,
                    type_list,
                    purchase_ranges,
                    type_counts,
                    generation=1,
                    logical_call_index=1,
                    requested_candidates=1,
                    elite_context_size=1,
                )
                self.assertEqual(len(accepted), 1)
                finalize_reproducibility()
            finally:
                DeepSeek.OpenAI = original_client
                if previous_key is None:
                    os.environ.pop("DEEPSEEK_API_KEY", None)
                else:
                    os.environ["DEEPSEEK_API_KEY"] = previous_key

            validation = json.loads(
                (temporary_path / "pipeline_run" / "validation_events.jsonl").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(validation["accepted"])
            self.assertEqual(validation["accepted_candidates"], 1)


if __name__ == "__main__":
    unittest.main()
