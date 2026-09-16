"""LLM candidate generation with explicit retry and validation records."""

from __future__ import annotations

from datetime import datetime, timezone

from mutil_agent_generation_individual.DeepSeek import call_deepseek
from mutil_agent_generation_individual.output_check2 import check_response
from mutil_agent_generation_individual.reproducibility import (
    get_reproducibility_logger,
)


class LLMAgent:
    def __init__(self, role_name: str):
        self.role_name = role_name
        self.prompt_text = None

    def build_prompt(self, context):
        return self.prompt_text

    def generate_with_retry(
        self,
        full_prompt,
        product_library,
        type_list,
        purchase_ranges,
        type_counts,
        *,
        generation,
        logical_call_index,
        requested_candidates,
        elite_context_size,
        max_retries=5,
    ):
        """Retry until at least one candidate passes parsing and feasibility checking."""
        run_logger = get_reproducibility_logger()
        for attempt in range(1, max_retries + 1):
            candidates, call_id = call_deepseek(
                full_prompt,
                generation=generation,
                logical_call_index=logical_call_index,
                attempt=attempt,
                requested_candidates=requested_candidates,
                elite_context_size=elite_context_size,
            )
            validation_error = None
            try:
                accepted = check_response(
                    candidates,
                    product_library,
                    type_list,
                    purchase_ranges,
                    type_counts,
                )
            except Exception as exc:
                accepted = []
                validation_error = f"{type(exc).__name__}: {exc}"

            run_logger.log_validation(
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "call_id": call_id,
                    "generation": generation,
                    "logical_call_index": logical_call_index,
                    "attempt": attempt,
                    "parsed_candidates": len(candidates),
                    "accepted_candidates": len(accepted),
                    "accepted": bool(accepted),
                    "validation_error": validation_error,
                    "retry_required": not bool(accepted),
                }
            )
            if accepted:
                print(f"LLM generation succeeded on attempt {attempt}")
                return accepted
            print(f"LLM generation attempt {attempt} failed validation; retrying")

        print("LLM generation exhausted the retry limit; returning no candidates")
        return []

    def generate(
        self,
        context,
        product_library,
        ordersss,
        order_delay_costss,
        product_Warehousing_Costss,
        order_Deadliness,
        type_list,
        purchase_ranges,
        type_counts,
        *,
        generation,
        logical_call_index,
        requested_candidates,
        elite_context_size,
    ):
        prompt = self.build_prompt(context)
        full_prompt = f"""
        你是一个进化算法编码助手，负责生成完整的六段染色体编码。
        问题定义：这是一个多产品、多工序、多资源的生产调度优化问题。每个产品由若干工序组成，工序可能需要从不同供应商采购原料，或在不同类型的机器上加工，并且存在前置依赖关系。不同供应商和机器在成本、时间等方面存在差异。
        优化目标：同时减少采购成本、订单延期成本和仓储成本。
        采购成本由各采购工序选择的供应商单位成本与采购数量决定。
        订单完成时间为该订单中最后一个产品的完工时间；超过截止时间的部分乘以订单延期成本系数得到延期成本。
        产品提前完成后储存至订单整体完成，仓储成本为储存时间乘以对应产品类型的单位时间仓储成本。
        工序类型0表示采购工序，工序类型1表示部装工序，工序类型2表示总装工序。
        产品库：{product_library}
        订单需求：{ordersss}
        各订单单位延期成本：{order_delay_costss}
        各产品单位时间仓储成本：{product_Warehousing_Costss}
        各订单截止时间：{order_Deadliness}
        {prompt}
        """
        return self.generate_with_retry(
            full_prompt,
            product_library,
            type_list,
            purchase_ranges,
            type_counts,
            generation=generation,
            logical_call_index=logical_call_index,
            requested_candidates=requested_candidates,
            elite_context_size=elite_context_size,
            max_retries=5,
        )


class individualAgent(LLMAgent):
    def __init__(self):
        super().__init__("complete six-segment chromosome")

    def build_prompt(self, context):
        return context
