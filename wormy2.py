__author__ = 'Chris'


import pygame
import sys
from worm import *
from pygame.locals import *
import constants as c
import time


#OPTIONS (CHANGE THESE TO CUSTOMIZE)

#in terms of grid squares
wormStartLength = 3
wormSplitLength = 6


#the percentage of randomness in the worms movement when it can't find a
#direction that takes it closer to its goal apple
randomness = .1

humanWormCount = 0
assert humanWormCount <= 2, "There can be at most 2 human-controlled worms. " \
                           "One is controlled by the arrow keys and the other by the WASD keys. " \
                           "The worm controlled by the arrow keys will be white. The other worm will be green"

computerWormCount = 2
appleValue = 1
fps= 500

windowSizeMult = 1.5
windowWidth = int(640 * windowSizeMult)
windowHeight = int(480 * windowSizeMult)
cellSize = int(20 * windowSizeMult)

paddingTopRight = humanWormCount + computerWormCount







def removeRemainder(int1, int2):
    return int1 - (int1 % int2)


windowWidth = removeRemainder(windowWidth, cellSize)
windowHeight = removeRemainder(windowHeight, cellSize)

cellWidth = int(windowWidth / cellSize)
cellHeight = int(windowHeight / cellSize)

assert windowWidth % cellSize == 0, "Window width must be a multiple of cell size."
assert windowHeight % cellSize == 0, "Window height must be a multiple of cell size."





class game:

    def __init__(self, windowWidth, windowHeight, cellSize, cellWidth, cellHeight, appleValue):
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.cellSize = cellSize
        self.cellWidth = cellWidth
        self.cellHeight = cellHeight
        self.appleValue = appleValue

        #lists of wormContainers
        self.humanWorms = []
        self.computerWorms = []
        self.apples = []









def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((windowWidth, windowHeight))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()

    trials = 2
    movesPerRound = 500
    scoresEachTrial = []
    for i in range(trials):

        rounds =20
        scoresOverall = []
        if i == 0:
            centrallyControlled = True
            smartWormVisionRadius = 100
        else:
            centrallyControlled = False
            smartWormVisionRadius = 1

        scoreLists = []
        while rounds > 0:
            rounds -= 1
            runGame(movesPerRound, centrallyControlled, smartWormVisionRadius)
            scores = []
            for wc in g.humanWorms:
                scores.append(wc.score)
            for wc in g.computerWorms:
                scores.append(wc.score)
            scoreLists.append(scores)

        scoresOverall = map(sum, zip(*scoreLists))
        scoresEachTrial.append(scoresOverall)


    showGameOverScreen(scoresEachTrial, True)






def runGame(moveLimit, centrallyControlled, smartWormVisionRadius):

    global g
    g = game(windowWidth, windowHeight, cellSize, cellWidth, cellHeight, appleValue)

    generateWorms(smartWormVisionRadius)
   # generateRandomMinMaxApples(g, 1, 2)

    if centrallyControlled:
        cenController = centralController(g.computerWorms, g.apples)


    moves = 0
    while moves <= moveLimit:  # main game loop
        generateRandomMinMaxApples(moves, 25, 1, 2)
        moves += 1
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:

               if event.key == K_ESCAPE:
                    terminate()
               else:
                   #check key presses for the human-controlled worms and change their directions if need be
                      #move human worms
                   for wContainer in g.humanWorms:
                        for w in wContainer.worms:
                           if event.key == c.LEFT_KEYS[w.index] and w.direction != c.RIGHT:
                               w.changeDirection(c.LEFT)
                           elif event.key == c.RIGHT_KEYS[w.index] and w.direction != c.LEFT:
                               w.changeDirection(c.RIGHT)
                           elif event.key == c.UP_KEYS[w.index] and w.direction != c.DOWN:
                                w.changeDirection(c.UP)
                           elif event.key == c.DOWN_KEYS[w.index] and w.direction != c.UP:
                                w.changeDirection(c.DOWN)



        if centrallyControlled:
            cenController.direct(True)


        #do direction changes for computer-controlled worms
        for wContainer in g.computerWorms:
            for w in wContainer.worms:
                #for now, look for the closest apple every time the worm considers a turn
                if not centrallyControlled:
                    w.findClosestApple(True)
                w.chooseBestDir()


        #move computer worms

        for wContainer in g.computerWorms:
            for w in wContainer.worms:
                    wormMove(w)
            #draw score
            drawScore(wContainer, False, 0)
            #update display
            pygame.display.update()

        #move human worms
        for wContainer in g.humanWorms:
            for w in wContainer.worms:
                wormMove(w)
            #draw score
            drawScore(wContainer, False, 0)
            #update display
            pygame.display.update()


        DISPLAYSURF.fill(c.BGCOLOR)

        drawApples()
        FPSCLOCK.tick(fps)
        drawGrid()

    return g

def wormMove(w):

     #do movement (also check's if they've eat an apple and updates their score or if they've hit something
     w.move()
     #draw them
     drawWorm(w)
     #update display
     #pygame.display.update()



def generateWorms(smartWormVisionRadius):

    ystarts = []

    #generate the human-controlled worms
    for i in range(humanWormCount):
        #game, index, length, y, spawnSide

        wc = wormContainer()

        w = worm(g, i, wc, wormStartLength, distinctY(ystarts), c.DIRECTIONS[random.randint(2, 3)])
        wc.firstWorm(w, False)
        g.humanWorms.append(wc)



    #generate computer-controlled worms
    for i in range(computerWormCount):
        #game, index, splitLength, visionRange, randomness, len, y, spawnSide

        wc = wormContainer()
        w = smartWorm(g, i +humanWormCount, wc, wormSplitLength, smartWormVisionRadius, randomness, wormStartLength,  distinctY(ystarts), c.DIRECTIONS[random.randint(2, 3)])
        wc.firstWorm(w,True)
        g.computerWorms.append(wc)





def distinctY(ystarts):
    while True:
        starty = random.randint(5, cellHeight - 6)
        if starty not in ystarts:
            break
        ystarts.append(starty)
    return starty

def generateRandomLocation(*args):

    if len(args) == 2:
        coord1 = args[0]
        coord2 = args[1]

    else:
        coord1 = coord(0, cellWidth - paddingTopRight)
        coord2 = coord(paddingTopRight, cellHeight)


    return {'x': random.randint(coord1.x, coord1.y), 'y': random.randint(coord2.x, coord2.y)}



#def generateRandomMinMaxApples_Q1(moves, freq, min, max):



def generateRandomMinMaxApples(moves, freq, min, max, *args):

    if moves % freq == 0:

        assert min <= max, "In generating a random number of apples between [min, max], " \
                        "min must be less than or equal to max. " \
                        "You supplied min = " + min + " and max = " + max
        for _ in range(min):
            rl = generateRandomLocation(args)
            i = len(g.apples)
            g.apples.append(apple(coord(rl['x'], rl['y']), i))

        if max > min:
            for _ in range(max - min):
                if random.randint(0, 1) == 1:
                    rl = generateRandomLocation(args)
                    i = len(g.apples)
                    g.apples.append(apple(coord(rl['x'], rl['y']), i))






def drawWorm(w):


    i = 0
    wormCoords = w.coords
    color = w.color
    headX = 0
    headY = 0
    for coord in wormCoords:

        x = coord.x * cellSize
        y = coord.y * cellSize
        if i == 0:
            #color the head orange
            fillColor = c.ORANGE
            headX = x
            headY = y
        else:
            fillColor = color

        wormSegmentRect = pygame.Rect(x, y, cellSize, cellSize)
        pygame.draw.rect(DISPLAYSURF, c.PEACH, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, cellSize - 8, cellSize - 8)
        pygame.draw.rect(DISPLAYSURF, fillColor, wormInnerSegmentRect)
        i += 1


    # vrX1 = headX - w.visionRange * cellSize
    # vrX2 = headX + w.visionRange* cellSize
    # vrY1 = headY - w.visionRange* cellSize
    # vrY2 = headY + w.visionRange* cellSize
    #
    # for i in range(vrX1, vrX2 + 1):
    #     for j in range(vrY1, vrY2 +1):
    #         if i <=windowWidth and j <=windowHeight and i>=0 and j >=0 and i != headX and j != headY:
    #             wormInnerSegmentRect = pygame.Rect(i, j, 1, 1)
    #             pygame.draw.rect(DISPLAYSURF, c.LIGHTYELLOW, wormInnerSegmentRect)

    #wormInnerSegmentRect = pygame.Rect(vrX1* cellSize, vrY1 * cellSize, (vrX1 + vrX2) * cellSize, (vrY1 + vrY2) * cellSize)
    #pygame.draw.rect(DISPLAYSURF, c.LIGHTYELLOW, wormInnerSegmentRect)



def drawApple(coord):
    x = coord.x * cellSize
    y = coord.y * cellSize
    appleRect = pygame.Rect(x, y, cellSize, cellSize)
    pygame.draw.rect(DISPLAYSURF, c.RED, appleRect)


def drawApples():
    for apple in g.apples:
        if not apple.eaten:
            drawApple(apple.apl)


def drawGrid():
    for x in range(0, windowWidth, cellSize):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, c.DARKGRAY, (x, 0), (x, windowHeight))
    for y in range(0, windowHeight, cellSize):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, c.DARKGRAY, (0, y), (windowWidth, y))


def drawScore(wContainer, overall, offset):

    if overall:
        score = overall[wContainer.index]
        scoreString = 'overall score'
    else:
        score = wContainer.score
        scoreString = 'score'

    name = wContainer.name
    index = wContainer.index

    if wContainer.allDead():
        color = c.RED
    else:
        color = wContainer.color



    scoreSurf = BASICFONT.render(' %s\'s %s: %s' % (name, scoreString, score), True, color)
    scoreRect = scoreSurf.get_rect()
    yloc = index * 25 + 10 + offset * 45
    scoreRect.topleft = (windowWidth - 280, yloc)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, c.DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (windowWidth - 200, windowHeight - 30)
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

def terminate():
    pygame.quit()
    sys.exit()








#the game over screen
def showGameOverScreen(overallScores, waitForKeyPress):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, c.WHITE)
    overSurf = gameOverFont.render('Over', True, c.WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (windowWidth / 2, 10)
    overRect.midtop = (windowHeight / 2, gameRect.height + 10 + 25)



    try:
        overallScores[0] / 1
        lisOverAllScores = [overallScores]
    except:
        lisOverAllScores = overallScores


    i = 0
    for os in lisOverAllScores:

        for wContainer in g.computerWorms:
            #draw score

            drawScore(wContainer, os, i)

            #move human worms
        for wContainer in g.humanWorms:
            #draw score
            drawScore(wContainer, os, i)

        i +=1

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while waitForKeyPress:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return







#the rotating start screen
def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, c.WHITE, c.DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, c.GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(c.BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (windowWidth / 2, windowHeight / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (windowWidth / 2, windowHeight / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(fps)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


if __name__ == '__main__':
    main()


















