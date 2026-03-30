from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QCheckBox,
                               QComboBox, QDoubleSpinBox, QSpinBox,
                               QScrollArea, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pandas as pd
import os

from modules.preprocess import interpolate_data, butterworth_filter
from modules.utils import show_info, show_warning, show_critical


class TabPreprocess(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.file_checkboxes = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.title = QLabel(self.main_window.tr("tab_preprocess.title"))
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.title)

        layout.addLayout(self._create_file_selection_section())
        layout.addLayout(self._create_interpolation_section())
        layout.addLayout(self._create_denoising_section())
        layout.addLayout(self._create_export_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_file_selection_section(self):
        self.group_files = QGroupBox(self.main_window.tr("tab_preprocess.select_files"))
        self.file_layout = QVBoxLayout()
        self.group_files.setLayout(self.file_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.group_files)
        scroll.setMinimumHeight(160)

        btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton(self.main_window.tr("tab_preprocess.select_all"))
        self.btn_select_all.clicked.connect(self.select_all_files)
        self.btn_deselect_all = QPushButton(self.main_window.tr("tab_preprocess.deselect_all"))
        self.btn_deselect_all.clicked.connect(self.deselect_all_files)
        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        btn_layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.addLayout(btn_layout)
        return layout

    def _create_interpolation_section(self):
        self.group_interp = QGroupBox(self.main_window.tr("tab_preprocess.interpolation_group"))
        layout = QHBoxLayout()

        self.interp_method_label = QLabel(self.main_window.tr("tab_preprocess.interp_method"))
        layout.addWidget(self.interp_method_label)
        self.combo_interp_method = QComboBox()
        self.combo_interp_method.addItems([
            self.main_window.tr("tab_preprocess.interp_linear"),
            self.main_window.tr("tab_preprocess.interp_cubic")
        ])
        layout.addWidget(self.combo_interp_method)

        self.target_points_label = QLabel(self.main_window.tr("tab_preprocess.target_points"))
        layout.addWidget(self.target_points_label)
        self.spin_target_points = QSpinBox()
        self.spin_target_points.setRange(2, 10000)
        self.spin_target_points.setValue(100)
        layout.addWidget(self.spin_target_points)

        self.btn_apply_interp = QPushButton(self.main_window.tr("tab_preprocess.apply_interp"))
        self.btn_apply_interp.clicked.connect(self.apply_interpolation)
        layout.addWidget(self.btn_apply_interp)

        layout.addStretch()
        self.group_interp.setLayout(layout)
        return self._wrap_widget(self.group_interp)

    def _create_denoising_section(self):
        self.group_denoise = QGroupBox(self.main_window.tr("tab_preprocess.denoising_group"))
        layout = QVBoxLayout()

        row1 = QHBoxLayout()
        self.filter_type_label = QLabel(self.main_window.tr("tab_preprocess.filter_type"))
        row1.addWidget(self.filter_type_label)
        self.combo_filter_type = QComboBox()
        self.combo_filter_type.addItems([
            self.main_window.tr("tab_preprocess.filter_lowpass"),
            self.main_window.tr("tab_preprocess.filter_highpass"),
            self.main_window.tr("tab_preprocess.filter_bandpass")
        ])
        self.combo_filter_type.currentIndexChanged.connect(self._on_filter_type_changed)
        row1.addWidget(self.combo_filter_type)
        row1.addStretch()

        row2 = QHBoxLayout()
        self.cutoff_label = QLabel(self.main_window.tr("tab_preprocess.cutoff_freq"))
        row2.addWidget(self.cutoff_label)
        self.spin_cutoff = QDoubleSpinBox()
        self.spin_cutoff.setRange(0.01, 10000.0)
        self.spin_cutoff.setValue(10.0)
        self.spin_cutoff.setDecimals(2)
        row2.addWidget(self.spin_cutoff)

        self.cutoff2_label = QLabel(self.main_window.tr("tab_preprocess.cutoff_freq2"))
        row2.addWidget(self.cutoff2_label)
        self.spin_cutoff2 = QDoubleSpinBox()
        self.spin_cutoff2.setRange(0.01, 10000.0)
        self.spin_cutoff2.setValue(50.0)
        self.spin_cutoff2.setDecimals(2)
        self.spin_cutoff2.setEnabled(False)
        self.cutoff2_label.setEnabled(False)
        row2.addWidget(self.spin_cutoff2)
        row2.addStretch()

        row3 = QHBoxLayout()
        self.fs_label = QLabel(self.main_window.tr("tab_preprocess.sampling_freq"))
        row3.addWidget(self.fs_label)
        self.spin_fs = QDoubleSpinBox()
        self.spin_fs.setRange(0.1, 100000.0)
        self.spin_fs.setValue(100.0)
        self.spin_fs.setDecimals(1)
        row3.addWidget(self.spin_fs)

        self.order_label = QLabel(self.main_window.tr("tab_preprocess.filter_order"))
        row3.addWidget(self.order_label)
        self.spin_order = QSpinBox()
        self.spin_order.setRange(1, 10)
        self.spin_order.setValue(4)
        row3.addWidget(self.spin_order)
        row3.addStretch()

        row4 = QHBoxLayout()
        self.btn_apply_denoise = QPushButton(self.main_window.tr("tab_preprocess.apply_denoise"))
        self.btn_apply_denoise.clicked.connect(self.apply_denoising)
        row4.addWidget(self.btn_apply_denoise)
        row4.addStretch()

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(row3)
        layout.addLayout(row4)
        self.group_denoise.setLayout(layout)
        return self._wrap_widget(self.group_denoise)

    def _create_export_section(self):
        self.group_export = QGroupBox(self.main_window.tr("tab_preprocess.export_group"))
        layout = QHBoxLayout()

        self.btn_export = QPushButton(self.main_window.tr("tab_preprocess.export_btn"))
        self.btn_export.clicked.connect(self.export_preprocessed)
        layout.addWidget(self.btn_export)
        layout.addStretch()

        self.group_export.setLayout(layout)
        return self._wrap_widget(self.group_export)

    def _create_button_section(self):
        layout = QHBoxLayout()

        self.btn_prev = QPushButton(self.main_window.tr("tab_preprocess.prev_import"))
        self.btn_prev.clicked.connect(self.go_prev)
        layout.addWidget(self.btn_prev)

        layout.addStretch()

        self.btn_next = QPushButton(self.main_window.tr("tab_preprocess.next_normality"))
        self.btn_next.clicked.connect(self.go_next)
        layout.addWidget(self.btn_next)

        return layout

    def _wrap_widget(self, widget):
        layout = QVBoxLayout()
        layout.addWidget(widget)
        return layout

    def _on_filter_type_changed(self, index):
        if index == 0:
            self.cutoff_label.setText(self.main_window.tr("tab_preprocess.cutoff_freq"))
            self.cutoff2_label.setText(self.main_window.tr("tab_preprocess.cutoff_freq2"))
            self.cutoff_label.setEnabled(True)
            self.spin_cutoff.setEnabled(True)
            self.cutoff2_label.setEnabled(False)
            self.spin_cutoff2.setEnabled(False)
        elif index == 1:
            self.cutoff_label.setText(self.main_window.tr("tab_preprocess.cutoff_freq2"))
            self.cutoff2_label.setText(self.main_window.tr("tab_preprocess.cutoff_freq"))
            self.cutoff_label.setEnabled(True)
            self.spin_cutoff.setEnabled(True)
            self.cutoff2_label.setEnabled(False)
            self.spin_cutoff2.setEnabled(False)
        elif index == 2:
            self.cutoff_label.setText(self.main_window.tr("tab_preprocess.cutoff_freq"))
            self.cutoff2_label.setText(self.main_window.tr("tab_preprocess.cutoff_freq2"))
            self.cutoff_label.setEnabled(True)
            self.spin_cutoff.setEnabled(True)
            self.cutoff2_label.setEnabled(True)
            self.spin_cutoff2.setEnabled(True)

    def _get_current_groups(self):
        data = self.main_window.analysis_data
        if not data:
            return {}
        indicator = getattr(self.main_window, 'selected_indicator', None)
        if indicator and indicator in data:
            return data[indicator]
        else:
            return list(data.values())[0]

    def _build_new_name(self, name, suffix):
        tag = self.main_window.tr(f"tab_preprocess.suffix_{suffix}")
        import re
        base = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()
        existing_tags = re.findall(r'\(([^)]+)\)', name)
        combined = ''.join(existing_tags)
        if tag not in combined:
            combined += tag
        return f"{base} ({combined})"

    def refresh_file_list(self):
        self.file_checkboxes.clear()
        while self.file_layout.count():
            item = self.file_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        groups = self._get_current_groups()
        for name in sorted(groups.keys()):
            cb = QCheckBox(name)
            cb.setChecked(False)
            self.file_checkboxes[name] = cb
            self.file_layout.addWidget(cb)

    def get_selected_files(self):
        return [name for name, cb in self.file_checkboxes.items() if cb.isChecked()]

    def select_all_files(self):
        for cb in self.file_checkboxes.values():
            cb.setChecked(True)

    def deselect_all_files(self):
        for cb in self.file_checkboxes.values():
            cb.setChecked(False)

    def apply_interpolation(self):
        selected = self.get_selected_files()
        if not selected:
            show_warning(self, self.main_window.tr("common.warning"),
                              self.main_window.tr("tab_preprocess.warn_no_selection"))
            return

        target = self.spin_target_points.value()
        method_key = self.combo_interp_method.currentText()
        method = 'cubic' if method_key == self.main_window.tr("tab_preprocess.interp_cubic") else 'linear'

        data = self.main_window.analysis_data
        indicator = getattr(self.main_window, 'selected_indicator', None)
        if not indicator or indicator not in data:
            show_warning(self, self.main_window.tr("common.warning"),
                              self.main_window.tr("tab_preprocess.warn_no_data"))
            return

        groups = data[indicator]
        renamed = []

        for name in selected:
            if name not in groups:
                continue
            arr = groups[name]
            if arr.ndim != 2:
                show_warning(self, self.main_window.tr("common.warning"),
                                  f"{name}: {self.main_window.tr('tab_preprocess.warn_invalid_shape')}")
                continue
            if arr.shape[1] < 2:
                show_warning(self, self.main_window.tr("common.warning"),
                                  f"{name}: {self.main_window.tr('tab_preprocess.warn_too_few_points')}")
                continue
            try:
                result = interpolate_data(arr, target, method)
                new_name = self._build_new_name(name, 'interp')
                del groups[name]
                groups[new_name] = result
                renamed.append((name, new_name))
            except Exception as e:
                show_warning(self, self.main_window.tr("common.warning"), f"{name}: {str(e)}")

        if renamed:
            self.main_window.analysis_data[indicator] = groups
            self.refresh_file_list()
            msg_lines = [self.main_window.tr("tab_preprocess.success_interp").format(old, new) for old, new in renamed]
            show_info(self, self.main_window.tr("common.success"), "\n".join(msg_lines))

    def apply_denoising(self):
        selected = self.get_selected_files()
        if not selected:
            show_warning(self, self.main_window.tr("common.warning"),
                              self.main_window.tr("tab_preprocess.warn_no_selection"))
            return

        filter_index = self.combo_filter_type.currentIndex()
        filter_types = ['lowpass', 'highpass', 'bandpass']
        filter_type = filter_types[filter_index]

        if filter_type == 'bandpass':
            cutoff = [self.spin_cutoff.value(), self.spin_cutoff2.value()]
        else:
            cutoff = self.spin_cutoff.value()

        fs = self.spin_fs.value()
        order = self.spin_order.value()

        data = self.main_window.analysis_data
        indicator = getattr(self.main_window, 'selected_indicator', None)
        if not indicator or indicator not in data:
            show_warning(self, self.main_window.tr("common.warning"),
                              self.main_window.tr("tab_preprocess.warn_no_data"))
            return

        groups = data[indicator]
        renamed = []

        for name in selected:
            if name not in groups:
                continue
            arr = groups[name]
            if arr.ndim != 2:
                show_warning(self, self.main_window.tr("common.warning"),
                                  f"{name}: {self.main_window.tr('tab_preprocess.warn_invalid_shape')}")
                continue
            try:
                result = butterworth_filter(arr, filter_type, cutoff, fs, order)
                new_name = self._build_new_name(name, 'denoise')
                del groups[name]
                groups[new_name] = result
                renamed.append((name, new_name))
            except Exception as e:
                show_warning(self, self.main_window.tr("common.warning"), f"{name}: {str(e)}")

        if renamed:
            self.main_window.analysis_data[indicator] = groups
            self.refresh_file_list()
            msg_lines = [self.main_window.tr("tab_preprocess.success_denoise").format(old, new) for old, new in renamed]
            show_info(self, self.main_window.tr("common.success"), "\n".join(msg_lines))

    def export_preprocessed(self):
        selected = self.get_selected_files()
        if not selected:
            show_warning(self, self.main_window.tr("common.warning"),
                              self.main_window.tr("tab_preprocess.warn_no_selection"))
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Save Preprocessed Data",
                                                   "Preprocessed_Data.xlsx",
                                                   "Excel Files (*.xlsx)")
        if not filename:
            return

        data = self.main_window.analysis_data
        indicator = getattr(self.main_window, 'selected_indicator', None)
        if not indicator or indicator not in data:
            show_warning(self, self.main_window.tr("common.warning"),
                              self.main_window.tr("tab_preprocess.warn_no_data"))
            return

        groups = data[indicator]

        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for name in selected:
                    if name not in groups:
                        continue
                    arr = groups[name]
                    if arr.ndim != 2:
                        continue
                    sheet_name = name[:31]
                    df = pd.DataFrame(arr, columns=[f'T{i}' for i in range(arr.shape[1])])
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            show_info(self, self.main_window.tr("common.success"),
                           self.main_window.tr("tab_preprocess.success_export").format(os.path.basename(filename)))

        except Exception as e:
            show_critical(self, self.main_window.tr("common.error"),
                               f"{self.main_window.tr('tab_preprocess.success_export')}: {str(e)}")

    def go_prev(self):
        self.main_window.prev_tab()

    def go_next(self):
        self.main_window.next_tab()

    def clear_data(self):
        self.file_checkboxes.clear()
        while self.file_layout.count():
            item = self.file_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def retranslate_ui(self):
        self.title.setText(self.main_window.tr("tab_preprocess.title"))
        self.group_files.setTitle(self.main_window.tr("tab_preprocess.select_files"))
        self.btn_select_all.setText(self.main_window.tr("tab_preprocess.select_all"))
        self.btn_deselect_all.setText(self.main_window.tr("tab_preprocess.deselect_all"))
        self.group_interp.setTitle(self.main_window.tr("tab_preprocess.interpolation_group"))
        self.interp_method_label.setText(self.main_window.tr("tab_preprocess.interp_method"))
        self.target_points_label.setText(self.main_window.tr("tab_preprocess.target_points"))
        self.btn_apply_interp.setText(self.main_window.tr("tab_preprocess.apply_interp"))
        self.group_denoise.setTitle(self.main_window.tr("tab_preprocess.denoising_group"))
        self.filter_type_label.setText(self.main_window.tr("tab_preprocess.filter_type"))
        self.fs_label.setText(self.main_window.tr("tab_preprocess.sampling_freq"))
        self.order_label.setText(self.main_window.tr("tab_preprocess.filter_order"))
        self.btn_apply_denoise.setText(self.main_window.tr("tab_preprocess.apply_denoise"))
        self.group_export.setTitle(self.main_window.tr("tab_preprocess.export_group"))
        self.btn_export.setText(self.main_window.tr("tab_preprocess.export_btn"))
        self.btn_prev.setText(self.main_window.tr("tab_preprocess.prev_import"))
        self.btn_next.setText(self.main_window.tr("tab_preprocess.next_normality"))

        current_method = self.combo_interp_method.currentIndex()
        self.combo_interp_method.clear()
        self.combo_interp_method.addItems([
            self.main_window.tr("tab_preprocess.interp_linear"),
            self.main_window.tr("tab_preprocess.interp_cubic")
        ])
        self.combo_interp_method.setCurrentIndex(current_method)

        current_filter = self.combo_filter_type.currentIndex()
        self.combo_filter_type.clear()
        self.combo_filter_type.addItems([
            self.main_window.tr("tab_preprocess.filter_lowpass"),
            self.main_window.tr("tab_preprocess.filter_highpass"),
            self.main_window.tr("tab_preprocess.filter_bandpass")
        ])
        self.combo_filter_type.setCurrentIndex(current_filter)
