import math
import sys
import warnings
from copy import deepcopy
import pygame_menu

class StartMenu():
    def __init__(self):
        self.init_main_menu()
        self.start_menu_state = True

    def init_main_menu(self):
        self.mainmenu = pygame_menu.Menu('Welcome', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED)
        self.mainmenu.add.button('Play', self.start_game)
        self.mainmenu.add.button('Quit', self.start_game)

    def start_game(self):
        self.start_menu_state = False

    def main(self,events,screen):
        screen.fill((0,0,0))
        self.mainmenu.update(events)
        self.mainmenu.draw(screen)