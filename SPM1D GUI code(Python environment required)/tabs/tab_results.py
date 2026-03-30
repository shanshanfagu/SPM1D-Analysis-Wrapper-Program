from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QTableWidget,
                               QTableWidgetItem, QTextEdit,
                               QHeaderView, QProgressDialog, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from modules.spm_analysis import SPMAnalyzer
from modules.utils import show_info, show_warning, show_critical
import numpy as np

class AnalysisThread(QThread):
    finished = pyqtSignal(dict, object, object)
    error = pyqtSignal(str)

    def __init__(self, main_window, data, params, method):
        super().__init__()
        self.main_window = main_window
        self.data = data
        self.params = params
        self.method = method

    def run(self):
        try:
            np.random.seed(42)

            test_type = self.params.get('test_type')
            indicator = getattr(self.main_window, 'selected_indicator', None)

            if indicator and indicator in self.data:
                test_data = self.data[indicator]
            else:
                test_data = list(self.data.values())[0]

            kwargs = {}
            if self.method == 'nonparam':
                kwargs['iterations'] = self.params.get('iterations', 500)
            if test_type == 'ttest':
                kwargs['y_data'] = self.params.get('y_data')
                kwargs['mu_data'] = self.params.get('mu_data', 0)
            if test_type == 'regress':
                kwargs['y_data'] = self.params.get('y_data')
                kwargs['x_data'] = self.params.get('x_data')
            if test_type in ['anova2', 'anova2rm', 'anova2onerm']:
                kwargs['y_data'] = self.params.get('y_data')
                kwargs['A'] = self.params.get('A')
                kwargs['B'] = self.params.get('B')
                if test_type in ['anova2rm', 'anova2onerm']:
                    kwargs['SUBJ'] = self.params.get('SUBJ')

            method = self.method

            analyzer = SPMAnalyzer(test_data, test_type=test_type,
                                 method=method, **kwargs)

            spm_result, error = analyzer.run_analysis()
            if error:
                raise Exception(error)

            if test_type in ['anova2', 'anova2rm', 'anova2onerm']:
                inference_result, inf_error = analyzer.inference(alpha=self.params['alpha'])
            elif self.method == 'param':
                if test_type in ['anova1', 'anova1rm']:
                    inference_result, inf_error = analyzer.inference(alpha=self.params['alpha'])
                else:
                    inference_result, inf_error = analyzer.inference(alpha=self.params['alpha'],
                                                      two_tailed=True)
            else:
                inference_result, inf_error = analyzer.inference(alpha=self.params['alpha'],
                                                          iterations=self.params.get('iterations', 500))
            if inf_error:
                raise Exception(inf_error)

            summary = analyzer.get_results_summary()
            
            if test_type == 'regress':
                summary['y_data'] = self.params.get('y_data')
                summary['y_name'] = self.params.get('y_name')
                summary['x_name'] = self.params.get('x_name')
            
            if test_type == 'anova2':
                summary['y_data'] = self.params.get('y_data')
                summary['y_name'] = self.params.get('y_name')
                summary['a_name'] = self.params.get('a_name')
                summary['b_name'] = self.params.get('b_name')
                summary['A'] = self.params.get('A')
                summary['B'] = self.params.get('B')
            
            if test_type in ['anova2rm', 'anova2onerm']:
                summary['y_data'] = self.params.get('y_data')
                summary['y_names'] = self.params.get('y_names')
                summary['a_name'] = self.params.get('a_name')
                summary['b_name'] = self.params.get('b_name')
                summary['A'] = self.params.get('A')
                summary['B'] = self.params.get('B')
                summary['SUBJ'] = self.params.get('SUBJ')
            
            self.finished.emit(summary, spm_result, inference_result)

        except Exception as e:
            self.error.emit(str(e))


class PosthocThread(QThread):
    finished = pyqtSignal(dict, dict, object)
    error = pyqtSignal(str)

    def __init__(self, main_window, data, alpha=0.05):
        super().__init__()
        self.main_window = main_window
        self.data = data
        self.alpha = alpha

    def run(self):
        try:
            np.random.seed(42)

            indicator = getattr(self.main_window, 'selected_indicator', None)
            if indicator and indicator in self.data:
                test_data = self.data[indicator]
            else:
                test_data = list(self.data.values())[0]

            actual_test_type = self.main_window.analysis_params.get('test_type', 'anova1')
            analyzer = SPMAnalyzer(test_data, test_type=actual_test_type,
                                 method=self.main_window.analysis_method)

            spm_result, error = analyzer.run_analysis()
            if error:
                raise Exception(error)

            posthoc_results, ph_error = analyzer.run_posthoc(alpha=self.alpha)
            if ph_error:
                raise Exception(ph_error)

            summary = analyzer.get_posthoc_summary()
            self.finished.emit(summary, posthoc_results, spm_result)

        except Exception as e:
            self.error.emit(str(e))

class TabResults(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.summary = None
        self.analysis_thread = None
        self.posthoc_summary = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        self.title = QLabel(self.main_window.tr("tab_results.title"))
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.title)

        layout.addLayout(self._create_run_section())
        layout.addLayout(self._create_summary_section())
        layout.addLayout(self._create_posthoc_section())
        layout.addLayout(self._create_export_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_run_section(self):
        layout = QHBoxLayout()

        self.group_run = QGroupBox(self.main_window.tr("tab_results.run_analysis"))
        group_layout = QHBoxLayout()

        self.btn_run = QPushButton(self.main_window.tr("tab_results.run_spm"))
        self.btn_run.clicked.connect(self.run_analysis)

        group_layout.addWidget(self.btn_run)
        group_layout.addStretch()

        self.group_run.setLayout(group_layout)
        layout.addWidget(self.group_run)

        return layout

    def _create_summary_section(self):
        layout = QHBoxLayout()

        self.group_summary = QGroupBox(self.main_window.tr("tab_results.summary"))
        group_layout = QVBoxLayout()

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels([
            self.main_window.tr("tab_results.col_param"),
            self.main_window.tr("tab_results.col_value")
        ])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.summary_table.setRowCount(0)

        group_layout.addWidget(self.summary_table)
        self.group_summary.setLayout(group_layout)
        layout.addWidget(self.group_summary)

        return layout

    def _create_posthoc_section(self):
        layout = QHBoxLayout()

        self.group_posthoc = QGroupBox(self.main_window.tr("tab_results.posthoc_results"))
        group_layout = QVBoxLayout()

        self.posthoc_text = QTextEdit()
        self.posthoc_text.setReadOnly(True)
        self.posthoc_text.setPlaceholderText(self.main_window.tr("tab_results.posthoc_placeholder"))

        self.btn_posthoc = QPushButton(self.main_window.tr("tab_results.run_posthoc"))
        self.btn_posthoc.clicked.connect(self.run_posthoc)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_posthoc)
        btn_layout.addStretch()

        group_layout.addWidget(self.posthoc_text)
        group_layout.addLayout(btn_layout)

        self.group_posthoc.setLayout(group_layout)
        layout.addWidget(self.group_posthoc)

        return layout

    def _create_export_section(self):
        layout = QHBoxLayout()

        self.group_export = QGroupBox(self.main_window.tr("tab_results.export"))
        group_layout = QHBoxLayout()

        self.btn_export_all = QPushButton(self.main_window.tr("tab_results.export_all"))
        self.btn_export_all.clicked.connect(self.export_all_data)

        group_layout.addWidget(self.btn_export_all)
        group_layout.addStretch()

        self.group_export.setLayout(group_layout)
        layout.addWidget(self.group_export)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        self.btn_prev = QPushButton(self.main_window.tr("tab_results.prev_params"))
        self.btn_prev.clicked.connect(self.go_prev)

        self.btn_next = QPushButton(self.main_window.tr("tab_results.next_charts"))
        self.btn_next.clicked.connect(self.go_next)

        layout.addWidget(self.btn_prev)
        layout.addStretch()
        layout.addWidget(self.btn_next)

        return layout

    def run_analysis(self):
        self.main_window.cached_spm_result = None
        self.main_window.cached_inference_result = None
        self.main_window.cached_posthoc_results = None
        self.main_window.posthoc_summary = None

        self.progress = QProgressDialog(self.main_window.tr("tab_results.analyzing"), 
                                        self.main_window.tr("tab_results.cancel"), 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()

        self.analysis_thread = AnalysisThread(
            self.main_window,
            self.main_window.analysis_data,
            self.main_window.analysis_params,
            self.main_window.analysis_method
        )
        self.analysis_thread.finished.connect(self.on_analysis_finished)
        self.analysis_thread.error.connect(self.on_analysis_error)
        self.analysis_thread.start()

    def on_analysis_finished(self, summary, spm_result, inference_result):
        self.progress.close()
        self.summary = summary
        self.main_window.analysis_result = summary
        self.main_window.analysis_summary = summary

        self.main_window.cached_spm_result = spm_result
        self.main_window.cached_inference_result = inference_result

        self.update_summary_table()

        show_info(self, self.main_window.tr("common.success"), 
                              self.main_window.tr("tab_results.analysis_complete"))

    def on_analysis_error(self, error):
        self.progress.close()
        show_critical(self, self.main_window.tr("common.error"), 
                           f"{self.main_window.tr('tab_results.analysis_failed')}: {error}")

    def update_summary_table(self):
        self.summary_table.setRowCount(0)

        if not self.summary:
            return

        test_type = self.summary.get('test_type', 'N/A')

        if test_type in ['anova2', 'anova2rm', 'anova2onerm'] and 'effects' in self.summary:
            self._update_anova2_summary_table()
            return

        method_text = (self.main_window.tr("tab_results.param_method_param") 
                      if self.summary.get('method') == 'param' 
                      else self.main_window.tr("tab_results.param_method_nonparam"))
        
        h0_text = (self.main_window.tr("tab_results.yes") 
                  if self.summary.get('h0reject') 
                  else self.main_window.tr("tab_results.no"))

        data = [
            (self.main_window.tr("tab_results.param_type"), test_type),
            (self.main_window.tr("tab_results.param_method"), method_text),
            (self.main_window.tr("tab_results.param_alpha"), str(self.summary.get('alpha', 'N/A'))),
            (self.main_window.tr("tab_results.param_threshold"), 
             f"{self.summary.get('zstar', 'N/A'):.4f}" if self.summary.get('zstar') else "N/A"),
            (self.main_window.tr("tab_results.param_h0reject"), h0_text),
            (self.main_window.tr("tab_results.param_clusters"), str(self.summary.get('n_clusters', 0))),
        ]

        self.summary_table.setRowCount(len(data))
        for i, (param, value) in enumerate(data):
            self.summary_table.setItem(i, 0, QTableWidgetItem(param))
            self.summary_table.setItem(i, 1, QTableWidgetItem(str(value)))

        if test_type == 'regress' and self.summary.get('r') is not None:
            r_mean = float(np.mean(self.summary['r']))
            self.summary_table.insertRow(len(data))
            self.summary_table.setItem(len(data), 0, QTableWidgetItem(self.main_window.tr("tab_results.avg_r")))
            self.summary_table.setItem(len(data), 1, QTableWidgetItem(f"{r_mean:.4f}"))

        self._add_beta_section()

    def _update_anova2_summary_table(self):
        effects = self.summary.get('effects', [])
        if not effects:
            return
        
        method_text = (self.main_window.tr("tab_results.param_method_param") 
                      if self.summary.get('method') == 'param' 
                      else self.main_window.tr("tab_results.param_method_nonparam"))

        test_type = self.summary.get('test_type', 'anova2')
        if test_type == 'anova2onerm':
            type_text = self.main_window.tr("tab_results.two_way_anova_mixed")
        elif test_type == 'anova2rm':
            type_text = self.main_window.tr("tab_results.two_way_anova_rm")
        else:
            type_text = self.main_window.tr("tab_results.two_way_anova")

        if test_type == 'anova2onerm':
            effect_names = [
                self.main_window.tr("export.mixed_effect_a"),
                self.main_window.tr("export.mixed_effect_b"),
                self.main_window.tr("export.interaction_effect")
            ]
        else:
            effect_names = [
                self.main_window.tr("export.main_effect_a"),
                self.main_window.tr("export.main_effect_b"),
                self.main_window.tr("export.interaction_effect")
            ]
        
        rows = []
        rows.append((self.main_window.tr("tab_results.param_type"), type_text))
        rows.append((self.main_window.tr("tab_results.param_method"), method_text))
        rows.append((self.main_window.tr("tab_results.param_alpha"), str(self.summary.get('alpha', 'N/A'))))
        
        for i, effect in enumerate(effects):
            effect_name = effect_names[i] if i < len(effect_names) else f'Effect {i}'
            h0reject = effect.get('h0reject', False)
            h0_text = self.main_window.tr("tab_results.yes") if h0reject else self.main_window.tr("tab_results.no")
            zstar_text = f"{effect.get('zstar', 0):.4f}" if effect.get('zstar') else "N/A"
            n_clusters = effect.get('n_clusters', 0)
            
            rows.append(("", ""))
            rows.append((f"{effect_name}", ""))
            rows.append((self.main_window.tr("tab_results.param_threshold"), zstar_text))
            rows.append((self.main_window.tr("tab_results.param_h0reject"), h0_text))
            rows.append((self.main_window.tr("tab_results.param_clusters"), str(n_clusters)))
        
        self.summary_table.setRowCount(len(rows))
        for i, (param, value) in enumerate(rows):
            self.summary_table.setItem(i, 0, QTableWidgetItem(param))
            self.summary_table.setItem(i, 1, QTableWidgetItem(str(value)))

    def _add_beta_section(self):
        beta = self.summary.get('beta')
        beta_slope = self.summary.get('beta_slope')
        beta_intercept = self.summary.get('beta_intercept')
        
        if beta is None and beta_slope is None and beta_intercept is None:
            return

        current_rows = self.summary_table.rowCount()
        self.summary_table.insertRow(current_rows)
        self.summary_table.setItem(current_rows, 0, QTableWidgetItem(""))
        self.summary_table.setItem(current_rows, 1, QTableWidgetItem(""))

        current_rows += 1
        self.summary_table.insertRow(current_rows)
        self.summary_table.setItem(current_rows, 0, QTableWidgetItem(self.main_window.tr("tab_results.regression_coef")))
        self.summary_table.setItem(current_rows, 1, QTableWidgetItem(""))

        test_type = self.summary.get('test_type', '')

        if test_type == 'regress':
            if beta_slope is not None:
                current_rows += 1
                self.summary_table.insertRow(current_rows)
                self.summary_table.setItem(current_rows, 0, QTableWidgetItem(self.main_window.tr("tab_results.beta_slope")))
                self.summary_table.setItem(current_rows, 1, QTableWidgetItem(f"shape: {beta_slope.shape}"))
            if beta_intercept is not None:
                current_rows += 1
                self.summary_table.insertRow(current_rows)
                self.summary_table.setItem(current_rows, 0, QTableWidgetItem(self.main_window.tr("tab_results.beta_intercept")))
                self.summary_table.setItem(current_rows, 1, QTableWidgetItem(f"shape: {beta_intercept.shape}"))
        elif isinstance(beta, dict):
            for key, beta_data in beta.items():
                if beta_data is not None:
                    current_rows += 1
                    self.summary_table.insertRow(current_rows)
                    self.summary_table.setItem(current_rows, 0, QTableWidgetItem(f"  {key}"))
                    self.summary_table.setItem(current_rows, 1, QTableWidgetItem(f"shape: {beta_data.shape}"))
        elif beta is not None:
            current_rows += 1
            self.summary_table.insertRow(current_rows)
            self.summary_table.setItem(current_rows, 0, QTableWidgetItem(self.main_window.tr("tab_results.beta_coef")))
            self.summary_table.setItem(current_rows, 1, QTableWidgetItem(f"shape: {beta.shape}"))

    def export_all_data(self):
        if not self.summary:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_results.warn_run_analysis"))
            return

        from modules.export import export_all_to_xlsx
        import os

        filename, _ = QFileDialog.getSaveFileName(self, self.main_window.tr("tab_results.export_dialog_title"), "SPM_Analysis_Results.xlsx", "Excel Files (*.xlsx)")
        if filename:
            export_all_to_xlsx(
                self.summary,
                self.main_window.normality_results,
                getattr(self, 'posthoc_summary', None),
                self.main_window.cached_spm_result,
                self.main_window.cached_inference_result,
                self.main_window.cached_posthoc_results,
                filename,
                tr=self.main_window.tr
            )
            show_info(self, self.main_window.tr("common.success"), 
                                  self.main_window.tr("tab_results.save_success").format(os.path.basename(filename)))

    def go_prev(self):
        self.main_window.prev_tab()

    def go_next(self):
        if not self.summary:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_results.warn_run_analysis"))
            return

        self.main_window.next_tab()

    def clear_data(self):
        self.summary = None
        if hasattr(self, 'posthoc_text'):
            self.posthoc_text.clear()
        if hasattr(self, 'summary_table'):
            self.summary_table.setRowCount(0)
        if hasattr(self, 'corr_table'):
            self.corr_table.setRowCount(0)

    def run_posthoc(self):
        if not self.summary:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_results.warn_run_analysis"))
            return

        test_type = self.summary.get('test_type')
        
        if test_type == 'anova2':
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_results.warn_posthoc_anova2"))
            return

        if test_type not in ['anova1', 'anova1rm']:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_results.warn_posthoc_anova"))
            return

        if not self.summary.get('h0reject', False):
            show_info(self, self.main_window.tr("common.info"), 
                                  self.main_window.tr("tab_results.info_no_posthoc"))
            return

        self.progress = QProgressDialog(self.main_window.tr("tab_results.running_posthoc"), 
                                        self.main_window.tr("tab_results.cancel"), 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()

        self.posthoc_thread = PosthocThread(
            self.main_window,
            self.main_window.analysis_data,
            alpha=self.summary.get('alpha', 0.05)
        )
        self.posthoc_thread.finished.connect(self.on_posthoc_finished)
        self.posthoc_thread.error.connect(self.on_posthoc_error)
        self.posthoc_thread.start()

    def on_posthoc_finished(self, summary, posthoc_results=None, spm_result=None):
        self.progress.close()
        self.posthoc_summary = summary
        self.main_window.posthoc_summary = summary

        if posthoc_results:
            self.main_window.cached_posthoc_results = posthoc_results

            if hasattr(self.main_window, 'tab_plots'):
                tab_plots = self.main_window.tab_plots
                if hasattr(tab_plots, 'group_combo') and tab_plots.group_combo is not None:
                    tab_plots.group_combo.clear()
                    pair_names = list(posthoc_results.keys())
                    tab_plots.group_combo.addItems(pair_names)
                    tab_plots.group_combo.setEnabled(True)

                    if len(pair_names) > 0:
                        tab_plots.group_combo.setCurrentIndex(0)

        self.update_posthoc_text()

        self.main_window.tab_widget.setCurrentIndex(5)
        self.main_window.tab_plots.chart_type_combo.setCurrentText(self.main_window.tr("tab_plots.posthoc_plot"))
        self.main_window.tab_plots.update_chart()

        show_info(self, self.main_window.tr("common.success"), 
                              self.main_window.tr("tab_results.posthoc_complete"))

    def on_posthoc_error(self, error):
        self.progress.close()
        show_critical(self, self.main_window.tr("common.error"), 
                           f"{self.main_window.tr('tab_results.posthoc_failed')}: {error}")

    def update_posthoc_text(self):
        if not self.posthoc_summary:
            return

        text = f"{self.main_window.tr('tab_results.posthoc_header')}\n"
        text += "=" * 50 + "\n\n"

        for pair_name, result in self.posthoc_summary.items():
            alpha_corr = result.get('alpha_corrected', 0)
            zstar = result.get('zstar')
            significant = result.get('significant')
            p_values = result.get('p_values', [])
            n_clusters = result.get('n_clusters', 0)

            text += f"{self.main_window.tr('tab_results.comparison_pair')} {pair_name}\n"
            text += f"{self.main_window.tr('tab_results.corrected_alpha')} {alpha_corr:.6f}\n"
            if zstar is not None:
                text += f"{self.main_window.tr('tab_results.threshold_z')} ±{zstar:.4f}\n"

            if significant is None:
                text += f"{self.main_window.tr('tab_results.result')} {self.main_window.tr('tab_results.calc_failed')}\n"
            elif significant:
                text += f"{self.main_window.tr('tab_results.result')} {self.main_window.tr('tab_results.result_significant').format(n_clusters)}\n"
                if p_values:
                    text += f"{self.main_window.tr('tab_results.cluster_pvalues')} " + ", ".join(p_values) + "\n"
            else:
                text += f"{self.main_window.tr('tab_results.result')} {self.main_window.tr('tab_results.result_not_significant')}\n"
            text += "\n"

        self.posthoc_text.setText(text)

    def retranslate_ui(self):
        self.title.setText(self.main_window.tr("tab_results.title"))
        self.group_run.setTitle(self.main_window.tr("tab_results.run_analysis"))
        self.btn_run.setText(self.main_window.tr("tab_results.run_spm"))
        self.group_summary.setTitle(self.main_window.tr("tab_results.summary"))
        self.summary_table.setHorizontalHeaderLabels([
            self.main_window.tr("tab_results.col_param"),
            self.main_window.tr("tab_results.col_value")
        ])
        self.group_posthoc.setTitle(self.main_window.tr("tab_results.posthoc_results"))
        self.posthoc_text.setPlaceholderText(self.main_window.tr("tab_results.posthoc_placeholder"))
        self.btn_posthoc.setText(self.main_window.tr("tab_results.run_posthoc"))
        self.group_export.setTitle(self.main_window.tr("tab_results.export"))
        self.btn_export_all.setText(self.main_window.tr("tab_results.export_all"))
        self.btn_prev.setText(self.main_window.tr("tab_results.prev_params"))
        self.btn_next.setText(self.main_window.tr("tab_results.next_charts"))
        
        if self.summary:
            self.update_summary_table()
        if self.posthoc_summary:
            self.update_posthoc_text()
