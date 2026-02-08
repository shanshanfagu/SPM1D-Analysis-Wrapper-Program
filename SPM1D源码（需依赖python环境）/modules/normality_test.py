import numpy as np
import spm1d

def dagostino_k2_normality(data):
    J, Q = data.shape
    if J < 8:
        return None, "样本量小于8，无法使用K2检验"
    
    try:
        result = spm1d.stats.normality.k2.ttest(data)
        inference_result = result.inference(alpha=0.05)
        
        k2_values = result.z
        if isinstance(k2_values, np.ndarray) and len(k2_values) > 0:
            mean_k2 = np.mean(k2_values)
        else:
            mean_k2 = k2_values
        
        p_value = inference_result.p
        if isinstance(p_value, (list, np.ndarray)) and len(p_value) > 0:
            mean_p = np.mean(p_value)
        else:
            mean_p = p_value
        
        is_normal = not inference_result.h0reject
        
        # 安全获取clusters属性
        try:
            n_clusters = getattr(inference_result, 'nClusters', None)
            if n_clusters is None and hasattr(inference_result, 'clusters'):
                clusters = inference_result.clusters
                if clusters is not None:
                    n_clusters = len(clusters) if isinstance(clusters, (list, tuple, np.ndarray)) else 1
                else:
                    n_clusters = 0
        except:
            n_clusters = None
        
        return {
            'spm_result': result,
            'inference_result': inference_result,
            'k2_statistic': mean_k2,
            'p_value': mean_p,
            'is_normal': is_normal,
            'h0reject': inference_result.h0reject,
            'n_clusters': n_clusters,
            'zstar': inference_result.zstar
        }, None
    except Exception as e:
        return None, str(e)

def recommend_test_method(normality_results, alpha=0.05):
    normal_groups = []
    abnormal_groups = []
    
    for group_name, result in normality_results.items():
        if result is None:
            abnormal_groups.append((group_name, "检验失败"))
        elif 'error' in result:
            abnormal_groups.append((group_name, result.get('error', '检验失败')))
        elif result.get('is_normal'):
            normal_groups.append(group_name)
        else:
            p_val = result.get('p_value', 'N/A')
            if isinstance(p_val, float):
                abnormal_groups.append((group_name, f"p={p_val:.4f}"))
            else:
                abnormal_groups.append((group_name, f"p={p_val}"))
    
    if len(abnormal_groups) == 0:
        recommendation = "param"
        reason = "所有组数据符合正态分布，建议使用参数检验"
    elif len(normal_groups) == 0:
        recommendation = "nonparam"
        reason = "部分/全部组数据不符合正态分布，建议使用非参数检验"
    else:
        recommendation = "nonparam"
        reason = f"部分组不符合正态分布（{', '.join([g[0] for g in abnormal_groups])}），建议使用非参数检验"
    
    return {
        'recommendation': recommendation,
        'reason': reason,
        'normal_groups': normal_groups,
        'abnormal_groups': abnormal_groups
    }

def run_normality_tests(merged_data, alpha=0.05):
    results = {}
    
    for group_name, data in merged_data.items():
        result, error = dagostino_k2_normality(data)
        if error:
            results[group_name] = {'error': error, 'is_normal': None}
        else:
            result['alpha'] = alpha
            results[group_name] = result
    
    recommendation = recommend_test_method(results, alpha)
    
    return {
        'groups': results,
        'recommendation': recommendation,
        'alpha': alpha
    }
