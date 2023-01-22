from Utils import *
from copy import deepcopy

class Piece():
    """
    Superclass used to represent a piece

    Attributes
    ----------

    valid_moves: List[List[Int]]
        list of valid positions piece can move from then to e.g. [x1,y1,x2,y2]

    taken: Bool
        true if piece has been taken
    """

    def __init__(self, color, pos, type, copy):
        """
        Paramters
        ---------

        :param color: Int
            0 -> represents black
            1 -> represents white
        :param pos: [Int, Int]
            represents x and y position of piece
        :param type:

        :param copy: Bool
            determines whether object requires pygame rendering
        """
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
        filename = "Images\\Chess_" + INITIALS[str(self.__class__.__name__)] + COLOR_INITIAL[self.color[0]] + "t45.svg"
        img = load_and_scale_svg(filename, SQUARE_SIZE / 45)
        return img

    def load_rect(self):
        return pygame.Rect(self.pos[0] * SQUARE_SIZE, self.pos[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

    def get_img(self):
        return self.img

    def get_rect(self):
        return pygame.Rect(self.pos[0] * SQUARE_SIZE, self.pos[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

    def move_pos(self, new_pos, board):
        """
        Update current position to new position if move is valid

        :param new_pos: List[int]
            New position to move to in [x,y] format
        :param board: List[Piece]
            List of pieces of opposite color
        :return: (Bool, List[int])
            true if move is made and position to which piece has been moved to
        """
        piece = None
        if new_pos not in self.valid_moves:
            return False, piece
        for move in board:
            if move.get_pos() == new_pos:
                piece = move
                board.remove(move)
        self.pos = new_pos
        return True, piece

    def force_move(self, new_pos):
        self.pos = new_pos

    def is_valid(self, new_pos, board):
        if new_pos not in [x[:2] for x in self.valid_moves]:
            return False
        else:
            return True

    def update_valid_moves(self, board):
        """
        Update valid moves

        :param board: List[Piece]
            list of pieces on current board
        :return:
        """
        self.valid_moves = []
        for i in self.moves:
            copy = self.pos[:]
            valid = True
            once = True
            while i[0] + copy[0] >= 0 and i[0] + copy[0] < 8 and i[1] + copy[1] >= 0 and i[1] + copy[1] < 8 and valid:
                if valid and not once:
                    valid = False
                for j in board:
                    if [i[0] + copy[0], i[1] + copy[1]] == j.get_pos() and once:
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
    """
    Class representing Pawn using Piece superclass
    """

    def __init__(self, color, pos, direction, type, copy=False):
        """

        :param color: Int
            0 -> represents black
            1 -> represents white
        :param pos: List[Int]
            [x,y] coordinate of pawn
        :param direction: Int
            -1 -> pawn is going upwards
            1 -> pawn is going downwards
        :param type:

        moves: List[List[Int]]
            represents default moves which can be taken

        check: List[List[Int]]
            represents moves which can be made if conditions are met

        moved: Bool
            true if pawn has moved

        en_passant: Bool
            true if pawn can be taken via en passant

        """
        super().__init__(color, pos, type, copy)
        self.direction = direction
        self.moves = []
        self.check = []
        self.valid_moves = []
        self.moved = False
        self.en_passant = False

    def __deepcopy__(self, memodict={}):
        piece = Pawn(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.direction), deepcopy(self.future), True)
        piece.moves = deepcopy(self.moves)
        piece.check = deepcopy(self.check)
        piece.moved = deepcopy(self.moved)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece

    def define_moves(self):
        """
        Initialises moves depending on pawn direction and if the pawn has moved
        :return:
        """
        if self.direction == 1:
            if not self.moved:
                self.moves = [[0, 1], [0, 2]]
            else:
                self.moves = [[0, 1]]
            self.check = [[1, 1], [-1, 1]]
        else:
            if not self.moved:
                self.moves = [[0, -1], [0, -2]]
            else:
                self.moves = [[0, -1]]
            self.check = [[-1, -1], [1, -1]]

    def move_pos(self, new_pos, board):
        """
        Update position of pawn with reference to board

        :param new_pos: List[int]
            new position to move to
        :param board: List[Piece]
            pieces that currently on the board
        :return: ( Bool, Piece | None )
            true if piece has been moved and Piece represents the piece that has been removed
        """
        dist = self.get_distance(new_pos)
        piece = None
        if new_pos not in [x[:2] for x in self.valid_moves]:
            return False, piece
        else:
            new_pos = [x for x in self.valid_moves if x[:2] == new_pos][0]
        for move in board:
            if move.get_pos() == new_pos[:2]:
                board.remove(move)
                piece = move
            try:
                if new_pos[2] == "EN PASSANT":
                    if abs(move.get_pos()[1] - new_pos[1]) == 1 and move.get_pos()[0] == new_pos[0]:
                        board.remove(move)

            except:
                pass

        if abs(self.pos[1] - new_pos[1]) == 2 and not self.moved:
            self.en_passant = True

        self.pos = new_pos[:2]
        return True, piece

    def force_move(self, new_pos):
        self.pos = new_pos

    def get_distance(self, new_pos):
        distance = 0
        if new_pos in self.valid_moves:
            distance = abs(new_pos[1] - self.pos[1])
        return distance

    def update_valid_moves(self, board):
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

                if i[0] + self.pos[0] == check_pos[0] and self.pos[1] == check_pos[1] and isinstance(j, Pawn):
                    if self.get_color() != j.get_color() and j.en_passant:
                        self.valid_moves.append([self.pos[0] + i[0], self.pos[1] + i[1], "EN PASSANT", j.get_pos()[:]])


class Knight(Piece):
    """
    Class represents Knight using superclass Piece
    """

    def __init__(self, color, pos, type, copy=False):
        super().__init__(color, pos, type, copy)
        self.moves = [[2, 1], [2, -1], [1, 2], [-1, 2], [1, -2], [-2, 1], [-2, -1], [-1, -2]]

    def __deepcopy__(self, memodict={}):
        piece = Knight(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece

    def update_valid_moves(self, board):
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
    """
    Class used to represent Bishop with superclass Piece
    """

    def __init__(self, color, pos, type, copy=False):
        super().__init__(color, pos, type, copy)
        self.moves = [[1, 1], [-1, -1], [1, -1], [-1, 1]]

    def __deepcopy__(self, memodict={}):
        piece = Bishop(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece


class Castle(Piece):
    """
    Class used to represent Castle with superclass Piece
    """

    def __init__(self, color, pos, type, copy=False):
        super().__init__(color, pos, type, copy)
        self.moves = [[0, 1], [0, -1], [1, 0], [-1, 0]]

    def __deepcopy__(self, memodict={}):
        piece = Castle(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece


class Queen(Piece):
    """
    Class used to represent Queen with superclass Piece
    """

    def __init__(self, color, pos, type, copy=False):
        super().__init__(color, pos, type, copy)
        self.moves = [[0, 1], [1, 0], [1, 1], [0, -1], [-1, 0], [-1, -1], [-1, 1], [1, -1]]

    def __deepcopy__(self, memodict={}):
        piece = Queen(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        return piece


class King(Piece):
    """
    Class used to represent King with superclass Piece
    """

    def __init__(self, color, pos, type, copy=False):
        super().__init__(color, pos, type, copy)
        self.moves = [[0, 1], [1, 0], [1, 1], [0, -1], [-1, 0], [-1, -1], [-1, 1], [1, -1]]
        self.check = False

        self.castle_moves = [[2, 0], [-2, 0]]
        self.castled = False
        self.can_castle = True

    def __deepcopy__(self, memodict={}):
        piece = King(deepcopy(self.color), deepcopy(self.pos), deepcopy(self.future), True)
        piece.valid_moves = deepcopy(self.valid_moves)
        piece.check = deepcopy(self.check)
        return piece

    def update_valid_moves(self, board):
        copy = self.pos[:]
        self.valid_moves = []
        for i in self.moves:
            valid = True
            if i[0] + copy[0] >= 0 and i[0] + copy[0] < 8 and i[1] + copy[1] >= 0 and i[1] + copy[
                1] < 8:
                for j in board:
                    check_pos = j.get_pos()
                    if [i[0] + copy[0], i[1] + copy[1]] == j.get_pos():
                        if j.get_color() == self.get_color():
                            valid = False
                        else:
                            valid = True
                if valid:
                    self.valid_moves.append([copy[0] + i[0], copy[1] + i[1]])
        if not self.castled and self.can_castle:
            for i in self.castle_moves:
                direction = i[0] // 2
                start_idx = copy[0] + direction
                if direction == -1:
                    end_idx = 0
                elif direction == 1:
                    end_idx = 7
                rook_pos = [end_idx, copy[1]]
                valid = True
                empty_positions = [[x, copy[1]] for x in range(start_idx, end_idx, direction)]
                for j in board:
                    if j.get_pos() in empty_positions:
                        valid = False
                    if j.get_pos() == rook_pos:
                        if not isinstance(j, Castle):
                            valid = False
                if valid:
                    self.valid_moves.append([copy[0] + i[0], copy[1], "CASTLING", rook_pos])
        return self.valid_moves

    def move_pos(self, new_pos, board):
        piece = None
        if new_pos not in [x[:2] for x in self.valid_moves]:
            return False, piece
        try:
            for i in self.valid_moves:
                if i[0] == new_pos[0] and i[1] == new_pos[1]:
                    status = i[2]
                    rook_pos = i[3]
        except IndexError:
            status = "NOT CASTLE"
        if status == "CASTLING":
            self.pos = [new_pos[0], new_pos[1]]
            for j in board:
                if j.get_pos() == rook_pos:
                    if rook_pos[0] == 0:
                        direction = 1
                    elif rook_pos[0] == 7:
                        direction = -1
                    j.pos = [self.pos[0] + direction, rook_pos[1]]
            self.can_castle = False
            self.castled = True
        else:
            for move in board:
                if move.get_pos() == new_pos:
                    piece = move
                    board.remove(move)
            self.pos = new_pos
        return True, piece

    # 7 -> king_pos - 1 , 0 -> king_pos + 1

    # -1 -> 0, 1 -> 7
    def check_if_in_check(self, board):
        """
        Updates class if King is currently in check

        :param board: List[Piece]
            list of opposite coloured pieces
        :return:
        """
        for i in board:
            if self.pos in i.valid_moves:
                self.check = True
                break
            else:
                self.check = False

    def get_check(self):
        return self.check