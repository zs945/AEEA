import csv
import os


def analyze_processes(processes):
    process_info = []
    for process in processes:
        operation_name = process[1]
        predecessors = process[6].split(',') if process[6] else []
        if '采购' in operation_name:
            process_type = 0
            suppliers = process[2].split(',') if process[2] else []
            costs = [float(x) for x in process[3].split(',')] if process[3] else []
            purchase_times = [float(x) for x in process[4].split(',')] if process[4] else []
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
            processing_times = [float(x) for x in process[5].split(',')] if process[5] else []
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
            processing_times = [float(x) for x in process[5].split(',')] if process[5] else []
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
        for filename in os.listdir(current_dir):
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


if __name__ == "__main__":
    product_library = read_csv_files()
    for i, product in enumerate(product_library):
        print(f"产品 {i + 1} 的工序信息:")
        for process in product:
            print(process)
        print()
