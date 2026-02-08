import sys
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QMenuBar, 
                              QMenu, QMessageBox, QLabel, QAction, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from tabs.tab_import import TabImport
from tabs.tab_normality import TabNormality
from tabs.tab_params import TabParams
from tabs.tab_results import TabResults
from tabs.tab_plots import TabPlots
from tabs.tab_about import TabAbout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPM1D 分析软件")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.current_tab_index = 0
        self.analysis_data = {}
        self.normality_results = None
        self.analysis_params = {}
        self.analysis_result = None
        self.analysis_method = 'param'
        self.posthoc_summary = None
        self.selected_indicator = None

        self.cached_spm_result = None
        self.cached_inference_result = None
        self.cached_posthoc_results = None

        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()

    def setup_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)

        self.tab_import = TabImport(self)
        self.tab_normality = TabNormality(self)
        self.tab_params = TabParams(self)
        self.tab_results = TabResults(self)
        self.tab_plots = TabPlots(self)
        self.tab_about = TabAbout(self)

        self.tab_widget.addTab(self.tab_about, "1. 项目说明")
        self.tab_widget.addTab(self.tab_import, "2. 数据导入")
        self.tab_widget.addTab(self.tab_normality, "3. 正态性检验")
        self.tab_widget.addTab(self.tab_params, "4. 参数设置")
        self.tab_widget.addTab(self.tab_results, "5. 分析结果")
        self.tab_widget.addTab(self.tab_plots, "6. 图表查看")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tab_widget)

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        self.statusBar().showMessage("就绪")
        self.statusBar().addPermanentWidget(QLabel("SPM1D Analyzer v1.1"))

    def on_tab_changed(self, index):
        self.current_tab_index = index
        if index == 3:  # 参数设置页面
            self.tab_params.refresh_test_types()

    def next_tab(self):
        if self.current_tab_index < self.tab_widget.count() - 1:
            self.tab_widget.setCurrentIndex(self.current_tab_index + 1)

    def prev_tab(self):
        if self.current_tab_index > 0:
            self.tab_widget.setCurrentIndex(self.current_tab_index - 1)

    def show_about(self):
        QMessageBox.about(self, "关于 SPM1D 分析软件",
                         """SPM1D 分析软件 v1.1

基于一维统计参数映射(SPM)的分析工具

功能特点:
- 支持多种SPM统计检验
- 正态性检验
- 参数/非参数检验
- 结果可视化与导出

技术栈: Python + PyQt5 + spm1d
""")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "确认退出",
                                    "确定要退出程序吗？",
                                    QMessageBox.StandardButton.Yes |
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
