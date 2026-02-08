from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox, 
                              QTextEdit, QScrollArea, QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class TabAbout(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("项目说明")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addWidget(self._create_content())

        layout.addStretch()
        self.setLayout(layout)

    def _create_content(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)

        software_info = QLabel("SPM1D 分析软件")
        software_info.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(software_info)

        desc = QLabel("基于一维统计参数映射(SPM)的桌面分析工具")
        desc.setFont(QFont("Arial", 11))
        content_layout.addWidget(desc)

        content_layout.addSpacing(20)

        features_title = QLabel("主要功能")
        features_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(features_title)

        features = QLabel(
            "• 数据导入：支持 .xlsx 和 .csv 格式\n"
            "• 正态性检验：D'Agostino K² 检验\n"
            "• SPM 统计分析：\n"
            "    - t 检验（独立样本t检验、配对样本t检验、单样本t检验）\n"
            "    - ANOVA（单因素方差分析）\n"
            "    - 简单回归（单指标）\n"
            "• 事后检验：采用Bonferroni 校正进行组间两两比较\n"
            "• 结果可视化：均值曲线、SPM曲线、K²曲线、事后检验图等\n"
            "• 数据导出：.xlsx 格式，包含全部原始数据"
        )
        features.setFont(QFont("Arial", 10))
        features.setWordWrap(True)
        content_layout.addWidget(features)

        content_layout.addSpacing(20)

        workflow_title = QLabel("分析流程")
        workflow_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(workflow_title)

        workflow = QTextEdit()
        workflow.setPlainText("1. 数据导入 → 2. 正态性检验 → 3. 参数设置 →4. 运行分析 → 5. 事后检验（如需要）→ 6. 查看图表 → 7. 导出数据")
        workflow.setFont(QFont("Arial", 10))
        workflow.setReadOnly(True)
        workflow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        workflow.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        workflow.setFrameStyle(QTextEdit.NoFrame)
        workflow.setStyleSheet("background: transparent;")
        workflow.setFixedHeight(40)
        content_layout.addWidget(workflow)

        content_layout.addSpacing(20)

        format_title = QLabel("数据格式要求")
        format_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(format_title)

        format_content = QLabel(
            "（1）读取目标文件夹下 .xlsx 或. csv 格式的数据；\n"
            "（2）文件名称即为需统计的组别名称；\n"
            "（3）数据格式以行为样本、列为时间点进行排列。"
        )
        format_content.setFont(QFont("Arial", 10))
        format_content.setWordWrap(True)
        content_layout.addWidget(format_content)

        content_layout.addStretch()

        version = QLabel("版本 v1.1 | 2026年2月 | 白啸天")
        version.setFont(QFont("Arial", 9))
        version.setStyleSheet("color: gray;")
        version.setAlignment(Qt.AlignRight)
        content_layout.addWidget(version)

        content_widget.setLayout(content_layout)
        return content_widget
