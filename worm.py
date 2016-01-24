__author__ = 'Chris'

import constants as c
import math
import random

class coord:
    def __init__(self, x, y):
        self.xy = {'x': x, 'y': y}
        self.x = self.xy['x']
        self.y = self.xy['y']

class apple:

    def __init__(self, coord, index):
        self.apl = coord
        self.assigned = False
        self.index = index
        self.eaten = False

    def assign(self):
        self.assigned = True

    def unAssign(self):
        self.assigned = False
    def eat(self):
        self.eaten = True



#basic worm that just moves
class worm:

    HEAD_I = 0
    COLORS = [c.WHITE, c.GREEN, c.BLUE, c.PURPLE, c.DARKGRAY]
    NAMES = ['WHITE', 'GREEN', 'BLUE', 'PURPLE', 'DARK GRAY']
    closestApple = {}




    #game, index, coords, score
    #game, index, length, y, spawnSide
    def __init__(self, *args):

        game = args[0]
        index = args[1]
        self.myContainer = args[2]
        self.game = game
        self.isMoving = True
        self.index = index
        self.name = self.NAMES[self.index]
        self.color = self.COLORS[self.index]
        self.stuckTime = 10
        self.stuckFor = 0
        if len(args) == 5:
            self.coords = args[3]
            self.score = args[4]
            self.direction = c.UP
        elif len(args) == 6:
            length = args[3]
            y = args[4]
            spawnSide = args[5]
            if spawnSide == c.RIGHT:
                x = game.cellWidth - 1
                offset = 1
                self.direction = c.LEFT
            elif spawnSide == c.LEFT:
                x = 0
                offset = -1
                self.direction = c.RIGHT
            else:
                assert "Worms must spawn from the left (moving ride) or right (moving left) side of the screen"
            self.coords = [coord(x, y)]
            self.score = 0

            for i in range(length - 1):
                self.coords.append(coord(self.coords[i].x + offset, y))



    def changeDirection(self, newDirection):
        self.direction = newDirection

    #moves the worm one segment forward and updates the score if an apple was eaten
    #movment happens by:
    #adding a new head in the direction its moving
    #deleting its tail, unless it ate an apple
    #returns 1 if worm ate an apple, 0 if just movement occurred, -1 if it hit something, and -2 if the worm stopped(its stuck)
    def move(self):

         if not self.isMoving and self.stuckFor < self.stuckTime:
            self.stuckFor += 1
            self.color = c.BLACK
            return -2
         else:
            self.stuckFor = 0
            self.color = self.COLORS[self.index]
        # move the worm by adding a segment in the direction it is moving
         if self.direction == c.UP:
            newHead = self.upHead()
         elif self.direction == c.DOWN:
            newHead = self.downHead()
         elif self.direction== c.LEFT:
            newHead = self.leftHead()
         elif self.direction == c.RIGHT:
            newHead = self.rightHead()

         #check if it hit anything
         if self.onABorder(newHead):
            self.myContainer.deleteWorm(self)
            return -1

         wormHit = self.onAWorm(newHead)
         if not wormHit is None:
             #kill the other worm
             if len(wormHit.coords) < len(self.coords):
                 wormHit.myContainer.deleteWorm(wormHit)
             elif len(wormHit.coords) > len(self.coords):
                self.myContainer.deleteWorm(self)
             else:
                if random.randint(0, 1) == 0:
                    wormHit.myContainer.deleteWorm(wormHit)
                else:
                    self.myContainer.deleteWorm(self)





         self.coords.insert(0, newHead)

         if not self.appleEaten():
            del self.coords[-1] # remove worm's tail
            return 0
         else:
             self.split()
             return 1

    def split(self):
        return

    def onABorder(self, p):
       return p.x == -1 or p.y == -1 or p.x == self.game.cellWidth or p.y == self.game.cellHeight

    def onAWorm(self, p):
        for wContainer in self.game.computerWorms:
            for w in wContainer.worms:
                if self.onWorm(w, p):
                    return w
        for wContainer in self.game.humanWorms:
            for w in wContainer.worms:
                if self.onWorm(w, p):
                    return w
        return None


    def onWorm(self, w, p):
        for ci in w.coords:
            if p.x == ci.x and p.y == ci.y:
                return True
        return False

    #updates the worms score by appleValue if an apple was eaten
    def appleEaten(self):
        head = self.coords[self.HEAD_I]
        for apple in self.game.apples:
            if not apple.eaten:
                a = apple.apl
                if head.x == a.x and head.y == a.y:
                    self.game.apples[apple.index].eat()
                    if hasattr(self.closestApple, 'apl') and self.closestApple.apl.x == a.x and self.closestApple.apl.y == a.y:
                        self.closestApple = None
                    self.score += self.game.appleValue
                    self.myContainer.updateScore(self.game.appleValue)
                    return True
        return False


    def leftHead(self):
        head = self.coords[self.HEAD_I]
        return coord(head.x - 1, head.y)
    def rightHead(self):
        head = self.coords[self.HEAD_I]
        return coord(head.x + 1, head.y)

    def upHead(self):
        head = self.coords[self.HEAD_I]
        return coord(head.x, head.y - 1)

    def downHead(self):
        head = self.coords[self.HEAD_I]
        return coord(head.x, head.y + 1)



class smartWorm(worm):





    #randomness is a number between 0 and 1
    #it determines the probability that the worm will turn in a random direction
    # if it can't find a direction that takes it closer to an apple within its vision range

    #game, index, splitLength, visionRange, randomness, coords, score
    #game, index, splitLength, visionRange, randomness, len, y, spawnSide
    def __init__(self, *args):


        game = args[0]
        index = args[1]
        myContainer = args[2]
        self.splitLength = args[3]
        self.visionRange = args[4]
        self.randomness = args[5]
        self.stuckTime = int(self.splitLength * 1.5)

        if len(args) == 8:
            coords = args[6]
            score  = args[7]

            #game, index, coords, score
            worm.__init__(self, game, index, myContainer, coords, score)

        elif len(args) == 9:
            length = args[6]
            y = args[7]
            spawnSide = args[8]
            #game, index, length, y, spawnSide
            worm.__init__(self, game, index, myContainer, length, y, spawnSide)



    def split(self):
        if len(self.coords) >= self.splitLength:
            halfLength = int(len(self.coords)/ 2)
            halfScore = int(self.score / 2)
            if len(self.coords) % 2 != 0:
                halfLength += 1

            secondHalfScore = halfScore
            if self.score % 2 != 0:
                halfScore += 1

            #game, index, splitLength, visionRange, randomness, coords, score
            w2 = smartWorm(self.game, self.index, self.myContainer, self.splitLength, self.visionRange, self.randomness, self.coords[halfLength:len(self.coords)], secondHalfScore)
            self.coords = self.coords[0:halfLength]
            self.score = halfScore
            w2.chooseBestDir()
            self.myContainer.addWorm(w2)


    def findClosestApple(self, dynamicReassign):


        closestApple = self.closestApple is not None and hasattr(self.closestApple, 'apl')

        if closestApple or dynamicReassign:

            if closestApple:
                self.game.apples[self.closestApple.index].unAssign()
                self.closestApple = None

            dist = float("inf")
            head = self.coords[self.HEAD_I]
            for apple in self.game.apples:
                if not apple.eaten:
                    a = apple.apl
                    tmp = self.eucDist(head, a)
                    if tmp <= self.visionRange and tmp < dist:
                        dist = tmp
                        apple.assign()
                        self.closestApple = apple


    def eucDist(self, p1, p2):
        return math.pow(math.pow(p1.x - p2.x, 2) + math.pow(p1.y - p2.y, 2), .5)


    #sets the direction to try and get it closer to its target apple
    #not guaranteed to get the worm closer
    #distance to apples defined by the discrete Euclidean distance from the apple to the worms head
    #in case of ties:
    #left is preferred to right
    #up is preferred to down
    #if all possible directions move the worm farther away from its closest apple,
    #  it will continue in the same direction or turn at random with a probability equal to "randomness"

    def chooseBestDir(self):


        head = self.coords[self.HEAD_I]
        if self.direction == c.UP:
            continueHead = self.upHead()
        elif self.direction == c.RIGHT:
            continueHead = self.rightHead()
        elif self.direction == c.DOWN:
            continueHead = self.downHead()
        else:
            continueHead = self.leftHead()


        leftHead = self.leftHead()
        rightHead = self.rightHead()
        upHead = self.upHead()
        downHead = self.downHead()

        goingHort = self.direction == c.LEFT or self.direction == c.RIGHT

        #first check to see if there are any directions
        #where the worm will hit another worm or a border
        #forbid those directions
        vertHeads = [leftHead, rightHead]
        hortHeads = [upHead, downHead]

        forbiddenDirections = []

        #will the worm hit something if it keeps going straight?
       # if self.onABorder(head) or self.onAWorm(head):
         #   forbiddenDirections.append(self.direction)


        #its moving vertically
        #will it hit something if it turns to go right or left?
        if not goingHort:
            for h in vertHeads:
                w = self.onAWorm(h)
                if self.onABorder(h) or not w is None:
                    if h.xy == rightHead.xy:
                        forbiddenDirections.append(c.RIGHT)
                    elif h.xy == leftHead.xy:
                        forbiddenDirections.append(c.LEFT)

        #its moving horizontally
        #will it hit something if it turns up or down?
        if goingHort:
            for h in hortHeads:
                w = self.onAWorm(h)
                if self.onABorder(h) or not w is None:
                   if h.xy == upHead.xy:
                        forbiddenDirections.append(c.UP)
                   elif h.xy == downHead.xy:
                        forbiddenDirections.append(c.DOWN)

        #will it hit something if it continues in its current direction

        w = self.onAWorm(continueHead)
        if self.onABorder(continueHead) or not w is None:
            forbiddenDirections.append(self.direction)


        canTurn = not (c.LEFT in forbiddenDirections and c.RIGHT in forbiddenDirections and not goingHort) and not (c.UP in forbiddenDirections and c.DOWN in forbiddenDirections and goingHort)

        if self.direction in forbiddenDirections and not canTurn:
                self.isMoving = False
                return 0


        if hasattr(self.closestApple, 'apl'):
            curDist = self.eucDist(self.closestApple.apl, head)

            if goingHort:
                upDist = self.eucDist(self.closestApple.apl, upHead)
                downDist = self.eucDist(self.closestApple.apl, downHead)

                minimum = min(curDist, upDist, downDist)

                if minimum == upDist and c.UP not in forbiddenDirections:
                    self.changeDirection(c.UP)
                    self.isMoving = True
                    return 1
                if minimum == downDist and c.DOWN not in forbiddenDirections:
                    self.changeDirection(c.DOWN)
                    self.isMoving = True
                    return 1

            else:
                leftDist = self.eucDist(self.closestApple.apl, leftHead)
                rightDist = self.eucDist(self.closestApple.apl, rightHead)

                minimum = min(curDist, leftDist, rightDist)

                if minimum == leftDist and c.LEFT not in forbiddenDirections:
                    self.changeDirection(c.LEFT)
                    return 1
                    self.isMoving = True
                if minimum == rightDist and c.RIGHT not in forbiddenDirections:
                    self.changeDirection(c.RIGHT)
                    self.isMoving= True
                    return 1



        #randomly see if the worm should change direction given it can't find a way to turn such that it gets
        #closer to an apple within its vision range
        #see if its current direction is going to get it killed, if so, change direction
        if ((random.random() < self.randomness and canTurn) or self.direction in forbiddenDirections):
            while(True):
                if goingHort:
                    #pick up or down randomly
                    dir = c.DIRECTIONS[random.randint(0, 1)]
                else:
                    #pick right or left randomly
                    dir = c.DIRECTIONS[random.randint(2, 3)]

                if dir not in forbiddenDirections:
                    self.changeDirection(dir)
                    self.isMoving = True
                    return 1

        #the worm is going to continue on in the same direction
        #it still could die if left, up, and right of it are borders or other worms



class wormContainer:

    def __init__(self):
        self.index = 0
        self.worms = []
        self.score = 0


    def firstWorm(self, worm, isComputer):

        self.index = worm.index
        self.worms.append(worm)
        self.isComputer = isComputer
        self.name = worm.name
        self.color = worm.color

    def addWorm(self, worm):
        self.worms.append(worm)

    def updateScore(self, scoreChange):
        self.score += scoreChange

    def deleteWorm(self, worm):
        self.worms.remove(worm)

    def allDead(self):
        return len(self.worms) == 0

    def worms(self):
        return self.worms



class centralController:

    def __init__(self, worms, apples):
       self.worms = worms
       self.apples = apples


    def direct(self, dynamicReassign):

        for apple in self.apples:
            if (not apple.assigned or dynamicReassign) and not apple.eaten:
                dist = float("inf")
                closestWorm = None
                for wormContainer in self.worms:
                    for worm in wormContainer.worms:
                        closestApple = worm.closestApple is not None and hasattr(worm.closestApple, 'apl')
                        if not closestApple or  dynamicReassign:
                            tmp = worm.eucDist(worm.coords[worm.HEAD_I], apple.apl)
                            curTargetDist = dist = float("inf")
                            if closestApple:
                                curTargetDist = worm.eucDist(worm.coords[worm.HEAD_I], worm.closestApple.apl)
                                if tmp < curTargetDist:
                                    self.apples[worm.closestApple.index].unAssign()
                                    worm.closestApple = None

                            if tmp <= worm.visionRange and tmp < dist and tmp < curTargetDist:
                                dist = tmp
                                closestWorm = worm
                if closestWorm is not None:
                    closestWorm.closestApple = apple
                    apple.assign()






