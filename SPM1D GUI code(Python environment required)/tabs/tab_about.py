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

        self.title = QLabel(self.main_window.tr("tab_about.title"))
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.title)

        layout.addWidget(self._create_content())

        layout.addStretch()
        self.setLayout(layout)

    def _create_content(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)

        self.software_info = QLabel(self.main_window.tr("tab_about.software_name"))
        self.software_info.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(self.software_info)

        self.desc = QLabel(self.main_window.tr("tab_about.description"))
        self.desc.setFont(QFont("Arial", 11))
        content_layout.addWidget(self.desc)

        content_layout.addSpacing(20)

        self.features_title = QLabel(self.main_window.tr("tab_about.main_features"))
        self.features_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(self.features_title)

        features_text = (
            f"• {self.main_window.tr('tab_about.feature_import')}\n"
            f"• {self.main_window.tr('tab_about.feature_normality')}\n"
            f"• {self.main_window.tr('tab_about.feature_spm')}\n"
            f"    - {self.main_window.tr('tab_about.feature_spm_ttest')}\n"
            f"    - {self.main_window.tr('tab_about.feature_spm_anova')}\n"
            f"    - {self.main_window.tr('tab_about.feature_spm_regress')}\n"
            f"• {self.main_window.tr('tab_about.feature_posthoc')}\n"
            f"• {self.main_window.tr('tab_about.feature_viz')}\n"
            f"• {self.main_window.tr('tab_about.feature_export')}"
        )
        self.features = QLabel(features_text)
        self.features.setFont(QFont("Arial", 10))
        self.features.setWordWrap(True)
        content_layout.addWidget(self.features)

        content_layout.addSpacing(20)

        self.workflow_title = QLabel(self.main_window.tr("tab_about.workflow"))
        self.workflow_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(self.workflow_title)

        self.workflow = QTextEdit()
        self.workflow.setPlainText(self.main_window.tr("tab_about.workflow_text"))
        self.workflow.setFont(QFont("Arial", 10))
        self.workflow.setReadOnly(True)
        self.workflow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.workflow.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.workflow.setFrameStyle(QTextEdit.NoFrame)
        self.workflow.setStyleSheet("background: transparent;")
        self.workflow.setFixedHeight(40)
        content_layout.addWidget(self.workflow)

        content_layout.addSpacing(20)

        self.format_title = QLabel(self.main_window.tr("tab_about.data_format"))
        self.format_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(self.format_title)

        format_content = (
            f"（1）{self.main_window.tr('tab_about.format_1')}\n"
            f"（2）{self.main_window.tr('tab_about.format_2')}\n"
            f"（3）{self.main_window.tr('tab_about.format_3')}"
        )
        self.format_content = QLabel(format_content)
        self.format_content.setFont(QFont("Arial", 10))
        self.format_content.setWordWrap(True)
        content_layout.addWidget(self.format_content)

        content_layout.addStretch()

        self.version = QLabel(self.main_window.tr("tab_about.version"))
        self.version.setFont(QFont("Arial", 9))
        self.version.setStyleSheet("color: gray;")
        self.version.setAlignment(Qt.AlignRight)
        content_layout.addWidget(self.version)

        content_widget.setLayout(content_layout)
        return content_widget

    def retranslate_ui(self):
        self.title.setText(self.main_window.tr("tab_about.title"))
        self.software_info.setText(self.main_window.tr("tab_about.software_name"))
        self.desc.setText(self.main_window.tr("tab_about.description"))
        self.features_title.setText(self.main_window.tr("tab_about.main_features"))
        
        features_text = (
            f"• {self.main_window.tr('tab_about.feature_import')}\n"
            f"• {self.main_window.tr('tab_about.feature_normality')}\n"
            f"• {self.main_window.tr('tab_about.feature_spm')}\n"
            f"    - {self.main_window.tr('tab_about.feature_spm_ttest')}\n"
            f"    - {self.main_window.tr('tab_about.feature_spm_anova')}\n"
            f"    - {self.main_window.tr('tab_about.feature_spm_regress')}\n"
            f"• {self.main_window.tr('tab_about.feature_posthoc')}\n"
            f"• {self.main_window.tr('tab_about.feature_viz')}\n"
            f"• {self.main_window.tr('tab_about.feature_export')}"
        )
        self.features.setText(features_text)
        
        self.workflow_title.setText(self.main_window.tr("tab_about.workflow"))
        self.workflow.setPlainText(self.main_window.tr("tab_about.workflow_text"))
        self.format_title.setText(self.main_window.tr("tab_about.data_format"))
        
        format_content = (
            f"{self.main_window.tr('tab_about.format_1')}\n"
            f"{self.main_window.tr('tab_about.format_2')}\n"
            f"{self.main_window.tr('tab_about.format_3')}"
        )
        self.format_content.setText(format_content)
        self.version.setText(self.main_window.tr("tab_about.version"))
