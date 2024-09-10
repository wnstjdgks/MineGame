import traceback
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QWidget, QGridLayout, QMessageBox, QApplication, QPushButton, QSizePolicy
from minegame.minegame import GameState, GameController, Difficulty, BlockInfo, BaseBlockInfo, MineBlockInfo


def show_warning_message(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("Warning")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


class CustomButton(QPushButton):
    def __init__(self, x, y, game: 'GameController', main_ui: 'GameUI', parent=None):
        super().__init__(parent)

        self.x = x
        self.y = y
        self.game = game
        self.main_ui = main_ui

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                self.left_click()

            elif event.button() == Qt.RightButton:
                self.right_click()

            self.main_ui.update_ui()

        except Exception as ex:
            print(ex)
            traceback.print_exc()

    def left_click(self):
        try:
            self.game.reveal(self.x, self.y)

        except Exception as ex:
            show_warning_message(str(ex))

    def right_click(self):
        try:
            self.game.cover(self.x, self.y)

        except Exception as ex:
            show_warning_message(str(ex))


class ImageResource:
    COVER_IMAGE_PATH = 'resources/cover.png'
    MINE_REVEAL_IMAGE_PATH = 'resources/mine.png'


class GameUI(QWidget):
    BASE_ZERO_BACKGROUND_COLOR = "#EEF1F1"
    DEFAULT_BACKGROUND_COLOR = "#D0EFFF"
    DEFAULT_FONT_SIZE = 20
    BUTTON_SIZE = 45

    def __init__(self, game: 'GameController', row, col):
        super().__init__()
        self.row_size: int = row
        self.col_size: int = col
        self.game: 'GameController' = game
        self.layout: 'QGridLayout' = QGridLayout()
        self.buttons: List[List[QPushButton]] = [[None for _ in range(self.row_size)] for _ in range(self.col_size)]
        self.init_ui()

        self.adjustSize()
        self.setFixedSize(self.size())

    def init_ui(self):
        self.setWindowTitle('Minesweeper')

        # 레이아웃에 대한 설정, 위젯 사이의 거리를 조정
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 버튼 텍스트의 폰트를 설정
        font = QFont()
        font.setPointSize(self.DEFAULT_FONT_SIZE)

        # 생성된 버튼을 레이아웃에 대해 연결
        for i in range(self.row_size):
            for j in range(self.col_size):
                button = CustomButton(i, j, self.game, self)

                # 버튼에 대한 크기 설정 최소 사이즈는 BUTTON_MIN_SIZE, 최대 사이즈는 BUTTON_MAX_SIZE
                button.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
                button.setFont(font)

                # 버튼에 대한 배경색을 설정 기본 배경색은 DEFAULT_BACKGROUND_COLOR
                button.setStyleSheet(
                    f"QPushButton {{ background-color: {self.DEFAULT_BACKGROUND_COLOR}; color: black; }}")

                self.layout.addWidget(button, i, j)
                self.buttons[i][j] = button

        self.setLayout(self.layout)

    def update_ui(self):

        for i in range(self.row_size):
            for j in range(self.col_size):
                block_info: 'BlockInfo' = self.game.get_block_info(i, j)
                self.set_button_text(block_info, i, j)
                self.set_button_image(block_info, i, j)

        self.display_game_result()

    def set_button_text(self, block_info: 'BlockInfo', i: int, j: int):

        def find_color(text: str):
            number = int(text)

            if number == 1:
                return "black"

            elif number == 2:
                return "blue"

            elif number == 3:
                return "green"

            else:
                return "red"

        def set_button_text_color(i, j, color):
            self.buttons[i][j].setStyleSheet(f"background-color: {self.DEFAULT_BACKGROUND_COLOR}; color: {color};")

        if not block_info.is_covered() and not block_info.is_reveal():
            return

        if block_info.is_covered():
            return

        if isinstance(block_info, MineBlockInfo):
            return

        if block_info.near_mine_count == 0:
            self.fill_button_background(i, j, self.BASE_ZERO_BACKGROUND_COLOR)

        else:
            self.buttons[i][j].setText(str(block_info.near_mine_count))
            color = find_color(str(block_info.near_mine_count))
            set_button_text_color(i, j, color)

    def fill_button_background(self, i, j, color):
        self.buttons[i][j].setStyleSheet(f"QPushButton {{ background-color: {color}; color: black; }}")

    def set_button_image(self, block_info, i, j):


        if isinstance(block_info, BaseBlockInfo):
            if block_info.is_covered():
                self.buttons[i][j].setIcon(QIcon(ImageResource.COVER_IMAGE_PATH))
                self.buttons[i][j].setIconSize(self.buttons[i][j].size())

            else:
                self.buttons[i][j].setIcon(QIcon())

        elif isinstance(block_info, MineBlockInfo):

            if block_info.is_reveal():
                self.buttons[i][j].setIcon(QIcon(ImageResource.MINE_REVEAL_IMAGE_PATH))
                self.buttons[i][j].setIconSize(self.buttons[i][j].size())

            elif block_info.is_covered():
                self.buttons[i][j].setIcon(QIcon(ImageResource.COVER_IMAGE_PATH))
                self.buttons[i][j].setIconSize(self.buttons[i][j].size())

            else:
                self.buttons[i][j].setIcon(QIcon())





    def display_game_result(self):

        if self.game.get_game_state() == GameState.WIN:
            self.show_message("Congratulations!", "You won the game!")
        if self.game.get_game_state() == GameState.LOSE:
            self.show_message("Game Over", "You hit a mine!")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        self.close()


class MineGame:

    @classmethod
    def run_with_difficulty(cls, text):
        difficulty = cls.find_difficulty(text)
        game = GameController.create_with_difficulty(difficulty=difficulty)
        game_ui = GameUI(game, difficulty.row_size, difficulty.col_size)
        game_ui.show()

    @classmethod
    def find_difficulty(cls, text):
        text_mapping = {"EASY": Difficulty.EASY, "MEDIUM": Difficulty.MEDIUM, "HARD": Difficulty.HARD}

        if text_mapping[text] and text_mapping[text] != "":
            return text_mapping[text]

        raise ValueError("The difficulty level should be either EASY, MEDIUM, or HARD")

    @classmethod
    def run_with_custom(cls, row, col, mine_count):
        game = GameController.create_with_user_setting(row, col, mine_count)
        game_ui = GameUI(game, row, col)
        game_ui.show()
