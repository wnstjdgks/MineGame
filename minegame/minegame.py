import enum
import random

from abc import *
from collections import deque
from typing import *


class ClickEventResult(enum.Enum):
    BASE_BLOCK_REVEAL = (False, 0, 0)  # 안전 블록 클릭
    MINE_BLOCK_REVEAL = (True, 0, 0)  # 지뢰 블록 클릭

    BASE_BLOCK_COVER = (False, 0, 1)  # 안전 블록 커버
    BASE_BLOCK_UNCOVER = (False, 0, -1)  # 안전 블록 커버 해제

    MINE_BLOCK_COVER = (True, 1, 1)  # 지뢰 블록 커버
    MINE_BLOCK_UNCOVER = (True, -1, -1)  # 지뢰 블록 커버 해제

    def __init__(self, is_mine, found_mine_count_offset: int, covered_block_count_offset: int):
        self.is_mine = is_mine  # 해당 블록이 지뢰인지 확인하는 변수
        self.found_mine_count_offset = found_mine_count_offset  # 클릭을 통해 찾은 지뢰 개수의 변화
        self.covered_block_count_offset = covered_block_count_offset  # 클릭을 통해 커버한 블록 개수의 변화

    def __str__(self):
        return f"{self.is_mine}, {self.found_mine_count_offset}, {self.covered_block_count_offset}"


class GamePiece(metaclass=ABCMeta):

    @abstractmethod
    def reveal(self):
        pass

    @abstractmethod
    def cover(self):
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def is_covered(self):
        pass


class BlockInfo(metaclass=ABCMeta):
    def is_reveal(self):
        pass

    def is_covered(self):
        pass


class BaseBlockInfo(BlockInfo):
    def __init__(self, is_reveal, is_covered, near_mine_count):
        self.reveal = is_reveal
        self.covered = is_covered
        self.near_mine_count = near_mine_count

    def is_reveal(self):
        return self.reveal

    def is_covered(self):
        return self.covered

    @staticmethod
    def unrevealed_block():
        return BaseBlockInfo(is_reveal=False, is_covered=False, near_mine_count=0)

    @staticmethod
    def covered_block():
        return BaseBlockInfo(is_reveal=False, is_covered=True, near_mine_count=0)


    @staticmethod
    def revealed_block(near_mine_count):
        return BaseBlockInfo(is_reveal=True, is_covered=False, near_mine_count=near_mine_count)

    print()

class MineBlockInfo(BlockInfo):
    def __init__(self, is_reveal, is_covered):
        self.reveal = is_reveal
        self.covered = is_covered

    def is_reveal(self):
        return self.reveal

    def is_covered(self):
        return self.covered

    @staticmethod
    def unrevealed_mine():
        return MineBlockInfo(is_reveal=False, is_covered=False)

    @staticmethod
    def revealed_mine():
        return MineBlockInfo(is_reveal=True, is_covered=False)

    @staticmethod
    def covered_mine():
        return MineBlockInfo(is_reveal=False, is_covered=True)

    @staticmethod
    def uncovered_mine():
        return MineBlockInfo(is_reveal=True, is_covered=False)


class BaseBlock(GamePiece):

    def __init__(self):
        self.near_mine_count = 0
        self.is_revealed = False
        self.is_cover = False

    def reveal(self):

        if self.is_revealed:
            return ClickEventResult.BASE_BLOCK_REVEAL

        self.is_revealed = True
        return ClickEventResult.BASE_BLOCK_REVEAL

    def cover(self):

        if self.is_revealed:
            return

        if self.is_cover:
            self.is_cover = False
            return ClickEventResult.BASE_BLOCK_UNCOVER

        else:
            self.is_cover = True
            return ClickEventResult.BASE_BLOCK_COVER

    def is_covered(self):
        return self.is_cover

    def increase_near_mine_count(self):
        self.near_mine_count += 1

    def get_info(self):
        if self.is_cover:
            return BaseBlockInfo.covered_block()

        if self.is_revealed:
            return BaseBlockInfo.revealed_block(self.near_mine_count)

        return BaseBlockInfo.unrevealed_block()

    def is_near_mine_count_zero(self):
        return self.near_mine_count == 0

    def set_reveal(self, reveal_state):
        self.is_revealed = reveal_state

    def __str__(self):
        return f"BaseBlock(near_mine_count = {self.near_mine_count})"

    def __repr__(self):
        return f"BaseBlock(near_mine_count = {self.near_mine_count})"


class MineBlock(GamePiece):
    def __init__(self):
        self.color = "black"
        self.is_cover = False
        self.is_game_end = False

    def reveal(self):
        return ClickEventResult.MINE_BLOCK_REVEAL

    def cover(self):

        if self.is_cover:
            self.is_cover = False
            return ClickEventResult.MINE_BLOCK_UNCOVER

        else:
            self.is_cover = True
            return ClickEventResult.MINE_BLOCK_COVER

    def is_covered(self):
        return self.is_cover

    def get_info(self):

        if self.is_game_end:
            return MineBlockInfo.revealed_mine()

        if self.is_cover:
            return MineBlockInfo.covered_mine()

        return MineBlockInfo.unrevealed_mine()

    def game_end(self):
        self.is_game_end = True

    def __str__(self):
        return f"MineBlock()"

    def __repr__(self):
        return f"MineBlock()"


class Map:
    MIN_ROW_SIZE = 4
    MAX_ROW_SIZE = 25

    MIN_COL_SIZE = 4
    MAX_COL_SIZE = 25

    def __init__(self, row: int, col: int, total_mine_count: int, board: List[List[GamePiece]]):

        # 유효성 검사
        self.validate(row, col, total_mine_count)

        self.row = row
        self.col = col
        self.board = board

    @classmethod
    def create(cls, row: int, col: int, total_mine_count):

        dx = [1, -1, 0, 0]
        dy = [0, 0, 1, -1]

        current_board = [[BaseBlock() for j in range(col)] for i in range(row)]

        mine_pos = random.sample([(i, j) for i in range(row) for j in range(col)], total_mine_count)

        for x, y in mine_pos:
            current_board[x][y] = MineBlock()

            for k in range(4):
                nx = x + dx[k]
                ny = y + dy[k]

                if nx < 0 or ny < 0 or nx >= row or ny >= col:
                    continue

                if isinstance(current_board[nx][ny], BaseBlock):
                    current_board[nx][ny].increase_near_mine_count()

        return Map(row, col, total_mine_count, current_board)

    @classmethod
    def validate(cls, row: int, col: int, total_mine_count: int):

        if not (1 <= total_mine_count < row * col):
            raise ValueError(f"Mine count ({total_mine_count}) must be between 1 and {row * col - 1}.")

        if not (cls.MIN_ROW_SIZE <= row <= cls.MAX_ROW_SIZE):
            raise ValueError(f"Rows ({row}) must be between {cls.MIN_ROW_SIZE} and {cls.MAX_ROW_SIZE}.")

        if not (cls.MIN_COL_SIZE <= col <= cls.MAX_COL_SIZE):
            raise ValueError(f"Columns ({col}) must be between {cls.MIN_COL_SIZE} and {cls.MAX_COL_SIZE}.")

    def get_block_info(self, x, y):
        return self.board[x][y].get_info()

    def get_block(self, x, y):
        return self.board[x][y]

    def reveal(self, x, y):

        if self.out_of_range(x, y):
            return

        block = self.board[x][y]

        if isinstance(block, BaseBlock) and block.is_near_mine_count_zero():
            self.reveal_adjacent_zero_blocks(x, y)

        return self.board[x][y].reveal()

    def cover(self, x, y):

        if self.out_of_range(x, y):
            return

        return self.board[x][y].cover()

    def reveal_adjacent_zero_blocks(self, x, y):

        dx = [1, -1, 0, 0]
        dy = [0, 0, 1, -1]

        queue = deque([(x, y)])

        while queue:
            cx, cy = queue.popleft()
            current_block = self.board[cx][cy]

            if not isinstance(current_block, BaseBlock) or current_block.is_revealed:
                continue

            current_block.set_reveal(True)

            if current_block.is_near_mine_count_zero():

                for k in range(4):
                    nx = cx + dx[k]
                    ny = cy + dy[k]

                    if self.out_of_range(nx, ny):
                        continue

                    queue.append((nx, ny))

    def out_of_range(self, x, y):
        return x < 0 or y < 0 or x >= self.row or y >= self.col

    def reveal_mine_block(self):
        for i in range(self.row):
            for j in range(self.col):
                block = self.board[i][j]

                if isinstance(block, MineBlock):
                    block.game_end()


class GameState:
    START = "START"
    PLAYING = "PLAYING"
    WIN = "WIN"
    LOSE = "LOSE"


class Game:

    def __init__(self, total_mine_count: int, map: 'Map'):
        self.total_mine_count = total_mine_count
        self.map = map
        self.find_mine_count = 0
        self.covered_block_count = 0
        self.is_game_end = False
        self.game_state = GameState.START

    @classmethod
    def create(cls, row: int, col: int, total_mine_count):
        current_map = Map.create(row, col, total_mine_count)
        return Game(total_mine_count=total_mine_count, map=current_map)

    @classmethod
    def create_with_map(cls, total_mine_count, map):
        return Game(total_mine_count, map)

    def get_block_info(self, x, y):
        return self.map.get_block_info(x, y)

    def reveal(self, x, y):

        if self.is_game_end:
            return

        block = self.map.get_block(x, y)

        if block.is_covered():
            return

        reveal_event = self.map.reveal(x, y)
        self.update_game_when_reveal(reveal_event)

    def cover(self, x, y):

        if self.is_game_end:
            return

        if not self.map.get_block(x, y).is_covered() and self.covered_block_count >= self.total_mine_count + 1:
            raise Exception(
                f"Too many blocks covered current : {self.covered_block_count} maximum : {self.total_mine_count + 1}"
            )

        cover_event = self.map.cover(x, y)
        self.update_game_when_cover(cover_event)

    def update_game_when_reveal(self, result: 'ClickEventResult'):

        if result is None:
            return

        if result.is_mine:
            self.set_game_over()
            return

    def update_game_when_cover(self, result: 'ClickEventResult'):

        if result is None:
            return

        self.update_find_mine_count(result.found_mine_count_offset)
        self.update_covered_count(result.covered_block_count_offset)

    def set_game_over(self):
        self.is_game_end = True
        self.game_state = GameState.LOSE
        self.map.reveal_mine_block()

    def update_find_mine_count(self, offset):
        self.find_mine_count += offset

        if self.find_mine_count == self.total_mine_count:
            self.is_game_end = True
            self.game_state = GameState.WIN
            return

    def update_covered_count(self, offset):
        self.covered_block_count += offset


class Difficulty(enum.Enum):
    EASY = (8, 8, 10)
    MEDIUM = (16, 16, 40)
    HARD = (24, 24, 99)

    def __init__(self, row_size: int, col_size: int, total_mine_count: int):
        self.row_size = row_size
        self.col_size = col_size
        self.total_mine_count = total_mine_count


class GameController:

    def __init__(self, game: Game):
        self.game = game
        self.game_state = GameState.START
        self.is_game_end = False

    def reveal(self, x: int, y: int):
        self.game.reveal(x, y)

    def cover(self, x: int, y: int):
        self.game.cover(x, y)

    def get_block_info(self, x, y):
        return self.game.get_block_info(x, y)

    def get_game_state(self):
        return self.game.game_state

    @classmethod
    def create_with_difficulty(cls, difficulty: 'Difficulty'):
        row = difficulty.row_size
        col = difficulty.col_size
        total_mine_count = difficulty.total_mine_count
        return cls.create_with_user_setting(row, col, total_mine_count)

    @classmethod
    def create_with_user_setting(cls, row: int, col: int, total_mine_count: int):
        game = Game.create(row, col, total_mine_count)
        return GameController(game)

