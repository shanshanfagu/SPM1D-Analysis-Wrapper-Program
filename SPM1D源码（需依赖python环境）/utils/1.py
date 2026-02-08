import numpy as np
import pandas as pd

def validate_data_format(data):
    if not isinstance(data, np.ndarray):
        return False, "数据必须是numpy数组"
    if data.ndim != 2:
        return False, f"数据必须是2维数组，当前为{data.ndim}维"
    return True, "数据格式正确"

def format_pvalue(p):
    if p < 0.001:
        return "< 0.001"
    return f"{p:.4f}"

def get_cluster_info(clusters):
    if clusters is None or len(clusters) == 0:
        return []
    cluster_list = []
    for i, cluster in enumerate(clusters):
        cluster_list.append({
            'id': i + 1,
            'start': cluster[0],
            'end': cluster[1],
            'extent': cluster[1] - cluster[0] + 1
        })
    return cluster_list
