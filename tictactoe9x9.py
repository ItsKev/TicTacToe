import copy
import sys

import numpy as np
import math
import time


class Node:
    total_plays = 0
    c = 1

    def __init__(self, parent, action: (int, int), player: int) -> None:
        self.parent = parent
        self.children = []
        self.action = action
        self.visited = 0
        self.reward = 0
        self.player = player

    def set_reward(self, reward):
        self.reward += reward
        self.visited += 1

    def increment_total_plays(self):
        Node.total_plays += 1

    def calc_ucb_score(self) -> float:
        if self.visited == 0:
            return 1000
        return self.reward / self.visited + Node.c * np.sqrt(np.log(Node.total_plays) / self.visited)


class Board:
    def __init__(self) -> None:
        self.playground = np.zeros((9, 9), dtype=int)
        self.playground_grid = np.zeros((3, 3), dtype=int)
        self.playground_next_board_size = 9
        self.playground_next_row_col = (0, 0)


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
        is_full = True
        for c in range(3):
            for r in range(3):
                if board.playground[next_row + r][next_col + c] == 0:
                    is_full = False
                    break
        if is_full:
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

    def selection_expansion(self, board: Board, node: Node) -> Node:
        plays_left = False
        next_row, next_col = board.playground_next_row_col
        for row in range(board.playground_next_board_size):
            for col in range(board.playground_next_board_size):
                if board.playground[row + next_row][col + next_col] == 0:
                    plays_left = True
                    break
        if not plays_left:
            print("No plays left", file=sys.stderr)
            return node

        if not node.children:
            player = node.player + 1 % 2
            for row in range(board.playground_next_board_size):
                for col in range(board.playground_next_board_size):
                    if board.playground[row + next_row][col + next_col] == 0:
                        child = Node(node, (row + next_row, col + next_col), player)
                        node.children.append(child)

        scores = []
        for child in node.children:
            ucb_score = child.calc_ucb_score()
            if ucb_score == 1000:
                return child
            scores.append(ucb_score)

        next_node_index = -1
        if node.children[0].player == 0:
            next_node_index = int(np.argmax(scores))
        else:
            next_node_index = int(np.argmin(scores))

        next_node = node.children[next_node_index]
        if next_node.player == 0:
            board.playground[next_node.action[0]][next_node.action[1]] = 1
        else:
            board.playground[next_node.action[0]][next_node.action[1]] = -1

        next_playground = Helper.get_next_playground(board, next_node.action[0], next_node.action[1])
        if next_playground == (-1, -1):
            board.playground_next_board_size = 9
            board.playground_next_row_col = (0, 0)
        else:
            board.playground_next_board_size = 3
            board.playground_next_row_col = next_playground

        return self.selection_expansion(board, next_node)

    def simulate(self, board: Board, node: Node) -> float:
        lastrow, lastcol = node.action
        player = node.player
        Helper.lock_won_playgrounds(board)
        while any(0 in subl for subl in board.playground):
            next_play = Helper.get_next_playground(board, lastrow, lastcol)
            winner = Helper.checkVictory(board.playground_grid, 0, 0)
            if winner != 0:
                return 1 if winner == 1 else 0
            player = (player + 1) % 2
            if next_play == (-1, -1):
                last_play = self.play_random_position(board, player, 9, 0, 0)
            else:
                last_play = self.play_random_position(board, player, 3, next_play[0], next_play[1])
            if last_play != (-1, -1):
                lastrow = last_play[0]
                lastcol = last_play[1]
            else:
                break
        return 0.5

    def play_random_position(self, board, player, size, next_row, next_col) -> (int, int):
        for col in range(size):
            for row in range(size):
                if board.playground[next_row + row][next_col + col] == 0:
                    if player == 0:
                        board.playground[next_row + row][next_col + col] = 1
                    else:
                        board.playground[next_row + row][next_col + col] = -1
                    return next_row + row, next_col + col
        return -1, -1

    def backtrack(self, node: Node, reward):
        node.increment_total_plays()
        node.set_reward(reward)
        while node.parent is not None:
            node = node.parent
            node.set_reward(reward)


class Main:

    def __init__(self) -> None:
        board = Board()
        # game loop
        while True:
            opponent_row, opponent_col = [int(i) for i in input().split()]

            if opponent_row != -1:
                board.playground[opponent_row][opponent_col] = -1
                next_playground = Helper.get_next_playground(board, opponent_row, opponent_col)
                if next_playground == (-1, -1):
                    board.playground_next_board_size = 9
                    board.playground_next_row_col = (0, 0)
                else:
                    board.playground_next_board_size = 3
                    board.playground_next_row_col = next_playground

            valid_action_count = int(input())
            for i in range(valid_action_count):
                _, _ = [int(j) for j in input().split()]

            Helper.lock_won_playgrounds(board)

            master_node = Node(None, (-1, -1), -1)
            Node.total_plays = 0

            mcts = MCTS()

            start_time = time.time()
            while time.time() - start_time < 0.09:
                test_playground = copy.deepcopy(board)
                selected_node = mcts.selection_expansion(test_playground, master_node)
                simulated_reward = mcts.simulate(test_playground, selected_node)
                mcts.backtrack(selected_node, simulated_reward)

            highest_value_move = (-1, (-1, -1))
            for master_child in master_node.children:
                if master_child.visited > highest_value_move[0]:
                    highest_value_move = (master_child.visited, master_child.action)

            # Write an action using print
            # To debug: print("Debug messages...", file=sys.stderr)

            print(master_node.visited, file=sys.stderr)
            board.playground[highest_value_move[1][0]][highest_value_move[1][1]] = 1
            Helper.lock_won_playgrounds(board)
            print(str(highest_value_move[1][0]) + " " + str(highest_value_move[1][1]))


if __name__ == '__main__':
    Main()
