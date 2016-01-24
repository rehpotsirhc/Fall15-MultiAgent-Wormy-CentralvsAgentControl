# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random
import sys

import pygame
from pygame.locals import *


WINDOW_SIZE_MULT = 1.5
FPS = 5
WORM_COUNT = 3
IS_TWO_PLAYER = True
MIN_APPLES = 2
MAX_APPLES = 5


# 5 worms maximum
assert WORM_COUNT <= 5 and WORM_COUNT >= 1, "There is a maximum of 5 worms in a single game"

assert MIN_APPLES >= 1, "There must be at least one apple on the board at any given time"

WINDOWWIDTH = int(640 * WINDOW_SIZE_MULT)
WINDOWHEIGHT = int(480 * WINDOW_SIZE_MULT)
CELLSIZE = int(20 * WINDOW_SIZE_MULT)


def removeRemainder(int1, int2):
    return int1 - (int1 % int2)


WINDOWWIDTH = removeRemainder(WINDOWWIDTH, CELLSIZE)
WINDOWHEIGHT = removeRemainder(WINDOWHEIGHT, CELLSIZE)

assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."

# When two player, there must be two worms. The worms are controlled by a different set of keys. One by the directional keys and the other by the WASD keys
if IS_TWO_PLAYER:
    WORM_COUNT = 2

CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

# R    G    B
WHITE = (255, 255, 255)
BLACK = (  0, 0, 0)
RED = (255, 0, 0)
GREEN = (  0, 255, 0)
DARKGREEN = (  0, 155, 0)
DARKGRAY = ( 40, 40, 40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

LEFT_KEYS = [K_LEFT, K_a]
RIGHT_KEYS = [K_RIGHT, K_d]
UP_KEYS = [K_UP, K_w]
DOWN_KEYS = [K_DOWN, K_s]

directionsList = [UP, DOWN, RIGHT, LEFT]
colorsList = [WHITE, GREEN, RED, DARKGREEN, DARKGRAY]
nameList = ['WHITE', 'GREEN', 'RED', 'DARK GREEN', 'DARK GRAY']

HEAD = 0  # syntactic sugar: index of the worm's head


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        worms = runGame()
        showGameOverScreen(worms)


def runGame():
    # create worms
    worms = generateWorms()

    # generate at least min apples and at most max apples

    apples = generateApples()

    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                x = 0
                for i, wormCoords, direction, color, name, score in worms:
                    if (event.key == LEFT_KEYS[x]) and direction[0] != RIGHT:
                        direction.pop()
                        direction.append(LEFT)
                    elif (event.key == RIGHT_KEYS[x]) and direction[0] != LEFT:
                        direction.pop()
                        direction.append(RIGHT)
                    elif (event.key == UP_KEYS[x]) and direction[0] != DOWN:
                        direction.pop()
                        direction.append(UP)
                    elif (event.key == DOWN_KEYS[x]) and direction[0] != UP:
                        direction.pop()
                        direction.append(DOWN)
                    elif event.key == K_ESCAPE:
                        terminate()

                    if IS_TWO_PLAYER == True:
                        x += 1

        for i, wormCoords, direction, color, name, score in worms:
            # check if the worm has hit itself or the edge
            if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or \
                            wormCoords[HEAD]['y'] == CELLHEIGHT:
                score[0] -= 2
                return worms
            for wormBody in wormCoords[1:]:
                if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                    score[0] -= 2
                    return worms

            # check if worm has eaten an apply
            origAppleC = len(apples)
            for apple in apples:
                if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
                    apples.remove(apple)
                    score[0] += 1

            if len(apples) == 0:
                apples = generateApples()  # generate more apples if all of them have been eaten

            if origAppleC == len(apples):
                del wormCoords[-1]  # remove worm's tail segment if it didn't eat an apple


            # move the worm by adding a segment in the direction it is moving
            if direction[0] == UP:
                newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
            elif direction[0] == DOWN:
                newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
            elif direction[0] == LEFT:
                newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
            elif direction[0] == RIGHT:
                newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

            wormCoords.insert(0, newHead)
            drawWorm(wormCoords, color)
            drawScore(i, name, score[0])
            pygame.display.update()

        DISPLAYSURF.fill(BGCOLOR)

        drawApples(apples)
        FPSCLOCK.tick(FPS)
        drawGrid()

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def generateApples():
    apples = []

    for _ in range(MIN_APPLES):
        apples.append(getRandomLocation())

    if MAX_APPLES > MIN_APPLES:
        for _ in range(MAX_APPLES - MIN_APPLES):
            if random.randint(0, 1) == 1:
                apples.append(getRandomLocation())

    return apples


def showGameOverScreen(worms):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    for i, wormCoords, direction, color, name, score in worms:
        drawScore(i, name, score[0])

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return


def drawScore(i, name, score):
    scoreSurf = BASICFONT.render(' %s\'s score: %s' % (name, score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    yloc = i * 25 + 10
    scoreRect.topleft = (WINDOWWIDTH - 240, yloc)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def generateWorms():
    worm = []

    ystarts = []

    for i in range(WORM_COUNT):
        #all worms start from the left boundary
        startx = 0
        #keep the worms from overlapping in the y-dimension
        while True:
            starty = random.randint(5, CELLHEIGHT - 6)
            if i == 0 or starty not in ystarts:
                break
        ystarts.append(starty)

        wormCoords = [{'x': startx, 'y': starty},
                      {'x': startx - 1, 'y': starty},
                      {'x': startx - 2, 'y': starty}]
        worm.append([i, wormCoords, [RIGHT], colorsList[i], nameList[i], [len(wormCoords) - 3]])
    return worm


def drawWorm(wormCoords, color):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, color, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, color, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawApples(coords):
    for apple in coords:
        drawApple(apple)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()