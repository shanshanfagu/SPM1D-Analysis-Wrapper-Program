from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QGroupBox, QRadioButton,
                              QButtonGroup, QDoubleSpinBox, QSpinBox,
                              QMessageBox, QTextEdit, QDialog, QComboBox,
                              QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class TabParams(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.main_layout = None
        self.test_type_group = None
        self.test_radios = {}
        self.test_type_widget = None
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)

        title = QLabel("参数设置")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(title)

        self._create_test_type_section()
        self._create_alpha_section()
        self._create_nonparam_section()
        self._create_method_selection_section()
        self._create_button_section()

        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

    def _create_test_type_section(self):
        if self.test_type_widget:
            self.test_type_widget.deleteLater()

        group = QGroupBox("分析类型")
        group_layout = QVBoxLayout()

        self.test_type_group = QButtonGroup()
        self.test_radios = {}

        test_types = self._get_test_types()

        if not test_types:
            warning_label = QLabel("无法进行统计检验\n\n请导入包含至少2个组别的数据")
            warning_label.setStyleSheet("color: red; font-weight: bold;")
            group_layout.addWidget(warning_label)
            self.test_radios = {}
        else:
            for name, value in test_types:
                radio = QRadioButton(name)
                self.test_type_group.addButton(radio)
                self.test_radios[value] = radio
                group_layout.addWidget(radio)

            if test_types:
                self.test_radios[test_types[0][1]].setChecked(True)

        group.setLayout(group_layout)
        self.main_layout.addWidget(group)
        self.test_type_widget = group

    def _get_test_types(self):
        if not self.main_window.analysis_data:
            return []

        for indicator_key, groups in self.main_window.analysis_data.items():
            n_groups = len(groups)
            break
        else:
            return []

        if n_groups == 2:
            return [
                ("单样本t检验", "ttest"),
                ("独立样本t检验", "ttest2"),
                ("配对样本t检验", "ttest_paired"),
                ("简单回归", "regress"),
            ]
        elif n_groups > 2:
            return [
                ("单因素ANOVA", "anova1"),
            ]
        else:
            return []

    def _create_alpha_section(self):
        group = QGroupBox("显著性水平")
        group_layout = QHBoxLayout()

        group_layout.addWidget(QLabel("α = "))
        self.alpha_input = QDoubleSpinBox()
        self.alpha_input.setRange(0.001, 0.1)
        self.alpha_input.setValue(0.05)
        self.alpha_input.setDecimals(3)
        group_layout.addWidget(self.alpha_input)

        group_layout.addStretch()
        group.setLayout(group_layout)
        self.main_layout.addWidget(group)

    def _create_nonparam_section(self):
        group = QGroupBox("非参数检验设置")
        group_layout = QHBoxLayout()

        group_layout.addWidget(QLabel("置换次数: "))
        self.iterations_input = QSpinBox()
        self.iterations_input.setRange(100, 10000)
        self.iterations_input.setValue(500)
        self.iterations_input.setSingleStep(100)
        group_layout.addWidget(self.iterations_input)

        group_layout.addStretch()
        group.setLayout(group_layout)
        self.main_layout.addWidget(group)

    def _create_method_selection_section(self):
        group = QGroupBox("选择检验方法")
        group_layout = QHBoxLayout()

        self.method_group = QButtonGroup()

        self.radio_param = QRadioButton("参数检验")
        self.radio_nonparam = QRadioButton("非参数检验")

        self.method_group.addButton(self.radio_param)
        self.method_group.addButton(self.radio_nonparam)

        group_layout.addWidget(self.radio_param)
        group_layout.addWidget(self.radio_nonparam)
        group_layout.addStretch()

        group.setLayout(group_layout)
        self.main_layout.addWidget(group)

    def _create_button_section(self):
        layout = QHBoxLayout()

        btn_prev = QPushButton("← 返回正态性检验")
        btn_prev.clicked.connect(self.go_prev)

        btn_next = QPushButton("下一步: 运行分析 →")
        btn_next.clicked.connect(self.go_next)

        layout.addWidget(btn_prev)
        layout.addStretch()
        layout.addWidget(btn_next)

        self.main_layout.addLayout(layout)

    def refresh_test_types(self):
        if not self.main_window.analysis_data:
            return

        test_types = self._get_test_types()
        if not test_types:
            return

        self._create_test_type_section()

    def go_prev(self):
        self.main_window.prev_tab()

    def _get_current_groups(self):
        if not self.main_window.analysis_data:
            return {}
        indicator = self.main_window.selected_indicator
        if indicator is None:
            indicator = list(self.main_window.analysis_data.keys())[0]
            self.main_window.selected_indicator = indicator
        return self.main_window.analysis_data.get(indicator, {})

    def _create_regress_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("简单回归 - 数据选择")
        dialog.setMinimumWidth(450)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        groups = self._get_current_groups()
        group_names = list(groups.keys())

        if len(group_names) < 2:
            QMessageBox.warning(self, "警告", "简单回归需要至少两组数据")
            dialog.setLayout(layout)
            dialog.get_results = lambda: (None, None)
            return dialog

        layout.addWidget(QLabel("请选择因变量和自变量数据："))

        layout.addWidget(QLabel("因变量Y（曲线数据）:"))
        y_combo = QComboBox()
        for name in group_names:
            y_combo.addItem(name, name)
        layout.addWidget(y_combo)

        layout.addWidget(QLabel("自变量x（标量数据）:"))
        x_combo = QComboBox()
        for name in group_names:
            if name != y_combo.currentData():
                x_combo.addItem(name, name)
        layout.addWidget(x_combo)

        def update_x_combo():
            y_selected = y_combo.currentData()
            x_combo.clear()
            for name in group_names:
                if name != y_selected:
                    x_combo.addItem(name, name)
        
        y_combo.currentIndexChanged.connect(update_x_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        def get_results():
            return (y_combo.currentData(), x_combo.currentData())

        dialog.get_results = get_results
        return dialog

    def _create_ttest_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("单样本t检验 - 数据选择")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        groups = self._get_current_groups()
        group_names = list(groups.keys())

        if len(group_names) < 2:
            QMessageBox.warning(self, "警告", "单样本t检验需要至少两组数据")
            dialog.setLayout(layout)
            dialog.get_results = lambda: (None, None)
            return dialog

        layout.addWidget(QLabel("请选择分析数据和比较曲线："))

        layout.addWidget(QLabel("分析数据（Y）:"))
        y_combo = QComboBox()
        for name in group_names:
            y_combo.addItem(name, name)
        layout.addWidget(y_combo)

        layout.addWidget(QLabel("比较曲线（mu）:"))
        mu_combo = QComboBox()
        for name in group_names:
            if name != y_combo.currentData():
                mu_combo.addItem(name, name)
        layout.addWidget(mu_combo)

        def update_mu_combo():
            y_selected = y_combo.currentData()
            mu_combo.clear()
            for name in group_names:
                if name != y_selected:
                    mu_combo.addItem(name, name)
        
        y_combo.currentIndexChanged.connect(update_mu_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        def get_results():
            return (y_combo.currentData(), mu_combo.currentData())

        dialog.get_results = get_results
        return dialog

    def go_next(self):
        test_type = None
        for value, radio in self.test_radios.items():
            if radio.isChecked():
                test_type = value
                break

        if not test_type:
            QMessageBox.warning(self, "警告", "请选择分析类型")
            return

        params = {
            'test_type': test_type,
            'alpha': self.alpha_input.value(),
            'method': 'param' if self.radio_param.isChecked() else 'nonparam',
            'iterations': self.iterations_input.value()
        }

        groups = self._get_current_groups()

        if test_type == 'ttest':
            if len(groups) != 2:
                QMessageBox.warning(self, "警告", "单样本t检验需要恰好两组数据")
                return

            dialog = self._create_ttest_dialog()
            if dialog.exec_() != QDialog.Accepted:
                return

            results = dialog.get_results()
            if results is None or len(results) != 2:
                QMessageBox.warning(self, "警告", "请选择分析数据和比较曲线")
                return

            y_name, mu_name = results
            if not y_name or not mu_name:
                QMessageBox.warning(self, "警告", "请选择分析数据和比较曲线")
                return

            params['y_data'] = groups[y_name]
            params['mu_data'] = groups[mu_name]

        elif test_type == 'regress':
            if len(groups) != 2:
                QMessageBox.warning(self, "警告", "简单回归需要恰好两组数据")
                return

            dialog = self._create_regress_dialog()
            if dialog.exec_() != QDialog.Accepted:
                return

            results = dialog.get_results()
            if results is None or len(results) != 2:
                QMessageBox.warning(self, "警告", "请选择因变量和自变量")
                return

            y_name, x_name = results
            if not y_name or not x_name:
                QMessageBox.warning(self, "警告", "请选择因变量和自变量")
                return

            y_data = groups[y_name]
            x_data = groups[x_name]

            x_data_flat = x_data.flatten()
            if len(x_data_flat.shape) != 1 or x_data_flat.dtype.kind in ('O', 'U'):
                QMessageBox.warning(self, "警告", "自变量x必须是数值型1维数组")
                return

            J, Q = y_data.shape
            if len(x_data_flat) != J:
                QMessageBox.warning(self, "警告", f"自变量长度({len(x_data_flat)})必须等于Y的样本数({J})")
                return

            params['y_data'] = y_data
            params['x_data'] = x_data_flat.astype(float)
            params['y_name'] = y_name
            params['x_name'] = x_name

        elif test_type in ['ttest2', 'ttest_paired']:
            if len(groups) != 2:
                msg = "独立样本t检验" if test_type == 'ttest2' else "配对样本t检验"
                QMessageBox.warning(self, "警告", f"{msg}需要恰好两组数据")
                return

        self.main_window.analysis_params = params
        self.main_window.analysis_method = params['method']
        self.main_window.next_tab()
