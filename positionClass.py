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

    def get_piece(self, board_x: int, board_y: int) -> str:
        "Returns the piece given the coordinates"
        return self.pos_array[board_x + 8*board_y]
    
    def get_location(self, piece: str) -> tuple[int, int]:
        "Return first occurring coordinate of the piece"
        ind = self.pos_array.index(piece)
        return ind%8, ind//8
    
    def set_piece(self, board_x: int, board_y: int, piece: str = '') -> None:
        self.pos_array[board_x + 8*board_y] = piece
    
    def get_highlights(self, board_x: int, board_y: int) -> list[tuple[int, int]]:
        "Returns a list of coordinates to which the piece can move"
        squares = []
        for x, y in product(range(8), repeat=2):
            if self.is_move_possible(board_x, board_y, x, y):
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
        return ForsythEdwardsNotation(FEN_notation = notation[1:])

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
    
    def move(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int, 
             promote_to: str | None = None, available_squares: list[tuple[int, int]] | None = None) -> bool:
        "Moves the piece if it is posible. Returns True if moved successfully, False otherwise"
        if self.is_move_possible(board_x1, board_y1, board_x2, board_y2, available_squares):
            if self.get_piece(board_x1, board_y1).lower() == 'p':
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1
            if self.is_white_to_move == False:
                self.fullmove_number += 1
            self.raw_move(board_x1, board_y1, board_x2, board_y2, promote_to)
            self.is_white_to_move = not self.is_white_to_move
            #self.history.append()
            return True
        return False
    
    def raw_move(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int, promote_to: str | None = None) -> None:
        "Makes a move without any checks and does not pass the move"
        piece = self.get_piece(board_x1, board_y1)
        self.set_piece(board_x2, board_y2, piece)
        self.set_piece(board_x1, board_y1, '')
        self.handle_en_passant(board_x1, board_y1, board_x2, board_y2, piece)
        self.handle_castling(board_x1, board_x2, piece)
        self.handle_promotion(board_x2, board_y2, promote_to)
    
    def handle_en_passant(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int, piece: str) -> None:
        if piece == 'P':
            if (board_x2, board_y2) == self.en_passant:
                self.set_piece(board_x2, board_y2 + 1)
            elif board_y2 - board_y1 == -2:
                self.en_passant = (board_x1, 5)
                return None
        elif piece == 'p':
            if (board_x2, board_y2) == self.en_passant:
                self.set_piece(board_x2, board_y2 - 1)
            elif board_y2 - board_y1 == 2:
                self.en_passant = (board_x1, 2)
                return None
        self.en_passant = None

    def handle_castling(self, board_x1: int, board_x2: int, piece: str) -> None:
        if piece == 'R':
            if board_x1 == 0:
                self.castles['Q'] = False
            elif board_x1 == 7:
                self.castles['K'] = False
        elif piece == 'r':
            if board_x1 == 0:
                self.castles['q'] = False
            elif board_x1 == 7:
                self.castles['k'] = False
        elif piece == 'K':
            self.castles['Q'] = False
            self.castles['K'] = False
            if board_x1 == 4:
                if board_x2 == 2:
                    self.set_piece(3, 7, 'R')
                    self.set_piece(0, 7, '')
                elif board_x2 == 6:
                    self.set_piece(5, 7, 'R')
                    self.set_piece(7, 7, '')
        elif piece == 'k':
            self.castles['q'] = False
            self.castles['k'] = False
            if board_x1 == 4:
                if board_x2 == 2:
                    self.set_piece(3, 0, 'r')
                    self.set_piece(0, 0, '')
                elif board_x2 == 6:
                    self.set_piece(5, 0, 'r')
                    self.set_piece(7, 0, '')

    def handle_promotion(self, board_x2: int, board_y2: int, promote_to: str | None) -> None:
        if promote_to != None:
            self.set_piece(board_x2, board_y2, promote_to)

    def is_move_possible(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int, available_squares: list[tuple[int, int]] | None = None) -> bool:
        "Returns True if the move can be made, False otherwise"
        if available_squares != None:
            return ((board_x2, board_y2) in available_squares)
        if not(0 <= board_x1 < 8 and 0 <= board_y1 < 8 and 0 <= board_x2 < 8 and 0 <= board_y2 < 8):
            return False
        piece = self.get_piece(board_x1, board_y1)
        if piece == '':
            return False
        if piece.isupper() != self.is_white_to_move:
            return False
        if (self.get_piece(board_x2, board_y2) != '' and 
            self.is_white_to_move == self.get_piece(board_x2, board_y2).isupper()):
            return False
        return (self.ismovable(board_x1, board_y1, board_x2, board_y2, piece) and 
            not(self.is_moved_into_check(board_x1, board_y1, board_x2, board_y2)))
    
    def ispromotion(self, board_y2: int, piece: str) -> bool:
        return (board_y2 == 0 and piece == 'P' or 
                board_y2 == 7 and piece == 'p')

    def is_moved_into_check(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        "Returns True if the king will be in check after the given move, False otherwise"
        saved_states = self.pos_array.copy(), self.castles.copy(), self.en_passant #saves the state of the game
        self.raw_move(board_x1, board_y1, board_x2, board_y2) #makes a move
        ischecked = self.ischecked()
        self.pos_array, self.castles, self.en_passant = saved_states #returns position to its initial state
        return ischecked

    "'ismovable' functions return True if the piece can make the given move, False otherwise"
    def ismovable(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int, piece: str) -> bool:
        match piece:
            case 'P':       return self.ismovable_wpawn(board_x1, board_y1, board_x2, board_y2)
            case 'p':       return self.ismovable_bpawn(board_x1, board_y1, board_x2, board_y2)
            case 'N' | 'n': return self.ismovable_knight(board_x1, board_y1, board_x2, board_y2)
            case 'B' | 'b': return self.ismovable_bishop(board_x1, board_y1, board_x2, board_y2)
            case 'R' | 'r': return self.ismovable_rook(board_x1, board_y1, board_x2, board_y2)
            case 'Q' | 'q': return self.ismovable_queen(board_x1, board_y1, board_x2, board_y2)
            case 'K' | 'k': return self.ismovable_king(board_x1, board_y1, board_x2, board_y2)
            case _: return False
    
    def ismovable_wpawn(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        if board_x1 == board_x2 and self.get_piece(board_x2, board_y2) == '':
            if board_y2 - board_y1 == -1: 
                return True
            elif board_y1 == 6 and board_y2 == 4 and self.get_piece(board_x2, 5) == '': 
                return True
        elif (board_y2 - board_y1 == -1 and abs(board_x2 - board_x1) == 1):
            if self.get_piece(board_x2, board_y2) != '': 
                return True
            elif (board_x2, board_y2) == self.en_passant: 
                return True
        return False

    def ismovable_bpawn(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        if board_x1 == board_x2 and self.get_piece(board_x2, board_y2) == '':
            if board_y2 - board_y1 == 1: 
                return True
            elif board_y1 == 1 and board_y2 == 3 and self.get_piece(board_x2, 2) == '': 
                return True
        elif (board_y2 - board_y1 == 1 and abs(board_x2 - board_x1) == 1):
            if self.get_piece(board_x2, board_y2) != '': 
                return True
            elif (board_x2, board_y2) == self.en_passant: 
                return True
        return False

    def ismovable_knight(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        if ((abs(board_x2 - board_x1) == 1 and abs(board_y2 - board_y1) == 2) or 
            (abs(board_y2 - board_y1) == 1 and abs(board_x2 - board_x1) == 2)):
            return True
        return False

    def ismovable_bishop(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        if abs(board_x2 - board_x1) != abs(board_y2 - board_y1): 
            return False
        x_direction = int(copysign(1, board_x2-board_x1))
        y_direction = int(copysign(1, board_y2-board_y1))
        for x, y in zip(range(board_x1 + x_direction, board_x2, x_direction), 
                        range(board_y1 + y_direction, board_y2, y_direction)):
            if self.get_piece(x, y) != '': 
                return False
        return True

    def ismovable_rook(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        if board_x1 == board_x2:
            y_direction = int(copysign(1, board_y2-board_y1))
            for y in range(board_y1 + y_direction, board_y2, y_direction):
                if self.get_piece(board_x1, y) != '': 
                    return False
            return True
        elif board_y1 == board_y2:
            x_direction = int(copysign(1, board_x2-board_x1))
            for x in range(board_x1 + x_direction, board_x2, x_direction):
                if self.get_piece(x, board_y1) != '': 
                    return False
            return True
        return False

    def ismovable_queen(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        if (self.ismovable_rook(board_x1, board_y1, board_x2, board_y2) or 
            self.ismovable_bishop(board_x1, board_y1, board_x2, board_y2)):
            return True
        return False

    def ismovable_king(self, board_x1: int, board_y1: int, board_x2: int, board_y2: int) -> bool:
        if (-1 <= board_x2 - board_x1 <= 1) and (-1 <= board_y2 - board_y1 <= 1): 
            return True
        if self.isattacked(board_x1, board_y1):
            return False
        if self.is_white_to_move and self.get_piece(4, 7) == 'K' and board_y2 == 7:
            if (board_x2 == 2 and self.castles['Q'] and self.get_piece(0, 7) == 'R' and 
                self.get_piece(1, 7) == '' and self.get_piece(3, 7) == '' and
                not(self.isattacked(3, 7))): 
                return True
            elif (board_x2 == 6 and self.castles['K'] and self.get_piece(7, 7) == 'R' and 
                  self.get_piece(5, 7) == ''and
                  not(self.isattacked(5, 7))): 
                return True
        elif not(self.is_white_to_move) and self.get_piece(4, 0) == 'k' and board_y2 == 0:
            if (board_x2 == 2 and self.castles['q'] and self.get_piece(0, 0) == 'r' and
                self.get_piece(1, 0) == '' and self.get_piece(3, 0) == ''and
                not(self.isattacked(3, 0))): 
                return True
            elif (board_x2 == 6 and self.castles['k'] and self.get_piece(7, 0) == 'r' and 
                  self.get_piece(5, 0) == ''and 
                  not(self.isattacked(5, 0))): 
                return True
        return False

    "'isatacked' functions return True if the given square is attacked by an enemy piece, False otherwise"
    def isattacked(self, board_x: int, board_y: int) -> bool:
        return (self.isattacked_by_pawn(board_x, board_y) or 
                self.isattacked_by_knight(board_x, board_y) or 
                self.isattacked_by_bishop_queen(board_x, board_y) or 
                self.isattacked_by_rook_queen(board_x, board_y) or 
                self.isattacked_by_king(board_x, board_y))
    
    def isattacked_by_pawn(self, board_x: int, board_y: int) -> bool:
        if self.is_white_to_move:
            return self.isattacked_by_bpawn(board_x, board_y)
        else:
            return self.isattacked_by_wpawn(board_x, board_y)

    def isattacked_by_wpawn(self, board_x: int, board_y: int) -> bool:
        if board_y == 7:
            return False
        if board_x - 1 >= 0 and self.get_piece(board_x-1, board_y+1) == 'P':
            return True
        if board_x + 1 <= 7 and self.get_piece(board_x+1, board_y+1) == 'P':
            return True
        return False

    def isattacked_by_bpawn(self, board_x: int, board_y: int) -> bool:
        if board_y == 0:
            return False
        if board_x - 1 >= 0 and self.get_piece(board_x-1, board_y-1) == 'p':
            return True
        if board_x + 1 <= 7 and self.get_piece(board_x+1, board_y-1) == 'p':
            return True
        return False

    def isattacked_by_knight(self, board_x: int, board_y: int) -> bool:
        if self.is_white_to_move:
            knight = 'n'
        else:
            knight = 'N'
        for dy in [-2, -1, 1, 2]:
            for dx in [-2, -1, 1, 2]:
                if (abs(dx) != abs(dy) and 
                    0 <= board_x + dx < 8 and 0 <= board_y + dy < 8 and
                    self.get_piece(board_x + dx, board_y + dy) == knight):
                    return True
        return False

    def isattacked_by_bishop_queen(self, board_x: int, board_y: int) -> bool:
        if self.is_white_to_move:
            bishop = 'b'
            queen = 'q'
        else:
            bishop = 'B'
            queen = 'Q'
        for x, y in zip(range(board_x-1, -1, -1), 
                        range(board_y-1, -1, -1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(board_x+1, 8, 1), 
                        range(board_y-1, -1, -1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(board_x-1, -1, -1), 
                        range(board_y+1, 8, 1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(board_x+1, 8, 1), 
                        range(board_y+1, 8, 1)):
            piece = self.get_piece(x, y)
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        return False

    def isattacked_by_rook_queen(self, board_x: int, board_y: int) -> bool:
        if self.is_white_to_move:
            rook = 'r'
            queen = 'q'
        else:
            rook = 'R'
            queen = 'Q'
        for y in range(board_y+1, 8, 1):
            piece = self.get_piece(board_x, y)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for y in range(board_y-1, -1, -1):
            piece = self.get_piece(board_x, y)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for x in range(board_x+1, 8, 1):
            piece = self.get_piece(x, board_y)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for x in range(board_x-1, -1, -1):
            piece = self.get_piece(x, board_y)
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        return False

    def isattacked_by_king(self, board_x: int, board_y: int) -> bool:
        if self.is_white_to_move:
            king = 'k'
        else:
            king = 'K'
        for y in range(max(0, board_y-1), min(board_y + 1, 7) + 1):
            for x in range(max(0, board_x-1), min(board_x + 1, 7) + 1):
                if self.get_piece(x, y) == king:
                    return True
        return False