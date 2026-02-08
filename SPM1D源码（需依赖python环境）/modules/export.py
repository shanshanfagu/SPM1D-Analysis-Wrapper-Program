import os
import pandas as pd
import numpy as np


def create_spm_curve_df(spm_result, inference_result):
    """创建SPM主曲线DataFrame"""
    z_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, z_val in enumerate(z_values):
        significant = 'Yes' if zstar and abs(z_val) > zstar else 'No'
        rows.append({
            'Time_Point': i,
            'SPM_Value': z_val,
            'Threshold': zstar if zstar else '',
            'Above_Threshold': significant
        })
    return pd.DataFrame(rows)


def create_k2_curve_df(group_name, spm_result, inference_result):
    """创建K2曲线DataFrame"""
    k2_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, k2_val in enumerate(k2_values):
        significant = 'Yes' if zstar and k2_val > zstar else 'No'
        rows.append({
            'Time_Point': i,
            f'{group_name}_K2': k2_val,
            f'{group_name}_Threshold': zstar if zstar else '',
            f'{group_name}_Above_Threshold': significant
        })
    return pd.DataFrame(rows)


def create_posthoc_curve_df(pair_name, spm_result, inference_result):
    """创建事后检验曲线DataFrame"""
    spm_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, spm_val in enumerate(spm_values):
        significant = 'Yes' if zstar and abs(spm_val) > zstar else 'No'
        rows.append({
            'Time_Point': i,
            f'{pair_name}': spm_val,
            f'{pair_name}_Threshold': zstar if zstar else '',
            f'{pair_name}_Above_Threshold': significant
        })
    return pd.DataFrame(rows)


def create_regress_curve_df(spm_result, inference_result, beta_slope=None, beta_intercept=None, r_curve=None):
    """创建简单回归完整曲线DataFrame（包含SPM、beta斜率、beta截距、相关系数）"""
    z_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, z_val in enumerate(z_values):
        significant = 'Yes' if zstar and abs(z_val) > zstar else 'No'
        row = {
            'Time_Point': i,
            'SPM_Value': z_val,
            'Threshold': zstar if zstar else '',
            'Above_Threshold': significant
        }
        if beta_slope is not None:
            row['Beta_Slope'] = beta_slope[i] if i < len(beta_slope) else ''
        if beta_intercept is not None:
            row['Beta_Intercept'] = beta_intercept[i] if i < len(beta_intercept) else ''
        if r_curve is not None:
            row['r_Correlation'] = r_curve[i] if i < len(r_curve) else ''
        rows.append(row)
    return pd.DataFrame(rows)


def export_all_to_xlsx(summary, normality_results, posthoc_summary,
                       cached_spm_result, cached_inference_result,
                       cached_posthoc_results, filepath):
    """导出全部数据到Excel文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        if summary:
            summary_df = pd.DataFrame([
                {'参数': '分析类型', '值': summary.get('test_type', 'N/A')},
                {'参数': '方法', '值': '参数检验' if summary.get('method') == 'param' else '非参数检验'},
                {'参数': '显著性水平', '值': summary.get('alpha', 'N/A')},
                {'参数': '临界阈值', '值': f"{summary.get('zstar', 'N/A'):.4f}" if summary.get('zstar') else 'N/A'},
                {'参数': 'H0拒绝', '值': '是' if summary.get('h0reject') else '否'},
                {'参数': '聚类数', '值': summary.get('n_clusters', 0)}
            ])
            summary_df.to_excel(writer, sheet_name='总报告', index=False, startrow=0, startcol=0)

        if cached_spm_result and cached_inference_result:
            test_type = summary.get('test_type', '') if summary else ''
            if test_type == 'regress':
                beta_slope = summary.get('beta_slope')
                beta_intercept = summary.get('beta_intercept')
                r_curve = summary.get('r')
                regress_df = create_regress_curve_df(cached_spm_result, cached_inference_result, beta_slope, beta_intercept, r_curve)
                regress_df.to_excel(writer, sheet_name='主效应检验结果', index=False, startrow=0, startcol=0)
            else:
                spm_df = create_spm_curve_df(cached_spm_result, cached_inference_result)
                spm_df.to_excel(writer, sheet_name='主效应检验结果', index=False, startrow=0, startcol=0)

        normality_summary_rows = []
        k2_dfs = []

        if normality_results and 'groups' in normality_results:
            for group_name, result in normality_results['groups'].items():
                normality_summary_rows.append({
                    '组别': group_name,
                    '检验方法': "D'Agostino K²",
                    '结论': '不支持' if 'error' in result else ('符合正态分布' if result.get('is_normal') else '不符合正态分布')
                })

            for group_name, result in normality_results['groups'].items():
                if 'error' in result:
                    continue
                spm_result = result.get('spm_result')
                inference_result = result.get('inference_result')
                if spm_result is not None:
                    k2_df = create_k2_curve_df(group_name, spm_result, inference_result)
                    k2_dfs.append(k2_df)

            if normality_summary_rows:
                summary_k2_df = pd.DataFrame(normality_summary_rows)
                summary_k2_df.to_excel(writer, sheet_name='正态分布结果', index=False, startrow=0, startcol=0)

            if k2_dfs:
                merged_k2 = k2_dfs[0]
                for df in k2_dfs[1:]:
                    merged_k2 = pd.merge(merged_k2, df, on='Time_Point', how='outer')
                merged_k2.to_excel(writer, sheet_name='正态分布结果', index=False, startrow=len(normality_summary_rows) + 2, startcol=0)

        posthoc_summary_rows = []
        posthoc_dfs = []

        if posthoc_summary and cached_posthoc_results:
            for pair_name, result in posthoc_summary.items():
                posthoc_summary_rows.append({
                    '比较对': pair_name,
                    '校正α': f"{result.get('alpha_corrected', 0):.6f}",
                    '阈值z*': f"±{result.get('zstar', 0):.4f}" if result.get('zstar') else '',
                    '显著性': '是' if result.get('significant') else ('否' if result.get('significant') is False else '计算失败'),
                    '聚类数': result.get('n_clusters', 0)
                })

            for pair_name in posthoc_summary.keys():
                if pair_name in cached_posthoc_results:
                    result = cached_posthoc_results[pair_name]
                    spm_result = result.get('spm_result')
                    inference_result = result.get('inference_result')
                    if spm_result is not None:
                        posthoc_df = create_posthoc_curve_df(pair_name, spm_result, inference_result)
                        posthoc_dfs.append(posthoc_df)

            if posthoc_summary_rows:
                summary_ph_df = pd.DataFrame(posthoc_summary_rows)
                summary_ph_df.to_excel(writer, sheet_name='事后检验结果', index=False, startrow=0, startcol=0)

            if posthoc_dfs:
                merged_ph = posthoc_dfs[0]
                for df in posthoc_dfs[1:]:
                    merged_ph = pd.merge(merged_ph, df, on='Time_Point', how='outer')
                merged_ph.to_excel(writer, sheet_name='事后检验结果', index=False, startrow=len(posthoc_summary_rows) + 2, startcol=0)

    return filepath

