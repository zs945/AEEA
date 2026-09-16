import random

def build_position_mapping(product_types, proc_counts):
    """建立染色体位置→（产品编号、产品类型、工序索引）的映射表（内部使用）"""
    pos_mapping = []
    current_chrom_pos = 0
    for product_id, product_type in enumerate(product_types):
        type_proc_count = proc_counts[product_type]
        for process_idx in range(type_proc_count):
            pos_mapping.append((product_id, product_type, process_idx))
            current_chrom_pos += 1
    return pos_mapping


def purchase_mutate_chromosome(chromosome, product_types, proc_counts, product_library, mutation_rate=0.3):
    """
    对采购编码段执行变异（假设外层已决定是否进行采购段变异）
    mutation_rate 控制变异位点比例
    """
    pos_mapping = build_position_mapping(product_types, proc_counts)
    mutated_chrom = chromosome.copy()
    chrom_length = len(mutated_chrom)

    # 随机选择要变异的位点集合
    num_mutations = max(1, int(chrom_length * mutation_rate))
    mutation_positions = random.sample(range(chrom_length), num_mutations)

    for chrom_pos in mutation_positions:
        product_id, product_type, process_idx = pos_mapping[chrom_pos]

        # 获取供应商列表
        try:
            supplier_list = product_library[product_type][process_idx]["供应商"]
        except (IndexError, KeyError):
            continue

        if len(supplier_list) <= 1:
            continue  # 无法变异

        current_idx = mutated_chrom[chrom_pos]
        if not (0 <= current_idx < len(supplier_list)):
            current_idx = 0

        # 选择一个不同的供应商
        possible_indices = [i for i in range(len(supplier_list)) if i != current_idx]
        mutated_chrom[chrom_pos] = random.choice(possible_indices)

    return mutated_chrom



import random
from collections import defaultdict
# from product_information.Initial_processing_of_product_information import read_csv_files

def compute_transitive_closure(precedence):
    """计算每个节点的所有前驱和后继集合"""
    all_preds = defaultdict(set)
    all_succs = defaultdict(set)

    successors = defaultdict(set)
    for task, preds in precedence.items():
        for p in preds:
            successors[p].add(task)

    def dfs_preds(t, visited):
        for p in precedence.get(t, []):
            if p not in visited:
                visited.add(p)
                dfs_preds(p, visited)

    def dfs_succs(t, visited):
        for s in successors.get(t, []):
            if s not in visited:
                visited.add(s)
                dfs_succs(s, visited)

    tasks = set(precedence.keys()) | {p for preds in precedence.values() for p in preds}
    for t in tasks:
        preds_set = set()
        dfs_preds(t, preds_set)
        all_preds[t] = preds_set

        succs_set = set()
        dfs_succs(t, succs_set)
        all_succs[t] = succs_set

    return all_preds, all_succs

def topo_resample(seq, precedence):
    """拓扑重采样变异，返回新序列和(原位置, 新位置)"""
    if len(seq) <= 1:
        return seq[:], None

    all_preds, all_succs = compute_transitive_closure(precedence)
    pos = {task: i for i, task in enumerate(seq)}

    t = random.choice(seq)

    left_bound = max([pos[p] for p in all_preds[t]] + [-1]) + 1
    right_bound = min([pos[s] for s in all_succs[t]] + [len(seq)]) - 1

    if right_bound <= left_bound:
        return seq[:], None

    current_pos = pos[t]
    possible_positions = [i for i in range(left_bound, right_bound + 1) if i != current_pos]
    if not possible_positions:
        return seq[:], None

    new_pos = random.choice(possible_positions)

    new_seq = seq[:]
    new_seq.pop(current_pos)
    new_seq.insert(new_pos, t)

    return new_seq, (current_pos, new_pos)

def mutate_assembly_orders(product_library, product_types, assembly_orders, mutation_rate=0.2):
    """
    返回:
      mutated_orders: 变异后的部装顺序
      changes: [(产品编号, 原位置, 新位置), ...] 仅记录发生变异的产品
    """
    mutated_orders = []
    changes = []

    for prod_idx, seq in enumerate(assembly_orders):
        if random.random() >= mutation_rate:
            mutated_orders.append(seq[:])
            continue

        prod_type = product_types[prod_idx]
        type_ops = product_library[prod_type]

        assembly_ops = [op for op in type_ops if op.get('工序类型') == 1]
        assembly_ids = {op['工序编号'] for op in assembly_ops}

        precedence = {}
        for op in assembly_ops:
            preds = [p for p in op.get('前置工序', []) if p in assembly_ids]
            if preds:
                precedence[op['工序编号']] = set(preds)

        new_seq, move_info = topo_resample(seq, precedence)
        mutated_orders.append(new_seq)

        if move_info:
            changes.append((prod_idx, move_info[0], move_info[1]))

    return mutated_orders, changes

def swap_machine_selection(change_positions, assembly_seq, machine_seq):
    """
    根据 change_positions 在 machine_seq 中交换对应位置的值
    :param change_positions: [(产品编号, 原部装序号, 新部装序号), ...]
    :param assembly_seq: assembly_process_sequence_chromosome 列表
    :param machine_seq: process_machine_selection_chromosome 列表
    :return: 修改后的 machine_seq
    """
    machine_seq = machine_seq[:]  # 复制，避免原地修改

    for prod_id, idx_a, idx_b in change_positions:
        # 找到 assembly_seq 中该产品编号的所有位置
        positions = [i for i, pid in enumerate(assembly_seq) if pid == prod_id]
        # print(f"产品 {prod_id} 的全局位置索引: {positions}")
        # print(f"change_positions: {change_positions}")
        # print(f"assembly_seq: {assembly_seq}")
        # input("Press Enter to continue...")

        # 确保索引合法
        if idx_a < len(positions) and idx_b < len(positions):
            pos_a = positions[idx_a]
            pos_b = positions[idx_b]
            # 交换 machine_seq 对应位置的值
            machine_seq[pos_a], machine_seq[pos_b] = machine_seq[pos_b], machine_seq[pos_a]
            # print(f"产品 {prod_id}：交换全局位置 {pos_a} 和 {pos_b} 的机器选择值")
        else:
            print(f"产品 {prod_id} 的部装工序数量不足，无法交换 {idx_a} 和 {idx_b}")

    return machine_seq

def mutate_shuffle_positions(seq, min_ratio=0.1, max_ratio=0.3):
    """
    随机采样位置集合打乱（均等变异机会；不改动长度与元素多重集）
    """
    n = len(seq)
    if n <= 1:
        return seq[:]
    min_k = max(1, int(n * min_ratio))
    max_k = max(min_k, int(n * max_ratio))
    k = random.randint(min_k, max_k)
    k = 2 * k

    # print(k)

    positions = random.sample(range(n), k)

    # print(positions)
    values = [seq[i] for i in positions]
    random.shuffle(values)
    new_seq = seq[:]
    for idx, pos in enumerate(positions):
        new_seq[pos] = values[idx]
    return new_seq

def remap_machine_selection(old_assembly, old_machine, new_assembly):
    """
    根据工序身份映射，生成变异后的机器选择序列
    工序身份 = (产品编号, 出现序号)
    """
    assert len(old_assembly) == len(old_machine) == len(new_assembly)

    # 1) 建立 (产品编号, 出现序号) -> 机器编号 的映射
    mapping = {}
    occ = {}
    for asm, mach in zip(old_assembly, old_machine):
        occ[asm] = occ.get(asm, 0) + 1
        mapping[(asm, occ[asm])] = mach

    # 2) 按新顺序重建机器列表
    new_machine = []
    occ.clear()
    for asm in new_assembly:
        occ[asm] = occ.get(asm, 0) + 1
        new_machine.append(mapping[(asm, occ[asm])])

    return new_machine

def mutate_with_machine_remap_positions(assembly_seq, machine_seq, min_ratio=0.1, max_ratio=0.3):
    """
    先对 assembly_seq 做“随机位置集合打乱”，再按工序身份重映射 machine_seq
    """
    new_assembly = mutate_shuffle_positions(assembly_seq, min_ratio, max_ratio)
    new_machine = remap_machine_selection(assembly_seq, machine_seq, new_assembly)
    return new_assembly, new_machine


def mutate_machine_selection_multi_dynamic(
    machine_seq,
    assembly_seq,
    assembly_orders_per_product,
    product_types,
    product_library,
    min_ratio=0.05,
    max_ratio=0.2
):
    """
    多点机器选择变异（变异数量按比例动态计算）
    """
    n = len(machine_seq)
    new_machine_seq = machine_seq[:]

    if n == 0:
        return new_machine_seq

    # 1. 动态计算变异数量范围
    min_mut = max(1, int(n * min_ratio))
    max_mut = max(min_mut, int(n * max_ratio))

    # 2. 每次随机取一个变异数量
    num_mutations = random.randint(min_mut, max_mut)

    # 3. 随机选变异位置
    mutation_positions = random.sample(range(n), num_mutations)

    # 4. 统计出现次数（确定第几道工序）
    occurrence_count = {}
    for pos in range(n):
        prod_id = assembly_seq[pos]
        occurrence_count[prod_id] = occurrence_count.get(prod_id, 0) + 1

        if pos in mutation_positions:
            step_index = occurrence_count[prod_id] - 1
            process_id = assembly_orders_per_product[prod_id][step_index]
            prod_type = product_types[prod_id]

            # 找到该工序的可用机器集合
            process_info = next(op for op in product_library[prod_type] if op['工序编号'] == process_id)
            available_machines = process_info.get('加工机器', [])

            if available_machines:
                current_machine = new_machine_seq[pos]
                possible_choices = [i for i in range(len(available_machines)) if i != current_machine]
                if possible_choices:
                    new_machine_seq[pos] = random.choice(possible_choices)

    return new_machine_seq


def mutate_shuffle_positions_dual(order_seq, machine_seq, min_ratio=0.2, max_ratio=0.5):
    """
    随机采样位置集合打乱（双列表同步）
    :param order_seq: 工序顺序列表（部装或总装）
    :param machine_seq: 对应的机器选择列表
    :param min_ratio: 最少变异比例
    :param max_ratio: 最大变异比例
    """
    assert len(order_seq) == len(machine_seq), "两个列表长度必须一致"
    n = len(order_seq)
    if n <= 1:
        return order_seq[:], machine_seq[:]

    # 计算变异位置数量范围
    min_k = max(1, int(n * min_ratio))
    max_k = max(min_k, int(n * max_ratio))

    # 随机确定本次变异位置数量
    k = random.randint(min_k, max_k)
    # print("k", k)
    k = 2 * k

    # 随机采样位置集合
    positions = random.sample(range(n), k)
    # print("positions", positions)

    # 提取并打乱
    paired = list(zip(order_seq, machine_seq))
    selected = [paired[i] for i in positions]
    random.shuffle(selected)

    # 放回
    for idx, pos in enumerate(positions):
        paired[pos] = selected[idx]

    # 拆分回两个列表
    new_order_seq, new_machine_seq = zip(*paired)
    return list(new_order_seq), list(new_machine_seq)


def mutate_final_assembly_machine_selection(
    process_seq,
    machine_seq,
    type_list,
    product_library,
    min_ratio=0.1,
    max_ratio=0.3
):
    """
    随机变异总装机器选择列表
    :param process_seq: 总装工序顺序列表（值是产品编号）
    :param machine_seq: 总装机器选择列表（值是加工机器索引）
    :param type_list: 产品编号 -> 产品类型
    :param product_library: 产品类型 -> 工序信息列表
    :param min_ratio: 最少变异比例
    :param max_ratio: 最大变异比例
    """
    n = len(machine_seq)
    new_machine_seq = machine_seq[:]

    # 计算变异数量
    min_k = max(1, int(n * min_ratio))
    max_k = max(min_k, int(n * max_ratio))
    k = random.randint(min_k, max_k)
    # The original pair-oriented count becomes 2 when n == 1, which makes
    # random.sample fail on the minimum validation instance.  Clamping keeps
    # the same operator for ordinary instances and gives the single gene one
    # valid mutation opportunity.
    k = min(n, k * 2)

    # 随机选变异位置
    mutation_positions = random.sample(range(n), k)

    for pos in mutation_positions:
        product_id = process_seq[pos]  # 该位置对应的产品编号
        product_type = type_list[product_id]  # 产品类型

        # 找到该类型产品的最后一道工序（总装工序）
        last_process = product_library[product_type][-1]
        available_machines = last_process.get("加工机器", [])

        if available_machines:
            current_machine_index = new_machine_seq[pos]
            possible_choices = [i for i in range(len(available_machines)) if i != current_machine_index]
            if possible_choices:
                new_machine_seq[pos] = random.choice(possible_choices)

    return new_machine_seq

# product_library = read_csv_files()
# print(
#     product_library
# )
# --------------------------
# 调用示例
# --------------------------
# if __name__ == "__main__":
#     # 加载产品库
#     product_library = read_csv_files()
#
#     # 业务参数
#     product_types = [0, 0, 1, 1, 1, 2, 2]
#     proc_counts = [3, 5, 4]
#     chromosome = [1, 0, 0, 1, 1, 0, 2, 0, 0, 0, 2, 2, 1, 1, 0, 0, 1, 0, 0, 2, 1, 3, 1, 1, 1, 2, 2, 0, 0]
#
#     # 执行变异（仅返回变异后的染色体）
#     mutated_chrom = mutate_chromosome(
#         chromosome=chromosome,
#         product_types=product_types,
#         proc_counts=proc_counts,
#         product_library=product_library,
#         mutation_rate=1
#     )
#
#     # 输出结果
#     print("\n原染色体：", chromosome)
#     print("变异后染色体：", mutated_chrom)
