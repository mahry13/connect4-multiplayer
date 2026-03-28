
import numpy as np

ROW_COUNT = 6
COL_COUNT = 7
WINNING_COUNT = 4
PLAYER_ONE = 1
PLAYER_TWO = 2


def create_board():
    board = np.zeros((ROW_COUNT, COL_COUNT), dtype=int)
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


def winning_move(board, piece):
    # horizontal
    for col in range(COL_COUNT - WINNING_COUNT + 1):
        for row in range(ROW_COUNT):
            if board[row][col] == piece and board[row][col + 1] == piece and board[row][col + 2] == piece and board[row][col + 3] == piece:
                return True

    # vertical
    for col in range(COL_COUNT):
        for row in range(ROW_COUNT - WINNING_COUNT + 1):
            if board[row][col] == piece and board[row + 1][col] == piece and board[row + 2][col] == piece and board[row + 3][col] == piece:
                return True

    # positive diagonal
    for col in range(COL_COUNT - WINNING_COUNT + 1):
        for row in range(WINNING_COUNT - 1, ROW_COUNT):
            if board[row][col] == piece and board[row - 1][col + 1] == piece and board[row - 2][col + 2] == piece and board[row - 3][col + 3] == piece:
                return True

    # negative diagonal
    for col in range(COL_COUNT - WINNING_COUNT + 1):
        for row in range(ROW_COUNT - WINNING_COUNT + 1):
            if board[row][col] == piece and board[row + 1][col + 1] == piece and board[row + 2][col + 2] == piece and board[row + 3][col + 3] == piece:
                return True
    return False


def is_board_full(board):
    return not np.any(board == 0)


def run():
    board = create_board()
    game_over = False
    turn = 0
    while not game_over:
        player = PLAYER_ONE if turn % 2 == 0 else PLAYER_TWO
        col = get_selection(player)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, player)
            if winning_move(board, player):
                print(f"Player {player} won!")
                game_over = True
        else:
            print("Column is full. Try another one.")
            continue

        if is_board_full(board):
            print("It's a draw!")
            game_over = True

        print(board)

        turn += 1
        turn = turn % 2



if __name__ == '__main__':
    run()
