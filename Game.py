import pygame
import math
import sys
import warnings
from copy import deepcopy
import pygame_menu
import chess
import io
import svgutils
import random
import numpy as np
from stockfish import Stockfish

from Piece import *
from Model import Model
from Utils import *
from Board import *

path = 'C:\\Users\\leish\\stockfish\\stockfish_20090216_x64'

stockfish = Stockfish(path=path)


warnings.filterwarnings(action='ignore',message="libpng warning: bKGD: invalid")

pygame.init()



class Game():
    """
    Class used to initialise and handle UI components
    """
    def __init__(self,screen, time, font, color=0, opponent=0):
        self.color = color
        self.opponent = opponent
        self.user,self.computer = self.get_user(self.color, self.opponent)
        self.turn = COLOR[WHITE]
        self.board = Board(self.user,self.computer,False)
        self.future_board = deepcopy(self.board)
        self.screen = screen
        self.time = time
        self.font = font
        self.selected = None
        self.valid_moves = None
        self.in_check = None
        self.game_state = 0
        self.model = Model()

    def get_best_move(self, color):
        moves, boards = self.board.get_all_possible_moves(color)

        scores = self.model.predict_scores(boards)
        print(scores)
        if color == COLOR[WHITE]:
            white_scores = scores[:,2]
            return moves[np.argmax(white_scores)]
        elif color == COLOR[BLACK]:
            black_scores = scores[:, 0]
            return moves[np.argmin(black_scores)]

    def drawStartWindow(self):
        pygame.display.update()

    def drawWindow(self):
        self.screen.fill(WHITE)
        pieces = self.board.get_pieces()

        for i in range(8):
            for j in range(8):
                if i % 2 == 0 and j % 2 == 0 or i % 2 == 1 and j % 2 ==1:
                    pygame.draw.rect(self.screen,(153, 102, 51),(i*SQUARE_SIZE,j*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))
                else:
                    pygame.draw.rect(self.screen, (255, 204, 153), (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        if self.selected != None:
            pygame.draw.rect(self.screen,(255,0,0),(self.selected[0]*SQUARE_SIZE,self.selected[1]*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE),2)
        if self.valid_moves != None:
            for move in self.valid_moves:
                pygame.draw.rect(self.screen, (0, 255, 0), (move[0] * SQUARE_SIZE, move[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
        if self.in_check != None:
            pygame.draw.rect(self.screen, (255, 0, 0), (self.in_check[0] * SQUARE_SIZE, self.in_check[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
        for i in pieces:
            self.screen.blit(i.get_img(), i.get_rect())
            if (isinstance(i, King)):
                if (i.check):
                    pygame.draw.rect(self.screen, (255, 0, 0), i.get_rect(), 2)


        text_surface = self.font.render(self.turn[0], False, (0, 0, 0))
        self.screen.blit(text_surface,(400,0))

        if (self.game_state == 1):
            text_surface = self.font.render("Stalemate", False, (0, 0, 0))
            self.screen.blit(text_surface, (400, 200))
        if (self.game_state == 2):
            text_surface = self.font.render(str("Checkmate. " + self.turn[0] + " wins"), False, (0, 0, 0))
            self.screen.blit(text_surface, (400, 200))

        pygame.display.update()


    def get_user(self, color, opponent):
        if opponent == 0:
            return COLOR[WHITE],COLOR[BLACK]
        elif opponent == 1:
            if color == 0:
                rand = random.randint(0,1)
                if rand == 0:
                    return COLOR[WHITE],COLOR[BLACK]
                elif rand == 1:
                    return COLOR[BLACK], COLOR[WHITE]
            elif color == 1:
                return COLOR[WHITE],COLOR[BLACK]
            elif color == 2:
                return COLOR[BLACK],COLOR[WHITE]

    def switch_turn(self):
        if self.turn == COLOR[WHITE]:
            self.turn = COLOR[BLACK]
        else:
            self.turn = COLOR[WHITE]

    def get_turn(self):
        return self.turn

    def move_piece(self):
        pass

    def get_cord(self,pos):
        cord = [0] * 2
        for i in range(len(pos)):
            cord[i] = math.floor(pos[i]/SQUARE_SIZE)
        return cord


    def main(self):
        """
        Main game loop

        :return:
        """
        selected = False
        self.drawStartWindow()
        self.board.init_valid(self.get_turn()[0])
        self.future_board.init_valid(self.get_turn()[0], True)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Game logic for Player vs Player or Player's turn vs Computer
                if self.opponent == 0 or self.user == self.turn:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        # Initialise all valid moves possible for all pieces of current color
                        self.board.init_valid(self.get_turn()[0])
                        self.future_board.init_valid(self.get_turn()[0], True)

                        # Select the piece
                        if not selected:
                            cord = self.get_cord(pos)
                            select = self.board.get_selected(cord)
                            print(select)
                            if select != None and select.color == self.turn:
                                self.selected = cord
                                self.valid_moves = self.board.get_valid_for_pos(cord)
                                self.future_board.get_valid_for_pos(cord)
                                selected = True

                        # Select the final position of the selected piece
                        else:
                            new_cord = self.get_cord(pos)
                            # Check move is valid
                            if self.board.get_valid(cord,new_cord,self.get_turn()[0]):
                                # Move piece and check if game is over
                                self.board.move_piece(cord,new_cord,real=True)
                                self.switch_turn()
                                self.board.init_valid(self.get_turn()[0], False)
                                self.game_state = self.board.check_mates(self.get_turn()[0])
                            selected = False
                            self.selected = None
                            self.valid_moves = None
                        self.future_board.pieces = deepcopy(self.board.pieces)
                        self.drawWindow()
                # Game logic for Computer's turn against Player
                else:
                    best_move = self.get_best_move(self.computer)
                    self.board.move_piece(best_move[0], best_move[1], real=True)
                    self.board.init_valid(self.get_turn()[0], True)
                    self.switch_turn()
                    self.board.init_valid(self.get_turn()[0], False)
                    self.game_state = self.board.check_mates(self.get_turn()[0])
                    self.drawWindow()
            if (self.game_state != 0):
                break
            self.time.tick(60)


if __name__ == "__main__":
    Game().start_menu()

