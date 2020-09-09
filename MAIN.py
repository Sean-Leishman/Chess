import pygame
import math
import sys
import copy

pygame.init()

WIDTH = 600
HEIGHT = 600

COLOR = {
    'WHITE': ['WHITE',(255,255,255)],
    'BLACK': ['BLACK',(0,0,0)]
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
        return "Images\\"+str(self.color[0][0]) + str(self.__class__.__name__)+".png"

    def get_rect(self):
        return (self.pos[0]*40,self.pos[1]*40,40,40)

    def move_pos(self,new_pos,board):
        if new_pos in self.valid_moves:
            for move in board:
                if move.get_pos() == new_pos:
                    board.remove(move)
            self.pos = new_pos

    def move_old_pos(self,new_pos,board):
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
            while i[0] + copy[0] >= 0 and i[0] + copy[0] < 8 and i[1] + copy[1] >= 0 and i[1] + copy[1] < 8 and valid:
                for j in board:
                    if [i[0] + copy[0],i[1]+copy[1]] == j.get_pos():
                        if j.get_color() == self.get_color():
                            valid = False
                        elif j.get_color() != None and j.get_color() != self.get_color():
                            self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])
                            valid = False
                        else:
                            valid = True
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
        if new_pos in self.valid_moves:
            for move in board:
                if move.get_pos() == new_pos:
                    board.remove(move)
            self.pos = new_pos

    def get_distance(self,new_pos):
        distance = None
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
                        elif j.get_color() != None and j.get_color() != self.get_color():
                            self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])
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
            'WHITE': False,
            'BLACK': False
        }
        self.in_checkMate = {
            'WHITE': False,
            'BLACK': False
        }

    def set_pieces(self,type):
        self.pieces = [Castle(self.user,[0,0],type),Knight(self.user,[1,0],type),Bishop(self.user,[2,0],type),Queen(self.user,[3,0],type),King(self.user,[4,0],type),Bishop(self.user,[5,0],type),Knight(self.user,[6,0],type),Castle(self.user,[7,0],type),
                       Pawn(self.user,[0,1],1,type),Pawn(self.user,[1,1],1,type),Pawn(self.user,[2,1],1,type),Pawn(self.user,[3,1],1,type),Pawn(self.user,[4,1],1,type),Pawn(self.user,[5,1],1,type),Pawn(self.user,[6,1],1,type),Pawn(self.user,[7,1],1,type),
                       Pawn(self.computer,[0,6],-1,type),Pawn(self.computer,[1,6],-1,type),Pawn(self.computer,[2,6],-1,type),Pawn(self.computer,[3,6],-1,type),Pawn(self.computer,[4,6],-1,type),Pawn(self.computer,[5,6],-1,type),Pawn(self.computer,[6,6],-1,type),Pawn(self.computer,[7,6],-1,type),
                       Castle(self.computer,[0,7],type),Knight(self.computer,[1,7],type),Bishop(self.computer,[2,7],type),Queen(self.computer,[3,7],type),King(self.computer,[4,7],type),Bishop(self.computer,[5,7],type),Knight(self.computer,[6,7],type),Castle(self.computer,[7,7],type)]

    def get_pieces(self):
        return self.pieces

    def init_valid(self):
        print("RRValid")
        for i in self.pieces:
            i.find_valid(self.pieces)
            print(i.__class__.__name__, i.get_color(), i.get_pos(), i.valid_moves)

    def get_valid(self,pos,new_pos,user):
        for i in self.pieces:
            if i.get_pos() == pos:
                if i.is_valid(new_pos,self.pieces):
                    return True
                else:
                    return False

    def move_piece(self,pos,new_pos):
        print("Move")
        for i in self.pieces:
            if i.get_pos() == pos:
                i.move_pos(new_pos,self.get_pieces())
            print(i.__class__.__name__, i.get_color(), i.get_pos(), i.valid_moves)

    def move_old_piece(self,pos,new_pos):
        print("Move")
        for i in self.pieces:
            if i.get_pos() == pos:
                i.move_old_pos(new_pos,self.get_pieces())
            print(i.__class__.__name__, i.get_color(), i.get_pos(), i.valid_moves)


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

    def set_checkMate(self,color):
        if self.get_check(color):
            self.in_checkMate[color] = True
            for x in self.pieces:
                old_pos = x.get_pos()
                for y in x.valid_moves:
                    self.move_piece(old_pos,y)
                    if not self.get_check(color):
                        self.in_checkMate[color] = False
                    self.move_old_piece(y,old_pos)



    def get_check(self,color):
        self.set_check()
        print("check:",self.in_check)
        print(color)
        print(self.in_check[color])
        return self.in_check[color]

    def get_check_mate(self,color):
        self.set_checkMate(color)
        print(color)
        print(self.in_checkMate)
        return self.in_checkMate[color]



class Game():
    def __init__(self):
        pygame.init()
        self.user,self.computer = self.get_user()
        self.turn = COLOR['WHITE']
        self.board = Board(self.user,self.computer,False)
        self.future_board = Board(self.user,self.computer,True)
        self.screen =  pygame.display.set_mode((WIDTH,HEIGHT))
        self.time = pygame.time.Clock()

    def drawWindow(self):
        self.screen.fill((255,255,255))
        pieces = self.board.get_pieces()
        for i in range(8):
            for j in range(8):
                if i % 2 == 0 and j % 2 == 0 or i % 2 == 1 and j % 2 ==1:
                    pygame.draw.rect(self.screen,(153, 102, 51),(i*40,j*40,40,40))
                else:
                    pygame.draw.rect(self.screen, (255, 204, 153), (i * 40, j * 40, 40, 40))
        for i in pieces:
            self.screen.blit(pygame.image.load(i.get_img()),pygame.Rect(i.get_rect()))
        pygame.display.update()


    def get_user(self):
        return COLOR['BLACK'],COLOR['WHITE']

    def switch_turn(self):
        if self.turn == COLOR['WHITE']:
            self.turn = COLOR['BLACK']
        else:
            self.turn = COLOR['WHITE']

    def get_turn(self):
        return self.turn

    def get_oppTurn(self):
        if self.turn == COLOR['WHITE']:
            return COLOR['BLACK']
        else:
            return COLOR['WHITE']

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
                    print('board')
                    self.board.init_valid()
                    print('futureboard')
                    self.future_board.init_valid()
                    if not selected:
                        cord = self.get_cord(pos)
                        select = self.board.get_selected(cord)
                        if select != None and select.color == self.turn:
                            selected = True
                    else:
                        new_cord = self.get_cord(pos)
                        print('futureboard')
                        self.future_board.move_piece(cord,new_cord)
                        self.future_board.init_valid()
                        future_check = self.future_board.get_check(self.get_turn()[0])
                        print("run2",self.board.get_valid(cord,new_cord,self.get_turn()[0]))
                        print("run3",future_check)
                        print('run4',self.get_turn())
                        if self.board.get_valid(cord,new_cord,self.get_turn()[0]) and not future_check:
                            print("run")
                            self.board.move_piece(cord,new_cord)
                            self.switch_turn()
                            if self.future_board.get_check_mate(self.get_turn()[0]):
                                print('Break')
                                break
                        else:
                            self.future_board.pieces = copy.deepcopy(self.board.pieces)
                            self.future_board.in_check = copy.deepcopy(self.board.in_check)
                        selected = False
                    # Check for checkmate



                self.drawWindow()
            self.time.tick(60)



if __name__ == "__main__":
    Game().main()

