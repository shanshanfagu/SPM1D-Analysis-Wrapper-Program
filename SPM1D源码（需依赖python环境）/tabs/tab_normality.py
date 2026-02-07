from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QGroupBox, QRadioButton, QButtonGroup,
                              QDoubleSpinBox, QMessageBox, QHeaderView,
                              QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modules.normality_test import run_normality_tests

class TabNormality(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.results = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("正态性检验")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addLayout(self._create_settings_section())
        layout.addLayout(self._create_results_section())
        layout.addLayout(self._create_recommendation_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_settings_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("检验设置")
        group_layout = QHBoxLayout()

        group_layout.addWidget(QLabel("显著性水平 (α):"))
        self.alpha_input = QDoubleSpinBox()
        self.alpha_input.setRange(0.001, 0.5)
        self.alpha_input.setValue(0.05)
        self.alpha_input.setDecimals(3)
        group_layout.addWidget(self.alpha_input)

        group_layout.addStretch()

        btn_run = QPushButton("运行正态性检验")
        btn_run.clicked.connect(self.run_test)

        group_layout.addWidget(btn_run)

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_results_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("检验结果")
        group_layout = QVBoxLayout()

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["组别", "平均K²统计量", "平均p值", "显著性", "状态"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        group_layout.addWidget(self.result_table)

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_recommendation_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("检验方法推荐")
        group_layout = QVBoxLayout()

        self.recommendation_text = QTextEdit()
        self.recommendation_text.setReadOnly(True)
        self.recommendation_text.setMaximumHeight(100)

        group_layout.addWidget(self.recommendation_text)

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        btn_prev = QPushButton("← 返回数据导入")
        btn_prev.clicked.connect(self.go_prev)

        btn_next = QPushButton("下一步: 参数设置 →")
        btn_next.clicked.connect(self.go_next)

        layout.addWidget(btn_prev)
        layout.addStretch()
        layout.addWidget(btn_next)

        return layout

    def run_test(self):
        data = self.main_window.analysis_data
        if not data:
            QMessageBox.warning(self, "警告", "请先加载数据")
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

            QMessageBox.information(self, "完成", "正态性检验完成！")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"检验失败: {str(e)}")

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
            status = "不显著" if is_normal else "显著"
            significance = "✓ 正态" if is_normal else "✗ 非正态"

            self.result_table.setItem(row, 3, QTableWidgetItem(status))
            self.result_table.setItem(row, 4, QTableWidgetItem(significance))

    def update_recommendation(self):
        rec = self.results['recommendation']
        text = f"推荐: {rec['reason']}\n\n"
        text += f"正常组: {', '.join(rec['normal_groups']) if rec['normal_groups'] else '无'}\n"
        text += f"非正常组: {', '.join([g[0] for g in rec['abnormal_groups']]) if rec['abnormal_groups'] else '无'}"

        self.recommendation_text.setText(text)

    def go_prev(self):
        self.main_window.prev_tab()

    def go_next(self):
        if not self.results:
            QMessageBox.warning(self, "警告", "请先运行正态性检验")
            return

        self.main_window.next_tab()
