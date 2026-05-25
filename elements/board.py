from connect4_console_ver import COL_COUNT
from elements.player import Player
import numpy as np

class Board:
    
    def __init__(self):
        self.ROW_COUNT = 6
        self.COL_COUNT = 7
        self.WINNING_COUNT = 4
        self.clear()

    def clear(self):
        self._grid = [[None for i in range(self.COL_COUNT)] for j in range(self.ROW_COUNT)]


    def get_next_open_row(self, player, col):
        for i in range(self.ROW_COUNT):
            if self._grid[i][col] is None:
                return i
        return -1
    
    def place_piece(self, player, col, row):
        self._grid[row][col] = player.get_id()

    def winning_move(self, player):

        player_id = player.get_id()

        # horizontal
        for col in range(self.COL_COUNT - self.WINNING_COUNT + 1):
            for row in range(self.ROW_COUNT):
                if self._grid[row][col] == player_id and self._grid[row][col + 1] == player_id and self._grid[row][col + 2] == player_id and self._grid[row][col + 3] == player_id:
                    return True

        # vertical
        for col in range(self.COL_COUNT):
            for row in range(self.ROW_COUNT - self.WINNING_COUNT + 1):
                if self._grid[row][col] == player_id and self._grid[row + 1][col] == player_id and self._grid[row + 2][col] == player_id and self._grid[row + 3][col] == player_id:
                    return True

        # positive diagonal
        for col in range(self.COL_COUNT - self.WINNING_COUNT + 1):
            for row in range(self.WINNING_COUNT - 1, self.ROW_COUNT):
                if self._grid[row][col] == player_id and self._grid[row - 1][col + 1] == player_id and self._grid[row - 2][col + 2] == player_id and self._grid[row - 3][col + 3] == player_id:
                    return True

        # negative diagonal
        for col in range(self.COL_COUNT - self.WINNING_COUNT + 1):
            for row in range(self.ROW_COUNT - self.WINNING_COUNT + 1):
                if self._grid[row][col] == player_id and self._grid[row + 1][col + 1] == player_id and self._grid[row + 2][col + 2] == player_id and self._grid[row + 3][col + 3] == player_id:
                    return True
        return False
