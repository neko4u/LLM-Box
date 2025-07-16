import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt6.QtCore import Qt


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_app()
    sys.exit(app.exec())