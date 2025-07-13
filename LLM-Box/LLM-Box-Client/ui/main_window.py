from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget
from PyQt6.QtGui import QIcon

from .deployment_widget import DeploymentWidget
from .monitoring_widget import MonitoringWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM-Box: 一键式大语言模型部署与监控平台")
        self.setGeometry(100, 100, 900, 700)
        # self.setWindowIcon(QIcon("assets/icon.png"))

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.deployment_tab = DeploymentWidget()
        self.monitoring_tab = MonitoringWidget()

        self.tabs.addTab(self.deployment_tab, "🚀 自动化部署")
        self.tabs.addTab(self.monitoring_tab, "📊 综合监控面板")

    def closeEvent(self, event):
        """确保在关闭窗口时，后台线程也能被正确停止"""
        self.monitoring_tab.stop_monitoring_thread()
        event.accept()