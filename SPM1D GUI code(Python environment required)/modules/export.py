import os
import pandas as pd
import numpy as np


def create_spm_curve_df(spm_result, inference_result, tr=None):
    tr = tr or (lambda x: x)
    z_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, z_val in enumerate(z_values):
        significant = tr('export.yes') if zstar and abs(z_val) > zstar else tr('export.no')
        rows.append({
            tr('export.time_point'): i,
            tr('export.spm_value'): z_val,
            tr('export.threshold'): zstar if zstar else '',
            tr('export.above_threshold'): significant
        })
    return pd.DataFrame(rows)


def create_k2_curve_df(group_name, spm_result, inference_result, tr=None):
    tr = tr or (lambda x: x)
    k2_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, k2_val in enumerate(k2_values):
        significant = tr('export.yes') if zstar and k2_val > zstar else tr('export.no')
        rows.append({
            tr('export.time_point'): i,
            f'{group_name}_{tr("export.k2")}': k2_val,
            f'{group_name}_{tr("export.threshold")}': zstar if zstar else '',
            f'{group_name}_{tr("export.above_threshold")}': significant
        })
    return pd.DataFrame(rows)


def create_posthoc_curve_df(pair_name, spm_result, inference_result, tr=None):
    tr = tr or (lambda x: x)
    spm_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, spm_val in enumerate(spm_values):
        significant = tr('export.yes') if zstar and abs(spm_val) > zstar else tr('export.no')
        rows.append({
            tr('export.time_point'): i,
            f'{pair_name}': spm_val,
            f'{pair_name}_{tr("export.threshold")}': zstar if zstar else '',
            f'{pair_name}_{tr("export.above_threshold")}': significant
        })
    return pd.DataFrame(rows)


def create_regress_curve_df(spm_result, inference_result, beta_slope=None, beta_intercept=None, r_curve=None, tr=None):
    tr = tr or (lambda x: x)
    z_values = spm_result.z
    zstar = inference_result.zstar if inference_result else None
    
    rows = []
    for i, z_val in enumerate(z_values):
        significant = tr('export.yes') if zstar and abs(z_val) > zstar else tr('export.no')
        row = {
            tr('export.time_point'): i,
            tr('export.spm_value'): z_val,
            tr('export.threshold'): zstar if zstar else '',
            tr('export.above_threshold'): significant
        }
        if beta_slope is not None:
            row[tr('export.beta_slope')] = beta_slope[i] if i < len(beta_slope) else ''
        if beta_intercept is not None:
            row[tr('export.beta_intercept')] = beta_intercept[i] if i < len(beta_intercept) else ''
        if r_curve is not None:
            row[tr('export.r_correlation')] = r_curve[i] if i < len(r_curve) else ''
        rows.append(row)
    return pd.DataFrame(rows)


def export_all_to_xlsx(summary, normality_results, posthoc_summary,
                       cached_spm_result, cached_inference_result,
                       cached_posthoc_results, filepath, tr=None):
    tr = tr or (lambda x: x)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        if summary:
            method_text = tr('export.param_method_param') if summary.get('method') == 'param' else tr('export.param_method_nonparam')
            h0_text = tr('export.yes') if summary.get('h0reject') else tr('export.no')
            
            summary_df = pd.DataFrame([
                {tr('export.param'): tr('export.param_type'), tr('export.value'): summary.get('test_type', 'N/A')},
                {tr('export.param'): tr('export.param_method'), tr('export.value'): method_text},
                {tr('export.param'): tr('export.param_alpha'), tr('export.value'): summary.get('alpha', 'N/A')},
                {tr('export.param'): tr('export.param_threshold'), tr('export.value'): f"{summary.get('zstar', 'N/A'):.4f}" if summary.get('zstar') else 'N/A'},
                {tr('export.param'): tr('export.param_h0reject'), tr('export.value'): h0_text},
                {tr('export.param'): tr('export.param_clusters'), tr('export.value'): summary.get('n_clusters', 0)}
            ])
            summary_df.to_excel(writer, sheet_name=tr('export.sheet_summary'), index=False, startrow=0, startcol=0)

        if cached_spm_result and cached_inference_result:
            test_type = summary.get('test_type', '') if summary else ''
            if test_type == 'regress':
                beta_slope = summary.get('beta_slope')
                beta_intercept = summary.get('beta_intercept')
                r_curve = summary.get('r')
                regress_df = create_regress_curve_df(cached_spm_result, cached_inference_result, beta_slope, beta_intercept, r_curve, tr)
                regress_df.to_excel(writer, sheet_name=tr('export.sheet_main_effect'), index=False, startrow=0, startcol=0)
            else:
                spm_df = create_spm_curve_df(cached_spm_result, cached_inference_result, tr)
                spm_df.to_excel(writer, sheet_name=tr('export.sheet_main_effect'), index=False, startrow=0, startcol=0)

        normality_summary_rows = []
        k2_dfs = []

        if normality_results and 'groups' in normality_results:
            for group_name, result in normality_results['groups'].items():
                if 'error' in result:
                    conclusion = tr('export.not_supported')
                elif result.get('is_normal'):
                    conclusion = tr('export.normal_yes')
                else:
                    conclusion = tr('export.normal_no')
                
                normality_summary_rows.append({
                    tr('export.group'): group_name,
                    tr('export.test_method'): "D'Agostino K²",
                    tr('export.conclusion'): conclusion
                })

            for group_name, result in normality_results['groups'].items():
                if 'error' in result:
                    continue
                spm_result = result.get('spm_result')
                inference_result = result.get('inference_result')
                if spm_result is not None:
                    k2_df = create_k2_curve_df(group_name, spm_result, inference_result, tr)
                    k2_dfs.append(k2_df)

            if normality_summary_rows:
                summary_k2_df = pd.DataFrame(normality_summary_rows)
                summary_k2_df.to_excel(writer, sheet_name=tr('export.sheet_normality'), index=False, startrow=0, startcol=0)

            if k2_dfs:
                merged_k2 = k2_dfs[0]
                for df in k2_dfs[1:]:
                    merged_k2 = pd.merge(merged_k2, df, on=tr('export.time_point'), how='outer')
                merged_k2.to_excel(writer, sheet_name=tr('export.sheet_normality'), index=False, startrow=len(normality_summary_rows) + 2, startcol=0)

        posthoc_summary_rows = []
        posthoc_dfs = []

        if posthoc_summary and cached_posthoc_results:
            for pair_name, result in posthoc_summary.items():
                if result.get('significant') is True:
                    sig_text = tr('export.yes')
                elif result.get('significant') is False:
                    sig_text = tr('export.no')
                else:
                    sig_text = tr('export.calc_failed')
                
                posthoc_summary_rows.append({
                    tr('export.comparison_pair'): pair_name,
                    tr('export.corrected_alpha'): f"{result.get('alpha_corrected', 0):.6f}",
                    tr('export.threshold_z'): f"±{result.get('zstar', 0):.4f}" if result.get('zstar') else '',
                    tr('export.significance'): sig_text,
                    tr('export.param_clusters'): result.get('n_clusters', 0)
                })

            for pair_name in posthoc_summary.keys():
                if pair_name in cached_posthoc_results:
                    result = cached_posthoc_results[pair_name]
                    spm_result = result.get('spm_result')
                    inference_result = result.get('inference_result')
                    if spm_result is not None:
                        posthoc_df = create_posthoc_curve_df(pair_name, spm_result, inference_result, tr)
                        posthoc_dfs.append(posthoc_df)

            if posthoc_summary_rows:
                summary_ph_df = pd.DataFrame(posthoc_summary_rows)
                summary_ph_df.to_excel(writer, sheet_name=tr('export.sheet_posthoc'), index=False, startrow=0, startcol=0)

            if posthoc_dfs:
                merged_ph = posthoc_dfs[0]
                for df in posthoc_dfs[1:]:
                    merged_ph = pd.merge(merged_ph, df, on=tr('export.time_point'), how='outer')
                merged_ph.to_excel(writer, sheet_name=tr('export.sheet_posthoc'), index=False, startrow=len(posthoc_summary_rows) + 2, startcol=0)

    return filepath
