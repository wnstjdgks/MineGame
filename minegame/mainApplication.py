import sys
import traceback

from PyQt5.QtWidgets import QMessageBox, QPushButton, QLineEdit, QFormLayout, QLabel, QVBoxLayout, QWidget, QApplication
from minegame.minegame_ui import MineGame


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Minesweeper: Select Difficulty or Custom")

        layout = QVBoxLayout()

        # 버튼 및 라벨 생성
        layout.addWidget(QLabel("Select Difficulty:"))
        easy_button = QPushButton("Easy")
        medium_button = QPushButton("Medium")
        hard_button = QPushButton("Hard")

        # 버튼에 대해 이벤트를 연결
        easy_button.clicked.connect(lambda: self.run_with_difficulty("EASY"))
        medium_button.clicked.connect(lambda: self.run_with_difficulty("MEDIUM"))
        hard_button.clicked.connect(lambda: self.run_with_difficulty("HARD"))

        # 레이아웃에 버튼위젯을 추가
        layout.addWidget(easy_button)
        layout.addWidget(medium_button)
        layout.addWidget(hard_button)

        layout.addWidget(QLabel("Or Enter Custom Settings:"))

        # 사용자 게임을 위한 레이아웃, 텍스트 라인 설정
        form_layout = QFormLayout()
        self.row_input = QLineEdit()
        self.col_input = QLineEdit()
        self.mine_count_input = QLineEdit()

        # 사용자 입력 텍스트 라인을 레이아웃에 추가
        form_layout.addRow("Rows:", self.row_input)
        form_layout.addRow("Columns:", self.col_input)
        form_layout.addRow("Mines:", self.mine_count_input)

        layout.addLayout(form_layout)

        # 게임 시작 버튼 추가 및 이벤트 연결
        custom_button = QPushButton("Start Custom Game")
        custom_button.clicked.connect(self.run_with_custom)
        layout.addWidget(custom_button)

        self.setLayout(layout)

    def run_with_difficulty(self, difficulty_text):
        try:
            MineGame.run_with_difficulty(difficulty_text)
        except Exception as e:
            self.show_error_message(str(e))
            traceback.print_exc()

    def run_with_custom(self):
        try:
            row = int(self.row_input.text())
            col = int(self.col_input.text())
            mine_count = int(self.mine_count_input.text())
            MineGame.run_with_custom(row, col, mine_count)

        except ValueError as e:
            self.show_error_message(f"Invalid input: {str(e)}")
        except Exception as e:
            self.show_error_message(f"Error: {str(e)}")

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class MainApplication:
    @classmethod
    def run(cls):
        app = QApplication(sys.argv)
        main_ui = MainUI()
        main_ui.show()
        sys.exit(app.exec_())
