__author__ = 'Chris'


from pygame.locals import *


#DONT CHANGE
#these direction are relative to the board, not the worm
# so they are really like north, south, west, and east
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

LEFT_KEYS = [K_LEFT, K_a]
RIGHT_KEYS = [K_RIGHT, K_d]
UP_KEYS = [K_UP, K_w]
DOWN_KEYS = [K_DOWN, K_s]

DIRECTIONS = [UP, DOWN, RIGHT, LEFT]
# R    G    B
WHITE = (255, 255, 255)
BLACK = (  0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (255, 0, 255)
DARKGREEN = (  0, 155, 0)
DARKGRAY = ( 40, 40, 40)
ORANGE = (255,140,0)
PEACH = (255,228,181)
LIGHTYELLOW= (255,255,100)

BGCOLOR = BLACK
