from typing import List, Dict

def hamming_similarity(seq1, seq2):
    """计算两个等长序列的汉明相似度（0~1）"""
    diff = sum(a != b for a, b in zip(seq1, seq2))
    return 1 - diff / len(seq1)

def flatten(seq):
    """展平二维列表（[['6','7'], ['5']] -> [6,7,5]）"""
    if isinstance(seq[0], list):
        return [int(x) for sub in seq for x in sub]
    return seq

def structure_similarity(ind1: Dict, ind2: Dict) -> float:
    """计算两个个体的结构相似度（多段平均）"""
    keys = [
        "采购供应商选择",
        "产品内部的部装工序顺序",
        "部装工序顺序列表",
        "部装机器选择列表",
        "总装工序顺序列表",
        "总装机器选择列表"
    ]
    sims = []
    for k in keys:
        seq1 = flatten(ind1[k])
        seq2 = flatten(ind2[k])
        sims.append(hamming_similarity(seq1, seq2))
    return sum(sims) / len(sims)

def find_top_k_similar_max_or_avg(target_individual: Dict, history_records: List[Dict], k=20):
    """
    对每条记录的 p1、p2、crossover_child1、crossover_child2、before_mutation、mutated_child
    计算相似度，取 max(最大值, 平均值) 作为该记录的最终相似度
    返回值只包含 record
    """
    compare_fields = ["p1", "p2", "crossover_child1", "crossover_child2", "before_mutation", "mutated_child"]
    scored = []

    for rec in history_records:
        sims = []
        for field in compare_fields:
            if rec.get(field) is not None:
                sims.append(structure_similarity(target_individual, rec[field]))
        if sims:
            max_sim = max(sims)
            avg_sim = sum(sims) / len(sims)
            final_sim = max(max_sim, avg_sim)
            scored.append((final_sim, rec))  # 只存相似度和记录

    # 按相似度排序
    scored.sort(key=lambda x: x[0], reverse=True)

    # 只返回 record
    return [rec for _, rec in scored[:k]]



# ===== 用法示例 =====
# target_individual = 你的精英个体（字典）
# history_records = EvolutionLogger.records（列表）
# top20 = find_top_k_similar_max_or_avg(target_individual, history_records, k=20)
#
# for item in top20:
#     print(f"最终相似度: {item['similarity']:.4f} | 最大: {item['max_similarity']:.4f} | 平均: {item['avg_similarity']:.4f}")
#     print("适应度:", item["record"].get("fitness_mutated", None))
#     print("-" * 50)
