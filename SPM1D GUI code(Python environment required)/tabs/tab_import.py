from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFileDialog, QTableWidget,
                               QTableWidgetItem, QGroupBox, QRadioButton,
                               QButtonGroup, QLineEdit, QProgressBar,
                               QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import os
import pandas as pd
import numpy as np
from modules.data_loader import load_data_by_indicator
from modules.utils import show_info, show_warning, show_critical, show_question

class TabImport(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.data = None
        self.indicator_layout = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        self.title = QLabel(self.main_window.tr("tab_import.title"))
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.title)

        layout.addLayout(self._create_select_section())
        layout.addLayout(self._create_indicator_section())
        layout.addLayout(self._create_preview_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_select_section(self):
        layout = QHBoxLayout()

        self.group_source = QGroupBox(self.main_window.tr("tab_import.select_source"))
        group_layout = QHBoxLayout()

        self.root_path = QLineEdit()
        self.root_path.setPlaceholderText(self.main_window.tr("tab_import.browse_hint"))
        self.root_path.setReadOnly(True)

        self.btn_browse = QPushButton(self.main_window.tr("tab_import.browse"))
        self.btn_browse.clicked.connect(self.browse_folder)

        self.btn_load = QPushButton(self.main_window.tr("tab_import.load_data"))
        self.btn_load.clicked.connect(self.load_data)

        group_layout.addWidget(self.root_path)
        group_layout.addWidget(self.btn_browse)
        group_layout.addWidget(self.btn_load)

        self.group_source.setLayout(group_layout)
        layout.addWidget(self.group_source)

        return layout

    def _create_indicator_section(self):
        layout = QHBoxLayout()

        self.group_indicator = QGroupBox(self.main_window.tr("tab_import.select_indicator"))
        self.indicator_layout = QVBoxLayout()

        self.indicator_group = QButtonGroup()
        self.indicator_radios = []

        self.indicator_hint = QLabel(self.main_window.tr("tab_import.select_indicator_hint"))
        self.indicator_layout.addWidget(self.indicator_hint)

        self.group_indicator.setLayout(self.indicator_layout)
        layout.addWidget(self.group_indicator)

        return layout

    def _create_preview_section(self):
        layout = QHBoxLayout()

        self.group_preview = QGroupBox(self.main_window.tr("tab_import.preview"))
        group_layout = QVBoxLayout()

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(6)
        self.preview_table.setHorizontalHeaderLabels([
            self.main_window.tr("tab_import.col_group"),
            self.main_window.tr("tab_import.col_samples"),
            self.main_window.tr("tab_import.col_timepoints"),
            self.main_window.tr("tab_import.col_indicator"),
            self.main_window.tr("tab_import.col_path"),
            self.main_window.tr("tab_import.col_status")
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.data_info = QLabel(self.main_window.tr("tab_import.no_data"))
        self.data_info.setFont(QFont("Arial", 12))

        group_layout.addWidget(self.data_info)
        group_layout.addWidget(self.preview_table)

        self.group_preview.setLayout(group_layout)
        layout.addWidget(self.group_preview)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        self.btn_clear = QPushButton(self.main_window.tr("tab_import.clear_data"))
        self.btn_clear.clicked.connect(self.clear_all)
        
        self.btn_next = QPushButton(self.main_window.tr("tab_import.next_normality"))
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.go_next)

        layout.addWidget(self.btn_clear)
        layout.addStretch()
        layout.addWidget(self.btn_next)

        return layout

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.main_window.tr("tab_import.select_root"),
                                                  "",
                                                  QFileDialog.Option.ShowDirsOnly)
        if folder:
            self.root_path.setText(folder)

    def load_data(self):
        root_path = self.root_path.text()
        if not root_path:
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_import.warn_select_root"))
            return

        if not os.path.exists(root_path):
            show_warning(self, self.main_window.tr("common.warning"), 
                              self.main_window.tr("tab_import.warn_dir_not_exist"))
            return

        try:
            data = load_data_by_indicator(root_path)

            if not data:
                show_warning(self, self.main_window.tr("common.warning"), 
                                  self.main_window.tr("tab_import.warn_no_valid"))
                return

            self.data = data
            self.update_indicator_list(data)
            self.update_preview(data)

            self.main_window.analysis_data = data
            self.btn_next.setEnabled(True)

            show_info(self, self.main_window.tr("common.success"), 
                           self.main_window.tr("tab_import.success_loaded"))

        except Exception as e:
            show_critical(self, self.main_window.tr("common.error"), 
                               f"{self.main_window.tr('tab_import.error_load_failed')}: {str(e)}")

    def clear_all(self):
        if show_question(self, self.main_window.tr("tab_import.confirm_clear_title"),
                              self.main_window.tr("tab_import.confirm_clear_msg")):
            self.main_window.clear_all_data()

    def clear_data(self):
        self.data = {}
        self.root_path.clear()
        self.update_indicator_list({})
        self.update_preview({})
        self.btn_next.setEnabled(False)

    def update_indicator_list(self, data):
        while self.indicator_layout.count() > 1:
            item = self.indicator_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        self.indicator_radios.clear()

        for i, (indicator_name, groups) in enumerate(data.items()):
            radio = QRadioButton(f"{indicator_name} ({len(groups)} {self.main_window.tr('tab_import.groups')})")
            radio.setChecked(i == 0)
            self.indicator_group.addButton(radio)
            self.indicator_radios.append(radio)
            self.indicator_layout.addWidget(radio)

    def update_preview(self, data):
        self.preview_table.setRowCount(0)

        for indicator_name, groups in data.items():
            # 计算各文件的时间点数（排除1列的因素文件）
            data_tp = [g.shape[1] for g in groups.values() if g.shape[1] > 1]

            # 找到出现最多的时间点数（众数）
            if data_tp:
                from collections import Counter
                tp_counter = Counter(data_tp)
                most_common_tp = tp_counter.most_common(1)[0][0]
            else:
                most_common_tp = None

            for group_name, group_data in groups.items():
                row = self.preview_table.rowCount()
                self.preview_table.insertRow(row)

                self.preview_table.setItem(row, 0, QTableWidgetItem(group_name))
                self.preview_table.setItem(row, 1, QTableWidgetItem(str(group_data.shape[0])))

                # 逐文件判断
                current_tp = group_data.shape[1]
                if np.isnan(group_data).any():
                    tp_text = self.main_window.tr("tab_import.timepoints_uneven")
                    tp_item = QTableWidgetItem(tp_text)
                    tp_item.setForeground(QColor("#E74C3C"))
                elif current_tp > 1 and most_common_tp is not None and current_tp != most_common_tp:
                    tp_text = self.main_window.tr("tab_import.timepoints_uneven")
                    tp_item = QTableWidgetItem(tp_text)
                    tp_item.setForeground(QColor("#E74C3C"))
                else:
                    tp_item = QTableWidgetItem(str(current_tp))

                self.preview_table.setItem(row, 2, tp_item)

                self.preview_table.setItem(row, 3, QTableWidgetItem(indicator_name))
                self.preview_table.setItem(row, 4, QTableWidgetItem(self.main_window.tr("tab_import.loaded")))
                self.preview_table.setItem(row, 5, QTableWidgetItem("\u2713"))

        total_samples = sum(sum(g.shape[0] for g in groups.values()) for groups in data.values())

        self.data_info.setText(
            f"{self.main_window.tr('tab_import.loaded')} {self.main_window.tr('tab_import.data_loaded')}, "
            f"{self.main_window.tr('tab_import.total')} {total_samples} {self.main_window.tr('tab_import.samples')}"
        )

    def go_next(self):
        for i, radio in enumerate(self.indicator_radios):
            if radio.isChecked():
                self.main_window.selected_indicator = list(self.main_window.analysis_data.keys())[i]
                break

        self.main_window.next_tab()

    def retranslate_ui(self):
        self.title.setText(self.main_window.tr("tab_import.title"))
        self.group_source.setTitle(self.main_window.tr("tab_import.select_source"))
        self.root_path.setPlaceholderText(self.main_window.tr("tab_import.browse_hint"))
        self.btn_browse.setText(self.main_window.tr("tab_import.browse"))
        self.btn_load.setText(self.main_window.tr("tab_import.load_data"))
        self.btn_clear.setText(self.main_window.tr("tab_import.clear_data"))
        self.group_indicator.setTitle(self.main_window.tr("tab_import.select_indicator"))
        self.indicator_hint.setText(self.main_window.tr("tab_import.select_indicator_hint"))
        self.group_preview.setTitle(self.main_window.tr("tab_import.preview"))
        
        self.preview_table.setHorizontalHeaderLabels([
            self.main_window.tr("tab_import.col_group"),
            self.main_window.tr("tab_import.col_samples"),
            self.main_window.tr("tab_import.col_timepoints"),
            self.main_window.tr("tab_import.col_indicator"),
            self.main_window.tr("tab_import.col_path"),
            self.main_window.tr("tab_import.col_status")
        ])
        
        if self.data is None:
            self.data_info.setText(self.main_window.tr("tab_import.no_data"))
        
        self.btn_next.setText(self.main_window.tr("tab_import.next_normality"))
