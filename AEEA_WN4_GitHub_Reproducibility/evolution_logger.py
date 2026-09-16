# evolution_logger.py
import pandas as pd

class EvolutionLogger:
    def __init__(self):
        self.records = []

    def log_crossover(self, generation,
                      p1, p2, c1, c2,
                      f_p1, f_p2, f_c1, f_c2):
        """
        记录交叉阶段（父代 -> 两个子代）
        注意：这里假设 c1 或 c2 会在变异前被选中作为 childcopy
        """
        self.records.append({
            "generation": generation,
            "p1": p1, "fitness_p1": f_p1,
            "p2": p2, "fitness_p2": f_p2,
            "crossover_child1": c1, "fitness_c1": f_c1,
            "crossover_child2": c2, "fitness_c2": f_c2,
            # 变异前/后信息
            "before_mutation": None, "fitness_before_mutation": None,
            "mutated_child": None, "fitness_mutated": None,
        })

    def log_mutation(self, before_mutation, f_before, mutated, f_mutated):
        """
        在变异阶段补充变异前后的信息
        匹配逻辑：找到第一条还没有 before_mutation 的记录，补上数据
        """
        for rec in self.records:
            if rec["before_mutation"] is None:
                rec["before_mutation"] = before_mutation
                rec["fitness_before_mutation"] = f_before
                rec["mutated_child"] = mutated
                rec["fitness_mutated"] = f_mutated
                break

    def get_last_generation_records(self, generation):
        return [r for r in self.records if r["generation"] == generation]

    def export_as_csv(self, path="evolution_log.csv"):
        df = pd.json_normalize(self.records, sep=".")
        df.to_csv(path, index=False)
        print(f"✅ 已保存演化日志为 CSV：{path}")
