import random
import copy


class Game:
    getVector = {0: [-1, 0], 1: [0, 1], 2: [1, 0], 3: [0, -1]}
    getDirectionName = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT"}

    def __init__(self, size):
        self.size = size
        self.score = 0

    def setup(self):
        self.grid = [[None] * self.size for i in range(self.size)]
        for i in range(2):
            self.addRandomTile()

    def copy(self):
        return copy.deepcopy(self)

    def addRandomTile(self):
        if random.random() < 0.9:
            tileValue = 1
        else:
            tileValue = 2
        cell = self.chooseRandomAvailableCell()
        self.insertTile(cell, tileValue)

    def insertTile(self, cellPosition, value):
        if cellPosition:
            i, j = cellPosition
            self.grid[i][j] = value

    def chooseRandomAvailableCell(self):
        x, y = self.emptyCells()
        if len(x) == 0:
            return None
        i = random.randint(0, len(x) - 1)
        return x[i], y[i]

    def emptyCells(self):
        x, y = [], []
        for i in range(self.size):
            for j in range(self.size):
                if not self.grid[i][j]:
                    x.append(i)
                    y.append(j)
        return x, y

    def isNotFull(self):
        for i in range(self.size):
            for j in range(self.size):
                if not self.grid[i][j]:
                    return True
        return False

    def swipe(self, direction):
        v_x, v_y = Game.getVector[direction]
        order_x, order_y = self.order(v_x, v_y)
        self.move(v_x, v_y, order_x, order_y)
        self.merge(v_x, v_y, order_x, order_y)
        self.move(v_x, v_y, order_x, order_y)

    def order(self, v_x, v_y):
        orderX = list(range(self.size))
        orderY = list(range(self.size))
        if v_x == 1:
            orderX.reverse()
        if v_y == 1:
            orderY.reverse()
        return orderX, orderY

    def move(self, v_x, v_y, order_x, order_y):
        for i in order_x:
            for j in order_y:
                if self.grid[i][j]:
                    self.moveTile(i, j, v_x, v_y)

    def moveTile(self, pos_x, pos_y, v_x, v_y):
        i, j = pos_x, pos_y
        while not (self.isNotInGrid(i + v_x, j + v_y) or self.grid[i + v_x][j + v_y]):
            i = i + v_x
            j = j + v_y
        tileValue = self.grid[pos_x][pos_y]
        self.grid[pos_x][pos_y] = None
        self.grid[i][j] = tileValue

    def merge(self, v_x, v_y, order_x, order_y):
        for i in order_x:
            for j in order_y:
                if self.grid[i][j]:
                    tileValue = self.grid[i][j]
                    if self.isInGrid(i - v_x, j - v_y):
                        neighborValue = self.grid[i - v_x][j - v_y]
                        if neighborValue == tileValue:
                            self.grid[i][j] = tileValue + 1
                            self.score += 2 ** self.grid[i][j]
                            self.grid[i - v_x][j - v_y] = None

    def isInGrid(self, i, j):
        return (i < self.size) and (i >= 0) and (j < self.size) and (j >= 0)

    def isNotInGrid(self, i, j):
        return (i >= self.size) or (i < 0) or (j >= self.size) or (j < 0)

    def display(self, direction):
        print("--------------------------")
        for i in range(self.size):
            line = "|"
            for j in range(self.size):
                tile = self.grid[i][j]
                if tile:
                    line += str(2 ** tile).center(6)
                else:
                    line += " " * 6
            line += "|"
            print(line)
        print("--------------------------")
        print(Game.getDirectionName[direction])

    def equals(self, other):
        if self.size == other.size():
            for i in range(self.size):
                for j in range(self.size):
                    if self.grid[i][j] != other.grid[i][j]:
                        return False
            return True
        else:
            return False

    def next(self, direction):
        possible = self.possibleMoves()
        if direction in possible:
            self.swipe(direction)
            self.addRandomTile()
            return True
        return False

    def possibleMoves(self):
        possible = {}
        i, j = 0, 0
        while len(possible) < 4 and i < self.size and j < self.size - 1:
            right_not_possible, left_not_possible = 1 not in possible, 3 not in possible
            if right_not_possible or left_not_possible:
                left, right = self.grid[i][j], self.grid[i][j + 1]
                if left == right:
                    possible.add(1)
                    possible.add(3)
                elif right_not_possible and left and (not right):
                    possible.add(1)
                elif left_not_possible and (not left) and right:
                    possible.add(3)

            up_not_possible, bottom_not_possible = 0 not in possible, 2 not in possible
            if up_not_possible or bottom_not_possible:
                i, j = j, i
                bottom, top = self.grid[i][j], self.grid[i + 1][j]
                if bottom == top:
                    possible.add(0)
                    possible.add(2)
                elif up_not_possible and bottom and (not top):
                    possible.add(0)
                elif bottom_not_possible and (not left) and right:
                    possible.add(2)
                i, j = j, i
            i += 1
            j += 1

        return possible

    def run(self, agent, display=False):
        over = False
        while not over:
            direction = agent.play(self)
            over = self.next(direction)
            if display:
                self.display(direction)
        if display:
            self.display(direction)
            print("Game over !\nVotre score : ", self.score)
        return self.score


if __name__ == "__main__":
    from agent import Human

    g = Game(4)
    g.setup()
    dumb_agent = Human("Jean")
    print(g.run(dumb_agent, display=True))
