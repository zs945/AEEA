import json
import requests
# from product_information.Initial_processing_of_product_information import read_csv_files
# from paper_six_wn1.Initial_processing_of_product_information import read_csv_files
# from paper_six_wn2.Initial_processing_of_product_information import read_csv_files
# from paper_six_wn3.Initial_processing_of_product_information import read_csv_files
from paper_six_wn4.Initial_processing_of_product_information import read_csv_files
from mutil_agent_generation_individual.theoretical_lower_bound import calculate_order_lower_bounds
Product_library = read_csv_files()
# print(product_library)


product_library = Product_library
# ordersss = [
#         [0, 3, 4],  # 订单1
#         [2, 0, 3],  # 订单2
#         [5, 3, 0]  # 订单3
#     ]
ordersss = [
        [2, 3, 0, 0, 0, 0], # 订单1
        [3, 4, 0, 0, 0, 0], # 订单2
        [0, 0, 3, 4, 0, 0], # 订单3
        [0, 0, 0, 0, 4, 5]  # 订单4
    ]

results, pool_info = calculate_order_lower_bounds(product_library, ordersss)

# 这是不同订单交付延期的单位时间内的违约成本
# order_delay_costss = [70, 100, 130]
order_delay_costss = [70, 100, 130, 160]

# 这是不同产品的单位时间仓库成本
product_Warehousing_Costss = [4, 3, 9, 8, 12, 14]

# 这是不同订单的截止时间
order_Deadliness = [results[i]["lower_bound"] for i in range(len(results))]
# print(order_Deadliness)



ELITE_RATIO = 0.2
LLM_GUIDED_RATIO = 0.3

def generate_product_mappings(orders):
    """
    生成产品编号对应的所属订单和产品类型列表

    参数:
        orders: 订单列表，每个子列表表示订单中各产品类型的采购量

    返回:
        order_list: 索引为产品编号，值为所属订单索引
        type_list: 索引为产品编号，值为产品类型
    """
    order_list = []
    type_list = []
    current_product_id = 0

    # 按产品类型(0→1→2)和订单顺序遍历
    for product_type in range(len(orders[0])):  # 自动适配产品类型数量
        for order_idx, order in enumerate(orders):
            count = order[product_type]
            # 为每个产品添加信息到列表
            for _ in range(count):
                order_list.append(order_idx)  # 订单索引（0开始）
                type_list.append(product_type)
                current_product_id += 1

    return order_list, type_list

order_list, type_list = generate_product_mappings(ordersss)

def get_purchase_ranges(type_list, product_library):
    """
    根据产品类型列表和产品库，生成采购段范围序列
    :param type_list: 每个产品的类型列表，例如 [0,0,1,2,...]
    :param product_library: 各类型产品的工序库
    :return: 采购段范围序列（list of list）
    """
    # 先为每个产品类型预计算采购段范围
    type_to_range = {}
    for t, processes in enumerate(product_library):
        ranges = []
        for proc in processes:
            if proc['工序类型'] == 0:  # 只取采购工序
                ranges.append(len(proc['供应商']))
        type_to_range[t] = ranges

    # 按照 type_list 展开
    result = [type_to_range[t] for t in type_list]
    flat = [x for sublist in result for x in sublist]
    return flat

purchase_ranges = get_purchase_ranges(type_list, product_library)
# print(purchase_ranges)
