# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtGui import QTextCursor, QFont
import sys


class ConsoleManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("동적 QTextEdit 교체 예제")
        self.resize(500, 400)

        # 3개의 콘솔(TextEdit)
        self.console_a = QTextEdit()
        self.console_b = QTextEdit()
        self.console_c = QTextEdit()

        self.console_a.setPlaceholderText("콘솔 A")
        self.console_b.setPlaceholderText("콘솔 B")
        self.console_c.setPlaceholderText("콘솔 C")

        # 현재 콘솔을 저장하는 내부 변수
        self._serial_console = None

        # 버튼들
        self.btn_set_a = QPushButton("A에 연결")
        self.btn_set_b = QPushButton("B에 연결")
        self.btn_set_c = QPushButton("C에 연결")
        self.btn_send = QPushButton("메시지 전송")

        # 버튼 이벤트 연결
        self.btn_set_a.clicked.connect(lambda: self.setSerialConsole(self.console_a))
        self.btn_set_b.clicked.connect(lambda: self.setSerialConsole(self.console_b))
        self.btn_set_c.clicked.connect(lambda: self.setSerialConsole(self.console_c))
        self.btn_send.clicked.connect(self.sendData)

        # 레이아웃 구성
        layout = QVBoxLayout()
        layout.addWidget(self.console_a)
        layout.addWidget(self.console_b)
        layout.addWidget(self.console_c)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_set_a)
        button_layout.addWidget(self.btn_set_b)
        button_layout.addWidget(self.btn_set_c)
        button_layout.addWidget(self.btn_send)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def setSerialConsole(self, text_console):
        self._serial_console = text_console
        print("콘솔이 바뀌었습니다")

    def sendData(self):
        if self._serial_console:
            self._serial_console.setFont(QFont("맑은 고딕", 10))
            self._serial_console.append("✅ 테스트: 설정이 변경되었습니다.")
            self._serial_console.moveCursor(QTextCursor.End)
            print("✅ 테스트: 설정이 변경되었습니다.")
        else:
            print("콘솔이 설정되지 않았습니다")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConsoleManager()
    window.show()
    sys.exit(app.exec())
