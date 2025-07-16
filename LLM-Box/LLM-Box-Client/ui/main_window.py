from PyQt6.QtWidgets import (QMainWindow, 
                            QTabWidget, 
                            QWidget, 
                            QApplication, 
                            QVBoxLayout, 
                            QFormLayout, 
                            QLabel, 
                            QLineEdit, 
                            QPushButton, 
                            QHBoxLayout, 
                            QGridLayout)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from .select_model_dialog import SelectModelDialog

# from .deployment_widget import DeploymentWidget
# from .monitoring_widget import MonitoringWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM-Box 主面板")
        self.setGeometry(200, 200, 800, 600)
        self.main_tabs = QTabWidget()
        self.setCentralWidget(self.main_tabs)
        self.setup_all_tabs()

    def setup_all_tabs(self):
        deployment_main_page = self.create_deployment_tab()

        monitoring_page = QWidget()
        monitoring_layout = QVBoxLayout(monitoring_page)
        monitoring_layout.addWidget(QLabel("性能监控图表"))

        other_page = QWidget()
        other_layout = QVBoxLayout(other_page)
        other_layout.addWidget(QLabel("其他设置"))

        about_page = QWidget()
        about_layout = QVBoxLayout(about_page)
        about_layout.addWidget(QLabel("关于"))

        self.main_tabs.addTab(deployment_main_page, "一键部署")
        self.main_tabs.addTab(monitoring_page, "性能监控")
        self.main_tabs.addTab(other_page, "其他")
        self.main_tabs.addTab(about_page, "关于")

    def create_deployment_tab(self):
        container_page = QWidget()
        container_layout = QVBoxLayout(container_page)

        sub_tabs = QTabWidget()
        container_layout.addWidget(sub_tabs)

        local_deployment_page = self.create_local_deployment_tab()
        remote_deployment_page = self.create_remote_deployment_tab()
        
        sub_tabs.addTab(local_deployment_page, "本地部署")
        sub_tabs.addTab(remote_deployment_page, "远程部署")

        return container_page

    def create_local_deployment_tab(self):
        page = QWidget()
        layout = QGridLayout(page)
        
        self.button1 = QPushButton("选择大模型")
        self.button2 = QPushButton("部署")
        self.label1 = QLabel("未选择任何模型")
        


        #button1 选择大模型
        self.button1.setFixedWidth(200)
        self.button1.setFixedHeight(50)
        self.button1.clicked.connect(self.select_model)
        #button2 部署启动
        self.button2.setFixedWidth(200)
        self.button2.setFixedHeight(50)
        #排版
        layout.addWidget(self.button1,1,1)
        layout.addWidget(self.button2,2,1)
        layout.addWidget(self.label1,1,2)

        return page

    def create_remote_deployment_tab(self):
        page = QWidget()
        layout = QFormLayout(page)

        layout.addRow("服务器地址:", QLineEdit())
        layout.addRow("SSH 用户名:", QLineEdit())
        layout.addRow("SSH 密码:", QLineEdit())
        layout.addRow(QPushButton("测试连接并部署"))

        return page

    def select_model(self):
        dialog = SelectModelDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            selected_model = dialog.get_selected_model()
            if selected_model:
                self.label1.setText(selected_model)
    

    def closeEvent(self, event):
        event.accept()