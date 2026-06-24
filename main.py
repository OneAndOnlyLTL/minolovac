import pygame as pg
import random

pg.init()

WIDTH = 800
HEIGHT = 800
belo = (255, 255, 255)
HUD = 80

nivoi = {
    1: (8, 8, 15, 70),
    2: (16, 16, 40, 40),
    3: (24, 24, 75, 30),
}

red, kolona, brojmina, SIZE = nivoi[3]

STARTX, STARTY = 0, 0

dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("minolovac")
#I was doing this for the first time, so I had to look up (and basically copy) this stuff
font1 = pg.font.SysFont("segoeui", 96)
font2 = pg.font.SysFont("segoeui", 48)
font3 = pg.font.SysFont("segoeui", 22)

win_txt = font1.render("pobeda", True, "black")
loser = font1.render("ajde opet :<", True, "black")

clock = pg.time.Clock()

pictures = []
grid = []
mines = []
flags = []
known = []

playing = True
running = True
first = True
brojostale = brojmina
kraj = None   

def rebuild_pictures():
    global pictures
    pictures = []
    for i in range(12):
        pictures.append(
            pg.transform.scale(
                pg.image.load("img/broj" + str(i) + ".png"),
                (SIZE, SIZE)
            )
        )

def reset_board():
    global grid, mines, flags, known
    grid = [[0] * kolona for _ in range(red)]
    mines = [[0] * kolona for _ in range(red)]
    flags = [[0] * kolona for _ in range(red)]
    known = [[0] * kolona for _ in range(red)]

def update_layout():
    global STARTX, STARTY
    STARTX = (WIDTH - SIZE * kolona) // 2
    STARTY = (HEIGHT - SIZE * red) // 2 + HUD // 2

def center_blit(text_surface, y):
    x = (WIDTH - text_surface.get_width()) // 2
    screen.blit(text_surface, (x, y))

def check(r, c, R, C):
    return 0 <= r < R and 0 <= c < C

def location(pos):
    x, y = pos
    r = (y - STARTY) // SIZE
    c = (x - STARTX) // SIZE
    if not check(r, c, red, kolona):
        return -1, -1
    return r, c

def generateMines(safe):
    global mines
    safe = set(safe)

    while True:
        for r in range(red):
            for c in range(kolona):
                mines[r][c] = 0

        candidates = [(r, c) for r in range(red) for c in range(kolona) if (r, c) not in safe]
        if len(candidates) < brojmina:
            raise ValueError("Too many mines for the current safe zone")

        random.shuffle(candidates)
        for r, c in candidates[:brojmina]:
            mines[r][c] = 1

        if any(mines[r][c] for r, c in safe):
            continue

        return

def generateGrid():
    for r in range(red):
        for c in range(kolona):
            if mines[r][c]:
                continue
            count = 0
            for k in range(8):
                rr, cc = r + dx[k], c + dy[k]
                if check(rr, cc, red, kolona) and mines[rr][cc]:
                    count += 1
            grid[r][c] = count

def count_flags(r, c):
    cnt = 0
    for k in range(8):
        rr, cc = r + dx[k], c + dy[k]
        if check(rr, cc, red, kolona) and flags[rr][cc]:
            cnt += 1
    return cnt

def reveal(r, c):
    q = [(r, c)]
    vis = [[0] * kolona for _ in range(red)]
    vis[r][c] = 1

    while q:
        x, y = q.pop(0)
        if flags[x][y]:
            continue
        known[x][y] = 1

        if grid[x][y] != 0:
            continue

        for k in range(8):
            rr, cc = x + dx[k], y + dy[k]
            if check(rr, cc, red, kolona) and not vis[rr][cc]:
                vis[rr][cc] = 1
                q.append((rr, cc))


def firstClick(pos):
    global first

    r, c = location(pos)
    if r == -1:
        return

    safe = {(r, c)}
    for k in range(8):
        rr, cc = r + dx[k], c + dy[k]
        if check(rr, cc, red, kolona):
            safe.add((rr, cc))

    generateMines(safe)
    generateGrid()
    reveal(r, c)
    first = False

def winChecker():
    for r in range(red):
        for c in range(kolona):
            if not mines[r][c] and not known[r][c]:
                return False
    return True

def lose():
    global running, kraj
    for r in range(red):
        for c in range(kolona):
            known[r][c] = 1
    kraj = "lose"
    running = False

def win():
    global running, kraj
    for r in range(red):
        for c in range(kolona):
            known[r][c] = 1
    kraj = "win"
    running = False

def leftClick(r, c):
    if known[r][c]:
        if grid[r][c] > 0 and count_flags(r, c) == grid[r][c]:
            for k in range(8):
                rr, cc = r + dx[k], c + dy[k]
                if check(rr, cc, red, kolona) and not flags[rr][cc]:
                    if mines[rr][cc]:
                        lose()
                        return
                    reveal(rr, cc)
        return

    if flags[r][c]:
        return

    if mines[r][c]:
        lose()
    else:
        reveal(r, c)

def rightClick(r, c):
    global brojostale
    if known[r][c]:
        return
    if flags[r][c]:
        flags[r][c] = 0
        brojostale += 1
    else:
        flags[r][c] = 1
        brojostale -= 1

def drawGrid():
    for r in range(red):
        for c in range(kolona):
            x = STARTX + c * SIZE
            y = STARTY + r * SIZE

            if known[r][c]:
                screen.blit(pictures[grid[r][c]], (x, y))
                if mines[r][c]:
                    screen.blit(pictures[11], (x, y))
            else:
                screen.blit(pictures[9], (x, y))
                if flags[r][c]:
                    screen.blit(pictures[10], (x, y))


def restart():
    global red, kolona, brojmina, SIZE, brojostale, first, kraj

    screen.fill(belo)
    t1 = font1.render("Izaberite težinu", True, 'black')
    t2 = font2.render("1 : najlakša", True, 'black')
    t3 = font2.render("2 : srednja", True, 'black')
    t4 = font2.render("3 : najteža", True, 'black')

    center_blit(t1, 200)
    center_blit(t2, 320)
    center_blit(t3, 390)
    center_blit(t4, 460)
    pg.display.flip()

    while True:
        clock.tick(60)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return True
            if e.type == pg.KEYUP:
                if e.key in [pg.K_1, pg.K_2, pg.K_3]:
                    red, kolona, brojmina, SIZE = nivoi[int(e.unicode)]
                    rebuild_pictures()
                    update_layout()
                    reset_board()
                    brojostale = brojmina
                    first = True
                    kraj = None
                    return False

rebuild_pictures()
update_layout()
reset_board()

while playing:
    running = True
    first = True
    kraj = None

    if restart():
        break

    brojostale = brojmina
    dt = 0

    while running:
        dt += clock.tick(60) / 1000
        for e in pg.event.get():
            if e.type == pg.QUIT:
                playing = False
                running = False
            if e.type == pg.MOUSEBUTTONUP:
                if first and e.button == 1:
                    firstClick(e.pos)
                else:
                    r, c = location(e.pos)
                    if r != -1:
                        if e.button == 1:
                            leftClick(r, c)
                        if e.button == 3:
                            rightClick(r, c)

        if kraj is None and winChecker():
            win()
        screen.fill(belo)
        pg.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, HUD))

        t1 = font3.render(f"sekunde: {int(dt)}", False, "black")
        t2 = font3.render(f"mine: {brojostale}", False, "black")
        screen.blit(t1, (20, 20))
        screen.blit(t2, (20, 45))

        drawGrid()
        pg.display.flip()
    screen.fill(belo)
    pg.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, HUD))

    t1 = font3.render(f"sekunde: {int(dt)}", False, "black")
    t2 = font3.render(f"mine: {brojostale}", False, "black")
    screen.blit(t1, (20, 20))
    screen.blit(t2, (20, 45))

    drawGrid()

    if kraj == "win":
        center_blit(win_txt, 5)
    else:
        center_blit(loser, 5)

    pg.display.flip()

    waiting = True
    while waiting:
        clock.tick(60)
        for e in pg.event.get():
            if e.type in (pg.QUIT, pg.MOUSEBUTTONUP, pg.KEYUP):
                waiting = False

pg.quit()