import os
import pandas as pd
import numpy as np

def load_single_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.csv':
        return pd.read_csv(filepath)
    elif ext in ['.xlsx', '.xls']:
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

def load_group_file(filepath):
    df = load_single_file(filepath)
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] == 0:
        raise ValueError(f"文件 {filepath} 中没有数值列")
    return numeric_df.values

def load_indicator_folder(folder_path):
    groups = {}
    files = [f for f in os.listdir(folder_path)
             if f.endswith(('.csv', '.xlsx', '.xls'))]

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        try:
            group_name = os.path.splitext(filename)[0]
            data = load_group_file(filepath)
            groups[group_name] = data
        except Exception as e:
            print(f"加载文件 {filename} 失败: {str(e)}")

    return groups

def load_data_by_indicator(root_path):
    indicators = {}
    items = os.listdir(root_path)
    
    folders = [item for item in items
               if os.path.isdir(os.path.join(root_path, item))]
    
    files = [f for f in items
             if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    if files and not folders:
        root_name = os.path.basename(root_path) if root_path else "数据"
        groups = load_indicator_folder(root_path)
        if groups:
            indicators[root_name] = groups
    elif folders:
        for folder in folders:
            folder_path = os.path.join(root_path, folder)
            groups = load_indicator_folder(folder_path)
            if groups:
                indicators[folder] = groups
    
    return indicators

def get_column_names(data_dict):
    if not data_dict:
        return []
    first_indicator = list(data_dict.keys())[0]
    first_group = list(data_dict[first_indicator].keys())[0]
    return list(data_dict[first_indicator][first_group].columns) if hasattr(data_dict[first_indicator][first_group], 'columns') else []

def validate_data_structure(data_dict):
    if not data_dict:
        return False, "数据为空"

    for indicator_name, groups in data_dict.items():
        timepoint_counts = {}
        for group_name, data in groups.items():
            timepoint_count = data.shape[1] if len(data.shape) > 1 else 0
            if timepoint_count not in timepoint_counts:
                timepoint_counts[timepoint_count] = []
            timepoint_counts[timepoint_count].append(group_name)

        if len(timepoint_counts) > 1:
            msg = f"指标 {indicator_name} 时间点数不一致:\n"
            for count, groups_list in timepoint_counts.items():
                msg += f"  - {count} 个时间点: {', '.join(groups_list)}\n"
            return False, msg

    return True, "数据结构一致"
