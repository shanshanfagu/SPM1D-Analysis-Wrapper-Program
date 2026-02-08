from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QGroupBox, QTableWidget,
                              QTableWidgetItem, QMessageBox, QTextEdit,
                              QHeaderView, QProgressDialog, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from modules.spm_analysis import SPMAnalyzer
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

            if test_type == 'regress':
                method = 'param'
            else:
                method = self.method

            analyzer = SPMAnalyzer(test_data, test_type=test_type,
                                 method=method, **kwargs)

            spm_result, error = analyzer.run_analysis()
            if error:
                raise Exception(error)

            if self.method == 'param':
                if test_type == 'anova1':
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

            analyzer = SPMAnalyzer(test_data, test_type='anova1',
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

        title = QLabel("分析结果")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addLayout(self._create_run_section())
        layout.addLayout(self._create_summary_section())
        layout.addLayout(self._create_posthoc_section())
        layout.addLayout(self._create_export_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_run_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("运行分析")
        group_layout = QHBoxLayout()

        self.btn_run = QPushButton("运行SPM分析")
        self.btn_run.clicked.connect(self.run_analysis)

        group_layout.addWidget(self.btn_run)
        group_layout.addStretch()

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_summary_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("统计摘要")
        group_layout = QVBoxLayout()

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["参数", "值"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.summary_table.setRowCount(0)

        group_layout.addWidget(self.summary_table)
        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_posthoc_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("事后检验结果")
        group_layout = QVBoxLayout()

        self.posthoc_text = QTextEdit()
        self.posthoc_text.setReadOnly(True)
        self.posthoc_text.setPlaceholderText("点击'执行事后检验'按钮查看结果")

        btn_posthoc = QPushButton("执行事后检验")
        btn_posthoc.clicked.connect(self.run_posthoc)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_posthoc)
        btn_layout.addStretch()

        group_layout.addWidget(self.posthoc_text)
        group_layout.addLayout(btn_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

        self.btn_posthoc = btn_posthoc

        return layout

    def _create_export_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("导出")
        group_layout = QHBoxLayout()

        btn_all = QPushButton("导出全部数据")
        btn_all.clicked.connect(self.export_all_data)

        group_layout.addWidget(btn_all)
        group_layout.addStretch()

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        btn_prev = QPushButton("← 返回参数设置")
        btn_prev.clicked.connect(self.go_prev)

        btn_next = QPushButton("下一步: 查看图表 →")
        btn_next.clicked.connect(self.go_next)

        layout.addWidget(btn_prev)
        layout.addStretch()
        layout.addWidget(btn_next)

        return layout

    def run_analysis(self):
        self.main_window.cached_spm_result = None
        self.main_window.cached_inference_result = None
        self.main_window.cached_posthoc_results = None
        self.main_window.posthoc_summary = None

        self.progress = QProgressDialog("正在运行分析...", "取消", 0, 0, self)
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

        QMessageBox.information(self, "完成", "分析完成！")

    def on_analysis_error(self, error):
        self.progress.close()
        QMessageBox.critical(self, "错误", f"分析失败: {error}")

    def update_summary_table(self):
        self.summary_table.setRowCount(0)

        if not self.summary:
            return

        test_type = self.summary.get('test_type', 'N/A')

        data = [
            ("分析类型", test_type),
            ("方法", "参数检验" if self.summary.get('method') == 'param' else "非参数检验"),
            ("显著性水平", str(self.summary.get('alpha', 'N/A'))),
            ("临界阈值", f"{self.summary.get('zstar', 'N/A'):.4f}" if self.summary.get('zstar') else "N/A"),
            ("H0拒绝", "是" if self.summary.get('h0reject') else "否"),
            ("聚类数", str(self.summary.get('n_clusters', 0))),
        ]

        self.summary_table.setRowCount(len(data))
        for i, (param, value) in enumerate(data):
            self.summary_table.setItem(i, 0, QTableWidgetItem(param))
            self.summary_table.setItem(i, 1, QTableWidgetItem(str(value)))

        if test_type == 'regress' and self.summary.get('r') is not None:
            r_mean = float(np.mean(self.summary['r']))
            self.summary_table.insertRow(len(data))
            self.summary_table.setItem(len(data), 0, QTableWidgetItem("平均相关系数r"))
            self.summary_table.setItem(len(data), 1, QTableWidgetItem(f"{r_mean:.4f}"))

        self._add_beta_section()

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
        self.summary_table.setItem(current_rows, 0, QTableWidgetItem("回归系数"))
        self.summary_table.setItem(current_rows, 1, QTableWidgetItem(""))

        test_type = self.summary.get('test_type', '')

        if test_type == 'regress':
            if beta_slope is not None:
                current_rows += 1
                self.summary_table.insertRow(current_rows)
                self.summary_table.setItem(current_rows, 0, QTableWidgetItem("  斜率(beta_0)"))
                self.summary_table.setItem(current_rows, 1, QTableWidgetItem(f"shape: {beta_slope.shape}"))
            if beta_intercept is not None:
                current_rows += 1
                self.summary_table.insertRow(current_rows)
                self.summary_table.setItem(current_rows, 0, QTableWidgetItem("  截距(beta_1)"))
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
            self.summary_table.setItem(current_rows, 0, QTableWidgetItem("  beta系数"))
            self.summary_table.setItem(current_rows, 1, QTableWidgetItem(f"shape: {beta.shape}"))

    def export_all_data(self):
        if not self.summary:
            QMessageBox.warning(self, "警告", "请先运行分析")
            return

        from modules.export import export_all_to_xlsx
        import os

        filename, _ = QFileDialog.getSaveFileName(self, "保存全部数据", "SPM_Analysis_Results.xlsx", "Excel Files (*.xlsx)")
        if filename:
            export_all_to_xlsx(
                self.summary,
                self.main_window.normality_results,
                getattr(self, 'posthoc_summary', None),
                self.main_window.cached_spm_result,
                self.main_window.cached_inference_result,
                self.main_window.cached_posthoc_results,
                filename
            )
            QMessageBox.information(self, "成功", f"数据已保存至: {os.path.basename(filename)}")

    def go_prev(self):
        self.main_window.prev_tab()

    def go_next(self):
        if not self.summary:
            QMessageBox.warning(self, "警告", "请先运行分析")
            return

        self.main_window.next_tab()

    def run_posthoc(self):
        if not self.summary:
            QMessageBox.warning(self, "警告", "请先运行分析")
            return

        if self.summary.get('test_type') != 'anova1':
            QMessageBox.warning(self, "警告", "事后检验仅适用于单因素ANOVA分析")
            return

        if not self.summary.get('h0reject', False):
            QMessageBox.information(self, "信息", "主效应不显著，无需进行事后检验")
            return

        self.progress = QProgressDialog("正在运行事后检验...", "取消", 0, 0, self)
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

        self.main_window.tab_widget.setCurrentIndex(4)
        self.main_window.tab_plots.chart_type_combo.setCurrentText("事后检验图")
        self.main_window.tab_plots.update_chart()

        QMessageBox.information(self, "完成", "事后检验完成！")

    def on_posthoc_error(self, error):
        self.progress.close()
        QMessageBox.critical(self, "错误", f"事后检验失败: {error}")

    def update_posthoc_text(self):
        if not self.posthoc_summary:
            return

        text = "事后检验结果 (Bonferroni校正)\n"
        text += "=" * 50 + "\n\n"

        for pair_name, result in self.posthoc_summary.items():
            alpha_corr = result.get('alpha_corrected', 0)
            zstar = result.get('zstar')
            significant = result.get('significant')
            p_values = result.get('p_values', [])
            n_clusters = result.get('n_clusters', 0)

            text += f"比较对: {pair_name}\n"
            text += f"校正α = {alpha_corr:.6f}\n"
            if zstar is not None:
                text += f"阈值 z* = ±{zstar:.4f}\n"

            if significant is None:
                text += "结果: 计算失败\n"
            elif significant:
                text += f"结果: 显著 (存在 {n_clusters} 个聚类)\n"
                if p_values:
                    text += "聚类 p 值: " + ", ".join(p_values) + "\n"
            else:
                text += "结果: 不显著\n"
            text += "\n"

        self.posthoc_text.setText(text)
