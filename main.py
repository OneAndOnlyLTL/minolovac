import pygame as pg
import random
pg.init()

WIDTH = 800
HEIGTH = 800
SIZE = 28
row, column = 24, 24
tot_mines = 60
left_mines = tot_mines
STARTX, STARTY = (WIDTH - SIZE * column) // 2, (HEIGTH - SIZE * row) // 2 
BACKGROUND = (100, 200, 200)
dx, dy = [0, 0, -1, 1, -1, 1, -1, 1], [-1, 1, 0, 0, 1, 1, -1, -1]
grid = [[0] * column for i in range(row)]
mines = [[0] * column for i in range(row)]
flags = [[0] * column for i in range(row)]
known = [[0] * column for i in range(row)]

screen = pg.display.set_mode((WIDTH, HEIGTH))
pg.display.set_caption("MINESWEEPER")
fontBIG = pg.font.Font('freesansbold.ttf', 104)
fontMED = pg.font.Font('freesansbold.ttf', 52)
fontSMALL = pg.font.Font('freesansbold.ttf', 36)
fontXS = pg.font.Font('freesansbold.ttf', 26)
BIG = 104
SMALL = 52
win_txt = fontBIG.render('WIN!', False, 'black')
loser = fontBIG.render('LOSER!', False, 'black')
txt = fontMED.render('Click anywhere to play again.', False, 'black')
clock = pg.time.Clock()
dt = 0

pictures = []
for i in range(12):
    pictures.append(pg.transform.scale(pg.image.load('img/broj' + str(i) + '.png'), (SIZE, SIZE)))

def check(i, j, endi, endj) -> bool:
    if i >= 0 and j >= 0 and i < endi and j < endj:
        return True
    return False

def location():
    if not check(mouse['x'] - STARTX, mouse['y'] - STARTY, SIZE * column, SIZE * row):
        return -1, -1
    i = (mouse['x'] - STARTX) // SIZE
    j = (mouse['y'] - STARTY) // SIZE
    return i, j

def restart():
    global grid, mines, flags, known, playing, dt, tot_mines, column, row, pictures, running, STARTX, STARTY, SIZE
    screen.fill(BACKGROUND)
    tekst = fontSMALL.render("Kliknite broj od 1-3 za odgovarajucu tezinu.", False, 'black')
    screen.blit(tekst, (20, 350))
    pg.display.flip()
    while True:
        st = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                playing = False
                running = False
                st = True
                return True
            if event.type == pg.KEYUP and event.key == pg.K_1:
                tot_mines = 15
                row, column = 8, 8
                SIZE = 35
                st = True
                break
            if event.type == pg.KEYUP and event.key == pg.K_2:
                tot_mines = 40
                row, column = 16, 16
                SIZE = 30
                st = True
                break
            if event.type == pg.KEYUP and event.key == pg.K_3:
                tot_mines = 75
                row, column = 24, 24
                SIZE = 22
                st = True
                break
        
        if st:
            pictures = []
            for i in range(12):
                pictures.append(pg.transform.scale(pg.image.load('img/broj' + str(i) + '.png'), (SIZE, SIZE)))
            STARTX, STARTY = (WIDTH - SIZE * column) // 2, (HEIGTH - SIZE * row) // 2 
            break

        dt = clock.tick(60) / 1000
    grid = [[0] * column for i in range(row)]
    mines = [[0] * column for i in range(row)]
    flags = [[0] * column for i in range(row)]
    known = [[0] * column for i in range(row)]
    return False

def drawGrid():
    for i in range(row):
        for j in range(column):
            if known[i][j]:
                screen.blit(pictures[grid[i][j]], (STARTX + SIZE * i, STARTY + SIZE * j))
            else:
                screen.blit(pictures[9], (STARTX + SIZE * i, STARTY + SIZE * j))
            if mines[i][j] == 1 and known[i][j] == 1:
                screen.blit(pictures[11], (STARTX + SIZE * i, STARTY + SIZE * j))
            if flags[i][j] == 1:
                screen.blit(pictures[10], (STARTX + SIZE * i, STARTY + SIZE * j))

def generateMines():
    global mines
    for i in range(tot_mines):
        x, y = random.randint(0, row - 1), random.randint(0, column - 1)
        while mines[x][y] != 0:
            x, y = random.randint(0, row - 1), random.randint(0, column - 1)
        mines[x][y] = 1

def generateGrid():
    global grid
    for i in range(row):
        for j in range(column):
            if mines[i][j] == 1:
                continue
            for k in range(8):
                ci, cj = i + dx[k], j + dy[k]
                if check(ci, cj, row, column) and mines[ci][cj] == 1:
                    grid[i][j] += 1

def BFS(i, j):
    global known
    queue = []
    if grid[i][j] == 0:
        queue.append((i, j))
    known[i][j] = 1
    visited = [[0] * column for i in range(row)]
    while len(queue):
        x, y = queue[0][0], queue[0][1]
        queue.pop(0) 
        for k in range(8):
            cx, cy = x + dx[k], y + dy[k]
            if check(cx, cy, row, column) and (visited[cx][cy] == 0):
                visited[cx][cy] = 1
                if mines[i][j] == 1 or flags[i][j] == 1:
                    continue
                known[cx][cy] = 1
                if grid[cx][cy] == 0:
                    queue.append((cx, cy))

def firstClick():
    global first
    if not mouse['left']:
        return
    if mouse['x'] - STARTX < 0 or mouse['y'] - STARTY < 0 or mouse['x'] - STARTX > SIZE * row or mouse['y'] - STARTX > SIZE * column:
        return
    i = (mouse['x'] - STARTX) // SIZE
    j = (mouse['y'] - STARTY) // SIZE
    mines[i][j] = -1
    for k in range(8):
        ci, cj = i + dy[k], j + dx[k]
        if check(ci, cj, row, column):
            mines[ci][cj] = -1
    generateMines()
    generateGrid()
    BFS(i, j)
    first = False

def lose():
    global running
    for i in range(row):
        for j in range(column):
            known[i][j] = 1
            flags[i][j] = 0
    screen.fill(BACKGROUND)
    drawGrid()
    screen.blit(loser, (205, 45))
    screen.blit(txt, (20, 670))
    running = False

def winChecker():
    for i in range(row):
        for j in range(column):
            if  not (known[i][j] == 1 and mines[i][j] != 1) and not (known[i][j] == 0 and mines[i][j] == 1):
                return False
    return True

def win():
    global running
    for i in range(row):
        for j in range(column):
            known[i][j] = 1
            flags[i][j] = 0
    screen.fill(BACKGROUND)
    drawGrid()
    screen.blit(win_txt, (270, 45))
    screen.blit(txt, (20, 670))
    running = False


def leftClick(i, j):
    if mines[i][j] == 1 and flags[i][j] == 0:
        lose()
    elif flags[i][j] == 0:
        if known[i][j] == 0:
            BFS(i, j)
        else:
            for k in range(8):
                ci, cj = i + dy[k], j + dx[k]
                if check(ci, cj, row, column) and flags[ci][cj] == 0 and known[ci][cj] == 0:
                    leftClick(ci, cj)

def rightClick(i, j):
    global left_mines
    if known[i][j] == 0 and flags[i][j] == 0:
        flags[i][j] = 1
        left_mines -= 1
    elif known[i][j] == 0 and flags[i][j] == 1:
        flags[i][j] = 0
        left_mines += 1


playing = True
while playing:      
    running = True
    first = True
    if restart():
        break
    dt = 0
    left_mines = tot_mines
    while running:
        screen.fill(BACKGROUND)
        drawGrid()
        second_txt = fontXS.render('Sekunde:' + str(int(dt)), False, 'black')
        screen.blit(second_txt, (0, 0))
        mines_txt = fontXS.render('Ostalo mina: ' + str(left_mines), False, 'black')
        screen.blit(mines_txt, (0, 30))
        mouse = {
            "x": pg.mouse.get_pos()[0],
            "y": pg.mouse.get_pos()[1],
            "left": pg.mouse.get_pressed()[0],
            "right": pg.mouse.get_pressed()[2]
        }

        while first:
            screen.fill(BACKGROUND)
            drawGrid()
            mouse = {
                "x": pg.mouse.get_pos()[0],
                "y": pg.mouse.get_pos()[1],
                "left": pg.mouse.get_pressed()[0],
                "right": pg.mouse.get_pressed()[2]
            }
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    playing = False
                    running = False
                    first = False
                if event.type == pg.MOUSEBUTTONUP:
                    firstClick()
            dt = clock.tick(60) / 1000
            pg.display.flip()

        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                playing = False
            if event.type == pg.MOUSEBUTTONUP:
                if mouse['left']:
                    i, j = location()
                    if i != -1:
                        leftClick(i, j)
                elif mouse['right']:
                    i, j = location()
                    if i != -1:
                        rightClick(i, j)
        if winChecker():
            win()
        dt += clock.tick(60) / 1000
        pg.display.flip()
    while True:
        st = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                playing = False
                st = True
                break
            if event.type == pg.MOUSEBUTTONUP:
                st = True
                break
        if st:
            break
        dt = clock.tick(60) / 1000