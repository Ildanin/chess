from math import copysign
from notation import ForsythEdwardsNotation, board_to_algebraic
from itertools import product

class Position:
    def __init__(self, init_position: ForsythEdwardsNotation): #add PortableGameNotation
        self.history = [init_position]
        self.pos_array = init_position.get_position_array()
        self.is_white_to_move = init_position.get_is_white_to_move()
        self.castles = init_position.get_castles()
        self.en_passant = init_position.get_en_passant()
        self.halfmove_clock = init_position.get_halfmove_clock()
        self.fullmove_number = init_position.get_fullmove_number()
    
    def __iter__(self):
        return iter(self.pos_array)

    def get_piece(self, file: int, rank: int) -> str:
        "Returns the piece given the coordinates"
        return self.pos_array[file + 8*rank]
    
    def get_location(self, piece: str) -> tuple[int, int]:
        "Return first occurring coordinate of the piece"
        ind = self.pos_array.index(piece)
        return ind%8, ind//8
    
    def set_piece(self, file: int, rank: int, piece: str = '') -> None:
        self.pos_array[file + 8*rank] = piece
    
    def get_highlights(self, file: int, rank: int) -> list[tuple[int, int]]:
        "Returns a list of coordinates to which the piece can move"
        squares = []
        for x, y in product(range(8), repeat=2):
            if self.is_move_possible(file, rank, x, y):
                squares.append((x, y))
        return squares
    
    def get_FEN(self) -> ForsythEdwardsNotation:
        notation = ''
        for i, piece in enumerate(self.pos_array):
            if (i)%8 == 0:
                notation += '/'
            if piece == '':
                if notation[-1].isdigit():
                    notation = notation[:-1] + str(int(notation[-1]) + 1)
                else:
                    notation += '1'
            else:
                notation += piece
        if self.is_white_to_move:
            notation += ' w '
        else:
            notation += ' b '
        for castle_type in self.castles:
            if self.castles[castle_type]:
                notation += castle_type
        if notation[-1] == '':
            notation += '-'
        if self.en_passant:
            notation += board_to_algebraic(*self.en_passant)
        else:
            notation += ' - '
        notation += f'{self.halfmove_clock} {self.fullmove_number}'
        return ForsythEdwardsNotation(FEN = notation[1:])

    def ischecked(self) -> bool:
        if self.is_white_to_move:
            return self.isattacked(*self.get_location('K'))
        else:
            return self.isattacked(*self.get_location('k'))

    def isdraw(self) -> bool:
        if self.ischecked():
            return False
        if self.pos_array.count('') == 62:
            return True
        for x1, y1, x2, y2 in product(range(8), repeat=4):
            if self.is_move_possible(x1, y1, y2, x2) == True:
                return False 
        return True

    def ischeckmate(self) -> bool:
        if self.is_white_to_move:
            king_x, king_y = self.get_location('K')
        else:
            king_x, king_y = self.get_location('k')
        if not self.isattacked(king_x, king_y):
            return False
        for x1, y1, x2, y2 in product(range(8), repeat=4):
            if self.is_move_possible(x1, y1, y2, x2) == True:
                return False
        return True

    def get_possible_moves(self) -> list[tuple[int, int, int, int]]:
        moves = []
        for x1, y1, x2, y2 in product(range(8), repeat=4):
            if self.is_move_possible(x1, y1, y2, x2) == True:
                moves.append((x1, y1, y2, x2))
        return moves
    
    def move(self, file1: int, rank1: int, file2: int, rank2: int, 
             promote_to: str = 'q', available_squares: list[tuple[int, int]] | None = None) -> bool:
        "Moves the piece if it is posible. Returns True if moved successfully, False otherwise"
        if self.is_move_possible(file1, rank1, file2, rank2, available_squares):
            if self.get_piece(file1, rank1).lower() == 'p':
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1
            if self.is_white_to_move == False:
                self.fullmove_number += 1
            self.raw_move(file1, rank1, file2, rank2, promote_to)
            self.is_white_to_move = not self.is_white_to_move
            #self.history.append()
            return True
        return False
    
    def raw_move(self, file1: int, rank1: int, file2: int, rank2: int, promote_to: str | None = None) -> None:
        "Makes a move without any checks and does not pass the move"
        piece = self.get_piece(file1, rank1)
        self.set_piece(file2, rank2, piece)
        self.set_piece(file1, rank1, '')
        self.handle_en_passant(file1, rank1, file2, rank2, piece)
        self.handle_castling(file1, file2, piece)
        self.handle_promotion(file2, rank2, promote_to)
    
    def handle_en_passant(self, file1: int, rank1: int, file2: int, rank2: int, piece: str) -> None:
        if piece == 'P':
            if (file2, rank2) == self.en_passant:
                self.set_piece(file2, rank2 + 1)
            elif rank2 - rank1 == -2:
                self.en_passant = (file1, 5)
                return None
        elif piece == 'p':
            if (file2, rank2) == self.en_passant:
                self.set_piece(file2, rank2 - 1)
            elif rank2 - rank1 == 2:
                self.en_passant = (file1, 2)
                return None
        self.en_passant = None

    def handle_castling(self, file1: int, file2: int, piece: str) -> None:
        if piece == 'R':
            if file1 == 0:
                self.castles['Q'] = False
            elif file1 == 7:
                self.castles['K'] = False
        elif piece == 'r':
            if file1 == 0:
                self.castles['q'] = False
            elif file1 == 7:
                self.castles['k'] = False
        elif piece == 'K':
            self.castles['Q'] = False
            self.castles['K'] = False
            if file1 == 4:
                if file2 == 2:
                    self.set_piece(3, 7, 'R')
                    self.set_piece(0, 7, '')
                elif file2 == 6:
                    self.set_piece(5, 7, 'R')
                    self.set_piece(7, 7, '')
        elif piece == 'k':
            self.castles['q'] = False
            self.castles['k'] = False
            if file1 == 4:
                if file2 == 2:
                    self.set_piece(3, 0, 'r')
                    self.set_piece(0, 0, '')
                elif file2 == 6:
                    self.set_piece(5, 0, 'r')
                    self.set_piece(7, 0, '')

    def handle_promotion(self, file2: int, rank2: int, promote_to: str | None) -> None:
        if promote_to != None:
            self.set_piece(file2, rank2, promote_to)

    def is_move_possible(self, file1: int, rank1: int, file2: int, rank2: int, available_squares: list[tuple[int, int]] | None = None) -> bool:
        "Returns True if the move can be made, False otherwise"
        if available_squares != None:
            return ((file2, rank2) in available_squares)
        if not(0 <= file1 < 8 and 0 <= rank1 < 8 and 0 <= file2 < 8 and 0 <= rank2 < 8):
            return False
        piece = self.get_piece(file1, rank1)
        if piece == '':
            return False
        if piece.isupper() != self.is_white_to_move:
            return False
        if (self.get_piece(file2, rank2) != '' and 
            self.is_white_to_move == self.get_piece(file2, rank2).isupper()):
            return False
        return (self.ismovable(file1, rank1, file2, rank2, piece) and 
            not(self.is_moved_into_check(file1, rank1, file2, rank2)))
    
    def ispromotion(self, rank2: int, piece: str) -> bool:
        return (rank2 == 0 and piece == 'P' or 
                rank2 == 7 and piece == 'p')

    def is_moved_into_check(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        "Returns True if the king will be in check after the given move, False otherwise"
        saved_states = self.pos_array.copy(), self.castles.copy(), self.en_passant #saves the state of the game
        self.raw_move(file1, rank1, file2, rank2) #makes a move
        ischecked = self.ischecked()
        self.pos_array, self.castles, self.en_passant = saved_states #returns position to its initial state
        return ischecked

    "'ismovable' functions return True if the piece can make the given move, False otherwise"
    def ismovable(self, file1: int, rank1: int, file2: int, rank2: int, piece: str) -> bool:
        match piece:
            case 'P':       return self.ismovable_wpawn(file1, rank1, file2, rank2)
            case 'p':       return self.ismovable_bpawn(file1, rank1, file2, rank2)
            case 'N' | 'n': return self.ismovable_knight(file1, rank1, file2, rank2)
            case 'B' | 'b': return self.ismovable_bishop(file1, rank1, file2, rank2)
            case 'R' | 'r': return self.ismovable_rook(file1, rank1, file2, rank2)
            case 'Q' | 'q': return self.ismovable_queen(file1, rank1, file2, rank2)
            case 'K' | 'k': return self.ismovable_king(file1, rank1, file2, rank2)
            case _: return False
    
    def ismovable_wpawn(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        if file1 == file2 and self.get_piece(file2, rank2) == '':
            if rank2 - rank1 == -1: 
                return True
            elif rank1 == 6 and rank2 == 4 and self.get_piece(file2, 5) == '': 
                return True
        elif (rank2 - rank1 == -1 and abs(file2 - file1) == 1):
            if self.get_piece(file2, rank2) != '': 
                return True
            elif (file2, rank2) == self.en_passant: 
                return True
        return False

    def ismovable_bpawn(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        if file1 == file2 and self.get_piece(file2, rank2) == '':
            if rank2 - rank1 == 1: 
                return True
            elif rank1 == 1 and rank2 == 3 and self.get_piece(file2, 2) == '': 
                return True
        elif (rank2 - rank1 == 1 and abs(file2 - file1) == 1):
            if self.get_piece(file2, rank2) != '': 
                return True
            elif (file2, rank2) == self.en_passant: 
                return True
        return False

    def ismovable_knight(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        if ((abs(file2 - file1) == 1 and abs(rank2 - rank1) == 2) or 
            (abs(rank2 - rank1) == 1 and abs(file2 - file1) == 2)):
            return True
        return False

    def ismovable_bishop(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        if abs(file2 - file1) != abs(rank2 - rank1): 
            return False
        x_direction = int(copysign(1, file2-file1))
        y_direction = int(copysign(1, rank2-rank1))
        for x, y in zip(range(file1 + x_direction, file2, x_direction), 
                        range(rank1 + y_direction, rank2, y_direction)):
            if self.get_piece(x, y) != '': 
                return False
        return True

    def ismovable_rook(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        if file1 == file2:
            y_direction = int(copysign(1, rank2-rank1))
            for y in range(rank1 + y_direction, rank2, y_direction):
                if self.get_piece(file1, y) != '': 
                    return False
            return True
        elif rank1 == rank2:
            x_direction = int(copysign(1, file2-file1))
            for x in range(file1 + x_direction, file2, x_direction):
                if self.get_piece(x, rank1) != '': 
                    return False
            return True
        return False

    def ismovable_queen(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        if (self.ismovable_rook(file1, rank1, file2, rank2) or 
            self.ismovable_bishop(file1, rank1, file2, rank2)):
            return True
        return False

    def ismovable_king(self, file1: int, rank1: int, file2: int, rank2: int) -> bool:
        if (-1 <= file2 - file1 <= 1) and (-1 <= rank2 - rank1 <= 1): 
            return True
        if self.isattacked(file1, rank1):
            return False
        if self.is_white_to_move and self.get_piece(4, 7) == 'K' and rank2 == 7:
            if (file2 == 2 and self.castles['Q'] and self.get_piece(0, 7) == 'R' and 
                self.get_piece(1, 7) == '' and self.get_piece(3, 7) == '' and
                not(self.isattacked(3, 7))): 
                return True
            elif (file2 == 6 and self.castles['K'] and self.get_piece(7, 7) == 'R' and 
                  self.get_piece(5, 7) == ''and
                  not(self.isattacked(5, 7))): 
                return True
        elif not(self.is_white_to_move) and self.get_piece(4, 0) == 'k' and rank2 == 0:
            if (file2 == 2 and self.castles['q'] and self.get_piece(0, 0) == 'r' and
                self.get_piece(1, 0) == '' and self.get_piece(3, 0) == ''and
                not(self.isattacked(3, 0))): 
                return True
            elif (file2 == 6 and self.castles['k'] and self.get_piece(7, 0) == 'r' and 
                  self.get_piece(5, 0) == ''and 
                  not(self.isattacked(5, 0))): 
                return True
        return False

    "'isatacked' functions return True if the given square is attacked by an enemy piece, False otherwise"
    def isattacked(self, file: int, rank: int) -> bool:
        return (self.isattacked_by_pawn(file, rank) or 
                self.isattacked_by_knight(file, rank) or 
                self.isattacked_by_bishop_queen(file, rank) or 
                self.isattacked_by_rook_queen(file, rank) or 
                self.isattacked_by_king(file, rank))
    
    def isattacked_by_pawn(self, file: int, rank: int) -> bool:
        if self.is_white_to_move:
            return self.isattacked_by_bpawn(file, rank)
        else:
            return self.isattacked_by_wpawn(file, rank)

    def isattacked_by_wpawn(self, file: int, rank: int) -> bool:
        if rank == 7:
            return False
        if file - 1 >= 0 and self.get_piece(file-1, rank+1) == 'P':
            return True
        if file + 1 <= 7 and self.get_piece(file+1, rank+1) == 'P':
            return True
        return False

    def isattacked_by_bpawn(self, file: int, rank: int) -> bool:
        if rank == 0:
            return False
        if file - 1 >= 0 and self.get_piece(file-1, rank-1) == 'p':
            return True
        if file + 1 <= 7 and self.get_piece(file+1, rank-1) == 'p':
            return True
        return False

    def isattacked_by_knight(self, file: int, rank: int) -> bool:
        if self.is_white_to_move:
            knight = 'n'
        else:
            knight = 'N'
        for dy in [-2, -1, 1, 2]:
            for dx in [-2, -1, 1, 2]:
                if (abs(dx) != abs(dy) and 
                    0 <= file + dx < 8 and 0 <= rank + dy < 8 and
                    self.get_piece(file + dx, rank + dy) == knight):
                    return True
        return False

    def isattacked_by_bishop_queen(self, file: int, rank: int) -> bool:
        if self.is_white_to_move:
            bishop = 'b'
            queen = 'q'
        else:
            bishop = 'B'
            queen = 'Q'
        for x, y in zip(range(file-1, -1, -1), 
                        range(rank-1, -1, -1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(file+1, 8, 1), 
                        range(rank-1, -1, -1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(file-1, -1, -1), 
                        range(rank+1, 8, 1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(file+1, 8, 1), 
                        range(rank+1, 8, 1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        return False

    def isattacked_by_rook_queen(self, file: int, rank: int) -> bool:
        if self.is_white_to_move:
            rook = 'r'
            queen = 'q'
        else:
            rook = 'R'
            queen = 'Q'
        for y in range(rank+1, 8, 1):
            piece = self.get_piece(file, y)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for y in range(rank-1, -1, -1):
            piece = self.get_piece(file, y)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for x in range(file+1, 8, 1):
            piece = self.get_piece(x, rank)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for x in range(file-1, -1, -1):
            piece = self.get_piece(x, rank)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        return False

    def isattacked_by_king(self, file: int, rank: int) -> bool:
        if self.is_white_to_move:
            king = 'k'
        else:
            king = 'K'
        for y in range(max(0, rank-1), min(rank + 1, 7) + 1):
            for x in range(max(0, file-1), min(file + 1, 7) + 1):
                if self.get_piece(x, y) == king:
                    return True
        return False