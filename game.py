import numpy as np
import random
import copy


class Game():
    getVector = {0: [-1, 0], 1: [0, 1], 2: [1, 0], 3: [0, -1]}
    getDirectionName = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT"}

    def __init__(self, size):
        self.size = size
        self.score = 0

    def setup(self):
        self.grid = np.zeros((self.size, self.size), dtype=np.uint8)
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
            self.grid[i, j] = value

    def chooseRandomAvailableCell(self):
        x, y = self.emptyCells()
        if len(x) == 0:
            return None
        i = random.randint(0,len(x)-1)
        return x[i], y[i]

    def emptyCells(self):
        x, y = (self.grid == 0).nonzero()
        return x, y

    def isNotFull(self):
        return (self.grid == 0).any()

    def swipe(self, direction):
        v_x, v_y = Game.getVector[direction]
        order_x, order_y = self.order(v_x, v_y)
        moved1 = self.move(v_x, v_y, order_x, order_y)
        moved2 = self.merge(v_x, v_y, order_x, order_y)
        moved3 = self.move(v_x, v_y, order_x, order_y)
        return (moved1 or moved2 or moved3)

    def order(self, v_x, v_y):
        orderX = list(range(self.size))
        orderY = list(range(self.size))
        if v_x == 1:
            orderX.reverse()
        if v_y == 1:
            orderY.reverse()
        return orderX, orderY

    def move(self, v_x, v_y, order_x, order_y):
        moved = False
        for i in order_x:
            for j in order_y:
                if self.grid[i, j] != 0:
                    m = self.moveTile(i, j, v_x, v_y)
                    moved = moved or m
        return moved

    def moveTile(self, pos_x, pos_y, v_x, v_y):
        i, j = pos_x, pos_y
        moved = False
        while not (
            self.isNotInGrid(i + v_x, j + v_y)
            or self.grid[i + v_x, j + v_y] > 0
        ):
            i = i + v_x
            j = j + v_y
            moved = True
        tileValue = self.grid[pos_x, pos_y]
        self.grid[pos_x, pos_y] = 0
        self.grid[i, j] = tileValue
        return moved

    def merge(self, v_x, v_y, order_x, order_y):
        moved = False
        for i in order_x:
            for j in order_y:
                if self.grid[i, j] != 0:
                    tileValue = self.grid[i, j]
                    if self.isInGrid(i - v_x, j - v_y):
                        neighborValue = self.grid[i - v_x, j - v_y]
                        if neighborValue == tileValue:
                            self.grid[i, j] = tileValue + 1
                            self.score += 2**self.grid[i, j]
                            self.grid[i - v_x, j - v_y] = 0
                            moved = True
        return moved

    def isInGrid(self, i, j):
        return (i < self.size) and (i >= 0) and (j < self.size) and (j >= 0)

    def isNotInGrid(self, i, j):
        return (i >= self.size) or (i < 0) or (j >= self.size) or (j < 0)

    def display(self, direction):

        powered = np.power(2,self.grid.astype(np.uint64))
        print(powered - (powered == 1))
        print(Game.getDirectionName[direction])

    def equals(self, other):
        return (self.grid == other.grid).all()

    def next(self, direction):
        moved = self.swipe(direction)
        if moved:
            self.addRandomTile()
        return moved

    def isOver(self):
        if not self.isNotFull():
            for i in range(4):
                g2 = self.copy()
                moved = g2.next(i)
                if moved:
                    return False
            return True
        return False

    def run(self, agent, display=False):
        while not self.isOver():
            direction = agent.play(self)
            if display:
                self.display(direction)
            self.next(direction)
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
