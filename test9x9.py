import numpy as np
import math


class Board:
    def __init__(self) -> None:
        self.playground = np.zeros((9, 9), dtype=int)
        self.playground_grid = np.zeros((3, 3), dtype=int)
        self.playground[0][5] = -1
        self.playground[0][4] = -1
        self.playground[0][3] = -1
        self.playground[3][5] = 1
        self.playground[4][4] = 1
        self.playground[5][3] = 1
        self.playground[3][0] = 1
        self.playground[4][0] = 1
        self.playground[5][0] = 1
        self.playground[7][8] = 1
        self.playground[7][7] = 1
        self.playground[7][6] = 1


class Helper:

    @staticmethod
    def get_next_playground(board: Board, lastrow, lastcol) -> (int, int):
        if lastrow == -1 and lastcol == -1:
            return -1, -1
        row_grid = int(lastrow / 3)
        col_grid = int(lastcol / 3)
        row = row_grid * 3
        col = col_grid * 3

        next_row = lastrow % 3 * 3
        next_col = lastcol % 3 * 3

        victory = Helper.checkVictory(board.playground, row, col)
        if victory != 0:
            board.playground_grid[row_grid][col_grid] = victory
            for c in range(3):
                for r in range(3):
                    if board.playground[row + r][col + c] == 0:
                        board.playground[row + r][col + c] = 2
        if board.playground_grid[int(next_row / 3)][int(next_col / 3)] != 0:
            return -1, -1
        return next_row, next_col

    @staticmethod
    def lock_won_playgrounds(board):
        for row in range(0, 8, 3):
            for col in range(0, 8, 3):
                rowgrid = int(row / 3)
                rowcol = int(col / 3)
                victory = Helper.checkVictory(board.playground, row, col)
                if victory != 0:
                    board.playground_grid[rowgrid][rowcol] = victory
                    for c in range(3):
                        for r in range(3):
                            if board.playground[row + r][col + c] == 0:
                                board.playground[row + r][col + c] = 2

    @staticmethod
    def checkVictory(board, row, col) -> int:
        for y in (0, 1, 2):
            if board[row + 0][col + y] == board[row + 1][col + y] == board[row + 2][col + y] \
                    and board[row + 0][col + y] != 0:
                return board[row + 0][col + y]

        for x in (0, 1, 2):
            if board[row + x][col + 0] == board[row + x][col + 1] == board[row + x][col + 2] \
                    and board[row + x][col + 0] != 0:
                return board[row + x][col + 0]

        if board[row + 0][col + 0] == board[row + 1][col + 1] == board[row + 2][col + 2] \
                and board[row + 0][col + 0] != 0:
            return board[row + 0][col + 0]

        if board[row + 0][col + 2] == board[row + 1][col + 1] == board[row + 2][col + 0] \
                and board[row + 0][col + 2] != 0:
            return board[row + 0][col + 2]

        return 0


class MCTS:

    def simulate(self, board: Board, lastrow, lastcol, player) -> int:
        Helper.lock_won_playgrounds(board)
        victory = Helper.checkVictory(board.playground_grid, 0, 0)
        while victory == 0:
            next_play = Helper.get_next_playground(board, lastrow, lastcol)
            victory = Helper.checkVictory(board.playground_grid, 0, 0)
            player = (player + 1) % 2
            if next_play == (-1, -1):
                last_play = self.play_random_position(board, player, 9, 0, 0)
            else:
                last_play = self.play_random_position(board, player, 3, next_play[0], next_play[1])
            lastrow = last_play[0]
            lastcol = last_play[1]
        return victory

    def play_random_position(self, board, player, size, next_row, next_col) -> (int, int):
        for col in range(size):
            for row in range(size):
                if board.playground[next_row + row][next_col + col] == 0:
                    if player == 0:
                        board.playground[next_row + row][next_col + col] = 1
                    else:
                        board.playground[next_row + row][next_col + col] = -1
                    return next_row + row, next_col + col


class Main:

    def __init__(self) -> None:
        board = Board()
        mcts = MCTS()
        mcts.simulate(board, -1, -1, 0)


if __name__ == '__main__':
    Main()
