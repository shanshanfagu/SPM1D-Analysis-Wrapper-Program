from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QRadioButton,
                               QButtonGroup, QDoubleSpinBox, QSpinBox,
                               QTextEdit, QDialog, QComboBox,
                               QDialogButtonBox, QListWidget, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import numpy as np
from modules.utils import show_warning

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

        self.title = QLabel(self.main_window.tr("tab_params.title"))
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title)

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

        self.group_test_type = QGroupBox(self.main_window.tr("tab_params.analysis_type"))
        group_layout = QVBoxLayout()

        self.test_type_group = QButtonGroup()
        self.test_radios = {}

        test_types = self._get_test_types()

        if not test_types:
            warning_label = QLabel(self.main_window.tr("tab_params.no_analysis_hint"))
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

        self.group_test_type.setLayout(group_layout)
        self.main_layout.addWidget(self.group_test_type)
        self.test_type_widget = self.group_test_type

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
                (self.main_window.tr("tab_params.ttest_one_sample"), "ttest"),
                (self.main_window.tr("tab_params.ttest_independent"), "ttest2"),
                (self.main_window.tr("tab_params.ttest_paired"), "ttest_paired"),
                (self.main_window.tr("tab_params.regress_simple"), "regress"),
            ]
        elif n_groups > 2:
            return [
                (self.main_window.tr("tab_params.anova_one_way"), "anova1"),
                (self.main_window.tr("tab_params.anova_one_way_rm"), "anova1rm"),
                (self.main_window.tr("tab_params.anova_two_way"), "anova2"),
                (self.main_window.tr("tab_params.anova_two_way_rm"), "anova2rm"),
                (self.main_window.tr("tab_params.anova_two_way_mixed"), "anova2onerm"),
            ]
        else:
            return []

    def _make_ok_cancel_box(self, dialog):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        button_box.button(QDialogButtonBox.Ok).setText(self.main_window.tr("common.ok"))
        button_box.button(QDialogButtonBox.Cancel).setText(self.main_window.tr("common.cancel"))
        return button_box

    def _create_alpha_section(self):
        self.group_alpha = QGroupBox(self.main_window.tr("tab_params.alpha_level"))
        group_layout = QHBoxLayout()

        group_layout.addWidget(QLabel("α = "))
        self.alpha_input = QDoubleSpinBox()
        self.alpha_input.setRange(0.001, 0.1)
        self.alpha_input.setValue(0.05)
        self.alpha_input.setDecimals(3)
        group_layout.addWidget(self.alpha_input)

        group_layout.addStretch()
        self.group_alpha.setLayout(group_layout)
        self.main_layout.addWidget(self.group_alpha)

    def _create_nonparam_section(self):
        self.group_nonparam = QGroupBox(self.main_window.tr("tab_params.nonparam_settings"))
        group_layout = QHBoxLayout()

        self.iterations_label = QLabel(self.main_window.tr("tab_params.iterations"))
        group_layout.addWidget(self.iterations_label)
        self.iterations_input = QSpinBox()
        self.iterations_input.setRange(100, 10000)
        self.iterations_input.setValue(500)
        self.iterations_input.setSingleStep(100)
        group_layout.addWidget(self.iterations_input)

        group_layout.addStretch()
        self.group_nonparam.setLayout(group_layout)
        self.main_layout.addWidget(self.group_nonparam)

    def _create_method_selection_section(self):
        self.group_method = QGroupBox(self.main_window.tr("tab_params.method_selection"))
        group_layout = QHBoxLayout()

        self.method_group = QButtonGroup()

        self.radio_param = QRadioButton(self.main_window.tr("tab_params.parametric"))
        self.radio_nonparam = QRadioButton(self.main_window.tr("tab_params.nonparametric"))

        self.method_group.addButton(self.radio_param)
        self.method_group.addButton(self.radio_nonparam)

        group_layout.addWidget(self.radio_param)
        group_layout.addWidget(self.radio_nonparam)
        group_layout.addStretch()

        self.group_method.setLayout(group_layout)
        self.main_layout.addWidget(self.group_method)

    def _create_button_section(self):
        layout = QHBoxLayout()

        self.btn_prev = QPushButton(self.main_window.tr("tab_params.prev_normality"))
        self.btn_prev.clicked.connect(self.go_prev)

        self.btn_next = QPushButton(self.main_window.tr("tab_params.next_analysis"))
        self.btn_next.clicked.connect(self.go_next)

        layout.addWidget(self.btn_prev)
        layout.addStretch()
        layout.addWidget(self.btn_next)

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
        dialog.setWindowTitle(self.main_window.tr("tab_params.regress_dialog_title"))
        dialog.setMinimumWidth(450)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        groups = self._get_current_groups()
        group_names = list(groups.keys())

        if len(group_names) < 2:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_params.warn_2groups"))
            dialog.setLayout(layout)
            dialog.get_results = lambda: (None, None)
            return dialog

        layout.addWidget(QLabel(self.main_window.tr("tab_params.select_y_x")))

        layout.addWidget(QLabel(self.main_window.tr("tab_params.dependent_y")))
        y_combo = QComboBox()
        for name in group_names:
            y_combo.addItem(name, name)
        layout.addWidget(y_combo)

        layout.addWidget(QLabel(self.main_window.tr("tab_params.independent_x")))
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

        button_box = self._make_ok_cancel_box(dialog)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        def get_results():
            return (y_combo.currentData(), x_combo.currentData())

        dialog.get_results = get_results
        return dialog

    def _create_ttest_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.main_window.tr("tab_params.ttest_dialog_title"))
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        groups = self._get_current_groups()
        group_names = list(groups.keys())

        if len(group_names) < 2:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_params.warn_2groups"))
            dialog.setLayout(layout)
            dialog.get_results = lambda: (None, None)
            return dialog

        layout.addWidget(QLabel(self.main_window.tr("tab_params.select_y_mu")))

        layout.addWidget(QLabel(self.main_window.tr("tab_params.analysis_data_y")))
        y_combo = QComboBox()
        for name in group_names:
            y_combo.addItem(name, name)
        layout.addWidget(y_combo)

        layout.addWidget(QLabel(self.main_window.tr("tab_params.comparison_curve_mu")))
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

        button_box = self._make_ok_cancel_box(dialog)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        def get_results():
            return (y_combo.currentData(), mu_combo.currentData())

        dialog.get_results = get_results
        return dialog

    def _create_anova2_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.main_window.tr("tab_params.anova2_dialog_title"))
        dialog.setMinimumWidth(450)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        groups = self._get_current_groups()
        group_names = list(groups.keys())

        if len(group_names) < 3:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_params.warn_anova2_min_groups"))
            dialog.setLayout(layout)
            dialog.get_results = lambda: (None, None, None)
            return dialog

        layout.addWidget(QLabel(self.main_window.tr("tab_params.select_y_ab")))

        layout.addWidget(QLabel(self.main_window.tr("tab_params.original_data_y")))
        y_combo = QComboBox()
        for name in group_names:
            y_combo.addItem(name, name)
        layout.addWidget(y_combo)

        layout.addWidget(QLabel(self.main_window.tr("tab_params.main_effect_a")))
        a_combo = QComboBox()
        layout.addWidget(a_combo)

        layout.addWidget(QLabel(self.main_window.tr("tab_params.main_effect_b")))
        b_combo = QComboBox()
        layout.addWidget(b_combo)

        def update_a_combo():
            y_sel = y_combo.currentData()
            current_a = a_combo.currentData()
            a_combo.blockSignals(True)
            a_combo.clear()
            for name in group_names:
                if name != y_sel:
                    a_combo.addItem(name, name)
            idx = a_combo.findData(current_a)
            a_combo.setCurrentIndex(max(0, idx))
            a_combo.blockSignals(False)
            update_b_combo()

        def update_b_combo():
            y_sel = y_combo.currentData()
            a_sel = a_combo.currentData()
            current_b = b_combo.currentData()
            b_combo.blockSignals(True)
            b_combo.clear()
            for name in group_names:
                if name != y_sel and name != a_sel:
                    b_combo.addItem(name, name)
            idx = b_combo.findData(current_b)
            b_combo.setCurrentIndex(max(0, idx))
            b_combo.blockSignals(False)

        y_combo.currentIndexChanged.connect(update_a_combo)
        a_combo.currentIndexChanged.connect(update_b_combo)

        update_a_combo()

        button_box = self._make_ok_cancel_box(dialog)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        def get_results():
            return (y_combo.currentData(), a_combo.currentData(), b_combo.currentData())

        dialog.get_results = get_results
        return dialog

    def _create_anova2rm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.main_window.tr("tab_params.anova2rm_dialog_title"))
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        groups = self._get_current_groups()
        group_names = list(groups.keys())

        y_combo = QComboBox()
        a_combo = QComboBox()
        b_combo = QComboBox()
        subj_combo = QComboBox()

        for name in group_names:
            y_combo.addItem(name, name)
            a_combo.addItem(name, name)
            b_combo.addItem(name, name)
            subj_combo.addItem(name, name)

        if len(group_names) >= 4:
            y_combo.setCurrentIndex(0)
            a_combo.setCurrentIndex(1)
            b_combo.setCurrentIndex(2)
            subj_combo.setCurrentIndex(3)
        elif len(group_names) >= 3:
            y_combo.setCurrentIndex(0)
            a_combo.setCurrentIndex(1)
            b_combo.setCurrentIndex(2)
            subj_combo.setCurrentIndex(0)
        elif len(group_names) >= 2:
            y_combo.setCurrentIndex(0)
            a_combo.setCurrentIndex(1)
            b_combo.setCurrentIndex(0)
            subj_combo.setCurrentIndex(1)

        def update_a_combo():
            y_sel = y_combo.currentData()
            current_a = a_combo.currentData()
            a_combo.blockSignals(True)
            a_combo.clear()
            for name in group_names:
                if name != y_sel:
                    a_combo.addItem(name, name)
            idx = a_combo.findData(current_a)
            a_combo.setCurrentIndex(max(0, idx))
            a_combo.blockSignals(False)
            update_b_combo()

        def update_b_combo():
            y_sel = y_combo.currentData()
            a_sel = a_combo.currentData()
            current_b = b_combo.currentData()
            b_combo.blockSignals(True)
            b_combo.clear()
            for name in group_names:
                if name != y_sel and name != a_sel:
                    b_combo.addItem(name, name)
            idx = b_combo.findData(current_b)
            b_combo.setCurrentIndex(max(0, idx))
            b_combo.blockSignals(False)
            update_subj_combo()

        def update_subj_combo():
            y_sel = y_combo.currentData()
            a_sel = a_combo.currentData()
            b_sel = b_combo.currentData()
            current_subj = subj_combo.currentData()
            subj_combo.blockSignals(True)
            subj_combo.clear()
            for name in group_names:
                if name != y_sel and name != a_sel and name != b_sel:
                    subj_combo.addItem(name, name)
            idx = subj_combo.findData(current_subj)
            subj_combo.setCurrentIndex(max(0, idx))
            subj_combo.blockSignals(False)

        y_combo.currentIndexChanged.connect(update_a_combo)
        a_combo.currentIndexChanged.connect(update_b_combo)
        b_combo.currentIndexChanged.connect(update_subj_combo)

        update_a_combo()

        layout.addWidget(QLabel(self.main_window.tr("tab_params.curve_data")))
        layout.addWidget(y_combo)
        layout.addWidget(QLabel(self.main_window.tr("tab_params.main_effect_a")))
        layout.addWidget(a_combo)
        layout.addWidget(QLabel(self.main_window.tr("tab_params.main_effect_b")))
        layout.addWidget(b_combo)
        layout.addWidget(QLabel(self.main_window.tr("tab_params.subject_id")))
        layout.addWidget(subj_combo)

        button_box = self._make_ok_cancel_box(dialog)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        def get_results():
            return (y_combo.currentData(), a_combo.currentData(), b_combo.currentData(), subj_combo.currentData())

        dialog.get_results = get_results
        return dialog

    def _create_anova2onerm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.main_window.tr("tab_params.anova2onerm_dialog_title"))
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        groups = self._get_current_groups()
        group_names = list(groups.keys())

        y_combo = QComboBox()
        a_combo = QComboBox()
        b_combo = QComboBox()
        subj_combo = QComboBox()

        for name in group_names:
            y_combo.addItem(name, name)
            a_combo.addItem(name, name)
            b_combo.addItem(name, name)
            subj_combo.addItem(name, name)

        if len(group_names) >= 4:
            y_combo.setCurrentIndex(0)
            a_combo.setCurrentIndex(1)
            b_combo.setCurrentIndex(2)
            subj_combo.setCurrentIndex(3)
        elif len(group_names) >= 3:
            y_combo.setCurrentIndex(0)
            a_combo.setCurrentIndex(1)
            b_combo.setCurrentIndex(2)
            subj_combo.setCurrentIndex(0)
        elif len(group_names) >= 2:
            y_combo.setCurrentIndex(0)
            a_combo.setCurrentIndex(1)
            b_combo.setCurrentIndex(0)
            subj_combo.setCurrentIndex(1)

        def update_a_combo():
            y_sel = y_combo.currentData()
            current_a = a_combo.currentData()
            a_combo.blockSignals(True)
            a_combo.clear()
            for name in group_names:
                if name != y_sel:
                    a_combo.addItem(name, name)
            idx = a_combo.findData(current_a)
            a_combo.setCurrentIndex(max(0, idx))
            a_combo.blockSignals(False)
            update_b_combo()

        def update_b_combo():
            y_sel = y_combo.currentData()
            a_sel = a_combo.currentData()
            current_b = b_combo.currentData()
            b_combo.blockSignals(True)
            b_combo.clear()
            for name in group_names:
                if name != y_sel and name != a_sel:
                    b_combo.addItem(name, name)
            idx = b_combo.findData(current_b)
            b_combo.setCurrentIndex(max(0, idx))
            b_combo.blockSignals(False)
            update_subj_combo()

        def update_subj_combo():
            y_sel = y_combo.currentData()
            a_sel = a_combo.currentData()
            b_sel = b_combo.currentData()
            current_subj = subj_combo.currentData()
            subj_combo.blockSignals(True)
            subj_combo.clear()
            for name in group_names:
                if name != y_sel and name != a_sel and name != b_sel:
                    subj_combo.addItem(name, name)
            idx = subj_combo.findData(current_subj)
            subj_combo.setCurrentIndex(max(0, idx))
            subj_combo.blockSignals(False)

        y_combo.currentIndexChanged.connect(update_a_combo)
        a_combo.currentIndexChanged.connect(update_b_combo)
        b_combo.currentIndexChanged.connect(update_subj_combo)

        update_a_combo()

        layout.addWidget(QLabel(self.main_window.tr("tab_params.curve_data")))
        layout.addWidget(y_combo)
        layout.addWidget(QLabel(self.main_window.tr("tab_params.mixed_main_effect_a")))
        layout.addWidget(a_combo)
        layout.addWidget(QLabel(self.main_window.tr("tab_params.mixed_main_effect_b")))
        layout.addWidget(b_combo)
        layout.addWidget(QLabel(self.main_window.tr("tab_params.subject_id")))
        layout.addWidget(subj_combo)

        button_box = self._make_ok_cancel_box(dialog)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        def get_results():
            return (y_combo.currentData(), a_combo.currentData(), b_combo.currentData(), subj_combo.currentData())

        dialog.get_results = get_results
        return dialog

    def clear_data(self):
        pass

    def go_next(self):
        test_type = None
        for value, radio in self.test_radios.items():
            if radio.isChecked():
                test_type = value
                break

        if not test_type:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_params.warn_select_type"))
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
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_2groups"))
                return

            dialog = self._create_ttest_dialog()
            if dialog.exec_() != QDialog.Accepted:
                return

            results = dialog.get_results()
            if results is None or len(results) != 2:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            y_name, mu_name = results
            if not y_name or not mu_name:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            params['y_data'] = groups[y_name]
            mu_data = groups[mu_name]
            params['mu_data'] = np.mean(mu_data, axis=0) if mu_data.ndim >= 2 else np.asarray(mu_data, dtype=float)

        elif test_type == 'regress':
            if len(groups) != 2:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_2groups"))
                return

            dialog = self._create_regress_dialog()
            if dialog.exec_() != QDialog.Accepted:
                return

            results = dialog.get_results()
            if results is None or len(results) != 2:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            y_name, x_name = results
            if not y_name or not x_name:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            y_data = groups[y_name]
            x_data = groups[x_name]

            x_data_flat = x_data.flatten()
            if len(x_data_flat.shape) != 1 or x_data_flat.dtype.kind in ('O', 'U'):
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_x_numeric"))
                return

            J, Q = y_data.shape
            if len(x_data_flat) != J:
                warn_msg = self.main_window.tr("tab_params.warn_x_length").format(len(x_data_flat), J)
                show_warning(self, self.main_window.tr("common.warning"), warn_msg)
                return

            params['y_data'] = y_data
            params['x_data'] = x_data_flat.astype(float)
            params['y_name'] = y_name
            params['x_name'] = x_name

        elif test_type in ['ttest2', 'ttest_paired']:
            if len(groups) != 2:
                msg = self.main_window.tr("tab_params.ttest_independent") if test_type == 'ttest2' else self.main_window.tr("tab_params.ttest_paired")
                show_warning(self, self.main_window.tr("common.warning"), 
                                  f"{msg} {self.main_window.tr('tab_params.warn_2groups')}")
                return

        elif test_type == 'anova2':
            if len(groups) < 3:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_anova2_min_groups"))
                return

            dialog = self._create_anova2_dialog()
            if dialog.exec_() != QDialog.Accepted:
                return

            results = dialog.get_results()
            if results is None or len(results) != 3:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            y_name, a_name, b_name = results
            if not y_name or not a_name or not b_name:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            y_data = groups[y_name]
            a_data = groups[a_name]
            b_data = groups[b_name]

            J_y, Q = y_data.shape
            J_a = a_data.shape[0]
            J_b = b_data.shape[0]

            if J_a != J_y or J_b != J_y:
                warn_msg = self.main_window.tr("tab_params.warn_ab_length")
                show_warning(self, self.main_window.tr("common.warning"), warn_msg)
                return

            a_flat = a_data.flatten().astype(int)
            b_flat = b_data.flatten().astype(int)

            if len(np.unique(a_flat)) < 2:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_ab_unique"))
                return

            if len(np.unique(b_flat)) < 2:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_params.warn_ab_unique"))
                return

            params['y_data'] = y_data
            params['A'] = a_flat
            params['B'] = b_flat
            params['y_name'] = y_name
            params['a_name'] = a_name
            params['b_name'] = b_name

        elif test_type == 'anova2rm':
            if len(groups) < 4:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_anova2rm_min_groups"))
                return

            dialog = self._create_anova2rm_dialog()
            if dialog.exec_() != QDialog.Accepted:
                return

            results = dialog.get_results()
            if results is None or len(results) != 4:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            y_name, a_name, b_name, subj_name = results

            Y = groups[y_name]
            A = groups[a_name].flatten().astype(int)
            B = groups[b_name].flatten().astype(int)
            SUBJ = groups[subj_name].flatten().astype(int)

            if len(np.unique(A)) < 2:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_ab_unique"))
                return

            if len(np.unique(B)) < 2:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_ab_unique"))
                return

            params['y_data'] = Y
            params['A'] = A
            params['B'] = B
            params['SUBJ'] = SUBJ
            params['y_names'] = [y_name]
            params['y_name'] = y_name
            params['a_name'] = a_name
            params['b_name'] = b_name

        elif test_type == 'anova2onerm':
            if len(groups) < 4:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_anova2onerm_min_groups"))
                return

            dialog = self._create_anova2onerm_dialog()
            if dialog.exec_() != QDialog.Accepted:
                return

            results = dialog.get_results()
            if results is None or len(results) != 4:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_select_data"))
                return

            y_name, a_name, b_name, subj_name = results

            Y = groups[y_name]
            A = groups[a_name].flatten().astype(int)
            B = groups[b_name].flatten().astype(int)
            SUBJ = groups[subj_name].flatten().astype(int)

            if len(np.unique(A)) < 2:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_ab_unique"))
                return

            if len(np.unique(B)) < 2:
                show_warning(self, self.main_window.tr("common.warning"),
                                  self.main_window.tr("tab_params.warn_ab_unique"))
                return

            params['y_data'] = Y
            params['A'] = A
            params['B'] = B
            params['SUBJ'] = SUBJ
            params['y_names'] = [y_name]
            params['y_name'] = y_name
            params['a_name'] = a_name
            params['b_name'] = b_name

        self.main_window.analysis_params = params
        self.main_window.analysis_method = params['method']
        self.main_window.next_tab()

    def retranslate_ui(self):
        self.title.setText(self.main_window.tr("tab_params.title"))
        self.group_test_type.setTitle(self.main_window.tr("tab_params.analysis_type"))
        self.group_alpha.setTitle(self.main_window.tr("tab_params.alpha_level"))
        self.group_nonparam.setTitle(self.main_window.tr("tab_params.nonparam_settings"))
        self.iterations_label.setText(self.main_window.tr("tab_params.iterations"))
        self.group_method.setTitle(self.main_window.tr("tab_params.method_selection"))
        self.radio_param.setText(self.main_window.tr("tab_params.parametric"))
        self.radio_nonparam.setText(self.main_window.tr("tab_params.nonparametric"))
        self.btn_prev.setText(self.main_window.tr("tab_params.prev_normality"))
        self.btn_next.setText(self.main_window.tr("tab_params.next_analysis"))
        
        self._create_test_type_section()
