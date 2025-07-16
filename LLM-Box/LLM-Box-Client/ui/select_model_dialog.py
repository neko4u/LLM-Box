from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QAbstractItemView,QDialogButtonBox)

class SelectModelDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("模型列表")
        self.setFixedSize(400,300)
        #self.setGeometry()

        layout = QVBoxLayout(self)

        self.list = QListWidget()
        #可以配合request,从服务器请求models内容
        models = ["GPT4o","LLaMA 3","Genmino Pro"]
        self.list.addItems(models)

        layout.addWidget(self.list)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.selected_model = ""

    def get_selected_model(self): #获取选择的model
        selected_items = self.list.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return ""