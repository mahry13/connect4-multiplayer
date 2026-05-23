from elements.player import Player

class Board:
    
    def __init__(self):
        self.ROW_COUNT = 6
        self.COL_COUNT = 7
        self.WINNING_COUNT = 4
        self.clear()

    def clear(self):
        self._grid = [[None for i in range(self.COL_COUNT)] for j in range(self.ROW_COUNT)]
    
    def place_piece(self, player, row, col):
        self._grid[row][col] = player.get_id()

    def winning_move(self, player):

        piece = player.get_id()

        # horizontal
        for col in range(self.COL_COUNT - self.WINNING_COUNT + 1):
            for row in range(self.ROW_COUNT):
                if self._grid[row][col] == piece and self._grid[row][col + 1] == piece and self._grid[row][col + 2] == piece and self._grid[row][col + 3] == piece:
                    return True

        # vertical
        for col in range(self.COL_COUNT):
            for row in range(self.ROW_COUNT - self.WINNING_COUNT + 1):
                if self._grid[row][col] == piece and self._grid[row + 1][col] == piece and self._grid[row + 2][col] == piece and self._grid[row + 3][col] == piece:
                    return True

        # positive diagonal
        for col in range(self.COL_COUNT - self.WINNING_COUNT + 1):
            for row in range(self.WINNING_COUNT - 1, self.ROW_COUNT):
                if self._grid[row][col] == piece and self._grid[row - 1][col + 1] == piece and self._grid[row - 2][col + 2] == piece and self._grid[row - 3][col + 3] == piece:
                    return True

        # negative diagonal
        for col in range(self.COL_COUNT - self.WINNING_COUNT + 1):
            for row in range(self.ROW_COUNT - self.WINNING_COUNT + 1):
                if self._grid[row][col] == piece and self._grid[row + 1][col + 1] == piece and self._grid[row + 2][col + 2] == piece and self._grid[row + 3][col + 3] == piece:
                    return True
        return False

