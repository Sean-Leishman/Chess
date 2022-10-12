import math
import sys
import warnings
from copy import deepcopy
import pygame_menu

class RestartMenu():
    def __init__(self,winner):
        self.init_main_menu(winner)
        self.start_menu_state = True

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
        self.mainmenu.add.button('Quit', self.start_game)

    def start_game(self):
        self.start_menu_state = False

    def main(self,events,screen):
        #screen.fill((0,0,0))
        self.mainmenu.update(events)
        self.mainmenu.draw(screen)