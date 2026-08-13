from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QRadioButton,
                               QButtonGroup, QFileDialog,
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
from modules.utils import show_info, show_warning, show_critical
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

        self.title = QLabel(self.main_window.tr("tab_plots.title"))
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.title)

        layout.addLayout(self._create_chart_section())
        layout.addLayout(self._create_settings_section())
        layout.addLayout(self._create_export_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_chart_section(self):
        layout = QHBoxLayout()

        self.group_chart = QGroupBox(self.main_window.tr("tab_plots.preview"))
        group_layout = QVBoxLayout()

        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        group_layout.addWidget(self.canvas)
        self.group_chart.setLayout(group_layout)
        layout.addWidget(self.group_chart)

        return layout

    def _create_settings_section(self):
        layout = QHBoxLayout()

        self.group_settings = QGroupBox(self.main_window.tr("tab_plots.settings"))
        group_layout = QHBoxLayout()

        self.chart_type_label = QLabel(self.main_window.tr("tab_plots.chart_type"))
        group_layout.addWidget(self.chart_type_label)
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            self.main_window.tr("tab_plots.mean_curve"),
            self.main_window.tr("tab_plots.spm_curve"),
            self.main_window.tr("tab_plots.normality_plot"),
            self.main_window.tr("tab_plots.posthoc_plot")
        ])
        self.chart_type_combo.currentTextChanged.connect(self.update_group_combo)
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        group_layout.addWidget(self.chart_type_combo)

        self.select_label = QLabel(self.main_window.tr("tab_plots.select"))
        group_layout.addWidget(self.select_label)
        self.group_combo = QComboBox()
        self.group_combo.setEnabled(False)
        self.group_combo.currentTextChanged.connect(self.update_chart)
        group_layout.addWidget(self.group_combo)

        group_layout.addStretch()
        self.group_settings.setLayout(group_layout)
        layout.addWidget(self.group_settings)

        return layout

    def _create_export_section(self):
        layout = QHBoxLayout()

        self.group_export = QGroupBox(self.main_window.tr("tab_plots.export_chart"))
        group_layout = QHBoxLayout()

        self.btn_png = QPushButton(self.main_window.tr("tab_plots.export_png"))
        self.btn_png.clicked.connect(lambda: self.export_chart('png'))

        self.btn_pdf = QPushButton(self.main_window.tr("tab_plots.export_pdf"))
        self.btn_pdf.clicked.connect(lambda: self.export_chart('pdf'))

        self.btn_svg = QPushButton(self.main_window.tr("tab_plots.export_svg"))
        self.btn_svg.clicked.connect(lambda: self.export_chart('svg'))

        group_layout.addWidget(self.btn_png)
        group_layout.addWidget(self.btn_pdf)
        group_layout.addWidget(self.btn_svg)
        group_layout.addStretch()

        self.group_export.setLayout(group_layout)
        layout.addWidget(self.group_export)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        self.btn_prev = QPushButton(self.main_window.tr("tab_plots.prev_results"))
        self.btn_prev.clicked.connect(self.go_prev)

        layout.addWidget(self.btn_prev)
        layout.addStretch()

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
            
            if chart_type == self.main_window.tr("tab_plots.mean_curve"):
                ax = self.figure.add_subplot(111)
                if test_type in ['anova2rm', 'anova2onerm']:
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
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.no_y_data"), ha='center', va='center', fontsize=14)
                elif test_type in ['regress', 'anova2']:
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
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.no_y_data"), ha='center', va='center', fontsize=14)
                else:
                    plot_mean_sd(test_data, ax=ax)

            elif chart_type == self.main_window.tr("tab_plots.spm_curve"):
                ax = self.figure.add_subplot(111)
                spm_result = None
                inference_result = None

                test_type = summary.get('test_type', '')
                
                if test_type in ['anova2', 'anova2rm', 'anova2onerm']:
                    selected_effect = self.group_combo.currentText()
                    effect_index = 0
                    if selected_effect == self.main_window.tr("tab_plots.spm_main_effect_b"):
                        effect_index = 1
                    elif selected_effect == self.main_window.tr("tab_plots.spm_interaction"):
                        effect_index = 2
                    
                    if self.main_window.cached_spm_result is not None and self.main_window.cached_inference_result is not None:
                        spm_result = self.main_window.cached_spm_result
                        inference_result_list = self.main_window.cached_inference_result
                        if isinstance(inference_result_list, list) and len(inference_result_list) > effect_index:
                            inference_result = inference_result_list[effect_index]
                        else:
                            inference_result = None
                    else:
                        from modules.spm_analysis import SPMAnalyzer
                        np.random.seed(42)
                        
                        analyzer = SPMAnalyzer(test_data, test_type=test_type,
                                              method=summary['method'])
                        kwargs = {}
                        kwargs['A'] = summary.get('A')
                        kwargs['B'] = summary.get('B')
                        kwargs['y_data'] = summary.get('y_data')
                        if test_type in ['anova2rm', 'anova2onerm']:
                            kwargs['SUBJ'] = summary.get('SUBJ')
                        
                        spm_result, _ = analyzer.run_analysis()
                        if spm_result:
                            inference_result_list, _ = analyzer.inference(alpha=summary['alpha'])
                            if inference_result_list and isinstance(inference_result_list, list) and len(inference_result_list) > effect_index:
                                inference_result = inference_result_list[effect_index]
                                self.main_window.cached_spm_result = spm_result
                                self.main_window.cached_inference_result = inference_result_list
                    
                    if spm_result and inference_result:
                        plot_spm_result(spm_result[effect_index], inference_result, ax=ax, test_type='anova2', two_tailed=False, method=summary.get('method', 'param'))
                else:
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
                                if test_type in ['anova1', 'anova1rm']:
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
                        if test_type in ['anova1', 'anova1rm', 'anova2', 'anova3']:
                            two_tailed = False
                        else:
                            two_tailed = True
                        plot_spm_result(spm_result, inference_result, ax=ax, test_type=test_type, two_tailed=two_tailed, method=summary.get('method', 'param'))

            elif chart_type == self.main_window.tr("tab_plots.posthoc_plot"):
                selected_group = self.group_combo.currentText()
                if not selected_group:
                    ax = self.figure.add_subplot(111)
                    ax.text(0.5, 0.5, self.main_window.tr("tab_plots.select_comparison"), ha='center', va='center', fontsize=14)
                    self.canvas.draw()
                    return

                ax = self.figure.add_subplot(111)
                spm_result = None
                inference_result = None

                cached = self.main_window.cached_posthoc_results
                if cached is not None and selected_group in cached:
                    pair_result = cached[selected_group]
                    spm_result = pair_result['spm_result']
                    inference_result = pair_result['inference_result']
                else:
                    np.random.seed(42)
                    from modules.spm_analysis import SPMAnalyzer
                    posthoc_type = summary.get('test_type', '') if summary else ''
                    if posthoc_type not in ('anova1', 'anova1rm'):
                        posthoc_type = 'anova1'
                    analyzer = SPMAnalyzer(test_data, test_type=posthoc_type,
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
                    z_full = pair_result.get('z_full') if pair_result else None
                    plot_posthoc_result(spm_result, inference_result, ax=ax, title=selected_group, z_full=z_full)
                else:
                    ax.text(0.5, 0.5, self.main_window.tr("tab_plots.calc_failed"), ha='center', va='center', fontsize=14)

            elif chart_type == self.main_window.tr("tab_plots.normality_plot"):
                ax = self.figure.add_subplot(111)
                
                test_type = summary.get('test_type', '') if summary else ''
                
                if test_type == 'regress':
                    normality_results = getattr(self.main_window, 'normality_results', None)
                    if not normality_results or 'groups' not in normality_results:
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.run_normality_first"), ha='center', va='center', fontsize=14)
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
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.normality_empty"), ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return
                    
                    if 'error' in group_result:
                        error_code = group_result['error']
                        if error_code == 'sample_size_too_small':
                            error_msg = self.main_window.tr("tab_normality.error_sample_size")
                        else:
                            error_msg = self.main_window.tr("tab_normality.error_test_failed")
                        ax.text(0.5, 0.5, f"{self.main_window.tr('tab_plots.test_failed')}: {error_msg}", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return
                    
                    spm_result = group_result.get('spm_result')
                    inference_result = group_result.get('inference_result')
                    
                    if spm_result is None or inference_result is None:
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.results_incomplete"), ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return
                    
                    plot_k2_result(spm_result, inference_result, ax=ax, group_name=y_name)
                else:
                    selected_group = self.group_combo.currentText()
                    if not selected_group:
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.select_group"), ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    normality_results = getattr(self.main_window, 'normality_results', None)
                    if not normality_results or 'groups' not in normality_results:
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.run_normality_first"), ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    groups = normality_results['groups']
                    if selected_group not in groups:
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.group_not_found"), ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    group_result = groups[selected_group]
                    
                    if 'error' in group_result:
                        error_code = group_result['error']
                        if error_code == 'sample_size_too_small':
                            error_msg = self.main_window.tr("tab_normality.error_sample_size")
                        else:
                            error_msg = self.main_window.tr("tab_normality.error_test_failed")
                        ax.text(0.5, 0.5, f"{self.main_window.tr('tab_plots.test_failed')}: {error_msg}", ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    spm_result = group_result.get('spm_result')
                    inference_result = group_result.get('inference_result')
                    
                    if spm_result is None or inference_result is None:
                        ax.text(0.5, 0.5, self.main_window.tr("tab_plots.results_incomplete"), ha='center', va='center', fontsize=14)
                        self.canvas.draw()
                        return

                    plot_k2_result(spm_result, inference_result, ax=ax, group_name=selected_group)

            self.canvas.draw()

        except Exception as e:
            print(f"Chart error: {e}")

    def clear_data(self):
        self.figure.clear()
        self.canvas.draw()
        self.chart_type_combo.setCurrentIndex(0)

    def update_group_combo(self, text=None):
        chart_type = self.chart_type_combo.currentText()
        self.group_combo.clear()
        
        summary = getattr(self.main_window, 'analysis_result', None)
        test_type = summary.get('test_type', '') if summary else ''
        
        if chart_type == self.main_window.tr("tab_plots.posthoc_plot"):
            cached = getattr(self.main_window, 'cached_posthoc_results', None)
            if cached:
                self.group_combo.addItems(list(cached.keys()))
                self.group_combo.setEnabled(True)
                return
        elif chart_type == self.main_window.tr("tab_plots.normality_plot"):
            if test_type == 'regress':
                self.group_combo.setEnabled(False)
                return
            normality_results = getattr(self.main_window, 'normality_results', None)
            if normality_results and 'groups' in normality_results:
                groups = list(normality_results['groups'].keys())
                self.group_combo.addItems(groups)
                self.group_combo.setEnabled(True)
                return
        elif chart_type == self.main_window.tr("tab_plots.spm_curve"):
            if test_type in ['anova2', 'anova2rm', 'anova2onerm']:
                self.group_combo.addItems([
                    self.main_window.tr("tab_plots.spm_main_effect_a"),
                    self.main_window.tr("tab_plots.spm_main_effect_b"),
                    self.main_window.tr("tab_plots.spm_interaction")
                ])
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
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_plots.warn_run_analysis"))
            return

        chart_type = self.chart_type_combo.currentText()
        summary = self.main_window.analysis_result
        test_type = summary.get('test_type', '') if summary else ''
        
        selected_group = None
        if chart_type == self.main_window.tr("tab_plots.posthoc_plot"):
            selected_group = self.group_combo.currentText()
            if not selected_group:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_plots.select_comparison"))
                return
            default_name = f"posthoc_{selected_group.replace(' ', '_').replace('vs.', 'vs')}"
        elif chart_type == self.main_window.tr("tab_plots.normality_plot"):
            if test_type == 'regress':
                selected_group = None
                default_name = f"k2_normality_y"
            else:
                selected_group = self.group_combo.currentText()
                if not selected_group:
                    show_warning(self, self.main_window.tr("common.warning"), 
                                      self.main_window.tr("tab_plots.select_group"))
                    return
                default_name = f"k2_normality_{selected_group}"
        else:
            default_name = f"chart"

        filename, _ = QFileDialog.getSaveFileName(self, f"Save Chart", f"{default_name}.{fmt}",
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

                if chart_type == self.main_window.tr("tab_plots.mean_curve"):
                    fig, ax = plt.subplots(figsize=(10, 6))
                    test_type = summary.get('test_type', '') if summary else ''
                    if test_type in ['anova2rm', 'anova2onerm']:
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
                            ax.text(0.5, 0.5, self.main_window.tr("tab_plots.no_y_data"), ha='center', va='center', fontsize=14)
                    elif test_type == 'regress':
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
                            ax.text(0.5, 0.5, self.main_window.tr("tab_plots.no_y_data"), ha='center', va='center', fontsize=14)
                    else:
                        plot_mean_sd(test_data, ax=ax)
                    export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                elif chart_type == self.main_window.tr("tab_plots.spm_curve"):
                    spm_result = None
                    inference_result = None

                    if self.main_window.cached_spm_result is not None and self.main_window.cached_inference_result is not None:
                        spm_result = self.main_window.cached_spm_result
                        inference_result = self.main_window.cached_inference_result

                    test_type = summary.get('test_type', '')

                    if test_type in ['anova2', 'anova2rm', 'anova2onerm']:
                        selected_effect = self.group_combo.currentText()
                        effect_index = 0
                        if selected_effect == self.main_window.tr("tab_plots.spm_main_effect_b"):
                            effect_index = 1
                        elif selected_effect == self.main_window.tr("tab_plots.spm_interaction"):
                            effect_index = 2

                        if spm_result and inference_result:
                            inf_list = inference_result
                            spm_list = spm_result
                            if isinstance(inf_list, list) and len(inf_list) > effect_index:
                                inference_result = inf_list[effect_index]
                            if hasattr(spm_list, '__getitem__') and len(spm_list) > effect_index:
                                spm_result = spm_list[effect_index]

                        if spm_result is None or inference_result is None:
                            show_warning(self, self.main_window.tr("common.warning"),
                                              self.main_window.tr("tab_plots.calc_failed"))
                            return
                    else:
                        if spm_result is None or inference_result is None:
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
                        if test_type in ['anova1', 'anova1rm', 'anova2', 'anova2rm', 'anova2onerm', 'anova3']:
                            two_tailed = False
                        else:
                            two_tailed = True
                        fig, ax = plt.subplots(figsize=(10, 6))
                        plot_spm_result(spm_result, inference_result, ax=ax, test_type=test_type, two_tailed=two_tailed, method=summary.get('method', 'param'))
                        export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                elif chart_type == self.main_window.tr("tab_plots.posthoc_plot"):
                    if selected_group:
                        spm_result = None
                        inference_result = None

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
                            z_full = pair_result.get('z_full') if pair_result else None
                            fig, ax = plt.subplots(figsize=(10, 6))
                            plot_posthoc_result(spm_result, inference_result, ax=ax, title=selected_group, z_full=z_full)
                            export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                elif chart_type == self.main_window.tr("tab_plots.normality_plot"):
                    test_type = summary.get('test_type', '') if summary else ''
                    if test_type == 'regress':
                        normality_results = getattr(self.main_window, 'normality_results', None)
                        if not normality_results or 'groups' not in normality_results:
                            show_warning(self, self.main_window.tr("common.warning"), 
                                              self.main_window.tr("tab_plots.run_normality_first"))
                            return
                        
                        groups = normality_results.get('groups', {})
                        y_name = summary.get('y_name') if summary else None
                        if y_name and y_name in groups:
                            group_result = groups[y_name]
                        elif groups:
                            y_name = list(groups.keys())[0]
                            group_result = groups[y_name]
                        else:
                            show_warning(self, self.main_window.tr("common.warning"), 
                                              self.main_window.tr("tab_plots.normality_empty"))
                            return
                        
                        if 'error' in group_result:
                            show_warning(self, self.main_window.tr("common.warning"), 
                                              f"{self.main_window.tr('tab_plots.test_failed')}: {group_result['error']}")
                            return
                        
                        spm_result = group_result.get('spm_result')
                        inference_result = group_result.get('inference_result')
                        
                        if spm_result is None or inference_result is None:
                            show_warning(self, self.main_window.tr("common.warning"), 
                                              self.main_window.tr("tab_plots.results_incomplete"))
                            return

                        fig, ax = plt.subplots(figsize=(10, 6))
                        plot_k2_result(spm_result, inference_result, ax=ax, group_name=y_name)
                        export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)
                    else:
                        if selected_group:
                            normality_results = getattr(self.main_window, 'normality_results', None)
                            
                            if not normality_results or 'groups' not in normality_results:
                                show_warning(self, self.main_window.tr("common.warning"), 
                                                  self.main_window.tr("tab_plots.run_normality_first"))
                                return

                            groups = normality_results['groups']
                            if selected_group not in groups:
                                show_warning(self, self.main_window.tr("common.warning"), 
                                                  self.main_window.tr("tab_plots.group_not_found"))
                                return

                            group_result = groups[selected_group]
                            
                            if 'error' in group_result:
                                show_warning(self, self.main_window.tr("common.warning"), 
                                                  f"{self.main_window.tr('tab_plots.test_failed')}: {group_result['error']}")
                                return

                            spm_result = group_result.get('spm_result')
                            inference_result = group_result.get('inference_result')
                            
                            if spm_result is None or inference_result is None:
                                show_warning(self, self.main_window.tr("common.warning"), 
                                                  self.main_window.tr("tab_plots.results_incomplete"))
                                return

                            fig, ax = plt.subplots(figsize=(10, 6))
                            plot_k2_result(spm_result, inference_result, ax=ax, group_name=selected_group)
                            export_figure(fig, filename.replace(f'.{fmt}', ''), fmt)

                show_info(self, self.main_window.tr("common.success"), 
                                      self.main_window.tr("tab_plots.chart_saved").format(filename))

            except Exception as e:
                show_critical(self, self.main_window.tr("common.error"), 
                                   f"{self.main_window.tr('tab_plots.export_failed')}: {str(e)}")

    def go_prev(self):
        self.main_window.prev_tab()

    def retranslate_ui(self):
        self.title.setText(self.main_window.tr("tab_plots.title"))
        self.group_chart.setTitle(self.main_window.tr("tab_plots.preview"))
        self.group_settings.setTitle(self.main_window.tr("tab_plots.settings"))
        self.chart_type_label.setText(self.main_window.tr("tab_plots.chart_type"))
        self.select_label.setText(self.main_window.tr("tab_plots.select"))
        self.group_export.setTitle(self.main_window.tr("tab_plots.export_chart"))
        self.btn_png.setText(self.main_window.tr("tab_plots.export_png"))
        self.btn_pdf.setText(self.main_window.tr("tab_plots.export_pdf"))
        self.btn_svg.setText(self.main_window.tr("tab_plots.export_svg"))
        self.btn_prev.setText(self.main_window.tr("tab_plots.prev_results"))
        
        current_chart = self.chart_type_combo.currentText()
        self.chart_type_combo.clear()
        self.chart_type_combo.addItems([
            self.main_window.tr("tab_plots.mean_curve"),
            self.main_window.tr("tab_plots.spm_curve"),
            self.main_window.tr("tab_plots.normality_plot"),
            self.main_window.tr("tab_plots.posthoc_plot")
        ])
        
        self.update_group_combo()
