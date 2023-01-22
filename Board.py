from Utils import *
from Piece import *
import numpy as np

class Board():
    """
    Class used to represent the entirity of the board

    Attributes
    ----------

    pieces: List[Piece]
    user: int
    computer: int
    in_check: {str: int}
    history: List[List[str]]
    """
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
        """
        Update valid moves for all pieces of color

        :param color: int
            represents color of piece to validate
        :param basic: Bool
            whether to check if a piece is in check
        :return:
        """
        for i in self.pieces:
            s = i.update_valid_moves(self.pieces)
        if not basic:
            self.validate_check(color)

    def validate_check(self,color):
        """
        Remove moves that result in current coloured King going into check

        :param color: int
            represents color of piece to validate
        :return:
        """
        original_board = deepcopy(self)
        copy_board = deepcopy(self)
        pieces = copy_board.pieces[:]
        for piece in pieces:
            if piece.color[0] == color:
                valid_moves = deepcopy(piece.valid_moves)
                # 4,5,6
                # 4,3,2
                if isinstance(piece, King):
                    bi_castling = [list(range(piece.pos[0],x[3][0], (x[0] - piece.pos[0])//abs(x[0] - piece.pos[0]))) for x in valid_moves if len(x) > 2]
                    for idx,direction in enumerate(bi_castling):
                        for position in direction:
                            original_pos = deepcopy(piece.pos)
                            copy_board.make_move_pos(original_pos, [position, original_pos[1]])
                            copy_board.init_valid(color, True)
                            future_check = copy_board.get_set_check(color)
                            copy_board.make_move_pos([position, original_pos[1]], original_pos)
                            copy_board.init_valid(color, True)
                            if future_check:
                                for i in self.pieces:
                                    if i.__class__.__name__ == piece.__class__.__name__ and i.color == piece.color and i.pos == piece.pos:
                                        castle_move = [x for x in valid_moves if len(x) > 2]
                                        move = castle_move[idx]
                                        for x in i.valid_moves:
                                            if [x[0],x[1]] == move[:2]:
                                                i.valid_moves.remove(move)


                for move in valid_moves:
                    original_pos = deepcopy(piece.pos)
                    moved, removed_piece = copy_board.move_piece(piece.pos, move)
                    if len(move) > 2:
                        if move[2] == "CASTLING":
                            status = move[2]
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
        """
        Get valid moves for Piece at position pos

        :param pos: List[int]
        :return: List[List[int]]
        """
        for i in self.pieces:
            if i.get_pos() == pos:
                return i.valid_moves

    def get_valid(self,pos,new_pos,user):
        """
        Check whether move is valid for piece at position pos

        :param pos: List[int]
        :param new_pos: List[int]
        :param user:
        :return: Bool
        """
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

    def make_move_pos(self, pos, new_pos):
        for i in self.pieces:
            if i.get_pos() == pos:
                i.pos = new_pos

    def move_piece(self,pos,new_pos,real=False):
        moved = False
        piece = None
        for i in self.pieces:
            if isinstance(i, Pawn):
                i.en_passant = False
            if i.get_pos() == pos:
                if (new_pos != pos):
                    moved, piece = i.move_pos(new_pos,self.get_pieces())
                    i.moved = True
                    if real:
                        if (isinstance(i, Pawn)):
                            i.define_moves()
                        if i.get_pos()[1] % 7 == 0:
                            self.pieces.remove(i)
                            self.pieces.append(Queen(i.color, i.pos, False))

                        move = convert_pos_to_coord(pos,self.user) + convert_pos_to_coord(new_pos, self.user)
                        print("Move here ", move)
                        self.history.append(move)
            #print(i.__class__.__name__, i.get_color(), i.get_pos(), i.valid_moves)
        return moved, piece

    def reverse_move(self, new_pos, pos, piece):
        for i in self.pieces:
            if i.get_pos() == new_pos:
                if (new_pos != pos):
                    i.force_move(pos)
                    if i.__class__.__name__ == "Pawn":
                        i.moved = False
                    if isinstance(i, King):
                        try:
                            if new_pos[2] == "CASTLING":
                                i.castled = False
                                i.can_castle = True
                                for j in self.pieces:
                                    if isinstance(j, Castle):
                                        if j.get_pos()[0] == i.get_pos()[0] + 1:
                                            j.force_move([0, j.get_pos()[1]])
                                        elif j.get_pos()[0] == i.get_pos()[0] - 1:
                                            j.force_move([7, j.get_pos()[1]])
                        except:
                            pass
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
                x.check_if_in_check(self.pieces)
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
