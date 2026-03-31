from math import copysign
from notation import ForsythEdwardsNotation, BoardMove, BoardSquare
from itertools import product

KINGS_FILE = 4
QUEEN_ROOKS_FILE = 0
KING_ROOKS_FILE = 7

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

    def get_piece(self, square: BoardSquare) -> str:
        "Returns the piece given the square"
        return self.pos_array[square.id]
    
    def get_rank(self, rank: int) -> list[str]:
        return self.pos_array[8*rank : 8*(rank+1)]
    
    def set_piece(self, square: BoardSquare, piece: str = '') -> None:
        self.pos_array[square.id] = piece
    
    def get_location(self, piece: str) -> BoardSquare:
        "Return first occurring square of the piece"
        ind = self.pos_array.index(piece)
        return BoardSquare(ind%8, ind//8)
    
    def get_highlights(self, square: BoardSquare) -> list[BoardSquare]:
        "Returns a list of square to which the piece can move"
        squares = []
        for x, y in product(range(8), repeat=2):
            if self.is_move_possible(BoardMove(square, BoardSquare(x, y))):
                squares.append(BoardSquare(x, y))
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
            notation += self.en_passant.get_algebraic()
        else:
            notation += ' - '
        notation += f'{self.halfmove_clock} {self.fullmove_number}'
        return ForsythEdwardsNotation(FEN = notation[1:])

    def ischecked(self) -> bool:
        if self.is_white_to_move:
            return self.isattacked(self.get_location('K'))
        else:
            return self.isattacked(self.get_location('k'))

    def isdraw(self) -> bool:
        if self.ischecked():
            return False
        if self.pos_array.count('') == 62:
            return True
        for x1, y1, x2, y2 in product(range(8), repeat=4):
            if self.is_move_possible(BoardMove(BoardSquare(x1, y1), BoardSquare(y2, x2))) == True:
                return False 
        return True

    def ischeckmate(self) -> bool:
        if self.is_white_to_move:
            king_square = self.get_location('K')
        else:
            king_square = self.get_location('k')
        if not self.isattacked(king_square):
            return False
        for x1, y1, x2, y2 in product(range(8), repeat=4):
            if self.is_move_possible(BoardMove(BoardSquare(x1, y1), BoardSquare(y2, x2))) == True:
                return False
        return True

    def get_possible_moves(self) -> list[BoardMove]:
        moves = []
        for x1, y1, x2, y2 in product(range(8), repeat=4):
            move = BoardMove(BoardSquare(x1, y1), BoardSquare(y2, x2))
            if self.is_move_possible(move) == True:
                moves.append(move)
        return moves
    
    def move(self, move: BoardMove, promote_to: str | None = None, available_squares: list[BoardSquare] | None = None) -> bool:
        "Moves the piece if it is posible. Returns True if moved successfully, False otherwise"
        if self.is_move_possible(move, available_squares):
            if self.get_piece(move.start_square).lower() == 'p':
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1
            if self.is_white_to_move == False:
                self.fullmove_number += 1
            self.raw_move(move, promote_to)
            self.is_white_to_move = not self.is_white_to_move
            return True
        return False
    
    def raw_move(self, move: BoardMove, promote_to: str | None = None) -> None:
        "Makes a move without any checks and does not pass the move"
        piece = self.get_piece(move.start_square)
        self.set_piece(move.target_square, piece)
        self.set_piece(move.start_square, '')
        self.handle_en_passant(move, piece)
        self.handle_castling(move.start_square.file, move.target_square.file, piece)
        self.handle_promotion(move.target_square, promote_to)
    
    def handle_en_passant(self, move: BoardMove, piece: str) -> None:
        file1, rank1, file2, rank2 = move
        if piece == 'P':
            if move.target_square == self.en_passant:
                self.set_piece(BoardSquare(file2, rank2 + 1))
            elif rank2 - rank1 == -2:
                self.en_passant = BoardSquare(file1, 5)
                return None
        elif piece == 'p':
            if move.target_square == self.en_passant:
                self.set_piece(BoardSquare(file2, rank2 - 1))
            elif rank2 - rank1 == 2:
                self.en_passant = BoardSquare(file1, 2)
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

    def handle_promotion(self, square: BoardSquare, promote_to: str | None) -> None:
        if promote_to != None:
            self.set_piece(square, promote_to)

    def is_move_possible(self, move: BoardMove, available_squares: list[BoardSquare] | None = None) -> bool:
        "Returns True if the move can be made, False otherwise"
        if available_squares != None:
            return (move.target_square in available_squares)
        if not(move.start_square.isinrange() and move.target_square.isinrange()):
            return False
        piece = self.get_piece(move.start_square)
        if piece == '':
            return False
        if piece.isupper() != self.is_white_to_move:
            return False
        if (self.get_piece(move.target_square) != '' and 
            self.is_white_to_move == self.get_piece(move.target_square).isupper()):
            return False
        return (self.ismovable(move, piece) and 
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

    "'ismovable' functions return True if the piece can make the given move, False otherwise"
    def ismovable(self, move: BoardMove, piece: str) -> bool:
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
        file1, rank1, file2, rank2 = move
        if file1 == file2 and self.get_piece(move.target_square) == '':
            if rank2 - rank1 == -1: 
                return True
            elif rank1 == 6 and rank2 == 4 and self.get_piece(BoardSquare(file2, 5)) == '': 
                return True
        elif (rank2 - rank1 == -1 and abs(file2 - file1) == 1):
            if self.get_piece(move.target_square) != '': 
                return True
            elif move.target_square == self.en_passant: 
                return True
        return False

    def ismovable_bpawn(self, move: BoardMove) -> bool:
        file1, rank1, file2, rank2 = move
        if file1 == file2 and self.get_piece(move.target_square) == '':
            if rank2 - rank1 == 1: 
                return True
            elif rank1 == 1 and rank2 == 3 and self.get_piece(BoardSquare(file2, 2)) == '': 
                return True
        elif (rank2 - rank1 == 1 and abs(file2 - file1) == 1):
            if self.get_piece(move.target_square) != '': 
                return True
            elif move.target_square == self.en_passant: 
                return True
        return False

    def ismovable_knight(self, move: BoardMove) -> bool:
        file1, rank1, file2, rank2 = move
        if ((abs(file2 - file1) == 1 and abs(rank2 - rank1) == 2) or 
            (abs(rank2 - rank1) == 1 and abs(file2 - file1) == 2)):
            return True
        return False

    def ismovable_bishop(self, move: BoardMove) -> bool:
        file1, rank1, file2, rank2 = move
        if abs(file2 - file1) != abs(rank2 - rank1): 
            return False
        x_direction = int(copysign(1, file2-file1))
        y_direction = int(copysign(1, rank2-rank1))
        for x, y in zip(range(file1 + x_direction, file2, x_direction), 
                        range(rank1 + y_direction, rank2, y_direction)):
            if self.get_piece(BoardSquare(x, y)) != '': 
                return False
        return True

    def ismovable_rook(self, move: BoardMove) -> bool:
        file1, rank1, file2, rank2 = move
        if file1 == file2:
            y_direction = int(copysign(1, rank2-rank1))
            for y in range(rank1 + y_direction, rank2, y_direction):
                if self.get_piece(BoardSquare(file1, y)) != '': 
                    return False
            return True
        elif rank1 == rank2:
            x_direction = int(copysign(1, file2-file1))
            for x in range(file1 + x_direction, file2, x_direction):
                if self.get_piece(BoardSquare(x, rank1)) != '': 
                    return False
            return True
        return False

    def ismovable_queen(self, move: BoardMove) -> bool:
        if (self.ismovable_rook(move) or 
            self.ismovable_bishop(move)):
            return True
        return False

    def ismovable_king(self, move: BoardMove) -> bool:
        file1, rank1, file2, rank2 = move
        if (-1 <= file2 - file1 <= 1) and (-1 <= rank2 - rank1 <= 1): 
            return True
        if self.isattacked(move.start_square):
            return False
        if self.is_white_to_move and rank2 == 7:
            if (file2 == 2 and self.castles['Q'] and self.get_rank(7)[:5] == ['R', '', '', '', 'K'] and 
                not(self.isattacked(BoardSquare(3, 7)))): 
                return True
            if (file2 == 6 and self.castles['K'] and self.get_rank(7)[4:] == ['K', '', '', 'R'] and 
                not(self.isattacked(BoardSquare(5, 7)))): 
                return True
        elif not(self.is_white_to_move) and rank2 == 0:
            if (file2 == 2 and self.castles['q'] and self.get_rank(0)[:5] == ['r', '', '', '', 'k'] and 
                not(self.isattacked(BoardSquare(3, 0)))): 
                return True
            if (file2 == 6 and self.castles['k'] and self.get_rank(0)[4:] == ['k', '', '', 'r'] and 
                not(self.isattacked(BoardSquare(5, 0)))): 
                return True
        return False

    "'isatacked' functions return True if the given square is attacked by an enemy piece, False otherwise"
    def isattacked(self, square: BoardSquare) -> bool:
        return (self.isattacked_by_pawn(square) or 
                self.isattacked_by_knight(square) or 
                self.isattacked_by_bishop_queen(square) or 
                self.isattacked_by_rook_queen(square) or 
                self.isattacked_by_king(square))
    
    def isattacked_by_pawn(self, square: BoardSquare) -> bool:
        if self.is_white_to_move:
            return self.isattacked_by_bpawn(square)
        else:
            return self.isattacked_by_wpawn(square)

    def isattacked_by_wpawn(self, square: BoardSquare) -> bool:
        if square.rank == 7:
            return False
        if square.file - 1 >= 0 and self.get_piece(BoardSquare(square.file-1, square.rank+1)) == 'P':
            return True
        if square.file + 1 <= 7 and self.get_piece(BoardSquare(square.file+1, square.rank+1)) == 'P':
            return True
        return False

    def isattacked_by_bpawn(self, square: BoardSquare) -> bool:
        if square.rank == 0:
            return False
        if square.file - 1 >= 0 and self.get_piece(BoardSquare(square.file-1, square.rank-1)) == 'p':
            return True
        if square.file + 1 <= 7 and self.get_piece(BoardSquare(square.file+1, square.rank-1)) == 'p':
            return True
        return False

    def isattacked_by_knight(self, square: BoardSquare) -> bool:
        if self.is_white_to_move:
            knight = 'n'
        else:
            knight = 'N'
        for dy in [-2, -1, 1, 2]:
            for dx in [-2, -1, 1, 2]:
                if (abs(dx) != abs(dy) and 
                    0 <= square.file + dx < 8 and 0 <= square.rank + dy < 8 and
                    self.get_piece(BoardSquare(square.file + dx, square.rank + dy)) == knight):
                    return True
        return False

    def isattacked_by_bishop_queen(self, square: BoardSquare) -> bool:
        if self.is_white_to_move:
            bishop = 'b'
            queen = 'q'
        else:
            bishop = 'B'
            queen = 'Q'
        for x, y in zip(range(square.file-1, -1, -1), 
                        range(square.rank-1, -1, -1)):
            piece = self.get_piece(BoardSquare(x, y))
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(square.file+1, 8, 1), 
                        range(square.rank-1, -1, -1)):
            piece = self.get_piece(BoardSquare(x, y))
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(square.file-1, -1, -1), 
                        range(square.rank+1, 8, 1)):
            piece = self.get_piece(BoardSquare(x, y))
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        for x, y in zip(range(square.file+1, 8, 1), 
                        range(square.rank+1, 8, 1)):
            piece = self.get_piece(BoardSquare(x, y))
            if piece == bishop or piece == queen:
                return True
            elif piece != '':
                break
        return False

    def isattacked_by_rook_queen(self, square: BoardSquare) -> bool:
        if self.is_white_to_move:
            rook = 'r'
            queen = 'q'
        else:
            rook = 'R'
            queen = 'Q'
        for y in range(square.rank+1, 8, 1):
            piece = self.get_piece(BoardSquare(square.file, y))
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for y in range(square.rank-1, -1, -1):
            piece = self.get_piece(BoardSquare(square.file, y))
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for x in range(square.file+1, 8, 1):
            piece = self.get_piece(BoardSquare(x, square.rank))
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        for x in range(square.file-1, -1, -1):
            piece = self.get_piece(BoardSquare(x, square.rank))
            if piece == rook or piece == queen:
                return True
            elif piece != '':
                break
        return False

    def isattacked_by_king(self, square: BoardSquare) -> bool:
        if self.is_white_to_move:
            king = 'k'
        else:
            king = 'K'
        for y in range(max(0, square.rank-1), min(square.rank + 1, 7) + 1):
            for x in range(max(0, square.file-1), min(square.file + 1, 7) + 1):
                if self.get_piece(BoardSquare(x, y)) == king:
                    return True
        return False