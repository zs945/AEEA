# from product_information.Initial_processing_of_product_information import read_csv_files
# from collections import Counter, defaultdict
# from collections import Counter, deque
# from typing import List, Dict
#
# product_library = read_csv_files()
# # print("product_library",product_library)
#
# orders = [
#         [0, 3, 4],  # 订单1
#         [2, 0, 3],  # 订单2
#         [2, 0, 0]  # 订单3
#     ]

from typing import List, Dict, Tuple
from collections import defaultdict, deque

def calculate_order_lower_bounds(
    product_library: List[List[Dict]],
    orders: List[List[int]]
) -> Tuple[List[Dict], Dict[str, int]]:
    """
    计算多个订单的理论完成时间下界，并返回机器池信息。

    参数:
        product_library: 产品工序库，每个产品是一个工序列表
        orders: 多个订单，每个订单是产品数量列表

    返回:
        Tuple:
            - 每个订单的下界信息列表 [{'order': [...], 'lower_bound': float}]
            - 机器池信息 {'m_sub': int, 'm_final': int, 'sub_set': set, 'final_set': set}
    """

    def op_duration(op: Dict) -> float:
        return min(op['采购时间']) if op['工序类型'] == 0 else min(op['加工时间'])

    def product_unit_lb(product_ops: List[Dict]) -> float:
        dur = {}
        succ = defaultdict(list)
        indeg = defaultdict(int)
        nodes = []

        for op in product_ops:
            oid = op['工序编号']
            nodes.append(oid)
            dur[oid] = op_duration(op)
            for pre in op.get('前置工序', []):
                succ[pre].append(oid)
                indeg[oid] += 1
            indeg.setdefault(oid, indeg.get(oid, 0))

        dq = deque([n for n in nodes if indeg[n] == 0])
        longest = {n: dur[n] for n in nodes}
        visited = 0
        while dq:
            u = dq.popleft()
            visited += 1
            for v in succ[u]:
                longest[v] = max(longest[v], longest[u] + dur[v])
                indeg[v] -= 1
                if indeg[v] == 0:
                    dq.append(v)
        if visited != len(nodes):
            raise ValueError("工序图包含环，无法计算关键路径")
        return max(longest.values())

    def infer_machine_pool_sizes(library: List[List[Dict]]) -> Dict[str, int]:
        sub_machines = set()
        final_machines = set()
        for ops in library:
            for op in ops:
                if op['工序类型'] == 1:
                    sub_machines.update(op['加工机器'])
                elif op['工序类型'] == 2:
                    final_machines.update(op['加工机器'])
        return {
            'm_sub': len(sub_machines),
            'm_final': len(final_machines),
            'sub_set': sub_machines,
            'final_set': final_machines
        }

    def stage_workloads(order: List[int]) -> Dict[str, float]:
        total_sub, total_final = 0.0, 0.0
        for pid, count in enumerate(order):
            if count == 0:
                continue
            for op in product_library[pid]:
                if op['工序类型'] == 1:
                    total_sub += op_duration(op) * count
                elif op['工序类型'] == 2:
                    total_final += op_duration(op) * count
        return {'sub': total_sub, 'final': total_final}

    def order_lower_bound(order: List[int], product_lb: Dict[int, float], m_sub: int, m_final: int) -> float:
        lb_struct = max(product_lb[pid] for pid, count in enumerate(order) if count > 0)
        workloads = stage_workloads(order)
        lb_load = (workloads['sub'] / m_sub) + (workloads['final'] / m_final)
        return max(lb_struct, lb_load)

    product_lb = {pid: product_unit_lb(ops) for pid, ops in enumerate(product_library)}
    pool_info = infer_machine_pool_sizes(product_library)
    m_sub, m_final = pool_info['m_sub'], pool_info['m_final']

    results = []
    for order in orders:
        lb = order_lower_bound(order, product_lb, m_sub, m_final)
        results.append({'order': order, 'lower_bound': round(lb, 2)})

    return results, pool_info

# results, pool_info = calculate_order_lower_bounds(product_library, orders)

# print(results)
# print(results[2]["lower_bound"])
# print(type(results[2]["lower_bound"]))
# print(pool_info)
#
# for i, res in enumerate(results, 1):
#     print(f"订单{i} 的需求: {res['order']}")
#     print(f"订单{i} 的理论完成时间下界: {res['lower_bound']} (m_sub={pool_info['m_sub']}, m_final={pool_info['m_final']})")