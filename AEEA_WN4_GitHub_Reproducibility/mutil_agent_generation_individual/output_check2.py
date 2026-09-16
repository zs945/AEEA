from collections import Counter
import random
# print(purchase_ranges)
# print(order_list)
# print(type_list)
# print(product_library)
# print(product_library)


# raw1 = [{'采购供应商选择': [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 2, 0, 2, 1, 1, 2, 1, 1, 1, 0, 2, 2, 3, 2, 0, 2, 2, 2, 0, 0, 1, 1, 3, 2, 0, 0, 0, 2, 2, 0, 2, 1, 2, 0, 1, 3, 1, 0, 1, 3, 2, 0, 1, 3, 2, 1, 0, 2, 2, 1, 0, 1, 1, 0, 2], '产品内部的部装工序顺序': [['4'], ['4'], ['4'], ['4'], ['4'], ['4'], ['4'], ['6', '7', '8'], ['7', '6', '8'], ['7', '6', '8'], ['6', '7', '8'], ['6', '7', '8'], ['6', '7', '8'], ['5', '6'], ['5', '6'], ['6', '5'], ['5', '6'], ['5', '6'], ['6', '5'], ['5', '6']], '部装工序顺序列表': [11, 7, 15, 10, 6, 10, 16, 8, 8, 13, 9, 4, 2, 14, 11, 18, 14, 11, 9, 13, 7, 12, 1, 0, 17, 18, 9, 10, 7, 19, 12, 12, 5, 8, 19, 16, 3, 15, 17], '部装机器选择列表': [2, 2, 1, 1, 1, 2, 0, 2, 1, 1, 0, 2, 1, 0, 0, 1, 2, 0, 1, 0, 2, 0, 0, 2, 1, 0, 1, 0, 2, 1, 2, 1, 1, 2, 0, 1, 0, 0, 0], '总装工序顺序列表': [4, 2, 15, 17, 6, 3, 13, 9, 8, 5, 10, 1, 16, 12, 19, 7, 11, 18, 0, 14], '总装机器选择列表': [1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0]}, {'采购供应商选择': [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 2, 0, 2, 2, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 3, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 2, 0, 0, 1, 3, 1, 0, 0, 2, 2, 0, 0, 2, 1, 0, 2, 3, 2, 0, 2, 0, 2, 1, 0], '产品内部的部装工序顺序': [['4'], ['4'], ['4'], ['4'], ['4'], ['4'], ['4'], ['6', '7', '8'], ['7', '6', '8'], ['6', '7', '8'], ['7', '6', '8'], ['6', '7', '8'], ['6', '7', '8'], ['5', '6'], ['5', '6'], ['5', '6'], ['6', '5'], ['6', '5'], ['5', '6'], ['6', '5']], '部装工序顺序列表': [17, 12, 8, 10, 6, 9, 16, 13, 11, 16, 18, 14, 3, 18, 9, 8, 2, 14, 8, 12, 7, 0, 11, 11, 15, 10, 7, 12, 1, 13, 9, 17, 15, 10, 7, 4, 5, 19, 19], '部装机器选择列表': [2, 0, 0, 0, 0, 2, 2, 2, 1, 0, 0, 1, 1, 2, 0, 0, 1, 2, 1, 1, 1, 1, 0, 2, 0, 0, 0, 0, 0, 2, 2, 2, 1, 0, 0, 0, 0, 0, 1], '总装工序顺序列表': [0, 17, 7, 11, 12, 16, 9, 13, 3, 14, 1, 4, 19, 10, 8, 15, 5, 18, 6, 2], '总装机器选择列表': [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1]}, {'采购供应商选择': [0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 2, 2, 0, 2, 0, 2, 2, 2, 0, 0, 1, 1, 1, 0, 1, 2, 0, 2, 0, 0, 1, 1, 0, 2, 0, 1, 2, 3, 2, 1, 0, 2, 0, 1, 2, 1, 2, 0, 0, 0, 1, 1, 2, 1, 2, 1, 0, 1, 2, 1, 0, 3, 0, 1, 0], '产品内部的部装工序顺序': [['4'], ['4'], ['4'], ['4'], ['4'], ['4'], ['4'], ['7', '6', '8'], ['7', '6', '8'], ['6', '7', '8'], ['7', '6', '8'], ['6', '7', '8'], ['7', '6', '8'], ['6', '5'], ['5', '6'], ['6', '5'], ['5', '6'], ['6', '5'], ['5', '6'], ['5', '6']], '部装工序顺序列表': [9, 9, 14, 7, 19, 12, 1, 11, 15, 9, 19, 11, 8, 8, 14, 17, 13, 3, 13, 12, 16, 8, 7, 17, 4, 11, 10, 16, 2, 0, 7, 5, 18, 18, 6, 10, 10, 15, 12], '部装机器选择列表': [0, 2, 0, 1, 2, 2, 0, 1, 2, 0, 2, 0, 2, 0, 2, 1, 2, 1, 2, 0, 2, 1, 1, 0, 2, 1, 1, 0, 2, 1, 0, 2, 0, 2, 2, 2, 0, 0, 0], '总装工序顺序列表': [1, 17, 9, 4, 18, 19, 8, 11, 16, 15, 3, 0, 13, 12, 5, 2, 6, 7, 10, 14], '总装机器选择列表': [0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]}]
# print(raw1[0]["产品内部的部装工序顺序"])

# def check_supplier_choices(choices, purchase_ranges):
#     if len(choices) != len(purchase_ranges):
#         print(f"长度不一致：choices={len(choices)}, purchase_ranges={len(purchase_ranges)}")
#         return False
#
#     for idx, (val, range_pair) in enumerate(zip(choices, purchase_ranges)):
#         min_val, max_val = range_pair
#         if not (min_val <= val <= max_val):
#             print(f"位置 {idx} 的值 {val} 超出范围 [{min_val}, {max_val}]")
#             return False
#     return True

# def check_supplier_choices(choices, purchase_ranges):
#     if len(choices) != len(purchase_ranges):
#         print(f"❌ 长度不一致：choices={len(choices)}, purchase_ranges={len(purchase_ranges)}")
#         return False, None
#
#     fixed_choices = choices.copy()
#     # modified = False
#
#     for idx, (val, (min_val, max_val)) in enumerate(zip(choices, purchase_ranges)):
#         if not (min_val <= val <= max_val):
#             new_val = random.randint(min_val, max_val)
#             # print(f"⚠️ 位置 {idx} 的值 {val} 超出范围 [{min_val}, {max_val}]，已替换为 {new_val}")
#             fixed_choices[idx] = new_val
#             # modified = True
#
#     return True, fixed_choices

def check_supplier_choices(choices, purchase_ranges):
    """
    验证并修复采购供应商选择列表
    - choices: 原始选择列表
    - purchase_ranges: 每个位置允许的供应商编号范围 [min, max]
    返回:
        (False, None) → 无法修复
        (True, 原始列表) → 全部合法
        (True, 修正后列表) → 已修复
    """
    if not isinstance(choices, list) or not isinstance(purchase_ranges, list):
        print("⚠️ 输入类型错误")
        return False, None

    expected_len = len(purchase_ranges)
    fixed_choices = choices.copy()

    # 如果长度不一致，先补齐或截断
    if len(fixed_choices) < expected_len:
        # print(f"❌ 长度不足：choices={len(fixed_choices)}, 需要={expected_len}")
        for i in range(len(fixed_choices), expected_len):
            min_val, max_val = purchase_ranges[i]
            fixed_choices.append(random.randint(min_val, max_val))
    elif len(fixed_choices) > expected_len:
        # print(f"❌ 长度过长：choices={len(fixed_choices)}, 需要={expected_len}")
        fixed_choices = fixed_choices[:expected_len]

    # 修复范围错误
    modified = False
    for idx, (val, (min_val, max_val)) in enumerate(zip(fixed_choices, purchase_ranges)):
        if not (min_val <= val <= max_val):
            new_val = random.randint(min_val, max_val)
            fixed_choices[idx] = new_val
            modified = True

    return True, fixed_choices if modified or len(choices) != expected_len else choices

#
# def check_single_sequence(product_library, sequence, product_type):
#     """
#     检查某个产品的部装工序顺序是否合理
#     - 只允许类型1工序出现在 sequence 中
#     - 类型1工序必须等前置工序完成后才能执行
#     - sequence 是一个列表，例如 ['8','7','6']
#     """
#     product = product_library[product_type]
#     proc_map = {p["工序编号"]: p for p in product}
#
#     # 初始化完成集：类型0工序默认完成（但不允许出现在 sequence 中）
#     finished = {p["工序编号"] for p in product if p.get("工序类型") == 0}
#
#     for idx, process_id in enumerate(sequence):
#         proc = proc_map.get(process_id)
#         if proc is None:
#             return False, {
#                 "step": idx,
#                 "process_id": process_id,
#                 "reason": f"工序 {process_id} 在产品 {product_type} 中不存在"
#             }
#
#         # 🚩 如果不是类型1，直接报错
#         if proc.get("工序类型") != 1:
#             return False, {
#                 "step": idx,
#                 "process_id": process_id,
#                 "reason": f"工序 {process_id} 类型为 {proc.get('工序类型')}，不是部装工序(1)",
#                 "sequence": sequence,
#                 "product_type": product_type
#             }
#
#         # 类型1工序必须检查前置
#         prereqs = proc.get("前置工序", [])
#         missing = [pre for pre in prereqs if pre not in finished]
#         if missing:
#             return False, {
#                 "step": idx,
#                 "process_id": process_id,
#                 "reason": f"前置工序未完成: {missing}",
#                 "sequence": sequence,
#                 "product_type": product_type
#             }
#
#         # 检查通过 → 加入完成集
#         finished.add(process_id)
#
#     return True, None
#
# def check_all_sequences(product_library, type_list, item):
#     """
#     检查所有产品的部装工序顺序是否合理
#     - 每个产品单独检查
#     - 调用 check_single_sequence 逐个验证
#     - 如果某个产品不合格 -> 立即返回 False
#     - 如果全部合格 -> 返回 True
#     """
#
#     # 基础防御性检查
#     if not isinstance(item, list):
#         print("⚠️ item 不是列表:", type(item))
#         return False
#     if len(item) < len(type_list):
#         print(f"⚠️ 长度不匹配: len(item)={len(item)}, len(type_list)={len(type_list)}")
#         return False
#     n_products = len(product_library)
#     passed_count = 0
#
#     for product_type in range(n_products):
#         # 找到属于该产品的所有组
#         product_groups = [item[i] for i, t in enumerate(type_list) if t == product_type]
#
#         # 逐组调用 check_single_sequence
#         for idx, seq in enumerate(product_groups):
#             ok, err = check_single_sequence(product_library, seq, product_type)
#             if not ok:
#                 # 发现错误，立即返回
#                 return False
#
#         # 如果该产品所有组都通过，计数+1
#         passed_count += 1
#
#     # 所有产品都通过
#     # return True, {"passed_products": passed_count, "total_products": n_products}
#     return True

def check_single_sequence(product_library, sequence, product_type):
    product = product_library[product_type]
    proc_map = {p["工序编号"]: p for p in product}
    finished = {p["工序编号"] for p in product if p.get("工序类型") == 0}

    for idx, process_id in enumerate(sequence):
        proc = proc_map.get(process_id)
        if proc is None or proc.get("工序类型") != 1:
            return False
        prereqs = proc.get("前置工序", [])
        if any(pre not in finished for pre in prereqs):
            return False
        finished.add(process_id)
    return True

def fix_sequence(product_library, sequence, product_type):
    product = product_library[product_type]
    proc_map = {p["工序编号"]: p for p in product}
    type1_procs = [p["工序编号"] for p in product if p.get("工序类型") == 1]

    # 构建依赖图
    from collections import defaultdict, deque
    graph = defaultdict(list)
    indegree = defaultdict(int)
    for pid in type1_procs:
        for pre in proc_map[pid].get("前置工序", []):
            if pre in type1_procs:
                graph[pre].append(pid)
                indegree[pid] += 1

    # 拓扑排序
    queue = deque([p for p in type1_procs if indegree[p] == 0])
    sorted_seq = []
    while queue:
        current = queue.popleft()
        sorted_seq.append(current)
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return sorted_seq

def validate_and_fix_all_sequences(product_library, type_list, item):
    """
    验证并修复所有产品的部装工序顺序列表
    - 确保每个产品的所有部装工序都完整覆盖
    - 返回统一结构：(False, None) / (True, 原始列表) / (True, 修正后列表)
    """
    if not isinstance(item, list) or not isinstance(type_list, list):
        print("⚠️ 输入类型错误")
        return False, None

    fixed = []
    modified = False
    total = len(type_list)

    for i in range(total):
        product_type = type_list[i]
        product = product_library[product_type]
        type1_procs = [p["工序编号"] for p in product if p.get("工序类型") == 1]

        # 获取当前序列
        seq = item[i] if i < len(item) else []

        # 如果不是列表或为空，直接修复
        if not isinstance(seq, list) or not seq:
            new_seq = fix_sequence(product_library, [], product_type)
            fixed.append(new_seq)
            modified = True
            continue

        # 检查是否包含所有部装工序
        seq_set = set(seq)
        missing = [pid for pid in type1_procs if pid not in seq_set]

        if missing or not check_single_sequence(product_library, seq, product_type):
            # 修复：用 fix_sequence 生成完整合法顺序
            new_seq = fix_sequence(product_library, seq, product_type)
            fixed.append(new_seq)
            modified = True
        else:
            fixed.append(seq)

    return True, fixed if modified or len(item) != total else item

def build_assembly_count_list(product_library, type_list):
    """
    输入:
        product_library: 列表，每个元素是一个产品的工序信息
        type_list: 列表，长度 = 产品总数
    输出:
        一个列表，长度与 type_list 相同，
        每个位置的值表示该产品编号对应的部装工序数量
    """

    result = []
    for processes in product_library:
        assembly_count = sum(1 for p in processes if p.get("工序类型") == 1)
        result.append(assembly_count)

    return [result[t] for t in type_list]


# def check_sequence(sequence, expected_counts):
#     """
#     检查 sequence 中每个产品编号出现的次数是否与 expected_counts 对应
#     输入:
#         sequence: 部装工序顺序列表 (list[int])
#         expected_counts: 列表，索引=产品编号，值=该产品应出现的次数
#     输出:
#         (是否一致, 实际统计, 差异信息)
#     """
#     # 实际统计
#     actual_counts = Counter(sequence)
#
#     # 构造完整的实际次数列表（长度与 expected_counts 一致）
#     actual_list = [actual_counts.get(i, 0) for i in range(len(expected_counts))]
#
#     # 检查是否一致
#     is_match = (actual_list == expected_counts)
#
#     # 找出差异
#     diffs = []
#     for i, (a, e) in enumerate(zip(actual_list, expected_counts)):
#         if a != e:
#             diffs.append((i, a, e))  # (产品编号, 实际次数, 期望次数)
#
#     return is_match

def validate_and_fix_sequence(sequence, expected_counts):
    """
    验证并修复产品编号统计是否符合预期
    返回值结构：
        (False, None) → 输入错误，无法修复
        (True, 原始列表) → 全部合法
        (True, 修正后列表) → 有不合法项已修正
    """
    if not isinstance(sequence, list) or not isinstance(expected_counts, list):
        print("⚠️ 输入类型错误")
        return False, None

    max_id = len(expected_counts) - 1

    # 过滤非法编号
    filtered = [x for x in sequence if isinstance(x, int) and 0 <= x <= max_id]

    actual_counts = Counter(filtered)
    actual_list = [actual_counts.get(i, 0) for i in range(len(expected_counts))]

    if actual_list == expected_counts:
        return True, filtered  # 全部合法

    # 修复数量
    fixed = []
    for product_id, expected in enumerate(expected_counts):
        current = actual_counts.get(product_id, 0)
        if current < expected:
            fixed.extend([product_id] * (expected - current))
        elif current > expected:
            # 删除多余项（从 filtered 中随机删）
            count_to_remove = current - expected
            removed = 0
            for i in range(len(filtered)):
                if filtered[i] == product_id and removed < count_to_remove:
                    filtered[i] = None
                    removed += 1

    cleaned = [x for x in filtered if x is not None]
    result = cleaned + fixed

    return True, result


def check_machine_choose(machine_choose, internal_sequence, sequence, product_library, type_list):
    """
    检查并修复机器选择是否合理
    - machine_choose[i] 表示第 i 步选择的机器编号
    - sequence[i] 表示第 i 步对应的产品编号
    - internal_sequence[product] 给出该产品的部装工序顺序
    - product_library + type_list 用来查找工序定义和可用机器
    返回:
        (False, None) → 无法修复
        (True, 原始 machine_choose) → 全部合法
        (True, 修正后的 machine_choose) → 有不合法项已修复
    """
    if not isinstance(machine_choose, list) or not isinstance(sequence, list):
        print("⚠️ 输入类型错误")
        return False, None

    fixed = machine_choose.copy()
    modified = False
    product_counter = {}

    # 补齐长度不足
    if len(fixed) < len(sequence):
        print(f"⚠️ 长度不足：machine_choose={len(fixed)}, sequence={len(sequence)}")
        for i in range(len(fixed), len(sequence)):
            prod_id = sequence[i]
            count = product_counter.get(prod_id, 0) + 1
            product_counter[prod_id] = count
            product_type = type_list[prod_id]
            process_id = internal_sequence[prod_id][count - 1]
            proc_index = int(process_id) - 1
            machine_list = product_library[product_type][proc_index].get("加工机器", [])
            fixed.append(random.randint(0, len(machine_list) - 1) if machine_list else -1)
        modified = True
    elif len(fixed) > len(sequence):
        print(f"⚠️ 长度过长：machine_choose={len(fixed)}, sequence={len(sequence)}")
        fixed = fixed[:len(sequence)]
        modified = True

    # 重置计数器再检查每一步合法性
    product_counter.clear()
    for i in range(len(sequence)):
        prod_id = sequence[i]
        count = product_counter.get(prod_id, 0) + 1
        product_counter[prod_id] = count

        product_type = type_list[prod_id]
        try:
            process_id = internal_sequence[prod_id][count - 1]
            proc_index = int(process_id) - 1
            proc_list = product_library[product_type]

            if proc_index >= len(proc_list):
                return False, {
                    "step": i,
                    "product_id": prod_id,
                    "process_id": process_id,
                    "reason": f"工序编号 {process_id} 超出产品类型 {product_type} 的工序定义范围"
                }

            machine_list = proc_list[proc_index].get("加工机器", [])
            if not (0 <= fixed[i] < len(machine_list)):
                fixed[i] = random.randint(0, len(machine_list) - 1) if machine_list else -1
                modified = True

        except Exception as e:
            return False, {
                "step": i,
                "product_id": prod_id,
                "reason": f"异常错误: {str(e)}"
            }

    return True, fixed if modified else machine_choose

def check_finalmachine_choose(machine_choose, sequence, product_library, type_list):
    """
    检查并修复最终工序的机器选择是否合理
    - machine_choose[i] 表示第 i 步选择的机器编号
    - sequence[i] 表示第 i 步对应的产品编号
    - product_library + type_list 用来查找工序定义和可用机器
    返回:
        (False, None) → 无法修复
        (True, 原始 machine_choose) → 全部合法
        (True, 修正后的 machine_choose) → 有不合法项已修复
    """
    if not isinstance(machine_choose, list) or not isinstance(sequence, list):
        print("⚠️ 输入类型错误")
        return False, None

    fixed = machine_choose.copy()
    modified = False

    # 补齐长度不足
    if len(fixed) < len(sequence):
        print(f"⚠️ 长度不足：machine_choose={len(fixed)}, sequence={len(sequence)}")
        for i in range(len(fixed), len(sequence)):
            prod_id = sequence[i]
            product_type = type_list[prod_id]
            machine_list = product_library[product_type][-1].get("加工机器", [])
            fixed.append(random.randint(0, len(machine_list) - 1) if machine_list else -1)
        modified = True
    elif len(fixed) > len(sequence):
        print(f"⚠️ 长度过长：machine_choose={len(fixed)}, sequence={len(sequence)}")
        fixed = fixed[:len(sequence)]
        modified = True

    # 检查每一步是否合法
    for i in range(len(sequence)):
        prod_id = sequence[i]
        product_type = type_list[prod_id]
        machine_list = product_library[product_type][-1].get("加工机器", [])

        if not (0 <= fixed[i] < len(machine_list)):
            fixed[i] = random.randint(0, len(machine_list) - 1) if machine_list else -1
            modified = True

    return True, fixed if modified else machine_choose

# def check_final_sequence(seq, type_list):
#     return sorted(seq) == list(range(len(type_list)))
def check_final_sequence(seq, type_list):
    """
    验证并修复最终工序顺序列表
    - seq: 原始顺序列表（如总装工序顺序）
    - type_list: 产品类型列表，用于确定应有的编号范围
    返回:
        (False, None) → 无法修复
        (True, 原始列表) → 全部合法
        (True, 修正后列表) → 已修复
    """
    if not isinstance(seq, list) or not isinstance(type_list, list):
        print("⚠️ 输入类型错误")
        return False, None

    expected_ids = set(range(len(type_list)))
    actual_ids = Counter(seq)

    # 如果完全匹配，直接返回
    if sorted(seq) == sorted(expected_ids):
        return True, seq

    # 去重：保留第一次出现的合法编号
    seen = set()
    fixed = []
    for val in seq:
        if val in expected_ids and val not in seen:
            fixed.append(val)
            seen.add(val)

    # 随机补全缺失编号
    missing = list(expected_ids - seen)
    random.shuffle(missing)
    fixed.extend(missing)

    return True, fixed


def check_response(raw, product_library, type_list, purchase_ranges, type_counts):
    result = []

    if isinstance(raw, list):
        if raw == []:
            return []
        if isinstance(raw[0], dict):
            for item in raw:
                check1, fixed_choices = check_supplier_choices(item["采购供应商选择"], purchase_ranges)
                # check1 = check_supplier_choices(item["采购供应商选择"], purchase_ranges)
                # print("采购供应商选择检查:", check1)
                if check1 == False:
                    continue
                if check1 == True:
                    item["采购供应商选择"] = fixed_choices

                check2, fixed_choices2 = validate_and_fix_all_sequences(product_library, type_list, item["产品内部的部装工序顺序"])

                # print("部装工序顺序检查:", check2)
                if check2 == False:
                    continue
                if check2 == True:
                    item["产品内部的部装工序顺序"] = fixed_choices2

                # check3 = check_sequence(item["部装工序顺序列表"], type_counts)
                check3, fixed_choices3 = validate_and_fix_sequence(item["部装工序顺序列表"], type_counts)
                # print("type_counts",type_counts)
                # print("type_list",type_list)

                # print("部装工序顺序列表检查:", check3)
                if check3 == False:
                    continue
                if check3 == True:
                    item["部装工序顺序列表"] = fixed_choices3

                # print("产品内部的部装工序顺序:", item["产品内部的部装工序顺序"])
                # print("部装工序顺序列表:", item["部装工序顺序列表"])
                # print("部装机器选择列表:", item["部装机器选择列表"])

                check4, fixed_choices4 = check_machine_choose(item["部装机器选择列表"], item["产品内部的部装工序顺序"], item["部装工序顺序列表"],product_library, type_list)

                # print("部装机器选择列表检查:", check4)
                if check4 == False:
                    continue
                if check4 == True:
                    item["部装机器选择列表"] = fixed_choices4

                check5, fixed_choices5 = check_final_sequence(item["总装工序顺序列表"], type_list)

                # print("总装工序顺序列表:", check5)
                if check5 == False:
                    continue
                if check5 == True:
                    item["总装工序顺序列表"] = fixed_choices5

                check6, fixed_choices6 = check_finalmachine_choose(item["总装机器选择列表"], item["总装工序顺序列表"], product_library, type_list)

                # print("总装机器选择列表检查:", check6)
                if check6 == False:
                    continue
                if check6 == True:
                    item["总装机器选择列表"] = fixed_choices6
                if check1 == True and check2 == True and check3 == True and check4 == True and check5 == True and check6 == True:
                    result.append(item)

            return result
    else:
        return []

# result = check_response(raw1)
#
# print("符合要求的个体:", result)
# print("符合要求的个体几个:", len(result))





# sequence = ['7','8']
# ok, err = check_single_sequence(product_library, sequence, product_type=1)
# print(ok, err)
