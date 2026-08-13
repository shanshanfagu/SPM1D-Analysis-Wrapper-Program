import numpy as np
import spm1d

class SPMAnalyzer:
    def __init__(self, data, test_type='ttest2', method='param', **kwargs):
        self.data = data
        self.test_type = test_type
        self.method = method
        self.kwargs = kwargs
        self.spm_result = None
        self.inference_result = None
        self.posthoc_results = None
        
    def run_analysis(self):
        try:
            stats = spm1d.stats if self.method == 'param' else spm1d.stats.nonparam
            is_param = self.method == 'param'
            group_names = list(self.data.keys())
            n_groups = len(group_names)

            if self.test_type in ('ttest2', 'ttest_paired'):
                if n_groups != 2:
                    return None, ("独立样本t检验需要两组数据" if self.test_type == 'ttest2'
                                  else "配对样本t检验需要两组数据")
                YA = self.data[group_names[0]]
                YB = self.data[group_names[1]]
                if self.test_type == 'ttest2':
                    param_kw = {'equal_var': False} if is_param else {}
                    self.spm_result = stats.ttest2(YA, YB, **param_kw)
                else:
                    self.spm_result = stats.ttest_paired(YA, YB)

            elif self.test_type == 'ttest':
                Y = self.kwargs.get('y_data')
                mu = self.kwargs.get('mu_data', 0)
                if Y is None:
                    return None, "单样本t检验需要提供y_data参数"
                mu = np.asarray(mu, dtype=float).squeeze()
                if mu.ndim >= 2:
                    return None, "参照曲线(y0)应为1维向量或标量，请选择参照组的均值曲线"
                self.spm_result = stats.ttest(Y, mu)

            elif self.test_type in ('anova1', 'anova1rm'):
                Y = np.vstack([self.data[g] for g in group_names])
                A = np.concatenate([np.full(self.data[g].shape[0], i)
                                   for i, g in enumerate(group_names)])
                param_kw = {'equal_var': True} if is_param else {}
                if self.test_type == 'anova1':
                    self.spm_result = stats.anova1(Y, A, **param_kw)
                else:
                    n_per_file = Y.shape[0] // n_groups
                    SUBJ = np.tile(np.arange(n_per_file), n_groups)
                    self.spm_result = stats.anova1rm(Y, A, SUBJ, **param_kw)

            elif self.test_type in ('anova2', 'anova2rm', 'anova2onerm'):
                A = self.kwargs.get('A', None)
                B = self.kwargs.get('B', None)
                SUBJ = self.kwargs.get('SUBJ', None)
                Y = self.kwargs.get('y_data')
                param_kw = {'equal_var': True} if is_param else {}
                if self.test_type == 'anova2':
                    if A is None or B is None:
                        return None, "双因素方差分析需要提供A和B分组信息"
                    if Y is None:
                        Y = self.data[group_names[0]]
                    self.spm_result = stats.anova2(Y, A, B, **param_kw)
                else:
                    if A is None or B is None or SUBJ is None:
                        return None, ("双因素重复测量方差分析需要提供A、B和SUBJ参数"
                                      if self.test_type == 'anova2rm'
                                      else "双因素混合设计方差分析需要提供A、B和SUBJ参数")
                    if Y is None:
                        return None, ("双因素重复测量方差分析需要提供Y数据"
                                      if self.test_type == 'anova2rm'
                                      else "双因素混合设计方差分析需要提供Y数据")
                    if self.test_type == 'anova2rm':
                        self.spm_result = stats.anova2rm(Y, A, B, SUBJ, **param_kw)
                    else:
                        self.spm_result = stats.anova2onerm(Y, A, B, SUBJ, **param_kw)

            elif self.test_type == 'regress':
                x = self.kwargs.get('x_data', None)
                Y = self.kwargs.get('y_data')
                if x is None:
                    return None, "回归分析需要提供自变量x"
                if Y is None:
                    return None, "回归分析需要提供因变量Y"
                try:
                    x = np.asarray(x, dtype=float)
                    Y = np.asarray(Y, dtype=float)
                    if np.any(np.isinf(x)) or np.any(np.isnan(x)):
                        return None, "自变量x包含无效值(inf或nan)，请检查数据"
                    if np.any(np.isinf(Y)) or np.any(np.isnan(Y)):
                        return None, "因变量Y包含无效值(inf或nan)，请检查数据"
                    if not is_param and Y.shape[0] > 150:
                        return None, f"非参数回归不支持样本数超过150的数据\n当前样本数: {Y.shape[0]}\n请使用参数检验代替"
                    self.spm_result = stats.regress(Y, x)
                except Exception as e:
                    return None, f"回归分析失败: {str(e)}"

            else:
                return None, f"不支持的分析类型: {self.test_type}"

            return self.spm_result, None

        except Exception as e:
            return None, str(e)
    
    def inference(self, alpha=0.05, **kwargs):
        if self.spm_result is None:
            return None, "请先运行分析"

        try:
            if self.test_type == 'anova2':
                if self.method == 'nonparam':
                    iterations = kwargs.get('iterations', 500)
                    self.inference_result = self.spm_result.inference(alpha, iterations=iterations)
                else:
                    self.inference_result = [r.inference(alpha) for r in self.spm_result]
                return self.inference_result, None
            
            elif self.test_type == 'anova2rm':
                if self.method == 'nonparam':
                    iterations = kwargs.get('iterations', 500)
                    self.inference_result = self.spm_result.inference(alpha, iterations=iterations)
                else:
                    self.inference_result = [r.inference(alpha) for r in self.spm_result]
                return self.inference_result, None

            elif self.test_type == 'anova2onerm':
                if self.method == 'nonparam':
                    iterations = kwargs.get('iterations', 500)
                    self.inference_result = self.spm_result.inference(alpha, iterations=iterations)
                else:
                    self.inference_result = [r.inference(alpha) for r in self.spm_result]
                return self.inference_result, None
            
            if self.method == 'param':
                if self.test_type in ['anova1', 'anova1rm']:
                    self.inference_result = self.spm_result.inference(alpha=alpha)
                else:
                    two_tailed = kwargs.get('two_tailed', True)
                    self.inference_result = self.spm_result.inference(alpha=alpha,
                                                                      two_tailed=two_tailed)
            else:
                iterations = kwargs.get('iterations', 500)
                self.inference_result = self.spm_result.inference(alpha=alpha,
                                                                  iterations=iterations)
            return self.inference_result, None
        except Exception as e:
            return None, str(e)

    def get_results_summary(self):
        if self.inference_result is None:
            return None

        if self.test_type in ['anova2', 'anova2rm', 'anova2onerm'] and isinstance(self.inference_result, list):
            summary = {
                'test_type': self.test_type,
                'method': self.method,
                'alpha': self.inference_result[0].alpha if hasattr(self.inference_result[0], 'alpha') else None,
                'effects': []
            }
            
            effect_names = ['A', 'B', 'AxB']
            for i, inf_result in enumerate(self.inference_result):
                effect_summary = {
                    'name': effect_names[i],
                    'zstar': inf_result.zstar if hasattr(inf_result, 'zstar') else None,
                    'h0reject': inf_result.h0reject if hasattr(inf_result, 'h0reject') else None,
                    'p_cluster': inf_result.p if hasattr(inf_result, 'p') else None,
                    'n_clusters': inf_result.nClusters if hasattr(inf_result, 'nClusters') else 0,
                }
                summary['effects'].append(effect_summary)
            
            summary['posthoc_results'] = self.posthoc_results
            return summary

        summary = {
            'test_type': self.test_type,
            'method': self.method,
            'z_field': self.spm_result.z if hasattr(self.spm_result, 'z') else None,
            'alpha': self.inference_result.alpha if hasattr(self.inference_result, 'alpha') else None,
            'zstar': self.inference_result.zstar if hasattr(self.inference_result, 'zstar') else None,
            'h0reject': self.inference_result.h0reject if hasattr(self.inference_result, 'h0reject') else None,
            'p_set': self.inference_result.p_set if hasattr(self.inference_result, 'p_set') else None,
            'p_cluster': self.inference_result.p if hasattr(self.inference_result, 'p') else None,
            'n_clusters': self.inference_result.nClusters if hasattr(self.inference_result, 'nClusters') else 0,
        }

        if self.test_type == 'regress':
            if hasattr(self.spm_result, 'r'):
                summary['r'] = self.spm_result.r
            if hasattr(self.spm_result, 'beta') and self.spm_result.beta is not None:
                beta = self.spm_result.beta
                if beta.shape[0] >= 2:
                    summary['beta_slope'] = beta[0]
                    summary['beta_intercept'] = beta[1]

        if hasattr(self.spm_result, 'beta'):
            summary['beta'] = self.spm_result.beta

        summary['clusters'] = []
        summary['posthoc_results'] = self.posthoc_results

        return summary

    def run_posthoc(self, alpha=0.05):
        """方差分析事后检验：组间两两比较，使用Bonferroni校正"""
        if self.test_type not in ['anova1', 'anova1rm']:
            return None, "事后检验仅适用于单因素方差分析"

        group_names = list(self.data.keys())
        n_groups = len(group_names)

        if n_groups < 2:
            return None, "至少需要两组数据才能进行事后检验"

        n_comparisons = n_groups * (n_groups - 1) // 2

        alpha_corrected = spm1d.util.p_critical_bonf(alpha, n_comparisons)

        self.posthoc_results = {}

        iterations = self.kwargs.get('iterations', 1000)

        for i in range(n_groups):
            for j in range(i + 1, n_groups):
                pair_name = f"{group_names[i]} vs {group_names[j]}"
                Ya = self.data[group_names[i]].copy()
                Yb = self.data[group_names[j]].copy()

                Q_orig = Ya.shape[1]
                deleted_cols = self._get_deleted_cols(Ya, Yb)
                if len(deleted_cols) > 0:
                    Ya = np.delete(Ya, deleted_cols, axis=1)
                    Yb = np.delete(Yb, deleted_cols, axis=1)

                if self.method == 'param':
                    if self.test_type == 'anova1rm':
                        ttest_result = spm1d.stats.ttest_paired(Ya, Yb)
                    else:
                        ttest_result = spm1d.stats.ttest2(Ya, Yb, equal_var=False)
                else:
                    if self.test_type == 'anova1rm':
                        ttest_result = spm1d.stats.nonparam.ttest_paired(Ya, Yb)
                    else:
                        ttest_result = spm1d.stats.nonparam.ttest2(Ya, Yb)

                try:
                    if self.method == 'param':
                        ttest_inference = ttest_result.inference(
                            alpha=alpha_corrected,
                            two_tailed=True
                        )
                    else:
                        ttest_inference = ttest_result.inference(
                            alpha=alpha_corrected,
                            two_tailed=True,
                            iterations=iterations
                        )
                except Exception as e:
                    ttest_inference = None

                z_full = None
                if len(deleted_cols) > 0:
                    z_full = self._get_full_z(ttest_result.z, deleted_cols, Q_orig)
                    if ttest_inference is not None and hasattr(ttest_inference, 'clusters') and ttest_inference.clusters is not None:
                        for cluster in ttest_inference.clusters:
                            if hasattr(cluster, 'endpoints') and cluster.endpoints is not None:
                                start, end = cluster.endpoints
                                s, e = int(round(start)), int(round(end))
                                adj_start = s + int(np.sum(deleted_cols <= s))
                                adj_end = e + int(np.sum(deleted_cols <= e))
                                cluster.endpoints = (float(adj_start), float(adj_end))

                self.posthoc_results[pair_name] = {
                    'spm_result': ttest_result,
                    'inference_result': ttest_inference,
                    'alpha_corrected': alpha_corrected,
                    'n_comparisons': n_comparisons,
                    'z_full': z_full,
                    'deleted_cols': deleted_cols.tolist() if len(deleted_cols) > 0 else []
                }

        return self.posthoc_results, None

    def _get_deleted_cols(self, Ya, Yb):
        zero_cols_a = np.where(np.var(Ya, axis=0) == 0)[0]
        zero_cols_b = np.where(np.var(Yb, axis=0) == 0)[0]
        return np.union1d(zero_cols_a, zero_cols_b)

    def _get_full_z(self, z_reduced, deleted_cols, Q_orig):
        if deleted_cols is None or len(deleted_cols) == 0:
            return np.asarray(z_reduced)
        z_full = np.full(Q_orig, np.nan)
        remaining = np.setdiff1d(np.arange(Q_orig), deleted_cols)
        z_full[remaining] = z_reduced
        return z_full

    def get_posthoc_summary(self):
        """获取事后检验汇总"""
        if self.posthoc_results is None:
            return None

        summary = {}
        for pair_name, results in self.posthoc_results.items():
            inference = results.get('inference_result')
            if inference is not None:
                h0reject = inference.h0reject if hasattr(inference, 'h0reject') else False
                zstar = inference.zstar if hasattr(inference, 'zstar') else None
                p_values = inference.p if hasattr(inference, 'p') else None
                n_clusters = inference.nClusters if hasattr(inference, 'nClusters') else 0

                p_values_str = []
                if p_values is not None:
                    if isinstance(p_values, (list, np.ndarray)):
                        for p in p_values:
                            if p < 0.001:
                                p_values_str.append("<0.001")
                            else:
                                p_values_str.append(f"{p:.4f}")
                    else:
                        if p_values < 0.001:
                            p_values_str.append("<0.001")
                        else:
                            p_values_str.append(f"{p_values:.4f}")

                summary[pair_name] = {
                    'significant': h0reject,
                    'alpha_corrected': results['alpha_corrected'],
                    'zstar': zstar,
                    'p_values': p_values_str,
                    'n_clusters': n_clusters
                }
            else:
                summary[pair_name] = {
                    'significant': None,
                    'alpha_corrected': results['alpha_corrected'],
                    'zstar': None,
                    'p_values': [],
                    'n_clusters': 0
                }

        return summary
