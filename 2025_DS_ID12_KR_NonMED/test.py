from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys

class UiDlg(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("다이얼로그 예시")
        self.resize(300, 300)

        layout = QVBoxLayout()

        label = QLabel("여기는 PyQt 다이얼로그입니다.")
        layout.addWidget(label)

        image_label = QLabel()
        pixmap = QPixmap("sample.jpg")  # 이미지 파일 필요
        image_label.setPixmap(pixmap)
        layout.addWidget(image_label)

        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def uiDlgStart(self):
        self.exec()

app = QApplication(sys.argv)
uiDlg = UiDlg()
uiDlg.uiDlgStart()
sys.exit(app.exec())
