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
from os import path
from pathlib import Path

from Model import Model

path = 'C:\\Users\\leish\\stockfish\\stockfish_20090216_x64'

stockfish = Stockfish(path=path)


warnings.filterwarnings(action='ignore',message="libpng warning: bKGD: invalid")

pygame.init()

WIDTH = 600
HEIGHT = 600

SQUARE_SIZE = WIDTH / 8

WHITE = (255,255,255)
BLACK  = (0,0,0)

COLOR = {
    WHITE: ['WHITE',(255,255,255)],
    BLACK : ['BLACK',(0,0,0)]
}

INITIALS = {
    "Pawn":"p",
    "Queen":"q",
    "King":"k",
    "Bishop":"b",
    "Knight":"n",
    "Castle":"r",
}

COLOR_INITIAL = {
    "WHITE":"l",
    "BLACK":"d"
}

white_letter_coord = ['a','b','c','d','e','f','g','h']

def convert_pos_to_coord(pos, turn):
    if turn == COLOR[WHITE]:
        return str(white_letter_coord[pos[0]] + str(8 - pos[1]))
    elif turn == COLOR[BLACK]:
        return str(list(reversed(white_letter_coord))[pos[0]] + str(1 + pos[1]))

def convert_coord_to_pos(coord,turn):
    pos = coord[:2]
    new_pos = coord[2:]
    if turn == COLOR[WHITE]:
        return [white_letter_coord.index(pos[0]), 8 - int(pos[1])] \
               ,[white_letter_coord.index(new_pos[0]), 8 - int(new_pos[1])]
    elif turn == COLOR[BLACK]:
        return [list(reversed(white_letter_coord)).index(pos[0]),int(pos[1]) - 1] \
                ,[list(reversed(white_letter_coord)).index(new_pos[0]),int(new_pos[1]) - 1]


def load_and_scale_svg(filename, scale):
    svg_string = open(filename, "rt").read()
    start = svg_string.find('<svg')
    if start > 0:
        svg_string = svg_string[:start+4] + f' transform="scale({scale})"' + svg_string[start+4:]

    start = svg_string.find('<g style="')
    if start > 0:
        svg_string = svg_string[:start + 10] + f'overflow=visible; ' + svg_string[start + 10:]

    svg = svgutils.compose.SVG(filename)
    svg.scale(scale)
    figure = svgutils.compose.Figure(float(svg.height) * 2, float(svg.width) * 2, svg)
    figure.save('svgNew.svg')
    svg_string = open('svgNew.svg', "rt").read()
    print(svg_string)
    return pygame.image.load(io.BytesIO(svg_string.encode()))


class Piece():
    def __init__(self,color,pos,type, copy):
        self.color = color
        self.taken = False
        self.pos = pos
        if not copy:
            self.img = self.load_img()
            self.rect = self.load_rect()
        else:
            self.img = None
            self.rect = None
        self.valid_moves = []
        self.future = type

    def is_taken(self):
        return self.taken

    def get_pos(self):
        return self.pos

    def get_color(self):
        return self.color

    def load_img(self):
        filename = "Images\\Chess_"+INITIALS[str(self.__class__.__name__)]+COLOR_INITIAL[self.color[0]]+"t45.svg"
        #img = pygame.image.load(filename)
        #img = pygame.transform.smoothscale(img, (SQUARE_SIZE,SQUARE_SIZE))
        img = load_and_scale_svg(filename, SQUARE_SIZE/45)
        return img

    def load_rect(self):
        return pygame.Rect(self.pos[0]*SQUARE_SIZE,self.pos[1]*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE)

    def get_img(self):
        return self.img
    
    def get_rect(self):
        return pygame.Rect(self.pos[0]*SQUARE_SIZE,self.pos[1]*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE)

    def move_pos(self,new_pos,board):
        piece = None
        if new_pos not in self.valid_moves:
            return False, piece
        for move in board:
            if move.get_pos() == new_pos:
                piece = move
                board.remove(move)
        self.pos = new_pos
        return True, piece

    def make_move_pos(self, new_pos):
        self.pos = new_pos

    def is_valid(self,new_pos,board):
        if new_pos not in self.valid_moves:
            return False
        else:
            return True

    def find_valid(self,board):
        self.valid_moves = []
        for i in self.moves:
            copy = self.pos[:]
            valid = True
            once = True
            while i[0] + copy[0] >= 0 and i[0] + copy[0] < 8 and i[1] + copy[1] >= 0 and i[1] + copy[1] < 8 and valid:
                if valid and not once:
                    valid = False
                for j in board:
                    if [i[0] + copy[0],i[1]+copy[1]] == j.get_pos() and once:
                        if j.get_color() == self.get_color():
                            valid = False
                        else:
                            valid = True
                            once = False
                if valid:
                    self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])
                copy = [copy[0] + i[0], copy[1] + i[1]]

    def get_valid_moves(self):
        return self.valid_moves

class Pawn(Piece):
    def __init__(self, color, pos,direction,type, copy = False):
        super().__init__(color, pos,type, copy)
        self.direction = direction
        self.moves = []
        self.check = []
        self.valid_moves = []
        self.moved = False

    def __deepcopy__(self, memodict={}):
        piece = Pawn(deepcopy(self.color),deepcopy(self.pos),deepcopy(self.direction),deepcopy(self.future),True)
        piece.moves = deepcopy(self.moves)
        piece.check = deepcopy(self.check)
        piece.moved = deepcopy(self.moved)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece

    def define_moves(self):
        if self.direction == 1:
            if not self.moved:
                self.moves = [[0,1],[0,2]]
            else:
                self.moves = [[0,1]]
            self.check = [[1,1],[-1,1]]
        else:
            if not self.moved:
                self.moves = [[0,-1],[0,-2]]
            else:
                self.moves = [[0, -1]]
            self.check = [[-1, -1], [1, -1]]

    def move_pos(self,new_pos,board):
        dist = self.get_distance(new_pos)
        piece = None
        if new_pos not in self.valid_moves:
            return False, piece
        for move in board:
            if move.get_pos() == new_pos:
                board.remove(move)
                piece = move
        self.pos = new_pos
        return True, piece

    def make_move_pos(self, new_pos):
        self.pos = new_pos

    def get_distance(self,new_pos):
        distance = 0
        if new_pos in self.valid_moves:
            distance = abs(new_pos[1] - self.pos[1])
        return distance

    def find_valid(self,board):
        self.define_moves()
        valid = True
        self.valid_moves = []
        copy = self.pos[:]
        for i in self.moves:
            if i[0] + copy[0] >= 0 and i[0] + copy[0] < 8 and i[1] + copy[1] >= 0 and i[1] + copy[
                1] < 8:
                for j in board:
                    check_pos = j.get_pos()
                    if i[0] + copy[0] == check_pos[0] and i[1] + copy[1] == check_pos[1]:
                        valid = False
                if valid:
                    self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])
        for i in self.check:
            for j in board:
                check_pos = j.get_pos()
                if i[0] + self.pos[0] == check_pos[0] and i[1] + self.pos[1] == check_pos[1]:
                    if self.get_color() != j.get_color():
                        self.valid_moves.append([self.pos[0] + i[0], self.pos[1] + i[1]])

class Knight(Piece):
    def __init__(self, color, pos,type, copy=False):
        super().__init__(color, pos,type, copy)
        self.moves = [[2, 1], [2, -1], [1, 2], [-1, 2], [1, -2], [-2, 1], [-2, -1], [-1, -2]]

    def __deepcopy__(self, memodict={}):
        piece = Knight(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece

    def find_valid(self, board):
        self.valid_moves = []
        for i in self.moves:
            copy = self.pos[:]
            valid = True
            if i[0] + copy[0] >= 0 and i[0] + copy[0] < 8 and i[1] + copy[1] >= 0 and i[1] + copy[1] < 8 and valid:
                for j in board:
                    if [i[0] + copy[0], i[1] + copy[1]] == j.get_pos():
                        if j.get_color() == self.get_color():
                            valid = False
                        else:
                            valid = True
                if valid:
                    self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])

class Bishop(Piece):
    def __init__(self, color, pos,type,copy=False):
        super().__init__(color, pos,type,copy)
        self.moves = [[1,1],[-1,-1],[1,-1],[-1,1]]
    def __deepcopy__(self, memodict={}):
        piece = Bishop(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece


class Castle(Piece):
    def __init__(self, color, pos,type, copy=False):
        super().__init__(color, pos,type, copy)
        self.moves = [[0, 1], [0, -1], [1, 0], [-1,0]]

    def __deepcopy__(self, memodict={}):
        piece = Castle(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece

class Queen(Piece):
    def __init__(self, color, pos,type, copy=False):
        super().__init__(color, pos,type, copy)
        self.moves = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[-1,1],[1,-1]]

    def __deepcopy__(self, memodict={}):
        piece = Queen(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece

class King(Piece):
    def __init__(self, color, pos,type, copy=False):
        super().__init__(color, pos,type, copy)
        self.moves = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[-1,1],[1,-1]]
        self.check = False
        self.castled = False

    def __deepcopy__(self, memodict={}):
        piece = King(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        piece.check = deepcopy(self.check)
        return piece

    def find_valid(self,board):
        copy = self.pos[:]
        self.valid_moves = []
        for i in self.moves:
            valid = True
            if i[0] + copy[0] >= 0 and i[0] + copy[0] < 8 and i[1] + copy[1] >= 0 and i[1] + copy[
                1] < 8:
                for j in board:
                    check_pos = j.get_pos()
                    if i[0] + copy[0] == check_pos[0] and i[1] + copy[1] == check_pos[1]:
                        valid = False
                if valid:
                    self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])
        return self.valid_moves

    def check_check(self,board):
        for i in board:
            if self.pos in i.valid_moves:
                self.check = True
                break
            else:
                self.check = False

    def get_check(self):
        return self.check

class Board():
    def __init__(self,user,computer,type, pieces=None):
        self.pieces = []
        self.user = user
        self.computer = computer
        if (pieces == None):
            self.set_pieces(type)
        else:
            self.pieces = pieces
        self.in_check = {
            "WHITE": False,
            "BLACK": False
        }
        self.history = []

    def set_pieces(self,type):
        if (self.user[0] == 'WHITE'):
            self.pieces = [Castle(self.computer,[0,0],type),Knight(self.computer,[1,0],type),Bishop(self.computer,[2,0],type),Queen(self.computer,[3,0],type),King(self.computer,[4,0],type),Bishop(self.computer,[5,0],type),Knight(self.computer,[6,0],type),Castle(self.computer,[7,0],type),
                           Pawn(self.computer,[0,1],1,type),Pawn(self.computer,[1,1],1,type),Pawn(self.computer,[2,1],1,type),Pawn(self.computer,[3,1],1,type),Pawn(self.computer,[4,1],1,type),Pawn(self.computer,[5,1],1,type),Pawn(self.computer,[6,1],1,type),Pawn(self.computer,[7,1],1,type),
                           Pawn(self.user,[0,6],-1,type),Pawn(self.user,[1,6],-1,type),Pawn(self.user,[2,6],-1,type),Pawn(self.user,[3,6],-1,type),Pawn(self.user,[4,6],-1,type),Pawn(self.user,[5,6],-1,type),Pawn(self.user,[6,6],-1,type),Pawn(self.user,[7,6],-1,type),
                           Castle(self.user,[0,7],type),Knight(self.user,[1,7],type),Bishop(self.user,[2,7],type),Queen(self.user,[3,7],type),King(self.user,[4,7],type),Bishop(self.user,[5,7],type),Knight(self.user,[6,7],type),Castle(self.user,[7,7],type)]
        elif self.user[0] == 'BLACK':
            self.pieces = [Castle(self.computer, [0, 0], type), Knight(self.computer, [1, 0], type),
                           Bishop(self.computer, [2, 0], type), Queen(self.computer, [4, 0], type),
                           King(self.computer, [3, 0], type), Bishop(self.computer, [5, 0], type),
                           Knight(self.computer, [6, 0], type), Castle(self.computer, [7, 0], type),
                           Pawn(self.computer, [0, 1], 1, type), Pawn(self.computer, [1, 1], 1, type),
                           Pawn(self.computer, [2, 1], 1, type), Pawn(self.computer, [3, 1], 1, type),
                           Pawn(self.computer, [4, 1], 1, type), Pawn(self.computer, [5, 1], 1, type),
                           Pawn(self.computer, [6, 1], 1, type), Pawn(self.computer, [7, 1], 1, type),
                           Pawn(self.user, [0, 6], -1, type), Pawn(self.user, [1, 6], -1, type),
                           Pawn(self.user, [2, 6], -1, type), Pawn(self.user, [3, 6], -1, type),
                           Pawn(self.user, [4, 6], -1, type), Pawn(self.user, [5, 6], -1, type),
                           Pawn(self.user, [6, 6], -1, type), Pawn(self.user, [7, 6], -1, type),
                           Castle(self.user, [0, 7], type), Knight(self.user, [1, 7], type),
                           Bishop(self.user, [2, 7], type), Queen(self.user, [4, 7], type),
                           King(self.user, [3, 7], type), Bishop(self.user, [5, 7], type),
                           Knight(self.user, [6, 7], type), Castle(self.user, [7, 7], type)]
    def get_pieces(self):
        return self.pieces

    def init_valid(self,color, basic=False):
        for i in self.pieces:
            s = i.find_valid(self.pieces)
        if not basic:
            self.validate_check(color)

    def validate_check(self,color):
        original_board = deepcopy(self)
        copy_board = deepcopy(self)
        pieces = copy_board.pieces[:]
        for piece in pieces:
            if piece.color[0] == color:
                valid_moves = deepcopy(piece.valid_moves)
                for move in valid_moves:
                    original_pos = deepcopy(piece.pos)
                    moved, removed_piece = copy_board.move_piece(piece.pos, move)
                    copy_board.init_valid(color, True)
                    future_check = copy_board.get_set_check(color)
                    copy_board.reverse_move(move, original_pos, removed_piece)
                    copy_board.init_valid(color, True)
                    if future_check:
                        for i in self.pieces:
                            if i.__class__.__name__ == piece.__class__.__name__ and i.color == piece.color and i.pos == piece.pos:
                                if (move in i.valid_moves):
                                    i.valid_moves.remove(move)

    def get_valid_for_pos(self,pos):
        for i in self.pieces:
            if i.get_pos() == pos:
                return i.valid_moves

    def get_valid(self,pos,new_pos,user):
        for i in self.pieces:
            if i.get_pos() == pos:
                if i.is_valid(new_pos,self.pieces):
                    return True
                else:
                    return False

    def get_piece_from_pos(self,pos):
        for i in self.pieces:
            if i.get_pos == pos:
                return i
        return None

    def move_piece(self,pos,new_pos,real=False):
        moved = False
        piece = None
        for i in self.pieces:
            if i.get_pos() == pos:
                if (new_pos != pos):
                    moved, piece = i.move_pos(new_pos,self.get_pieces())
                    i.moved = True
                    if real:
                        if (isinstance(i, Pawn)):
                            i.define_moves()
                        # TODO -> Add history of moves to be read by stockfish
                        move = convert_pos_to_coord(pos,self.user) + convert_pos_to_coord(new_pos, self.user)
                        print("Move here ", move)
                        self.history.append(move)
            #print(i.__class__.__name__, i.get_color(), i.get_pos(), i.valid_moves)
        return moved, piece

    def reverse_move(self, new_pos, pos, piece):
        for i in self.pieces:
            if i.get_pos() == new_pos:
                if (new_pos != pos):
                    i.make_move_pos(pos)
                    if i.__class__.__name__ == "Pawn":
                        i.moved = False
                    if piece:
                        self.pieces.append(piece)
                    break

    def get_selected(self,pos):
        for i in self.pieces:
            if i.get_pos() == pos:
                return i

    def set_check(self):
        for x in self.pieces:
            color = x.get_color()[0]
            if x.__class__.__name__ == "King":
                x.check_check(self.pieces)
                if color == 'WHITE':
                    self.in_check['WHITE'] = x.get_check()
                else:
                    self.in_check['BLACK'] = x.get_check()

    def get_set_check(self,color):
        self.set_check()
        return self.in_check[color]

    def get_check(self,color):
        return self.in_check[color]

    def get_all_possible_moves(self, color):
        possible_boards = []
        possible_moves = []
        for i in self.pieces:
            if i.color == color:
                for j in i.valid_moves:
                    pos = i.pos[:]
                    new_pos = j[:]
                    moved, piece = self.move_piece(pos, new_pos, False)
                    possible_boards.append(self.convert_board_to_model_format())
                    possible_moves.append([pos, new_pos])
                    self.reverse_move(new_pos, pos, piece)

        return possible_moves, np.array(possible_boards)

    def convert_board_to_model_format(self):
        pawn_board = np.zeros((8, 8))
        rook_board = np.zeros((8, 8))
        bishop_board = np.zeros((8, 8))
        knight_board = np.zeros((8, 8))
        queen_board = np.zeros((8, 8))
        king_board = np.zeros((8, 8))

        for i in self.pieces:
            if isinstance(i, Pawn):
                if i.color == COLOR[WHITE]:
                    pawn_board[i.pos[1]][7-i.pos[0]] = 1
                elif i.color == COLOR[BLACK]:
                    pawn_board[i.pos[1]][7-i.pos[0]] = -1
            elif isinstance(i, Castle):
                if i.color == COLOR[WHITE]:
                    rook_board[i.pos[1]][7-i.pos[0]] = 1
                elif i.color == COLOR[BLACK]:
                    rook_board[i.pos[1]][7-i.pos[0]] = -1
            elif isinstance(i, Bishop):
                if i.color == COLOR[WHITE]:
                    bishop_board[i.pos[1]][7-i.pos[0]] = 1
                elif i.color == COLOR[BLACK]:
                    bishop_board[i.pos[1]][7-i.pos[0]] = -1

            elif isinstance(i, Knight):
                if i.color == COLOR[WHITE]:
                    knight_board[i.pos[1]][7-i.pos[0]] = 1
                elif i.color == COLOR[BLACK]:
                    knight_board[i.pos[1]][7-i.pos[0]] = -1

            elif isinstance(i, Queen):
                if i.color == COLOR[WHITE]:
                    queen_board[i.pos[1]][7-i.pos[0]] = 1
                elif i.color == COLOR[BLACK]:
                    queen_board[i.pos[1]][7-i.pos[0]] = -1

            elif isinstance(i, King):
                if i.color == COLOR[WHITE]:
                    king_board[i.pos[1]][7-i.pos[0]] = 1
                elif i.color == COLOR[BLACK]:
                    king_board[i.pos[1]][7-i.pos[0]] = -1

        return np.stack((rook_board, knight_board, bishop_board, queen_board, king_board, pawn_board), axis=-1)

    # No Mate - 0, Stalemate - 1, Checkmate - 2
    def check_mates(self,color):
        for i in self.pieces:
            if i.color[0] == color:
                if len(i.valid_moves) > 0:
                    return 0
        if self.in_check[color]:
            return 2
        else:
            return 1

class Game():
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
        selected = False
        self.drawStartWindow()
        self.board.init_valid(self.get_turn()[0])
        self.future_board.init_valid(self.get_turn()[0], True)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.opponent == 0 or self.user == self.turn:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        self.board.init_valid(self.get_turn()[0])
                        self.future_board.init_valid(self.get_turn()[0], True)
                        if not selected:
                            cord = self.get_cord(pos)
                            select = self.board.get_selected(cord)
                            print(select)
                            if select != None and select.color == self.turn:
                                self.selected = cord
                                self.valid_moves = self.board.get_valid_for_pos(cord)
                                print("Valid Moves: ",self.valid_moves)
                                selected = True
                        else:
                            new_cord = self.get_cord(pos)
                            moved, piece = self.future_board.move_piece(cord,new_cord)
                            if self.board.get_valid(cord,new_cord,self.get_turn()[0]) and moved:
                                self.board.move_piece(cord,new_cord,real=True)
                                #print("Future Check: ", self.future_board.get_set_check(self.get_turn()[1]))
                                #self.board.init_valid(self.get_turn()[0], True)
                                self.switch_turn()
                                self.board.init_valid(self.get_turn()[0], False)
                                print("Future Check: ", self.board.get_set_check(self.get_turn()[0]))
                                self.game_state = self.board.check_mates(self.get_turn()[0])
                            selected = False
                            self.selected = None
                            self.valid_moves = None
                        self.future_board.pieces = deepcopy(self.board.pieces)
                        self.drawWindow()
                else:
                    print("hist",self.board.history)
                    """if len(self.board.history) > 1:
                        stockfish.make_moves_from_current_position(self.board.history[-2:])
                    elif len(self.board.history) > 0:
                        stockfish.make_moves_from_current_position(self.board.history[-1:])
                    best_move = stockfish.get_best_move()"""
                    #print("best move 1", best_move)
                    best_move = self.get_best_move(self.computer)
                    print("best move 2", best_move)
                    #coord, new_coord = convert_coord_to_pos(best_move, self.user)
                    self.board.move_piece(best_move[0], best_move[1], real=True)
                    self.board.init_valid(self.get_turn()[0], True)
                    self.switch_turn()
                    self.board.init_valid(self.get_turn()[0], False)
                    print("Future Check: ", self.board.get_set_check(self.get_turn()[0]))
                    self.game_state = self.board.check_mates(self.get_turn()[0])
                    self.drawWindow()
            if (self.game_state != 0):
                break
            self.time.tick(60)


if __name__ == "__main__":
    Game().start_menu()

