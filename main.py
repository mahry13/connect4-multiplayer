
import numpy as np

ROW_COUNT = 6
COL_COUNT = 7

def create_board():
    board = np.zeros((ROW_COUNT, COL_COUNT))
    return board

def get_selection(player):
    while True:
        try:
            selection = int(input(f"Player {player} select (0-6): "))
            if 0 <= selection <= COL_COUNT - 1:
                return selection
        except ValueError:
            pass
        print("Enter a valid number between 0 and 6.")

def drop_piece(board, row, col, piece):
    board[row][col] = piece
    return board

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for i in range(ROW_COUNT - 1, -1, -1):
        if board[i][col] == 0:
            return i


def run():
    board = create_board()
    game_over = False
    turn = 0
    while not game_over:
        player = 1 if turn % 2 == 0 else 2
        col = get_selection(player)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            print(row)
            drop_piece(board, row, col, player)
        print(board)

        turn += 1
        turn = turn % 2



if __name__ == '__main__':
    run()
