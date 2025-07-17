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
                            QGridLayout,
                            QFileDialog,
                            QMessageBox,)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt,QThread
import os
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

        self.save_path = ""
        self.download_thread = None
        self.worker = None

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
        self.button3 = QPushButton("选择安装路径")

        self.label2 = QLineEdit()
        self.label2.setPlaceholderText("请选择模型下载与安装的路径")
        self.label2.setReadOnly(True)
        


        #button1 选择大模型
        self.button1.setFixedWidth(100)
        self.button1.setFixedHeight(40)
        self.button1.clicked.connect(self.select_model)
        #button2 部署启动
        self.button2.setFixedWidth(200)
        self.button2.setFixedHeight(40)
        #button3 选择路径
        self.button3.setFixedWidth(100)
        self.button3.setFixedHeight(40)
        self.button3.clicked.connect(self.select_save_path)
        #样式
        self.label2.setFixedHeight(40)

        #排版
        layout.addWidget(self.button1,0,0)
        layout.addWidget(self.label1,0,1)

        layout.addWidget(self.button3,1,0)
        layout.addWidget(self.label2,1,1,1,4)
        ##如果有需要说明的文件,添加在row2

        layout.addWidget(self.button2,3,2,2,1)
        ##如果需要显示进度条,添加在row4

        return page

    def create_remote_deployment_tab(self):
        page = QWidget()
        layout = QGridLayout(page)

        self.button1 = QPushButton("测试连接并部署")
        self.line_serverIp = QLineEdit()
        self.line_sshAccount = QLineEdit()
        self.line_sshPwd = QLineEdit()
        self.label1 = QLabel("服务器地址:")
        self.label2 = QLabel("SSH 用户名:")
        self.label3 = QLabel("SSH 密码:")

        #样式
        ##button

        self.button1.setFixedWidth(140)
        self.button1.setFixedHeight(60)
        ##label
        self.label1.setFixedWidth(80)
        self.label1.setFixedHeight(30)
        self.label2.setFixedWidth(80)
        self.label2.setFixedHeight(30)
        self.label3.setFixedWidth(80)
        self.label3.setFixedHeight(30)

        layout.addWidget(self.label1,0,0)
        layout.addWidget(self.line_serverIp,0,1,1,4)
        layout.addWidget(self.label2,1,0)
        layout.addWidget(self.line_sshAccount,1,1,1,4)
        layout.addWidget(self.label3,2,0)
        layout.addWidget(self.line_sshPwd,2,1,1,4)
        layout.addWidget(self.button1,3,2,2,1)

        return page

    def select_model(self):
        dialog = SelectModelDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            selected_model = dialog.get_selected_model()
            if selected_model:
                self.label1.setText(selected_model)

    def select_save_path(self):
        default_path = self.save_path if self.save_path else os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(self, "选择保存路径", default_path)
        if path:
            self.save_path = path
            self.label2.setText(self.save_path)
    

    def closeEvent(self, event):
        event.accept()