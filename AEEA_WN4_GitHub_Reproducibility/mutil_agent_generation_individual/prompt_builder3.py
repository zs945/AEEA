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
    flat = [[0,x - 1] for sublist in result for x in sublist]
    return flat

def build_prompt_for_llm(target_individual,fitness,num_llm,type_list, purchase_ranges,type_counts):
    prompt = f"""
    产品类型编码规则：
        构造一个一维整数列表 type_list。
        位置索引（list 的下标）表示产品的编号（即第几个产品）。
        该位置的值表示该编号产品所属的产品类型。
    本问题的type_list为{type_list}
    1.采购供应商选择：
        依据type_list中依次对不同编号产品进行采购工序的供应商的选择，比如{type_list}里第0位是0，那么就表示我将要生产的产品的编号为0的产品的产品类型是0，产品类型0的采购工序是3位，那么采购供应商选择段的第0位到第2位就表示我将要生产的产品的编号为0的产品的采购供应商选择。依次类推
        类似{target_individual[0]["采购供应商选择"]}
    2.产品内部的部装工序顺序：
        依据type_list中依次对不同编号产品的部装工序进行排序，比如{type_list}里第0位是0，那么就表示我将要生产的产品的编号为0的产品的产品类型是0，那么我就需要对这个编号为0的产品的部装工序进行排序。依次类推
        类似{target_individual[0]["产品内部的部装工序顺序"]}
    3.部装工序顺序列表：
        依据type_list中依次对不同编号产品的部装工序的加工顺序进行排序，比如类型0的产品的部装工序只有1个，那么在部装工序顺序列表中编号0就只出现1次，出现的位置表示这个编号为0的产品的部装工序的加工顺序。第几次出现表示这个编号产品0的产品内部的部装工序的第几个。依次类推
        类似{target_individual[0]["部装工序顺序列表"]}
    4.部装机器选择列表：
        长度与部装工序顺序列表相等，每个位置的值对应部装工序顺序列表中相同位置的部装工序的加工机器。
        类似{target_individual[0]["部装机器选择列表"]}
    5.总装工序顺序列表：
        依据type_list中依次对不同编号产品的总装工序进行排序，在总装工序顺序列表每一个位置的值表示对应编号产品的总装工序的加工顺序。
        类似{target_individual[0]["总装工序顺序列表"]}
    6.总装机器选择列表：
        长度与总装工序顺序列表相等，每个位置的值对应总装工序顺序列表中相同位置的总装工序的加工机器。
        类似{target_individual[0]["总装机器选择列表"]}     
    请你依据我精英个体的集合{target_individual}和每一个个体对应适应度值{fitness},适应度是越低越好。
    请根据上述结构样本和趋势，提出若干新的完整个体建议，用于探索更优个体。，生成{num_llm}个新的更低成本的个体的六段编码，尽量尝试新的探索。
    约束：
        1.每个采购供应商选择的供应商编号必须在其对应工序采购范围序列中，每一个位置对应编码的取值范围是{purchase_ranges}，这一条绝对不能违反，请仔细检查。
        2.每个产品内部的部装工序顺序必须在符合符合前后加工顺序,并且包含全部的部装工序。
        3.部装工序顺序列表要为全部部装工序进行合理排序，部装工序顺序列表中每一个产品的编号的出现次数列表为{type_counts}，其中位置的索引表示产品的编号，每一个位置的值表示索引对应的产品编号在部装工序顺序列表中出现的次数。
        4.每个部装机器选择列表中的部装机器编号必须在其对应部装工序的部装机器选择列表范围序列中。
        5.总装工序顺序列表要为全部总装工序进行排序。
        5.每个总装机器选择列表中的总装机器编号必须在其对应工序总装机器范围序列中。
    满足以上所有约束条件。
    每一个个体的格式参考{target_individual[0]}，但只能参考格式。
    请输出一个JSON对象，其唯一顶层字段为"individuals"。
    格式为{{"individuals": [个体1，个体2，...，个体{num_llm}]}}，不要包含额外文字。
    """

    return prompt

    # 每一个个体的格式参考{target_individual[0]}
