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

def scan_folder_files(root_path):
    """
    扫描文件夹获取文件基本信息（不加载数据内容）
    返回：[{name, rows, cols, filepath}, ...]
    """
    files_info = []
    files = [f for f in os.listdir(root_path)
             if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    for filename in files:
        filepath = os.path.join(root_path, filename)
        try:
            df = load_single_file(filepath)
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] == 0:
                continue
            group_name = os.path.splitext(filename)[0]
            files_info.append({
                'name': group_name,
                'rows': numeric_df.shape[0],
                'cols': numeric_df.shape[1],
                'filepath': filepath
            })
        except Exception as e:
            print(f"扫描文件 {filename} 失败: {str(e)}")
    
    return files_info

def load_selected_files(root_path, selected_files):
    """
    加载用户选择的文件
    selected_files: [{name, rows, cols, filepath}, ...]
    返回: {indicator_name: {group_name: data_array}}
    """
    indicators = {}
    groups = {}
    
    for file_info in selected_files:
        try:
            data = load_group_file(file_info['filepath'])
            groups[file_info['name']] = data
        except Exception as e:
            print(f"加载文件 {file_info['name']} 失败: {str(e)}")
    
    if groups:
        root_name = os.path.basename(root_path) if root_path else "Data"
        indicators[root_name] = groups
    
    return indicators
