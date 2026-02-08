from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QGroupBox, QRadioButton,
                              QButtonGroup, QMessageBox, QFileDialog,
                              QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

from modules.visualization import plot_mean_sd, plot_spm_result, plot_posthoc_result, plot_k2_result
from utils.config import COLORS

class TabPlots(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.group_combo = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("图表查看")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addLayout(self._create_chart_section())
        layout.addLayout(self._create_settings_section())
        layout.addLayout(self._create_export_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_chart_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("图表预览")
        group_layout = QVBoxLayout()

        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        group_layout.addWidget(self.canvas)
        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_settings_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("图表设置")
        group_layout = QHBoxLayout()

        group_layout.addWidget(QLabel("图表类型:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["均值曲线图", "SPM统计曲线图", "检验正态分布图", "事后检验图"])
        self.chart_type_combo.currentTextChanged.connect(self.update_group_combo)
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        group_layout.addWidget(self.chart_type_combo)

        group_layout.addWidget(QLabel("  选择:"))
        self.group_combo = QComboBox()
        self.group_combo.setEnabled(False)
        self.group_combo.currentTextChanged.connect(self.update_chart)
        group_layout.addWidget(self.group_combo)

        group_layout.addStretch()
        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_export_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("导出图表")
        group_layout = QHBoxLayout()

        btn_png = QPushButton("导出PNG")
        btn_png.clicked.connect(lambda: self.export_chart('png'))

        btn_pdf = QPushButton("导出PDF")
        btn_pdf.clicked.connect(lambda: self.export_chart('pdf'))

        btn_svg = QPushButton("导出SVG")
        btn_svg.clicked.connect(lambda: self.export_chart('svg'))

        group_layout.addWidget(btn_png)
        group_layout.addWidget(btn_pdf)
        group_layout.addWidget(btn_svg)
        group_layout.addStretch()

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        btn_prev = QPushButton("← 返回分析结果")
        btn_prev.clicked.connect(self.go_prev)

        btn_restart = QPushButton("重新开始")
        btn_restart.clicked.connect(self.restart)

        layout.addWidget(btn_prev)
        layout.addStretch()
        layout.addWidget(btn_restart)

        return layout

    def update_chart(self, text=None):
        if not self.main_window.analysis_data or not self.main_window.analysis_result:
            return

        chart_type = self.chart_type_combo.currentText()
        data = self.main_window.analysis_data
        summary = self.main_window.analysis_result

        indicator = getattr(self.main_window, 'selected_indicator', None)
        if indicator and indicator in data:
            test_data = data[indicator]
        else:
            test_data = list(data.values())[0]

        self.figure.clear()

        try:
            test_type = summary.get('test_type', '') if summary else ''
            
            if chart_type == "均值曲线图":
                ax = self.figure.add_subplot(111)
                if test_type == 'regress':
                    y_data = summary.get('y_data') if summary else None
                    y_name = summary.get('y_name', 'Y') if summary else 'Y'
                    if y_data is not None:
                        mean = np.mean(y_data, axis=0)
                        sd = np.std(y_data, axis=0, ddof=1)
                        x = np.arange(len(mean))
                        color = COLORS['line_colors'][0]
                        ax.plot(x, mean, color=color, linewidth=2, label=y_name)
                        ax.fill_between(x, mean - sd, mean + sd, color=color, alpha=0.2)
                        ax.set_xlabel('Time Point', fontsize=12)
                        ax.set_ylabel('Value', fontsize=12)
                        ax.legend(loc='best', fontsize=10)
                        ax.grid(True, alpha=0.3)
                    else:
                        ax.text(0.5, 0.5, "无法获取Y数据", ha='center', va='center', fontsize=14)
                else:
                    plot_mean_sd(test_data, ax=ax)

            elif chart_type == "SPM统计曲线图":
                ax = self.figure.add_subplot(111)
                spm_result = None
                inference_result = None

                if self.main_window.cached_spm_result is not None and self.main_window.cached_inference_result is not None:
                    spm_result = self.main_window.cached_spm_result
                    inference_result = self.main_window.cached_inference_result
                else:
                    from modules.spm_analysis import SPMAnalyzer
                    np.random.seed(42)
                    
                    test_type = summary.get('test_type', '')
                    analyzer = SPMAnalyzer(test_data, test_type=test_type,
                                          method=summary['method'])
                    spm_result, _ = analyzer.run_analysis()
                    if spm_result:
                        if summary['method'] == 'param':
                            if test_type == 'anova1':
                                inference_result, _ = analyzer.inference(alpha=summary['alpha'])
                            else:
                                inference_result, _ = analyzer.inference(alpha=summary['alpha'], two_tailed=True)
                        else:
                            inference_result, _ = analyzer.inference(alpha=summary['alpha'],
                                                               iterations=summary.get('iterations', 500))
                        if inference_result:
                            self.main_window.cached_spm_result = spm_result
                            self.main_window.cached_inference_result = inference_result

                if spm_result and inference_result:
                    test_type = summary.get('test_type', '')
                    if test_type in ['anova1', 'anova2', 'anova3']:
                        two_tailed = False
                    else:
                        two_tailed = True
                    plot_spm_result(spm_result, inference_result, ax=ax, test_type=test_type, two_tailed=two_tailed)

            elif chart_type == "事后检验图":
                selected_group = self.group_combo.currentText()
                if not selected_group:
                    ax = self.figure.add_subplot(111)
                    ax.text(0.5, 0.5, "请选择比较对", ha='center', va='center', fontsize=14)
                    self.canvas.draw()
                    return

                ax = self.figure.add_subplot(111)
                spm_result = None
                inference_result = None

                # 使用缓存
                cached = self.main_window.cached_posthoc_results
                if cached is not None and selected_group in cached:
                    pair_result = cached[selected_group]
                    spm_result = pair_result['spm_result']
                    inference_result = pair_result['inference_result']
                else:
                    np.random.seed(42)
                    from modules.spm_analysis import SPMAnalyzer
                    analyzer = SPMAnalyzer(test_data, test_type='anova1',
                                          method=summary['method'])
                    spm_result, _ = analyzer.run_analysis()
                    if spm_result:
                        posthoc_results, _ = analyzer.run_posthoc(alpha=summary.get('alpha', 0.05))
                        if posthoc_results:
                            self.main_window.cached_posthoc_results = posthoc_results
                            if selected_group in posthoc_results:
                                pair_result = posthoc_results[selected_group]
                                spm_result = pair_result['spm_result']
                                inference_result = pair_result['inference_result']

                if spm_result and inference_result:
                    plot_posthoc_result(spm_result, inference_result, ax=ax, title=selected_group)
                else:
                    ax.text(0.5, 0.5, "计算失败", ha='center', va='center', fontsize=14)

            elif chart_type == "检验正态分布图":
                ax = self.figure.add_subplot(111)
                
                test_type = summary.get('test_type', '') if summary else ''
                
                if test_type == 'regress':
                    normality_results = getattr(self.main_window, 'normality_results', None)
                    if not normality_results or 'groups' not in normality_results:
                        ax.text(0.5, 0.5, "请先执行正态性检验", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return
                    
                    groups = normality_results.get('groups', {})
                    y_name = summary.get('y_name') if summary else None
                    if y_name and y_name in groups:
                        group_result = groups[y_name]
                    elif groups:
                        y_name = list(groups.keys())[0]
                        group_result = groups[y_name]
                    else:
                        ax.text(0.5, 0.5, "正态性检验结果为空", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return
                    
                    if 'error' in group_result:
                        ax.text(0.5, 0.5, f"检验失败: {group_result['error']}", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return
                    
                    spm_result = group_result.get('spm_result')
                    inference_result = group_result.get('inference_result')
                    
                    if spm_result is None or inference_result is None:
                        ax.text(0.5, 0.5, "结果不完整，请重新运行正态性检验", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return
                    
                    plot_k2_result(spm_result, inference_result, ax=ax, group_name=y_name)
                else:
                    selected_group = self.group_combo.currentText()
                    if not selected_group:
                        ax.text(0.5, 0.5, "请选择组别", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    normality_results = getattr(self.main_window, 'normality_results', None)
                    if not normality_results or 'groups' not in normality_results:
                        ax.text(0.5, 0.5, "请先执行正态性检验", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    groups = normality_results['groups']
                    if selected_group not in groups:
                        ax.text(0.5, 0.5, "选择的组不在检验结果中", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    group_result = groups[selected_group]
                    
                    if 'error' in group_result:
                        ax.text(0.5, 0.5, f"检验失败: {group_result['error']}", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    spm_result = group_result.get('spm_result')
                    inference_result = group_result.get('inference_result')
                    
                    if spm_result is None or inference_result is None:
                        ax.text(0.5, 0.5, "结果不完整，请重新运行正态性检验", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    plot_k2_result(spm_result, inference_result, ax=ax, group_name=selected_group)

            self.canvas.draw()

        except Exception as e:
            print(f"绑图错误: {e}")

    def update_group_combo(self, text=None):
        chart_type = self.chart_type_combo.currentText()
        self.group_combo.clear()
        
        summary = getattr(self.main_window, 'analysis_result', None)
        test_type = summary.get('test_type', '') if summary else ''
        
        if chart_type == "事后检验图":
            cached = getattr(self.main_window, 'cached_posthoc_results', None)
            if cached:
                self.group_combo.addItems(list(cached.keys()))
                self.group_combo.setEnabled(True)
                return
        elif chart_type == "检验正态分布图":
            if test_type == 'regress':
                self.group_combo.setEnabled(False)
                return
            normality_results = getattr(self.main_window, 'normality_results', None)
            if normality_results and 'groups' in normality_results:
                groups = list(normality_results['groups'].keys())
                self.group_combo.addItems(groups)
                self.group_combo.setEnabled(True)
                return
        
        self.group_combo.setEnabled(False)

    def update_posthoc_combo(self):
        if self.group_combo is not None:
            cached = getattr(self.main_window, 'cached_posthoc_results', None)
            if cached:
                self.group_combo.clear()
                self.group_combo.addItems(list(cached.keys()))
                self.group_combo.setEnabled(True)

    def export_chart(self, fmt):
        if not self.main_window.analysis_result:
            QMessageBox.warning(self, "警告", "请先运行分析")
            return

        chart_type = self.chart_type_combo.currentText()
        summary = self.main_window.analysis_result
        test_type = summary.get('test_type', '') if summary else ''
        
        selected_group = None
        if chart_type == "事后检验图":
            selected_group = self.group_combo.currentText()
            if not selected_group:
                QMessageBox.warning(self, "警告", "请选择比较对")
                return
            default_name = f"posthoc_{selected_group.replace(' ', '_').replace('vs.', 'vs')}"
        elif chart_type == "检验正态分布图":
            if test_type == 'regress':
                selected_group = None
                default_name = f"k2_normality_y"
            else:
                selected_group = self.group_combo.currentText()
                if not selected_group:
                    QMessageBox.warning(self, "警告", "请选择组别")
                    return
                default_name = f"k2_normality_{selected_group}"
        else:
            default_name = f"chart"

        filename, _ = QFileDialog.getSaveFileName(self, f"保存图表", f"{default_name}.{fmt}",
                                                  f"{fmt.upper()} Files (*.{fmt})")
        if filename:
            if not filename.endswith(f'.{fmt}'):
                filename += f'.{fmt}'

            data = self.main_window.analysis_data
            indicator = getattr(self.main_window, 'selected_indicator', None)
            if indicator and indicator in data:
                test_data = data[indicator]
            else:
                test_data = list(data.values())[0]

            try:
                from modules.visualization import export_figure

                if chart_type == "均值曲线图":
                    fig, ax = plt.subplots(figsize=(10, 6))
                    test_type = summary.get('test_type', '') if summary else ''
                    if test_type == 'regress':
                        y_data = summary.get('y_data') if summary else None
                        y_name = summary.get('y_name', 'Y') if summary else 'Y'
                        if y_data is not None:
                            mean = np.mean(y_data, axis=0)
                            sd = np.std(y_data, axis=0, ddof=1)
                            x = np.arange(len(mean))
                            ax.plot(x, mean, color='blue', linewidth=2, label=y_name)
                            ax.fill_between(x, mean - sd, mean + sd, color='blue', alpha=0.2)
                            ax.set_xlabel('Time Point', fontsize=12)
                            ax.set_ylabel('Value', fontsize=12)
                            ax.legend(loc='best', fontsize=10)
                            ax.grid(True, alpha=0.3)
                        else:
                            ax.text(0.5, 0.5, "无法获取Y数据", ha='center', va='center', fontsize=14)
                    else:
                        plot_mean_sd(test_data, ax=ax)
                    export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                elif chart_type == "SPM统计曲线图":
                    spm_result = None
                    inference_result = None

                    # 使用缓存
                    if self.main_window.cached_spm_result is not None and self.main_window.cached_inference_result is not None:
                        spm_result = self.main_window.cached_spm_result
                        inference_result = self.main_window.cached_inference_result
                    else:
                        np.random.seed(42)
                        from modules.spm_analysis import SPMAnalyzer
                        analyzer = SPMAnalyzer(test_data, test_type=summary['test_type'],
                                              method=summary['method'])
                        spm_result, _ = analyzer.run_analysis()
                        if spm_result:
                            if summary['method'] == 'param':
                                if summary.get('test_type') == 'anova1':
                                    inference_result, _ = analyzer.inference(alpha=summary['alpha'])
                                else:
                                    inference_result, _ = analyzer.inference(alpha=summary['alpha'], two_tailed=True)
                            else:
                                inference_result, _ = analyzer.inference(alpha=summary['alpha'],
                                                               iterations=summary.get('iterations', 500))
                            if inference_result:
                                self.main_window.cached_spm_result = spm_result
                                self.main_window.cached_inference_result = inference_result

                    if spm_result and inference_result:
                        # 根据检验类型确定阈值线显示
                        test_type = summary.get('test_type', '')
                        if test_type in ['anova1', 'anova2', 'anova3']:
                            two_tailed = False
                        else:
                            two_tailed = True
                        fig, ax = plt.subplots(figsize=(10, 6))
                        plot_spm_result(spm_result, inference_result, ax=ax, test_type=test_type, two_tailed=two_tailed)
                        export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                elif chart_type == "事后检验图":
                    if selected_group:
                        spm_result = None
                        inference_result = None

                        # 使用缓存
                        cached = self.main_window.cached_posthoc_results
                        if cached is not None and selected_group in cached:
                            pair_result = cached[selected_group]
                            spm_result = pair_result['spm_result']
                            inference_result = pair_result['inference_result']
                        else:
                            np.random.seed(42)
                            from modules.spm_analysis import SPMAnalyzer
                            analyzer = SPMAnalyzer(test_data, test_type='anova1',
                                                  method=summary['method'])
                            spm_result, _ = analyzer.run_analysis()
                            if spm_result:
                                posthoc_results, _ = analyzer.run_posthoc(alpha=summary.get('alpha', 0.05))
                                if posthoc_results:
                                    self.main_window.cached_posthoc_results = posthoc_results
                                    if selected_group in posthoc_results:
                                        pair_result = posthoc_results[selected_group]
                                        spm_result = pair_result['spm_result']
                                        inference_result = pair_result['inference_result']

                        if spm_result and inference_result:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            plot_posthoc_result(spm_result, inference_result, ax=ax, title=selected_group)
                            export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                elif chart_type == "检验正态分布图":
                    test_type = summary.get('test_type', '') if summary else ''
                    if test_type == 'regress':
                        normality_results = getattr(self.main_window, 'normality_results', None)
                        if not normality_results or 'groups' not in normality_results:
                            QMessageBox.warning(self, "警告", "请先执行正态性检验")
                            return
                        
                        groups = normality_results.get('groups', {})
                        y_name = summary.get('y_name') if summary else None
                        if y_name and y_name in groups:
                            group_result = groups[y_name]
                        elif groups:
                            y_name = list(groups.keys())[0]
                            group_result = groups[y_name]
                        else:
                            QMessageBox.warning(self, "警告", "正态性检验结果为空")
                            return
                        
                        if 'error' in group_result:
                            QMessageBox.warning(self, "警告", f"检验失败: {group_result['error']}")
                            return
                        
                        spm_result = group_result.get('spm_result')
                        inference_result = group_result.get('inference_result')
                        
                        if spm_result is None or inference_result is None:
                            QMessageBox.warning(self, "警告", "结果不完整，请重新运行正态性检验")
                            return

                        fig, ax = plt.subplots(figsize=(10, 6))
                        plot_k2_result(spm_result, inference_result, ax=ax, group_name=y_name)
                        export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)
                    else:
                        if selected_group:
                            normality_results = getattr(self.main_window, 'normality_results', None)
                            
                            if not normality_results or 'groups' not in normality_results:
                                QMessageBox.warning(self, "警告", "请先执行正态性检验")
                                return

                            groups = normality_results['groups']
                            if selected_group not in groups:
                                QMessageBox.warning(self, "警告", "选择的组不在检验结果中")
                                return

                            group_result = groups[selected_group]
                            
                            if 'error' in group_result:
                                QMessageBox.warning(self, "警告", f"检验失败: {group_result['error']}")
                                return

                            spm_result = group_result.get('spm_result')
                            inference_result = group_result.get('inference_result')
                            
                            if spm_result is None or inference_result is None:
                                QMessageBox.warning(self, "警告", "结果不完整，请重新运行正态性检验")
                                return

                            fig, ax = plt.subplots(figsize=(10, 6))
                            plot_k2_result(spm_result, inference_result, ax=ax, group_name=selected_group)
                            export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                QMessageBox.information(self, "成功", f"图表已保存: {filename}")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def go_prev(self):
        self.main_window.prev_tab()

    def restart(self):
        from tabs.tab_import import TabImport
        self.main_window.analysis_data = {}
        self.main_window.normality_results = None
        self.main_window.analysis_params = {}
        self.main_window.analysis_result = None
        self.main_window.analysis_summary = None
        self.main_window.posthoc_summary = None
        self.main_window.selected_indicator = None

        # 清空缓存
        self.main_window.cached_spm_result = None
        self.main_window.cached_inference_result = None
        self.main_window.cached_posthoc_results = None
        self.main_window.cached_k2_result = None

        if self.group_combo is not None:
            self.group_combo.clear()
            self.group_combo.setEnabled(False)
        if self.chart_type_combo is not None:
            self.chart_type_combo.setCurrentIndex(0)

        self.main_window.tab_widget.setCurrentIndex(0)
        self.main_window.tab_widget.widget(0).data = None
        self.main_window.tab_widget.widget(0).btn_next.setEnabled(False)
