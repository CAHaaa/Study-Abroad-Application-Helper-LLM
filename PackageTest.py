
from PyQt5.QtWidgets import QApplication, QWidget
def PTestQt():
    # 创建应用实例
    app = QApplication([])
    # 创建主窗口
    window = QWidget()
    window.setWindowTitle("Head")
    window.setGeometry(100, 100, 400, 300)  # (x, y, width, height)
    # 显示窗口
    window.show()
    # 运行应用
    app.exec_()