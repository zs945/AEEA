import csv
import os
from fractions import Fraction

def safe_float(x: str):
    """
    将字符串安全转换为浮点数。
    支持普通数字（'3.5'）、整数（'10'）、分数（'10/3'）。
    """
    x = x.strip()
    if not x:
        return None
    try:
        return float(x)
    except ValueError:
        # 如果是分数形式
        if "/" in x:
            try:
                return float(Fraction(x))
            except Exception:
                raise ValueError(f"无法解析为数字: {x}")
        else:
            raise

def analyze_processes(processes):
    process_info = []
    for process in processes:
        operation_name = process[1]
        predecessors = process[6].split(',') if process[6] else []
        if '采购' in operation_name:
            process_type = 0
            suppliers = process[2].split(',') if process[2] else []
            costs = [safe_float(x) for x in process[3].split(',')] if process[3] else []
            purchase_times = [safe_float(x) for x in process[4].split(',')] if process[4] else []
            process_info.append({
                '工序编号': process[0],
                '工序类型': process_type,
                '供应商': suppliers,
                '单位成本': costs,
                '采购时间': purchase_times,
                '前置工序': predecessors
            })
        elif '部装' in operation_name:
            process_type = 1
            machines = process[2].split(',') if process[2] else []
            processing_times = [safe_float(x) for x in process[5].split(',')] if process[5] else []
            process_info.append({
                '工序编号': process[0],
                '工序类型': process_type,
                '加工机器': machines,
                '加工时间': processing_times,
                '前置工序': predecessors
            })
        elif '总装' in operation_name:
            process_type = 2
            machines = process[2].split(',') if process[2] else []
            processing_times = [safe_float(x) for x in process[5].split(',')] if process[5] else []
            process_info.append({
                '工序编号': process[0],
                '工序类型': process_type,
                '加工机器': machines,
                '加工时间': processing_times,
                '前置工序': predecessors
            })
    return process_info

def read_csv_files():
    product_library = []
    current_dir = os.path.dirname(__file__)
    try:
        # Sort filenames so the product-type index is reproducible on every OS.
        for filename in sorted(os.listdir(current_dir)):
            if filename.endswith('.csv'):
                file_path = os.path.join(current_dir, filename)
                try:
                    processes = []
                    with open(file_path, 'r', encoding='GBK') as file:
                        csv_reader = csv.reader(file)
                        # 跳过表头
                        next(csv_reader)
                        for row in csv_reader:
                            processes.append(row)
                    product_info = analyze_processes(processes)
                    product_library.append(product_info)
                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {e}")
    except FileNotFoundError:
        print(f"错误：未找到文件夹 {current_dir}。")
    return product_library

# if __name__ == "__main__":
#     product_library = read_csv_files()
#     for i, product in enumerate(product_library):
#         print(f"产品 {i + 1} 的工序信息:")
#         for process in product:
#             print(process)
#         print()
