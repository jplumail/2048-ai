import game
import random
from time import time
import math


class Agent:
    def play(self, grid: list) -> int:
        pass


class Human(Agent):
    def __init__(self, name):
        print("Bonjour {} !".format(name))

    def play(self, grid):
        inputs_to_dir = {8: 0, 6: 1, 2: 2, 4: 3}
        return inputs_to_dir[int(input())]


class Dummy(Agent):
    def __init__(self):
        pass

    def play(self, grid):
        moves = list(game.possibleMoves(grid))
        if len(moves) > 0:
            return random.choice(moves)
        else:
            return 0


class MCTS(Agent):
    def __init__(self, timeout=0.5, UCT_param=1000):
        self.tree = {}
        self.prev_tree = None
        self.dummy = Dummy()
        self.timeout = timeout
        self.UCT_param = UCT_param

    def play(self, grid):
        # Monte-Carlo Tree : [sum of scores, number of simulations, game state, dict of children]
        self.tree = {None: [0, 0, game.copy_grid(grid), {}]}
        t0 = time()
        i = 0
        while (time() - t0) < self.timeout:
            list_moves = self.selection()
            leaf = self.getNode(list_moves)
            if self.expansion(leaf):
                list_moves += [list(leaf[3])[0]]
                new_leaf = self.getNode(list_moves)
                leaf_score = self.simulation(new_leaf)
                self.backpropagation(list_moves, leaf_score)
                i += 1
        print("Number of sim : ", i)

        root = self.tree[None]
        best_move = None
        max_avg_score = 0
        for move in list(root[3]):
            child = root[3][move]
            if child[0] / (1 + child[1]) > max_avg_score:
                max_avg_score = child[0] / (1 + child[1])
                best_move = move

        return best_move

    def getDepth(self, root):
        children = root[3]
        if len(children) == 0:
            return 1
        else:
            return 1 + max([self.getDepth(children[t]) for t in children])

    def getNode(self, list_moves):
        node = self.tree[None]
        for move in list_moves:
            node = node[3][move]
        return node

    def selection(self):
        list_moves = []
        node = self.tree[None]
        # print("------------------")
        j = 0
        while len(node[3]) > 0:  # while the node has children
            children = node[3]
            max_uct = 0
            # print("Level : ", j)
            j += 1
            for i in children:
                uct = self.UCT(node, children[i])
                # print(uct)
                if uct > max_uct:
                    best_child = i
                    max_uct = uct
            node = children[best_child]
            list_moves.append(best_child)
        return list_moves

    def UCT(self, father, child):
        if child[1] == 0:
            return math.inf
        else:
            return (
                child[0] / child[1]
                + self.UCT_param * (math.log(father[1]) / child[1]) ** 0.5
            )

    def expansion(self, node):
        grid = node[2]
        for move in game.possibleMoves(grid):
            next_grid = game.copy_grid(grid)
            node[3][move] = [0, 0, next_grid, {}]
        return len(node[3]) > 0

    def simulation(self, node):
        grid = game.copy_grid(node[2])
        score = game.run(grid, self.dummy)
        return score

    def backpropagation(self, list_moves, score):
        node = self.tree[None]
        for move in list_moves:
            node[0] += score
            node[1] += 1
            node = node[3][move]
        node[0] += score
        node[1] += 1


class MCTS2(Agent):
    def __init__(self, max_iter=10):
        self.max_iter = max_iter
        self.dummy = Dummy()

    def play(self, grid):
        moves = game.possibleMoves(grid)
        i = 0
        scores = [0] * 4
        while i < self.max_iter:
            for move in moves:
                new_grid = game.copy_grid(grid)
                game.next(new_grid, move)
                scores[move] += game.run(new_grid, self.dummy)
            i += 1
        max_score = 0
        best_move = 0
        for move, score in enumerate(scores):
            if score > max_score:
                max_score = score
                best_move = move

        return best_move


class Expectiminimax(Agent):
    def __init__(self, max_depth=4):
        self.max_depth = max_depth

    def play(self, grid):
        root = {"random_event": False, "game_state": grid}
        best_move, _ = self.expectiminimax(root, 0)
        if best_move is None:
            best_move = 0
        return best_move

    def randomEvents(self, grid):
        x, y = game.emptyCells(grid)
        n = len(x)
        children = []
        for i, j in zip(x, y):
            g1 = game.copy_grid(grid)
            g2 = game.copy_grid(grid)
            g1[i][j] = 1
            g2[i][j] = 2
            children.append((0.9 / n, {"random_event": False, "game_state": g1}))
            children.append((0.1 / n, {"random_event": False, "game_state": g2}))
        return children

    def heuristic(self, grid):
        """https://github.com/nneonneo/2048-ai/blob/master/2048.cpp
        SCORE_LOST_PENALTY = 200000
        SCORE_MONOTONICITY_POWER = 4
        SCORE_MONOTONICITY_WEIGHT = 47
        SCORE_SUM_POWER = 3.5
        SCORE_SUM_WEIGHT = 11
        SCORE_MERGES_WEIGHT = 700
        SCORE_EMPTY_WEIGHT = 270"""
        
        return game.getScore(grid)

    def expectiminimax(self, node, depth):
        if depth == self.max_depth:
            return None, self.heuristic(node["game_state"])
        if node["random_event"]:
            possible_game_states = self.randomEvents(node["game_state"])
            alpha = 0
            for probability, child_node in possible_game_states:
                alpha += probability * self.expectiminimax(child_node, depth + 1)[1]
            return None, alpha
        else:
            moves = game.possibleMoves(node["game_state"])
            if len(moves) == 0:
                return None, self.heuristic(node["game_state"])
            else:
                moves = game.possibleMoves(node["game_state"])
                alpha = -1
                for move in moves:
                    grid = game.copy_grid(node["game_state"])
                    game.swipe(grid, move)
                    child_node = {"random_event": True, "game_state": grid}
                    _, alpha_child = self.expectiminimax(child_node, depth + 1)
                    if alpha_child > alpha:
                        alpha = alpha_child
                        best_move = move
                return best_move, alpha

