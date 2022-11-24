import math
import sys
import warnings
from copy import deepcopy
import pygame_menu

class StartMenu():
    def __init__(self):
        self.init_main_menu()
        self.start_menu_state = True
        self.color = 0
        self.opponent = 0

    def init_main_menu(self):
        self.mainmenu = pygame_menu.Menu('Welcome', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED)
        self.mainmenu.add.button('Play', self.start_game)
        self.mainmenu.add.selector('Piece Color', [('Random',0),('White',1),('Black',2)], onchange=self.set_color)
        self.mainmenu.add.selector('Opponent', [('vs Player', 0), ('vs Computer', 1)], onchange=self.set_opponent)
        self.mainmenu.add.button('Quit', pygame_menu.events.EXIT)

    def set_color(self, color, value):
        print(color)
        self.color = value

    def set_opponent(self, opponent, value):
        print(opponent, value)
        self.opponent = value

    def start_game(self):
        self.start_menu_state = False

    def main(self,events,screen):
        screen.fill((0,0,0))
        self.mainmenu.update(events)
        self.mainmenu.draw(screen)