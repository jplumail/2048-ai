import random


getVector = {0: [-1, 0], 1: [0, 1], 2: [1, 0], 3: [0, -1]}
getDirectionName = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT"}

def init_grid(size):
    grid = [[None] * size for i in range(size)]
    return grid

def setup(grid):
    for i in range(2):
        addRandomTile(grid)

def copy_grid(grid):
    return [[v for v in row] for row in grid]

def addRandomTile(grid):
    if random.random() < 0.9:
        tileValue = 1
    else:
        tileValue = 2
    i, j = chooseRandomAvailableCell(grid)
    if (i,j) is not (None, None):
        insertTile(grid, i, j, tileValue)

def insertTile(grid, i, j, value):
    grid[i][j] = value

def chooseRandomAvailableCell(grid):
    x, y = emptyCells(grid)
    if len(x) == 0:
        return None, None
    i = random.randint(0, len(x) - 1)
    return x[i], y[i]

def emptyCells(grid):
    size = len(grid)
    x, y = [], []
    for i in range(size):
        for j in range(size):
            if not grid[i][j]:
                x.append(i)
                y.append(j)
    return x, y

def isNotFull(grid):
    size = len(grid)
    for i in range(size):
        for j in range(size):
            if not grid[i][j]:
                return True
    return False

def swipe(grid, direction):
    v_x, v_y = getVector[direction]
    order_x, order_y = order(grid, v_x, v_y)
    move(grid, v_x, v_y, order_x, order_y)
    merge(grid, v_x, v_y, order_x, order_y)
    move(grid, v_x, v_y, order_x, order_y)

def order(grid, v_x, v_y):
    size = len(grid)
    orderX = list(range(size))
    orderY = list(range(size))
    if v_x == 1:
        orderX.reverse()
    if v_y == 1:
        orderY.reverse()
    return orderX, orderY

def move(grid, v_x, v_y, order_x, order_y):
    for i in order_x:
        for j in order_y:
            if grid[i][j]:
                moveTile(grid, i, j, v_x, v_y)

def moveTile(grid, pos_x, pos_y, v_x, v_y):
    i, j = pos_x, pos_y
    while isInGrid(grid, i + v_x, j + v_y) and (not grid[i + v_x][j + v_y]):
        i = i + v_x
        j = j + v_y
    tileValue = grid[pos_x][pos_y]
    grid[pos_x][pos_y] = None
    grid[i][j] = tileValue

def merge(grid, v_x, v_y, order_x, order_y):
    for i in order_x:
        for j in order_y:
            if grid[i][j]:
                tileValue = grid[i][j]
                if isInGrid(grid, i - v_x, j - v_y):
                    neighborValue = grid[i - v_x][j - v_y]
                    if neighborValue == tileValue:
                        grid[i][j] = tileValue + 1
                        grid[i - v_x][j - v_y] = None

def isInGrid(grid, i, j):
    size = len(grid)
    return (i < size) and (i >= 0) and (j < size) and (j >= 0)

def show(grid, direction=None):
    size = len(grid)
    if direction is not None:
        print(getDirectionName[direction])
    print("-"*(size*6+2))
    for i in range(size):
        line = "|"
        for j in range(size):
            tile = grid[i][j]
            if tile:
                line += str(2 ** tile).center(6)
            else:
                line += " " * 6
        line += "|"
        print(line)
    print("-"*(size*6+2))

def next(grid, direction):
    possible = possibleMoves(grid)
    if direction in possible:
        swipe(grid, direction)
        addRandomTile(grid)
        over = False
    else:
        over = True
    return over

def possibleMoves(grid):
    possible = set()
    size = len(grid)
    i = 0
    while len(possible) < 4 and i < size:
        j = 0
        while j < size - 1:
            right_not_possible, left_not_possible = 1 not in possible, 3 not in possible
            if right_not_possible or left_not_possible:
                left, right = grid[i][j], grid[i][j + 1]
                if left and (left == right):
                    possible.add(1)
                    possible.add(3)
                elif right_not_possible and left and (not right):
                    possible.add(1)
                elif left_not_possible and (not left) and right:
                    possible.add(3)

            up_not_possible, bottom_not_possible = 0 not in possible, 2 not in possible
            if up_not_possible or bottom_not_possible:
                i, j = j, i
                top, bottom = grid[i][j], grid[i + 1][j]
                if bottom and bottom == top:
                    possible.add(0)
                    possible.add(2)
                elif up_not_possible and bottom and (not top):
                    possible.add(0)
                elif bottom_not_possible and (not bottom) and top:
                    possible.add(2)
                i, j = j, i
            j += 1
        i += 1

    return possible

def getScore(grid):
    return sum([sum([(v-1)*2**v for v in row if v]) for row in grid])

def run(grid, agent, display=False):
    over = False
    if display:
        show(grid)
    while not over:
        direction = agent.play(grid)
        over = next(grid, direction)
        if display:
            show(grid, direction)
            print(possibleMoves(grid))
    final_score = getScore(grid)
    if display:
        print("Game over !\nVotre score : ", final_score)
    return final_score


if __name__ == "__main__":
    from agent import Expectiminimax, MCTS

    g = init_grid(4)
    setup(g)
    a = Expectiminimax(max_depth=4)
    print(run(g, a, display=True))
