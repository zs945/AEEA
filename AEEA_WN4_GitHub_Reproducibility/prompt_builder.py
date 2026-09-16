# prompt_builder.py

def format_individual(ind):
    """将个体结构转为简短可读的字符串"""
    return (
        f"采购供应商选择: {ind['采购供应商选择']}\n"
        f"产品内部部装顺序: {ind['产品内部的部装工序顺序']}\n"
        f"部装工序顺序列表: {ind['部装工序顺序列表']}\n"
        f"部装机器选择列表: {ind['部装机器选择列表']}\n"
        f"总装工序顺序列表: {ind['总装工序顺序列表']}\n"
        f"总装机器选择列表: {ind['总装机器选择列表']}"
    )

def format_sample(record, idx):
    """格式化一条日志记录"""
    return (
        f"样本 {idx}：\n"
        f"父代1:\n{format_individual(record['p1'])}\n 适应度: {record['fitness_p1']}\n"
        f"父代2:\n{format_individual(record['p2'])}\n 适应度: {record['fitness_p2']}\n"
        f"→ 交叉子代1:\n{format_individual(record['crossover'][0])}\n 适应度: {record['fitness_c1']}\n"
        f"→ 交叉子代2:\n{format_individual(record['crossover'][1])}\n 适应度: {record['fitness_c2']}\n"
        f"→ 变异子代1:\n{format_individual(record['mutation'][0])}\n 适应度: {record['fitness_m1']}\n"
        f"→ 变异子代2:\n{format_individual(record['mutation'][1])}\n 适应度: {record['fitness_m2']}\n"
    )

def build_prompt(records, elite_ind, elite_fit):
    """
    构造给大模型的提示词
    records: 上一代的 GA 行为样本
    elite_ind: 精英个体
    elite_fit: 精英适应度
    """
    prompt = """你是一个多目标优化与调度问题的遗传算法专家。
当前问题涉及采购、部装、总装等多阶段工序的优化，目标是最小化综合成本（采购成本 + 延迟成本 + 仓储成本）。

以下是上一代的部分演化样本：
"""
    for i, rec in enumerate(records):
        prompt += format_sample(rec, i)

    prompt += f"\n💎 当前精英个体：\n{format_individual(elite_ind)}\n适应度: {elite_fit}\n\n"
    prompt += """🎯 请基于这些样本，提出若干新的完整个体结构建议（必须合法且多样化）。
输出格式为 JSON 数组，每个元素是一个个体结构，字段与示例一致。
</think>"""
    return prompt
