import pygame
import pygame.locals
import pygame.freetype
import time
from collections import Counter

running =  True
pygame.init()

from state import GameState
from vars import GameVars

screen = pygame.display.set_mode((GameVars.X_MAX, GameVars.Y_MAX))
state = GameState(screen)

state.run()