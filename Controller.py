import pygame
import math
import sys
import warnings
from copy import deepcopy
import pygame_menu
from StartMenu import StartMenu
from Game import Game
from RestartMenu import RestartMenu

WIDTH = 600
HEIGHT = 600

SQUARE_SIZE = WIDTH / 8

WHITE = (255,255,255)
BLACK  = (0,0,0)

class Controller():
    """
    Class used as a wrapper for the game
    """
    def __init__(self):
        """
        Parameters
        ----------

        font: Default font to use
        screen: Initialise pygame display
        time: Initialise pygame clock
        state: Represent state of game (-1 is unstarted, 1 is started, 0 is restart)
        start_menu: Initialise StartMenu class
        color_selected: Color of player (1) piece
        opponent_selected: Color of computer/player (2) piece
        """
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.time = pygame.time.Clock()
        self.state = -1
        self.start_menu = StartMenu()

        self.color_selected = None
        self.opponent_selected = None

    def main(self):
        """
        Main game loop
        """
        winner = None
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.state == -1:
                # Runs when game is first initialised
                self.start_menu.main(events,self.screen)
                pygame.display.update()

                if not self.start_menu.start_menu_state:
                    # Runs when user starts game
                    self.state = 1
                    self.start_menu.start_menu_state = True

                    self.color_selected = self.start_menu.color
                    self.opponent_selected = self.start_menu.opponent
            elif self.state == 0:
                # Runs when game is over to initialise restart menu
                self.restart_menu.winner = winner
                self.restart_menu.main(events, self.screen)
                pygame.display.update()
                if not self.restart_menu.start_menu_state:
                    # Runs when user restarts game
                    self.state = 1
                    self.restart_menu.start_menu_state = True

                    self.color_selected = self.restart_menu.color
                    self.opponent_selected = self.restart_menu.opponent
            elif self.state == 1:
                # Runs when user starts game and game is initialised
                self.game = Game(self.screen, self.time, self.font
                                 , self.color_selected, self.opponent_selected)
                break
        # Main game loop
        self.game.main()
        self.game.switch_turn()
        if self.game.game_state == 2:
            winner = self.game.turn[0]
        else:
            winner = None
        self.game.game_state = 0
        self.state = 0
        self.restart_menu = RestartMenu(winner)
        self.main()

if __name__ == "__main__":
    Controller().main()
