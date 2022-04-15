import pygame
import math
import sys
import warnings

warnings.filterwarnings(action='ignore',message="libpng warning: bKGD: invalid")

pygame.init()

WIDTH = 600
HEIGHT = 600

WHITE = (255,255,255)
BLACK  = (0,0,0)

COLOR = {
    WHITE: ['WHITE',(255,255,255)],
    BLACK: ['BLACK',(0,0,0)]
}


class Piece():
    def __init__(self,color,pos,type):
        self.color = color
        self.taken = False
        self.pos = pos
        self.img = self.get_img()
        self.rect = self.get_rect()
        self.valid_moves = []
        self.future = type

    def is_taken(self):
        return self.taken

    def get_pos(self):
        return self.pos

    def get_color(self):
        return self.color

    def get_img(self):
        return pygame.image.load("Images\\"+str(self.color[0][0]) + str(self.__class__.__name__)+".png")

    def get_rect(self):
        return pygame.Rect(self.pos[0]*40,self.pos[1]*40,40,40)

    def move_pos(self,new_pos,board):
        if new_pos not in self.valid_moves:
            return False
        for move in board:
            if move.get_pos() == new_pos:
                board.remove(move)
        self.pos = new_pos
        return True

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
    def __init__(self, color, pos,direction,type):
        super().__init__(color, pos,type)
        self.direction = direction
        self.moves = []
        self.check = []
        self.moved = False

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
        if new_pos not in self.valid_moves:
            return False
        for move in board:
            if move.get_pos() == new_pos:
                board.remove(move)
        self.pos = new_pos
        return True

    def get_distance(self,new_pos):
        distance = 0
        if new_pos in self.valid_moves:
            distance = abs(new_pos[1] - self.pos[1])
            print(distance)
            print("!")
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
                        if self.get_color() == j.get_color():
                            valid = False
                if valid:
                    self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])
        for i in self.check:
            for j in board:
                check_pos = j.get_pos()
                if i[0] + self.pos[0] == check_pos[0] and i[1] + self.pos[1] == check_pos[1]:
                    self.valid_moves.append([self.pos[0] + i[0], self.pos[1] + i[1]])

class Knight(Piece):
    def __init__(self, color, pos,type):
        super().__init__(color, pos,type)
        self.moves = [[2, 1], [2, -1], [1, 2], [-1, 2], [1, -2], [-2, 1], [-2, -1], [-1, -2]]

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
    def __init__(self, color, pos,type):
        super().__init__(color, pos,type)
        self.moves = [[1,1],[-1,-1],[1,-1],[-1,1]]


class Castle(Piece):
    def __init__(self, color, pos,type):
        super().__init__(color, pos,type)
        self.moves = [[0, 1], [0, -1], [1, 0], [-1,0]]

class Queen(Piece):
    def __init__(self, color, pos,type):
        super().__init__(color, pos,type)
        self.moves = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[-1,1],[1,-1]]

class King(Piece):
    def __init__(self, color, pos,type):
        super().__init__(color, pos,type)
        self.moves = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[-1,1],[1,-1]]
        self.check = False

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
    def __init__(self,user,computer,type):
        self.pieces = []
        self.user = user
        self.computer = computer
        self.set_pieces(type)
        self.in_check = {
            WHITE: False,
            BLACK: False
        }

    def set_pieces(self,type):
        self.pieces = [Castle(self.user,[0,0],type),Knight(self.user,[1,0],type),Bishop(self.user,[2,0],type),Queen(self.user,[3,0],type),King(self.user,[4,0],type),Bishop(self.user,[5,0],type),Knight(self.user,[6,0],type),Castle(self.user,[7,0],type),
                       Pawn(self.user,[0,1],1,type),Pawn(self.user,[1,1],1,type),Pawn(self.user,[2,1],1,type),Pawn(self.user,[3,1],1,type),Pawn(self.user,[4,1],1,type),Pawn(self.user,[5,1],1,type),Pawn(self.user,[6,1],1,type),Pawn(self.user,[7,1],1,type),
                       Pawn(self.computer,[0,6],-1,type),Pawn(self.computer,[1,6],-1,type),Pawn(self.computer,[2,6],-1,type),Pawn(self.computer,[3,6],-1,type),Pawn(self.computer,[4,6],-1,type),Pawn(self.computer,[5,6],-1,type),Pawn(self.computer,[6,6],-1,type),Pawn(self.computer,[7,6],-1,type),
                       Castle(self.computer,[0,7],type),Knight(self.computer,[1,7],type),Bishop(self.computer,[2,7],type),Queen(self.computer,[3,7],type),King(self.computer,[4,7],type),Bishop(self.computer,[5,7],type),Knight(self.computer,[6,7],type),Castle(self.computer,[7,7],type)]

    def get_pieces(self):
        return self.pieces

    def init_valid(self):
        print("Valid")
        for i in self.pieces:
            s = i.find_valid(self.pieces)
            print(i.__class__.__name__, i.get_color(), i.get_pos(), i.valid_moves)

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
        for i in self.pieces:
            if i.get_pos() == pos:
                if (new_pos != pos):
                    moved = i.move_pos(new_pos,self.get_pieces())
            elif i.get_pos() == new_pos and real:
                i.moved = True
            print(i.__class__.__name__, i.get_color(), i.get_pos(), i.valid_moves)
        return moved

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

    def get_check(self,color):
        self.set_check()
        print("check:",self.in_check)
        print(color)
        print(self.in_check[color])
        return self.in_check[color]


class Game():
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS',30)
        self.user,self.computer = self.get_user()
        self.turn = COLOR[WHITE]
        self.board = Board(self.user,self.computer,False)
        self.future_board = Board(self.user,self.computer,True)
        self.screen =  pygame.display.set_mode((WIDTH,HEIGHT))
        self.time = pygame.time.Clock()
        self.selected = None
        self.valid_moves = None

    def drawWindow(self):
        self.screen.fill(WHITE)
        pieces = self.board.get_pieces()
        for i in range(8):
            for j in range(8):
                if i % 2 == 0 and j % 2 == 0 or i % 2 == 1 and j % 2 ==1:
                    pygame.draw.rect(self.screen,(153, 102, 51),(i*40,j*40,40,40))
                else:
                    pygame.draw.rect(self.screen, (255, 204, 153), (i * 40, j * 40, 40, 40))

        if self.selected != None:
            pygame.draw.rect(self.screen,(255,0,0),(self.selected[0]*40,self.selected[1]*40,40,40),2)
        if self.valid_moves != None:
            print(self.valid_moves)
            for move in self.valid_moves:
                pygame.draw.rect(self.screen, (0, 255, 0), (move[0] * 40, move[1] * 40, 40, 40), 2)
        for i in pieces:
            self.screen.blit(i.get_img(), i.get_rect())

        text_surface = self.font.render(self.turn[0], False, (0, 0, 0))
        self.screen.blit(text_surface,(400,0))
        pygame.display.update()


    def get_user(self):
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
            cord[i] = math.floor(pos[i]/40)
        return cord

    def main(self):
        self.drawWindow()
        selected = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.board.init_valid()
                    self.future_board.init_valid()
                    if not selected:
                        cord = self.get_cord(pos)
                        select = self.board.get_selected(cord)
                        print(select)
                        if select != None and select.color == self.turn:
                            self.selected = cord
                            self.valid_moves = self.board.get_valid_for_pos(cord)
                            print(self.valid_moves)
                            selected = True
                    else:
                        new_cord = self.get_cord(pos)
                        moved = self.future_board.move_piece(cord,new_cord)
                        future_check = self.future_board.get_check(self.get_turn()[0])
                        if not self.board.get_valid(cord,new_cord,self.get_turn()[0]) and not future_check and moved:
                            self.board.move_piece(cord,new_cord,real=True)
                            self.switch_turn()
                        selected = False
                        self.selected = None
                        self.valid_moves = None
                    self.future_board.pieces = self.board.pieces
                    self.drawWindow()
            self.time.tick(60)



if __name__ == "__main__":
    Game().main()

