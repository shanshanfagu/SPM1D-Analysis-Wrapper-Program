from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFileDialog, QTableWidget,
                              QTableWidgetItem, QGroupBox, QRadioButton,
                              QButtonGroup, QLineEdit, QProgressBar,
                              QMessageBox, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os
import pandas as pd
import numpy as np
from modules.data_loader import load_data_by_indicator

class TabImport(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.data = None
        self.indicator_layout = None  # 添加这个
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("数据导入")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addLayout(self._create_select_section())
        layout.addLayout(self._create_indicator_section())
        layout.addLayout(self._create_preview_section())
        layout.addLayout(self._create_button_section())

        layout.addStretch()
        self.setLayout(layout)

    def _create_select_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("选择数据源")
        group_layout = QHBoxLayout()

        self.root_path = QLineEdit()
        self.root_path.setPlaceholderText("选择包含指标文件夹的根目录")
        self.root_path.setReadOnly(True)

        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self.browse_folder)

        btn_load = QPushButton("加载数据")
        btn_load.clicked.connect(self.load_data)

        group_layout.addWidget(self.root_path)
        group_layout.addWidget(btn_browse)
        group_layout.addWidget(btn_load)

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_indicator_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("选择指标")
        self.indicator_layout = QVBoxLayout()

        self.indicator_group = QButtonGroup()
        self.indicator_radios = []

        self.indicator_layout.addWidget(QLabel("请选择要分析的指标："))

        group.setLayout(self.indicator_layout)
        layout.addWidget(group)

        return layout

    def _create_preview_section(self):
        layout = QHBoxLayout()

        group = QGroupBox("数据预览")
        group_layout = QVBoxLayout()

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(6)
        self.preview_table.setHorizontalHeaderLabels(["组别", "样本数", "时间点数", "指标", "文件路径", "状态"])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.data_info = QLabel("尚未加载数据")
        self.data_info.setFont(QFont("Arial", 12))

        group_layout.addWidget(self.data_info)
        group_layout.addWidget(self.preview_table)

        group.setLayout(group_layout)
        layout.addWidget(group)

        return layout

    def _create_button_section(self):
        layout = QHBoxLayout()

        self.btn_next = QPushButton("下一步: 正态性检验 →")
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.go_next)

        layout.addStretch()
        layout.addWidget(self.btn_next)

        return layout

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择根目录",
                                                  "",
                                                  QFileDialog.Option.ShowDirsOnly)
        if folder:
            self.root_path.setText(folder)

    def load_data(self):
        root_path = self.root_path.text()
        if not root_path:
            QMessageBox.warning(self, "警告", "请先选择根目录")
            return

        if not os.path.exists(root_path):
            QMessageBox.warning(self, "警告", "目录不存在")
            return

        try:
            data = load_data_by_indicator(root_path)

            if not data:
                QMessageBox.warning(self, "警告", "未找到有效的指标文件夹")
                return

            self.data = data
            self.update_indicator_list(data)
            self.update_preview(data)

            self.main_window.analysis_data = data
            self.btn_next.setEnabled(True)

            QMessageBox.information(self, "成功", "成功加载数据")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")

    def update_indicator_list(self, data):
        # 清除现有的单选按钮（保留第一个标签）
        while self.indicator_layout.count() > 1:
            item = self.indicator_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        self.indicator_radios.clear()

        for i, (indicator_name, groups) in enumerate(data.items()):
            radio = QRadioButton(f"{indicator_name} ({len(groups)} 个组别)")
            radio.setChecked(i == 0)
            self.indicator_group.addButton(radio)
            self.indicator_radios.append(radio)
            self.indicator_layout.addWidget(radio)

    def update_preview(self, data):
        self.preview_table.setRowCount(0)

        for indicator_name, groups in data.items():
            for group_name, group_data in groups.items():
                row = self.preview_table.rowCount()
                self.preview_table.insertRow(row)

                self.preview_table.setItem(row, 0, QTableWidgetItem(group_name))
                self.preview_table.setItem(row, 1, QTableWidgetItem(str(group_data.shape[0])))
                self.preview_table.setItem(row, 2, QTableWidgetItem(str(group_data.shape[1])))
                self.preview_table.setItem(row, 3, QTableWidgetItem(indicator_name))
                self.preview_table.setItem(row, 4, QTableWidgetItem("已加载"))
                self.preview_table.setItem(row, 5, QTableWidgetItem("✓"))

        total_samples = sum(sum(g.shape[0] for g in groups.values()) for groups in data.values())
        
        first_group_data = None
        for groups in data.values():
            for group_data in groups.values():
                first_group_data = group_data
                break
            break
        
        total_timepoints = first_group_data.shape[1] if first_group_data is not None else 0

        self.data_info.setText(f"已加载 {len(data)} 个指标，共 {total_samples} 个样本，{total_timepoints} 个时间点")

    def go_next(self):
        for i, radio in enumerate(self.indicator_radios):
            if radio.isChecked():
                self.main_window.selected_indicator = list(self.main_window.analysis_data.keys())[i]
                break

        self.main_window.next_tab()
