import sys
import math
import numpy as np
import time


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

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


class PlayGround:

    def __init__(self) -> None:
        self.playground = np.zeros((3, 3), dtype=int)

    def get_test_playground(self):
        return self.playground.copy()


class MCTS:
    def selection_expansion(self, pground, node: Node) -> Node:
        if not any(0 in subl for subl in pground):
            return node

        if not node.children:
            player = node.player + 1 % 1
            for c in range(3):
                for r in range(3):
                    if pground[r][c] == 0:
                        child = Node(node, (r, c), player)
                        node.children.append(child)

        scores = []
        for child in node.children:
            ucb_score = child.calc_ucb_score()
            if ucb_score == 1000:
                return child
            scores.append(ucb_score)

        next_node_index = -1
        if node.children[0].player % 1 == 0:
            next_node_index = int(np.argmax(scores))
        else:
            next_node_index = int(np.argmin(scores))

        next_node = node.children[next_node_index]
        if next_node.player % 1 == 0:
            pground[next_node.action[0]][next_node.action[1]] = 1
        else:
            pground[next_node.action[0]][next_node.action[1]] = -1

        return self.selection_expansion(pground, next_node)

    def simulate(self, pground, node: Node) -> float:
        while any(0 in subl for subl in pground):
            player = node.player + 1 % 1
            for c in range(3):
                for r in range(3):
                    if pground[r][c] == 0:
                        if player == 0:
                            pground[r][c] = 1
                        else:
                            pground[r][c] = -1
            winner = self.checkVictory(pground)
            if winner != 0:
                return 1 if winner == 1 else 0
        return 0.5

    def checkVictory(self, board) -> int:
        for y in (0, 1, 2):
            if board[0][y] == board[1][y] == board[2][y] and board[0][y] != 0:
                return board[0][y]

        for x in (0, 1, 2):
            if board[x][0] == board[x][1] == board[x][2] and board[x][0] != 0:
                return board[x][0]

        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != 0:
            return board[0][0]

        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != 0:
            return board[0][2]

        return 0

    def backtrack(self, node: Node, reward):
        node.increment_total_plays()
        node.set_reward(reward)
        while node.parent is not None:
            node = node.parent
            node.set_reward(reward)


playground = PlayGround()
# game loop
while True:
    opponent_row, opponent_col = [int(i) for i in input().split()]
    playground.playground[opponent_row][opponent_col] = -1
    valid_action_count = int(input())

    for i in range(valid_action_count):
        row, col = [int(j) for j in input().split()]
        playground.playground[row][col] = 0

    master_node = Node(None, (-1, -1), -1)
    Node.total_plays = 0

    mcts = MCTS()

    start_time = time.time()
    while time.time() - start_time < 0.08:
        test_playground = playground.get_test_playground()
        selected_node = mcts.selection_expansion(test_playground, master_node)
        simulated_reward = mcts.simulate(test_playground, selected_node)
        mcts.backtrack(selected_node, simulated_reward)

    highest_value_move = (0, (-1, -1))
    for master_child in master_node.children:
        if master_child.visited > highest_value_move[0]:
            highest_value_move = (master_child.visited, master_child.action)
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    playground.playground[highest_value_move[1][0]][highest_value_move[1][1]] = 1
    print(str(highest_value_move[1][0]) + " " + str(highest_value_move[1][1]))
