from math import copysign
from notation.fen import ForsythEdwardsNotation
from notation.square import BoardSquare, BoardMove
from itertools import product
from typing import Generator

KINGS_FILE = 4
QUEEN_ROOKS_FILE = 0
KING_ROOKS_FILE = 7

WHITE_BACK_RANK = 7
BLACK_BACK_RANK = 0

WHITE_KING_SQUARE = BoardSquare(KINGS_FILE, WHITE_BACK_RANK)
BLACK_KING_SQUARE = BoardSquare(KINGS_FILE, BLACK_BACK_RANK)

class Position:
    def __init__(self, init_position: ForsythEdwardsNotation = ForsythEdwardsNotation()):
        self.init_position = init_position
        self.history: list[BoardMove] = []
        self.pos_array = init_position.get_position_array()
        self.white_move = init_position.get_white_move()
        self.castles = init_position.get_castles()
        self.en_passant = init_position.get_en_passant()
        self.halfmove_clock = init_position.get_halfmove_clock()
        self.fullmove_number = init_position.get_fullmove_number()
    
    def __iter__(self):
        return iter(self.pos_array)
    
    def reset(self) -> None:
        self.__init__(self.init_position)
    
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
        if self.white_move:
            notation += ' w '
        else:
            notation += ' b '
        for castle_type in self.castles:
            if self.castles[castle_type]:
                notation += castle_type
        if notation[-1] == ' ':
            notation += '-'
        if self.en_passant:
            notation += self.en_passant.get_algebraic()
        else:
            notation += ' - '
        notation += f'{self.halfmove_clock} {self.fullmove_number}'
        return ForsythEdwardsNotation(FEN = notation[1:])
    
    def get_piece(self, square: BoardSquare) -> str:
        "Returns the piece given the square"
        return self.pos_array[square.id]
    
    def get_rank(self, rank: int) -> list[str]:
        return self.pos_array[8*rank : 8*(rank+1)]
    
    def set_piece(self, square: BoardSquare, piece: str = '') -> None:
        self.pos_array[square.id] = piece
    
    def locate(self, piece: str) -> BoardSquare:
        "Return first occurring square of the piece"
        ind = self.pos_array.index(piece)
        return BoardSquare(ind%8, ind//8)
    
    def get_legal_squares(self, start: BoardSquare) -> Generator[BoardSquare]:
        "Returns a list of square to which the piece can move"
        piece = self.get_piece(start)
        if piece.isupper() != self.white_move:
            return
        for target in self.getsquares(start, piece):
            if (self.get_piece(target) != '' and 
                self.white_move == self.get_piece(target).isupper()):
                continue
            if not(self.is_moved_into_check(BoardMove(start, target))):
                yield target
    
    def get_legal_moves(self) -> Generator[BoardMove]:
        for x, y in product(range(8), repeat=2):
            start = BoardSquare(x, y)
            for target in self.get_legal_squares(start):
                yield BoardMove(start, target)
    
    def ischecked(self) -> bool:
        if self.white_move:
            return self.isattacked(self.locate('K'))
        else:
            return self.isattacked(self.locate('k'))
    
    def isdraw(self) -> bool:
        if self.ischecked():
            return False
        if self.pos_array.count('') == 62:
            return True
        if any(self.get_legal_moves()):
            return False
        return True
    
    def ischeckmate(self) -> bool:
        if not self.ischecked():
            return False
        if any(self.get_legal_moves()):
            return False
        return True
    
    def move(self, move: BoardMove, promote_to: str | None = None, available_squares: list[BoardSquare] | None = None) -> bool:
        "Moves the piece if it is posible. Returns True if moved successfully, False otherwise"
        if not(self.is_move_possible(move, available_squares)):
            return False
        if self.get_piece(move.start).lower() == 'p':
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        if self.white_move == False:
            self.fullmove_number += 1
        self.raw_move(move, promote_to)
        self.white_move = not self.white_move
        self.history.append(move)
        return True
    
    def raw_move(self, move: BoardMove, promote_to: str | None = None) -> None:
        "Makes a move without any checks and does not pass the move"
        piece = self.get_piece(move.start)
        self.set_piece(move.target, piece)
        self.set_piece(move.start, '')
        self.handle_en_passant(move, piece)
        self.handle_castling(move.file1, move.file2, piece)
        self.handle_promotion(move.target, piece, promote_to)
    
    def handle_en_passant(self, move: BoardMove, piece: str) -> None:
        if piece == 'P':
            if move.target == self.en_passant:
                self.set_piece(move.target.shift(0, 1))
            elif move.get_dy() == -2:
                self.en_passant = BoardSquare(move.file1, 5)
                return None
        elif piece == 'p':
            if move.target == self.en_passant:
                self.set_piece(move.target.shift(0, -1))
            elif move.get_dy() == 2:
                self.en_passant = BoardSquare(move.file1, 2)
                return None
        self.en_passant = None
    
    def handle_castling(self, file1: int, file2: int, piece: str) -> None:
        if piece == 'R':
            if file1 == QUEEN_ROOKS_FILE:
                self.castles['Q'] = False
            elif file1 == KING_ROOKS_FILE:
                self.castles['K'] = False
        elif piece == 'r':
            if file1 == QUEEN_ROOKS_FILE:
                self.castles['q'] = False
            elif file1 == KING_ROOKS_FILE:
                self.castles['k'] = False
        elif piece == 'K':
            self.castles['Q'] = False
            self.castles['K'] = False
            if file1 == KINGS_FILE:
                if file2 == 2:
                    self.set_piece(BoardSquare(3, 7), 'R')
                    self.set_piece(BoardSquare(0, 7), '')
                elif file2 == 6:
                    self.set_piece(BoardSquare(5, 7), 'R')
                    self.set_piece(BoardSquare(7, 7), '')
        elif piece == 'k':
            self.castles['q'] = False
            self.castles['k'] = False
            if file1 == KINGS_FILE:
                if file2 == 2:
                    self.set_piece(BoardSquare(3, 0), 'r')
                    self.set_piece(BoardSquare(0, 0), '')
                elif file2 == 6:
                    self.set_piece(BoardSquare(5, 0), 'r')
                    self.set_piece(BoardSquare(7, 0), '')
    
    def handle_promotion(self, square: BoardSquare, piece: str, promote_to: str | None) -> None:
        if promote_to != None:
            self.set_piece(square, promote_to)
        elif piece == 'P' and square.rank == 0:
            self.set_piece(square, 'Q')
        elif piece == 'p' and square.rank == 7:
            self.set_piece(square, 'q')
    
    def is_move_possible(self, move: BoardMove, available_squares: list[BoardSquare] | None = None) -> bool:
        "Returns True if the move can be made, False otherwise"
        if available_squares != None:
            return(move.target in available_squares)
        if not(move.start.isinrange() and move.target.isinrange()):
            return False
        piece = self.get_piece(move.start)
        if piece == '':
            return False
        if piece.isupper() != self.white_move:
            return False
        if (self.get_piece(move.target) != '' and 
            self.white_move == self.get_piece(move.target).isupper()):
            return False
        return(self.ismovable(move, piece) and 
           not(self.is_moved_into_check(move)))
    
    def ispromotion(self, rank2: int, piece: str) -> bool:
        return(rank2 == 0 and piece == 'P' or 
               rank2 == 7 and piece == 'p')
    
    def is_moved_into_check(self, move: BoardMove) -> bool:
        "Returns True if the king will be in check after the given move, False otherwise"
        saved_states = self.pos_array.copy(), self.castles.copy(), self.en_passant #saves the state of the game
        self.raw_move(move) #makes a move
        ischecked = self.ischecked()
        self.pos_array, self.castles, self.en_passant = saved_states #returns position to its initial state
        return ischecked
    
    def ismovable(self, move: BoardMove, piece: str) -> bool:
        "Return True if the piece can make the given move, False otherwise"
        match piece:
            case 'P':       return self.ismovable_wpawn(move)
            case 'p':       return self.ismovable_bpawn(move)
            case 'N' | 'n': return self.ismovable_knight(move)
            case 'B' | 'b': return self.ismovable_bishop(move)
            case 'R' | 'r': return self.ismovable_rook(move)
            case 'Q' | 'q': return self.ismovable_queen(move)
            case 'K' | 'k': return self.ismovable_king(move)
            case _: return False
    
    def ismovable_wpawn(self, move: BoardMove) -> bool:
        if move.get_dx() == 0 and self.get_piece(move.target) == '':
            if move.get_dy() == -1: 
                return True
            if move.rank1 == 6 and move.rank2 == 4 and self.get_piece(BoardSquare(move.file2, 5)) == '': 
                return True
        elif (move.get_dy() == -1 and abs(move.get_dx()) == 1):
            if self.get_piece(move.target) != '': 
                return True
            if move.target == self.en_passant: 
                return True
        return False
    
    def ismovable_bpawn(self, move: BoardMove) -> bool:
        if move.get_dx() == 0 and self.get_piece(move.target) == '':
            if move.get_dy() == 1: 
                return True
            if move.rank1 == 1 and move.rank2 == 3 and self.get_piece(BoardSquare(move.file2, 2)) == '': 
                return True
        elif (move.get_dy() == 1 and abs(move.get_dx()) == 1):
            if self.get_piece(move.target) != '': 
                return True
            if move.target == self.en_passant: 
                return True
        return False
    
    def ismovable_knight(self, move: BoardMove) -> bool:
        return((abs(move.get_dx()) == 1 and abs(move.get_dy()) == 2) or 
               (abs(move.get_dy()) == 1 and abs(move.get_dx()) == 2))
    
    def ismovable_bishop(self, move: BoardMove) -> bool:
        if abs(move.get_dx()) != abs(move.get_dy()): 
            return False
        x_direction = int(copysign(1, move.get_dx()))
        y_direction = int(copysign(1, move.get_dy()))
        for x, y in zip(range(move.file1 + x_direction, move.file2, x_direction), 
                        range(move.rank1 + y_direction, move.rank2, y_direction)):
            if self.get_piece(BoardSquare(x, y)) != '': 
                return False
        return True
    
    def ismovable_rook(self, move: BoardMove) -> bool:
        if move.get_dx() == 0:
            y_direction = int(copysign(1, move.get_dy()))
            for y in range(move.rank1 + y_direction, move.rank2, y_direction):
                if self.get_piece(BoardSquare(move.file1, y)) != '': 
                    return False
            return True
        if move.get_dy() == 0:
            x_direction = int(copysign(1, move.get_dx()))
            for x in range(move.file1 + x_direction, move.file2, x_direction):
                if self.get_piece(BoardSquare(x, move.rank1)) != '': 
                    return False
            return True
        return False
    
    def ismovable_queen(self, move: BoardMove) -> bool:
        return(self.ismovable_rook(move) or 
               self.ismovable_bishop(move))
    
    def ismovable_king(self, move: BoardMove) -> bool:
        if (-1 <= move.get_dx() <= 1) and (-1 <= move.get_dy() <= 1): 
            return True
        if self.isattacked(move.start):
            return False
        if self.white_move and move.rank2 == WHITE_BACK_RANK:
            if (move.file2 == 2 and self.castles['Q'] and self.get_rank(WHITE_BACK_RANK)[:5] == ['R', '', '', '', 'K'] and 
                not(self.isattacked(BoardSquare(3, WHITE_BACK_RANK)))): 
                return True
            if (move.file2 == 6 and self.castles['K'] and self.get_rank(WHITE_BACK_RANK)[4:] == ['K', '', '', 'R'] and 
                not(self.isattacked(BoardSquare(5, WHITE_BACK_RANK)))): 
                return True
        elif not(self.white_move) and move.rank2 == BLACK_BACK_RANK:
            if (move.file2 == 2 and self.castles['q'] and self.get_rank(BLACK_BACK_RANK)[:5] == ['r', '', '', '', 'k'] and 
                not(self.isattacked(BoardSquare(3, BLACK_BACK_RANK)))): 
                return True
            if (move.file2 == 6 and self.castles['k'] and self.get_rank(BLACK_BACK_RANK)[4:] == ['k', '', '', 'r'] and 
                not(self.isattacked(BoardSquare(5, BLACK_BACK_RANK)))): 
                return True
        return False
    
    def isattacked(self, square: BoardSquare) -> bool:
        "Returns True if the given square is attacked by an enemy piece, False otherwise"
        if self.white_move:
            enemy_pieces = ['n', 'b', 'r', 'q', 'k']
        else:
            enemy_pieces = ['N', 'B', 'R', 'Q', 'K']
        return(self.isattacked_by_pawn(square) or 
               self.isattacked_by_knight(square, enemy_pieces[0]) or 
               self.isattacked_by_bishop_queen(square, enemy_pieces[1], enemy_pieces[3]) or 
               self.isattacked_by_rook_queen(square, enemy_pieces[2], enemy_pieces[3]) or 
               self.isattacked_by_king(square, enemy_pieces[4]))
    
    def isattacked_by_pawn(self, square: BoardSquare) -> bool:
        if self.white_move:
            return self.isattacked_by_bpawn(square)
        else:
            return self.isattacked_by_wpawn(square)
    
    def isattacked_by_wpawn(self, square: BoardSquare) -> bool:
        if square.rank == 7:
            return False
        if square.file > 0 and self.get_piece(square.shift(-1, 1)) == 'P':
            return True
        if square.file < 7 and self.get_piece(square.shift(1, 1)) == 'P':
            return True
        return False
    
    def isattacked_by_bpawn(self, square: BoardSquare) -> bool:
        if square.rank == 0:
            return False
        if square.file > 0 and self.get_piece(square.shift(-1, -1)) == 'p':
            return True
        if square.file < 7 and self.get_piece(square.shift(1, -1)) == 'p':
            return True
        return False
    
    def isattacked_by_knight(self, square: BoardSquare, knight: str) -> bool:
        return any(self.getcandidates_knight(square, knight))
    
    def isattacked_by_bishop_queen(self, square: BoardSquare, bishop: str, queen: str) -> bool:
        return any(self.get_piece(attack_square) == bishop or 
                   self.get_piece(attack_square) == queen 
                   for attack_square in self.getsquares_bishop(square))
    
    def isattacked_by_rook_queen(self, square: BoardSquare, rook: str, queen: str) -> bool:
        return any(self.get_piece(attack_square) == rook or 
                   self.get_piece(attack_square) == queen 
                   for attack_square in self.getsquares_rook(square))
    
    def isattacked_by_king(self, square: BoardSquare, king: str) -> bool:
        return any(self.getcandidates_king(square, king))
    
    def getcandidates(self, square: BoardSquare, piece: str) -> Generator[BoardSquare]:
        "Returns the list of squares from wich the piece can be moved to the given square"
        match piece:
            case 'P':       return self.getcandidates_wpawn(square)
            case 'p':       return self.getcandidates_bpawn(square)
            case 'N' | 'n': return self.getcandidates_knight(square, piece)
            case 'B' | 'b': return self.getcandidates_bishop(square, piece)
            case 'R' | 'r': return self.getcandidates_rook(square, piece)
            case 'Q' | 'q': return self.getcandidates_queen(square, piece)
            case 'K' | 'k': return self.getcandidates_king(square, piece)
            case _: return(i for i in [])
    
    def getcandidates_wpawn(self, target: BoardSquare) -> Generator[BoardSquare]:
        if self.get_piece(target) == '':
            start = target.shift(0, 1)
            if self.get_piece(start) == 'P':
                yield start
            elif target.rank == 4 and self.get_piece(start) == '':
                start = target.shift(0, 2)
                if self.get_piece(start) == 'P':
                    yield start
        if self.get_piece(target) != '' or target == self.en_passant:
            if target.file != 0:
                start = target.shift(-1, 1)
                if self.get_piece(start) == 'P':
                    yield start
            if target.file != 7:
                start = target.shift(1, 1)
                if self.get_piece(start) == 'P':
                    yield start
    
    def getcandidates_bpawn(self, target: BoardSquare) -> Generator[BoardSquare]:
        if self.get_piece(target) == '':
            start = target.shift(0, -1)
            if self.get_piece(start) == 'p':
                yield start
            elif target.rank == 3 and self.get_piece(start) == '':
                start = target.shift(0, -2)
                if self.get_piece(start) == 'p':
                    yield start
        if self.get_piece(target) != '' or target == self.en_passant:
            if target.file != 0:
                start = target.shift(-1, -1)
                if self.get_piece(start) == 'p':
                    yield start
            if target.file != 7:
                start = target.shift(1, -1)
                if self.get_piece(start) == 'p':
                    yield start
    
    def getcandidates_knight(self, target: BoardSquare, knight: str) -> Generator[BoardSquare]:
        return(start for start in self.getsquares_knight(target) if self.get_piece(start) == knight)
    
    def getcandidates_bishop(self, target: BoardSquare, bishop: str) -> Generator[BoardSquare]:
        return(start for start in self.getsquares_bishop(target) if self.get_piece(start) == bishop)
    
    def getcandidates_rook(self, target: BoardSquare, rook: str) -> Generator[BoardSquare]:
        return(start for start in self.getsquares_rook(target) if self.get_piece(start) == rook)
    
    def getcandidates_queen(self, target: BoardSquare, queen: str) -> Generator[BoardSquare]:
        for start in self.getcandidates_bishop(target, queen):
            if self.get_piece(start) == queen:
                yield start
        for start in self.getcandidates_rook(target, queen):
            if self.get_piece(start) == queen:
                yield start
    
    def getcandidates_king(self, target: BoardSquare, king: str) -> Generator[BoardSquare]:
        return(start for start in self.getsquares_king(target) if self.get_piece(start) == king)
    
    def getsquares(self, start: BoardSquare, piece: str) -> Generator[BoardSquare]:
        """Returns the squares to which the piece can move ignoring king's safety and piece colors.
        Will return squares that are oqupied by the same color piece"""
        match piece:
            case 'P':       return self.getsquares_wpawn(start)
            case 'p':       return self.getsquares_bpawn(start)
            case 'N' | 'n': return self.getsquares_knight(start)
            case 'B' | 'b': return self.getsquares_bishop(start)
            case 'R' | 'r': return self.getsquares_rook(start)
            case 'Q' | 'q': return self.getsquares_queen(start)
            case 'K':       return self.getsquares_wking(start)
            case 'k':       return self.getsquares_bking(start)
            case _: return(i for i in [])
    
    def getsquares_wpawn(self, start: BoardSquare) -> Generator[BoardSquare]:
        target = start.shift(0, -1)
        if self.get_piece(target) == '':
            yield target
            target = start.shift(0, -2)
            if start.rank == 6 and self.get_piece(target) == '':
                yield target
        if start.file != 0:
            target = start.shift(-1, -1)
            if self.get_piece(target) != '' or target == self.en_passant:
                yield target
        if start.file != 7:
            target = start.shift(1, -1)
            if self.get_piece(target) != '' or target == self.en_passant:
                yield target
    
    def getsquares_bpawn(self, start: BoardSquare) -> Generator[BoardSquare]:
        target = start.shift(0, 1)
        if self.get_piece(target) == '':
            yield target
            target = start.shift(0, 2)
            if start.rank == 1 and self.get_piece(target) == '':
                yield target
        if start.file != 0:
            target = start.shift(-1, 1)
            if self.get_piece(target) != '' or target == self.en_passant:
                yield target
        if start.file != 7:
            target = start.shift(1, 1)
            if self.get_piece(target) != '' or target == self.en_passant:
                yield target
    
    def getsquares_knight(self, start: BoardSquare) -> Generator[BoardSquare]:
        for dx, dy in product([-2, -1, 1, 2], repeat=2):
            target = start.shift(dx, dy)
            if abs(dx) != abs(dy) and target.isinrange():
                yield target
    
    def getsquares_bishop(self, start: BoardSquare) -> Generator[BoardSquare]:
        for x, y in zip(range(start.file-1, -1, -1), 
                        range(start.rank-1, -1, -1)):
            target = BoardSquare(x, y)
            yield target
            if self.get_piece(target) != '':
                break
        for x, y in zip(range(start.file+1, 8, 1), 
                        range(start.rank-1, -1, -1)):
            target = BoardSquare(x, y)
            yield target
            if self.get_piece(target) != '':
                break
        for x, y in zip(range(start.file-1, -1, -1), 
                        range(start.rank+1, 8, 1)):
            target = BoardSquare(x, y)
            yield target
            if self.get_piece(target) != '':
                break
        for x, y in zip(range(start.file+1, 8, 1), 
                        range(start.rank+1, 8, 1)):
            target = BoardSquare(x, y)
            yield target
            if self.get_piece(target) != '':
                break
    
    def getsquares_rook(self, start: BoardSquare) -> Generator[BoardSquare]:
        for y in range(start.rank+1, 8, 1):
            target = BoardSquare(start.file, y)
            yield target
            if self.get_piece(target) != '':
                break
        for y in range(start.rank-1, -1, -1):
            target = BoardSquare(start.file, y)
            yield target
            if self.get_piece(target) != '':
                break
        for x in range(start.file+1, 8, 1):
            target = BoardSquare(x, start.rank)
            yield target
            if self.get_piece(target) != '':
                break
        for x in range(start.file-1, -1, -1):
            target = BoardSquare(x, start.rank)
            yield target
            if self.get_piece(target) != '':
                break
    
    def getsquares_queen(self, start: BoardSquare) -> Generator[BoardSquare]:
        for target in self.getsquares_bishop(start):
            yield target
        for target in self.getsquares_rook(start):
            yield target
    
    def getsquares_king(self, start: BoardSquare) -> Generator[BoardSquare]:
        for x, y in product(range(max(0, start.file-1), min(start.file + 1, 7) + 1), 
                            range(max(0, start.rank-1), min(start.rank + 1, 7) + 1)):
            target = BoardSquare(x, y)
            if target != start:
                yield target
    
    def getsquares_wking(self, start: BoardSquare) -> Generator[BoardSquare]:
        for target in self.getsquares_king(start):
            yield target
        if start != WHITE_KING_SQUARE:
            return
        if (self.castles['Q'] and self.get_rank(WHITE_BACK_RANK)[:5] == ['R', '', '', '', 'K'] and 
            not(self.isattacked(BoardSquare(3, WHITE_BACK_RANK)))):
            yield BoardSquare(2, WHITE_BACK_RANK)
        if (self.castles['K'] and self.get_rank(7)[4:] == ['K', '', '', 'R'] and 
            not(self.isattacked(BoardSquare(5, WHITE_BACK_RANK)))):
            yield BoardSquare(6, WHITE_BACK_RANK)
    
    def getsquares_bking(self, start: BoardSquare) -> Generator[BoardSquare]:
        for target in self.getsquares_king(start):
            yield target
        if start != BLACK_KING_SQUARE:
            return
        if (self.castles['q'] and self.get_rank(BLACK_BACK_RANK)[:5] == ['r', '', '', '', 'k'] and 
            not(self.isattacked(BoardSquare(3, BLACK_BACK_RANK)))):
            yield BoardSquare(2, BLACK_BACK_RANK)
        if (self.castles['k'] and self.get_rank(BLACK_BACK_RANK)[4:] == ['k', '', '', 'r'] and 
            not(self.isattacked(BoardSquare(5, BLACK_BACK_RANK)))):
            yield BoardSquare(6, BLACK_BACK_RANK)