import math
import sys
import warnings
from copy import deepcopy
import pygame_menu

class RestartMenu():
    def __init__(self,winner):
        self.init_main_menu(winner)
        self.start_menu_state = True

        self.color = 0
        self.opponent = 0

    def init_main_menu(self, winner):
        mytheme = pygame_menu.themes.THEME_ORANGE.copy()
        mytheme.background_color = (128, 128, 128,10)
        if not winner:
            string = "Stalemate"
        else:
            string = str(winner+" won!")

        self.mainmenu = pygame_menu.Menu(string, 600, 400,
                                         theme=mytheme)
        self.mainmenu.add.button('Restart', self.start_game)
        self.mainmenu.add.selector('Piece Color', [('Random', 1), ('White', 2), ('Black', 3)], onchange=self.set_color)
        self.mainmenu.add.selector('Opponent', [('vs Player', 1), ('vs Computer', 2)], onchange=self.set_opponent)
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
        #screen.fill((0,0,0))
        self.mainmenu.update(events)
        self.mainmenu.draw(screen)