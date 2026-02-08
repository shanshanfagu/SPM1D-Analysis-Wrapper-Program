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
        if self.method == 'param':
            return self._run_parametric()
        else:
            return self._run_nonparametric()
    
    def _run_parametric(self):
        try:
            if self.test_type == 'ttest2':
                if len(self.data) != 2:
                    return None, "独立样本t检验需要两组数据"
                group_names = list(self.data.keys())
                YA = self.data[group_names[0]]
                YB = self.data[group_names[1]]
                self.spm_result = spm1d.stats.ttest2(YA, YB, equal_var=False)
                
            elif self.test_type == 'ttest_paired':
                if len(self.data) != 2:
                    return None, "配对样本t检验需要两组数据"
                group_names = list(self.data.keys())
                YA = self.data[group_names[0]]
                YB = self.data[group_names[1]]
                self.spm_result = spm1d.stats.ttest_paired(YA, YB)
                
            elif self.test_type == 'ttest':
                Y = self.kwargs.get('y_data')
                mu = self.kwargs.get('mu_data', 0)
                if Y is None:
                    return None, "单样本t检验需要提供y_data参数"
                self.spm_result = spm1d.stats.ttest(Y, mu)
                
            elif self.test_type == 'anova1':
                group_names = list(self.data.keys())
                Y = np.vstack([self.data[g] for g in group_names])
                A = np.concatenate([np.full(self.data[g].shape[0], i) 
                                   for i, g in enumerate(group_names)])
                self.spm_result = spm1d.stats.anova1(Y, A, equal_var=False)
                
            elif self.test_type == 'anova2':
                A = self.kwargs.get('A', None)
                B = self.kwargs.get('B', None)
                if A is None or B is None:
                    return None, "双因素ANOVA需要提供A和B分组信息"
                group_name = list(self.data.keys())[0]
                Y = self.data[group_name]
                self.spm_result = spm1d.stats.anova2(Y, A, B, equal_var=True)
                
            elif self.test_type == 'regress':
                x = self.kwargs.get('x_data', None)
                if x is None:
                    return None, "回归分析需要提供自变量x"
                Y = self.kwargs.get('y_data')
                if Y is None:
                    return None, "回归分析需要提供因变量Y"
                try:
                    x = np.asarray(x, dtype=float)
                    Y = np.asarray(Y, dtype=float)
                    if np.any(np.isinf(x)) or np.any(np.isnan(x)):
                        return None, "自变量x包含无效值(inf或nan)，请检查数据"
                    if np.any(np.isinf(Y)) or np.any(np.isnan(Y)):
                        return None, "因变量Y包含无效值(inf或nan)，请检查数据"
                    self.spm_result = spm1d.stats.regress(Y, x)
                except Exception as e:
                    return None, f"回归分析失败: {str(e)}"
                
            else:
                return None, f"不支持的分析类型: {self.test_type}"
            
            return self.spm_result, None
            
        except Exception as e:
            return None, str(e)
    
    def _run_nonparametric(self):
        try:
            if self.test_type == 'ttest2':
                if len(self.data) != 2:
                    return None, "独立样本t检验需要两组数据"
                group_names = list(self.data.keys())
                YA = self.data[group_names[0]]
                YB = self.data[group_names[1]]
                self.spm_result = spm1d.stats.nonparam.ttest2(YA, YB)
                
            elif self.test_type == 'ttest_paired':
                if len(self.data) != 2:
                    return None, "配对样本t检验需要两组数据"
                group_names = list(self.data.keys())
                YA = self.data[group_names[0]]
                YB = self.data[group_names[1]]
                self.spm_result = spm1d.stats.nonparam.ttest_paired(YA, YB)
                
            elif self.test_type == 'ttest':
                Y = self.kwargs.get('y_data')
                mu = self.kwargs.get('mu_data', 0)
                if Y is None:
                    return None, "单样本t检验需要提供y_data参数"
                self.spm_result = spm1d.stats.nonparam.ttest(Y, mu)
                
            elif self.test_type == 'anova1':
                group_names = list(self.data.keys())
                Y = np.vstack([self.data[g] for g in group_names])
                A = np.concatenate([np.full(self.data[g].shape[0], i) 
                                   for i, g in enumerate(group_names)])
                self.spm_result = spm1d.stats.nonparam.anova1(Y, A)
                
            elif self.test_type == 'regress':
                return None, "简单回归暂不支持非参数检验\n\n请使用参数检验代替"
                
            else:
                return None, f"不支持的分析类型: {self.test_type}"
            
            return self.spm_result, None
            
        except Exception as e:
            return None, str(e)
    
    def inference(self, alpha=0.05, **kwargs):
        if self.spm_result is None:
            return None, "请先运行分析"

        try:
            if self.method == 'param':
                if self.test_type == 'anova1':
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
        """ANOVA事后检验：组间两两比较，使用Bonferroni校正"""
        if self.test_type != 'anova1':
            return None, "事后检验仅适用于单因素ANOVA"

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

                Ya, Yb = self._remove_zero_variance_columns_pair(Ya, Yb)

                if self.method == 'param':
                    ttest_result = spm1d.stats.ttest2(Ya, Yb, equal_var=False)
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

                self.posthoc_results[pair_name] = {
                    'spm_result': ttest_result,
                    'inference_result': ttest_inference,
                    'alpha_corrected': alpha_corrected,
                    'n_comparisons': n_comparisons
                }

        return self.posthoc_results, None

    def _remove_zero_variance_columns_pair(self, Ya, Yb):
        """删除两组比较中方差为0的列"""
        zero_cols_a = np.where(np.var(Ya, axis=0) == 0)[0]
        zero_cols_b = np.where(np.var(Yb, axis=0) == 0)[0]
        zero_cols = np.union1d(zero_cols_a, zero_cols_b)
        if len(zero_cols) > 0:
            Ya = np.delete(Ya, zero_cols, axis=1)
            Yb = np.delete(Yb, zero_cols, axis=1)
        return Ya, Yb

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
