import sys
import json
import os
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QMenuBar, 
                               QMenu, QLabel, QAction, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from tabs.tab_import import TabImport
from tabs.tab_preprocess import TabPreprocess
from tabs.tab_normality import TabNormality
from tabs.tab_params import TabParams
from tabs.tab_results import TabResults
from tabs.tab_plots import TabPlots
from tabs.tab_about import TabAbout
from modules.utils import show_info, show_question


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = "en"
        self.translations = {}
        self.load_translations()
        
        self.setWindowTitle(self.tr("main.title"))
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

    def clear_all_data(self):
        self.analysis_data = {}
        self.normality_results = None
        self.analysis_params = {}
        self.analysis_result = None
        self.selected_indicator = None
        self.cached_spm_result = None
        self.cached_inference_result = None
        self.cached_posthoc_results = None
        
        if hasattr(self, 'tab_import'):
            self.tab_import.clear_data()
        if hasattr(self, 'tab_preprocess'):
            self.tab_preprocess.clear_data()
        if hasattr(self, 'tab_normality'):
            self.tab_normality.clear_data()
        if hasattr(self, 'tab_params'):
            self.tab_params.clear_data()
        if hasattr(self, 'tab_results'):
            self.tab_results.clear_data()
        if hasattr(self, 'tab_plots'):
            self.tab_plots.clear_data()
        
        self.statusBar().showMessage(self.tr("main.ready"))

    def load_translations(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            trans_file = os.path.join(base_dir, "translations.json")
            with open(trans_file, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"Failed to load translations: {e}")
            self.translations = {}

    def tr(self, key):
        try:
            keys = key.split(".")
            value = self.translations.get(self.current_language, {})
            for k in keys:
                value = value.get(k, {})
            return value if isinstance(value, str) else key
        except:
            return key

    def set_language(self, lang):
        if lang != self.current_language:
            self.current_language = lang
            self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("main.title"))
        self.statusBar().showMessage(self.tr("main.ready"))
        
        self.menu_file.setTitle(self.tr("menu.file"))
        self.action_exit.setText(self.tr("menu.exit"))
        self.menu_language.setTitle(self.tr("menu.language"))
        self.action_chinese.setText(self.tr("menu.chinese"))
        self.action_english.setText(self.tr("menu.english"))
        self.menu_help.setTitle(self.tr("menu.help"))
        self.action_about.setText(self.tr("menu.about"))
        
        for i in range(self.tab_widget.count()):
            tab_name_keys = ["tabs.about", "tabs.import", "tabs.preprocess", "tabs.normality", 
                            "tabs.params", "tabs.results", "tabs.plots"]
            if i < len(tab_name_keys):
                self.tab_widget.setTabText(i, self.tr(tab_name_keys[i]))
        
        if hasattr(self.tab_about, 'retranslate_ui'):
            self.tab_about.retranslate_ui()
        if hasattr(self.tab_import, 'retranslate_ui'):
            self.tab_import.retranslate_ui()
        if hasattr(self.tab_preprocess, 'retranslate_ui'):
            self.tab_preprocess.retranslate_ui()
        if hasattr(self.tab_normality, 'retranslate_ui'):
            self.tab_normality.retranslate_ui()
        if hasattr(self.tab_params, 'retranslate_ui'):
            self.tab_params.retranslate_ui()
        if hasattr(self.tab_results, 'retranslate_ui'):
            self.tab_results.retranslate_ui()
        if hasattr(self.tab_plots, 'retranslate_ui'):
            self.tab_plots.retranslate_ui()

    def setup_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)

        self.tab_about = TabAbout(self)
        self.tab_import = TabImport(self)
        self.tab_preprocess = TabPreprocess(self)
        self.tab_normality = TabNormality(self)
        self.tab_params = TabParams(self)
        self.tab_results = TabResults(self)
        self.tab_plots = TabPlots(self)

        self.tab_widget.addTab(self.tab_about, self.tr("tabs.about"))
        self.tab_widget.addTab(self.tab_import, self.tr("tabs.import"))
        self.tab_widget.addTab(self.tab_preprocess, self.tr("tabs.preprocess"))
        self.tab_widget.addTab(self.tab_normality, self.tr("tabs.normality"))
        self.tab_widget.addTab(self.tab_params, self.tr("tabs.params"))
        self.tab_widget.addTab(self.tab_results, self.tr("tabs.results"))
        self.tab_widget.addTab(self.tab_plots, self.tr("tabs.plots"))

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tab_widget)

    def setup_menu(self):
        menubar = self.menuBar()
        
        self.menu_file = menubar.addMenu(self.tr("menu.file"))
        self.action_exit = QAction(self.tr("menu.exit"), self)
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.triggered.connect(self.close)
        self.menu_file.addAction(self.action_exit)

        self.menu_language = menubar.addMenu(self.tr("menu.language"))
        self.action_chinese = QAction(self.tr("menu.chinese"), self)
        self.action_chinese.triggered.connect(lambda: self.set_language("zh"))
        self.menu_language.addAction(self.action_chinese)
        
        self.action_english = QAction(self.tr("menu.english"), self)
        self.action_english.triggered.connect(lambda: self.set_language("en"))
        self.menu_language.addAction(self.action_english)

        self.menu_help = menubar.addMenu(self.tr("menu.help"))
        self.action_about = QAction(self.tr("menu.about"), self)
        self.action_about.triggered.connect(self.show_about)
        self.menu_help.addAction(self.action_about)

    def setup_statusbar(self):
        self.statusBar().showMessage(self.tr("main.ready"))
        self.statusBar().addPermanentWidget(QLabel("SPM1D Analyzer v2.81"))

    def on_tab_changed(self, index):
        self.current_tab_index = index
        if index == 2:
            self.tab_preprocess.refresh_file_list()
        elif index == 4:
            self.tab_params.refresh_test_types()
        elif index == 6:
            self.tab_plots.update_chart()

    def next_tab(self):
        if self.current_tab_index < self.tab_widget.count() - 1:
            self.tab_widget.setCurrentIndex(self.current_tab_index + 1)

    def prev_tab(self):
        if self.current_tab_index > 0:
            self.tab_widget.setCurrentIndex(self.current_tab_index - 1)

    def show_about(self):
        show_info(self, self.tr("main.about_title"), self.tr("main.about_text"))

    def closeEvent(self, event):
        if show_question(self, self.tr("main.confirm_exit"), self.tr("main.confirm_exit_msg")):
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
