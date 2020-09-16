from game import Game
import random
from time import time
import math


class Agent:
    def play(self, game: Game) -> int:
        pass


class Human(Agent):
    def __init__(self, name):
        print("Bonjour {} !".format(name))

    def play(self, game):
        inputs_to_dir = {8: 0, 6: 1, 2: 2, 4: 3}
        return inputs_to_dir[int(input())]


class Dummy(Agent):
    def __init__(self):
        pass

    def play(self, game):
        moves = list(game.possibleMoves())
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

    def play(self, game):
        # Monte-Carlo Tree : [sum of scores, number of simulations, game state, dict of children]
        self.tree = {None: [0, 0, game.copy(), {}]}
        t0 = time()
        while (time() - t0) < self.timeout:
            list_moves = self.selection()
            leaf = self.getNode(list_moves)
            if self.expansion(leaf):
                list_moves += [list(leaf[3])[0]]
                new_leaf = self.getNode(list_moves)
                leaf_score = self.simulation(new_leaf)
                self.backpropagation(list_moves, leaf_score)

        root = self.tree[None]
        best_move = None
        max_avg_score = 0
        for move in list(root[3]):
            child = root[3][move]
            #print(move, " : ", child[0] / (1 + child[1]))
            if child[0] / (1 + child[1]) > max_avg_score:
                max_avg_score = child[0] / (1 + child[1])
                best_move = move
        #print(self.getDepth(self.tree[None]))
        #print("Number of Monte Carlo simulations : ", self.tree[None][1])

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
        if len(node[3]) > 0:
            print("Erreur, le noeud a déjà des enfants")
        game = node[2]
        for move in game.possibleMoves():
            next_game = game.copy()
            node[3][move] = [0, 0, next_game, {}]
        return len(node[3]) > 0

    def simulation(self, node):
        game = node[2].copy()
        score = game.run(self.dummy)
        return score

    def backpropagation(self, list_moves, score):
        node = self.tree[None]
        for move in list_moves:
            node[0] += score
            node[1] += 1
            node = node[3][move]
        node[0] += score
        node[1] += 1