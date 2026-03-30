from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QGroupBox, QRadioButton, QButtonGroup,
                               QDoubleSpinBox, QHeaderView,
                               QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modules.normality_test import run_normality_tests
from modules.utils import show_info, show_warning, show_critical

class TabNormality(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.results = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        self.title = QLabel(self.main_window.tr("tab_normality.title"))
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.title)

        layout.addLayout(self._create_settings_section())
        layout.addLayout(self._create_results_section())
        layout.addLayout(self._create_recommendation_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_settings_section(self):
        layout = QHBoxLayout()

        self.group_settings = QGroupBox(self.main_window.tr("tab_normality.test_settings"))
        group_layout = QHBoxLayout()

        self.alpha_label = QLabel(self.main_window.tr("tab_normality.alpha_label"))
        group_layout.addWidget(self.alpha_label)
        self.alpha_input = QDoubleSpinBox()
        self.alpha_input.setRange(0.001, 0.5)
        self.alpha_input.setValue(0.05)
        self.alpha_input.setDecimals(3)
        group_layout.addWidget(self.alpha_input)

        group_layout.addStretch()

        self.btn_run = QPushButton(self.main_window.tr("tab_normality.run_test"))
        self.btn_run.clicked.connect(self.run_test)

        group_layout.addWidget(self.btn_run)

        self.group_settings.setLayout(group_layout)
        layout.addWidget(self.group_settings)

        return layout

    def _create_results_section(self):
        layout = QHBoxLayout()

        self.group_results = QGroupBox(self.main_window.tr("tab_normality.test_results"))
        group_layout = QVBoxLayout()

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            self.main_window.tr("tab_normality.col_group"),
            self.main_window.tr("tab_normality.col_k2"),
            self.main_window.tr("tab_normality.col_pvalue"),
            self.main_window.tr("tab_normality.col_significance"),
            self.main_window.tr("tab_normality.col_status")
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        group_layout.addWidget(self.result_table)

        self.group_results.setLayout(group_layout)
        layout.addWidget(self.group_results)

        return layout

    def _create_recommendation_section(self):
        layout = QHBoxLayout()

        self.group_recommend = QGroupBox(self.main_window.tr("tab_normality.method_recommendation"))
        group_layout = QVBoxLayout()

        self.recommendation_text = QTextEdit()
        self.recommendation_text.setReadOnly(True)
        self.recommendation_text.setMaximumHeight(100)

        group_layout.addWidget(self.recommendation_text)

        self.group_recommend.setLayout(group_layout)
        layout.addWidget(self.group_recommend)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        self.btn_prev = QPushButton(self.main_window.tr("tab_normality.prev_import"))
        self.btn_prev.clicked.connect(self.go_prev)

        self.btn_next = QPushButton(self.main_window.tr("tab_normality.next_params"))
        self.btn_next.clicked.connect(self.go_next)

        layout.addWidget(self.btn_prev)
        layout.addStretch()
        layout.addWidget(self.btn_next)

        return layout

    def run_test(self):
        data = self.main_window.analysis_data
        if not data:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_normality.warn_load_data"))
            return

        indicator = getattr(self.main_window, 'selected_indicator', None)
        if indicator and indicator in data:
            test_data = data[indicator]
        else:
            test_data = list(data.values())[0]

        try:
            alpha = self.alpha_input.value()
            self.results = run_normality_tests(test_data, alpha)

            self.update_results_table()
            self.update_recommendation()

            self.main_window.normality_results = self.results

            show_info(self, self.main_window.tr("common.success"), 
                                  self.main_window.tr("tab_normality.test_complete"))

        except Exception as e:
            show_critical(self, self.main_window.tr("common.error"), 
                               f"{self.main_window.tr('tab_normality.error_test_failed')}: {str(e)}")

    def update_results_table(self):
        self.result_table.setRowCount(0)

        for group_name, result in self.results['groups'].items():
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)

            k2_val = result.get('k2_statistic', 'N/A')
            p_val = result.get('p_value', 'N/A')

            self.result_table.setItem(row, 0, QTableWidgetItem(group_name))
            self.result_table.setItem(row, 1, QTableWidgetItem(f"{k2_val:.4f}" if isinstance(k2_val, float) else str(k2_val)))
            self.result_table.setItem(row, 2, QTableWidgetItem(f"{p_val:.4f}" if isinstance(p_val, float) else str(p_val)))

            is_normal = result.get('is_normal', False)
            status = self.main_window.tr("tab_normality.not_significant") if is_normal else self.main_window.tr("tab_normality.significant")
            significance = self.main_window.tr("tab_normality.normal") if is_normal else self.main_window.tr("tab_normality.non_normal")

            if 'error' in result:
                error_code = result.get('error', 'test_failed')
                if error_code == 'sample_size_too_small':
                    error_msg = self.main_window.tr("tab_normality.error_sample_size")
                else:
                    error_msg = self.main_window.tr("tab_normality.error_test_failed")
                status = error_msg
                significance = "✗ " + error_msg

            self.result_table.setItem(row, 3, QTableWidgetItem(status))
            self.result_table.setItem(row, 4, QTableWidgetItem(significance))

    def update_recommendation(self):
        rec = self.results['recommendation']
        reason_code = rec['reason']
        
        if reason_code == "all_normal":
            reason_text = self.main_window.tr("tab_normality.reason_all_normal")
        elif reason_code == "all_abnormal":
            reason_text = self.main_window.tr("tab_normality.reason_all_abnormal")
        else:
            abnormal_names = ', '.join([g[0] for g in rec['abnormal_groups']])
            reason_text = self.main_window.tr("tab_normality.reason_some_abnormal").format(abnormal_names)
        
        def translate_error(msg):
            if msg == 'sample_size_too_small':
                return self.main_window.tr("tab_normality.error_sample_size")
            elif msg == 'test_failed':
                return self.main_window.tr("tab_normality.error_test_failed")
            elif 'gradient' in msg.lower() or 'edge_order' in msg.lower():
                return self.main_window.tr("tab_normality.error_gradient")
            return msg
        
        abnormal_display = []
        for g in rec['abnormal_groups']:
            translated_msg = translate_error(g[1])
            abnormal_display.append(f"{g[0]} ({translated_msg})")
        
        text = f"{self.main_window.tr('tab_normality.recommendation')} {reason_text}\n\n"
        text += f"{self.main_window.tr('tab_normality.normal_groups')} {', '.join(rec['normal_groups']) if rec['normal_groups'] else self.main_window.tr('tab_normality.none')}\n"
        text += f"{self.main_window.tr('tab_normality.abnormal_groups')} {', '.join(abnormal_display) if abnormal_display else self.main_window.tr('tab_normality.none')}"

        self.recommendation_text.setText(text)

    def go_prev(self):
        self.main_window.prev_tab()

    def clear_data(self):
        self.results = None
        self.result_table.setRowCount(0)
        self.recommendation_text.clear()

    def go_next(self):
        if not self.results:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_normality.warn_run_normality"))
            return

        self.main_window.next_tab()

    def retranslate_ui(self):
        self.title.setText(self.main_window.tr("tab_normality.title"))
        self.group_settings.setTitle(self.main_window.tr("tab_normality.test_settings"))
        self.alpha_label.setText(self.main_window.tr("tab_normality.alpha_label"))
        self.btn_run.setText(self.main_window.tr("tab_normality.run_test"))
        self.group_results.setTitle(self.main_window.tr("tab_normality.test_results"))
        
        self.result_table.setHorizontalHeaderLabels([
            self.main_window.tr("tab_normality.col_group"),
            self.main_window.tr("tab_normality.col_k2"),
            self.main_window.tr("tab_normality.col_pvalue"),
            self.main_window.tr("tab_normality.col_significance"),
            self.main_window.tr("tab_normality.col_status")
        ])
        
        self.group_recommend.setTitle(self.main_window.tr("tab_normality.method_recommendation"))
        self.btn_prev.setText(self.main_window.tr("tab_normality.prev_import"))
        self.btn_next.setText(self.main_window.tr("tab_normality.next_params"))
        
        if self.results:
            self.update_results_table()
            self.update_recommendation()
