from notation import BoardMove,  BoardSquare
from positionClass import Position
from math import copysign

#castling constants
KINGS_FILE = 4
QUEEN_ROOKS_FILE = 0
KING_ROOKS_FILE = 7

WHITE_KING       = BoardSquare(4, 7)
WHITE_ROOK_QUEEN = BoardSquare(0, 7)
WHITE_ROOK_KING  = BoardSquare(7, 7)
BLACK_KING       = BoardSquare(4, 0)
BLACK_ROOK_QUEEN = BoardSquare(0, 0)
BLACK_ROOK_KING  = BoardSquare(7, 0)


def handle_en_passant(position: Position, move: BoardMove, piece: str) -> None:
    file1, rank1, file2, rank2 = move
    if piece == 'P':
        if move.target_square == position.en_passant:
            position.set_piece(BoardSquare(file2, rank2 + 1))
        elif rank2 - rank1 == -2:
            position.en_passant = BoardSquare(file1, 5)
            return None
    elif piece == 'p':
        if move.target_square == position.en_passant:
            position.set_piece(BoardSquare(file2, rank2 - 1))
        elif rank2 - rank1 == 2:
            position.en_passant = BoardSquare(file1, 2)
            return None
    position.en_passant = None

def handle_castling(position: Position, file1: int, file2: int, piece: str) -> None:
    if piece == 'R':
        if file1 == QUEEN_ROOKS_FILE:
            position.castles['Q'] = False
        elif file1 == KING_ROOKS_FILE:
            position.castles['K'] = False
    elif piece == 'r':
        if file1 == QUEEN_ROOKS_FILE:
            position.castles['q'] = False
        elif file1 == KING_ROOKS_FILE:
            position.castles['k'] = False
    elif piece == 'K':
        position.castles['Q'] = False
        position.castles['K'] = False
        if file1 == KINGS_FILE:
            if file2 == 2:
                position.set_piece(BoardSquare(3, 7), 'R')
                position.set_piece(BoardSquare(0, 7), '')
            elif file2 == 6:
                position.set_piece(BoardSquare(5, 7), 'R')
                position.set_piece(BoardSquare(7, 7), '')
    elif piece == 'k':
        position.castles['q'] = False
        position.castles['k'] = False
        if file1 == KINGS_FILE:
            if file2 == 2:
                position.set_piece(BoardSquare(3, 0), 'r')
                position.set_piece(BoardSquare(0, 0), '')
            elif file2 == 6:
                position.set_piece(BoardSquare(5, 0), 'r')
                position.set_piece(BoardSquare(7, 0), '')

def handle_promotion(position: Position, square: BoardSquare, promote_to: str | None) -> None:
    if promote_to != None:
        position.set_piece(square, promote_to)

def is_move_possible(position: Position, move: BoardMove, available_squares: list[BoardSquare] | None = None) -> bool:
    "Returns True if the move can be made, False otherwise"
    if available_squares != None:
        return (move.target_square in available_squares)
    if not(move.start_square.isinrange() and move.target_square.isinrange()):
        return False
    piece = position.get_piece(move.start_square)
    if piece == '':
        return False
    if piece.isupper() != position.is_white_to_move:
        return False
    if (position.get_piece(move.target_square) != '' and 
        position.is_white_to_move == position.get_piece(move.target_square).isupper()):
        return False
    return (position.ismovable(move, piece) and 
        not(position.is_moved_into_check(move)))

def ispromotion(position: Position, rank2: int, piece: str) -> bool:
    return (rank2 == 0 and piece == 'P' or 
            rank2 == 7 and piece == 'p')

def is_moved_into_check(position: Position, move: BoardMove) -> bool:
    "Returns True if the king will be in check after the given move, False otherwise"
    saved_states = position.pos_array.copy(), position.castles.copy(), position.en_passant #saves the state of the game
    position.raw_move(move) #makes a move
    ischecked = position.ischecked()
    position.pos_array, position.castles, position.en_passant = saved_states #returns position to its initial state
    return ischecked

"'ismovable' functions return True if the piece can make the given move, False otherwise"
def ismovable(position: Position, move: BoardMove, piece: str) -> bool:
    match piece:
        case 'P':       return position.ismovable_wpawn(move)
        case 'p':       return position.ismovable_bpawn(move)
        case 'N' | 'n': return position.ismovable_knight(move)
        case 'B' | 'b': return position.ismovable_bishop(move)
        case 'R' | 'r': return position.ismovable_rook(move)
        case 'Q' | 'q': return position.ismovable_queen(move)
        case 'K' | 'k': return position.ismovable_king(move)
        case _: return False

def ismovable_wpawn(position: Position, move: BoardMove) -> bool:
    file1, rank1, file2, rank2 = move
    if file1 == file2 and position.get_piece(move.target_square) == '':
        if rank2 - rank1 == -1: 
            return True
        elif rank1 == 6 and rank2 == 4 and position.get_piece(BoardSquare(file2, 5)) == '': 
            return True
    elif (rank2 - rank1 == -1 and abs(file2 - file1) == 1):
        if position.get_piece(move.target_square) != '': 
            return True
        elif move.target_square == position.en_passant: 
            return True
    return False

def ismovable_bpawn(position: Position, move: BoardMove) -> bool:
    file1, rank1, file2, rank2 = move
    if file1 == file2 and position.get_piece(move.target_square) == '':
        if rank2 - rank1 == 1: 
            return True
        elif rank1 == 1 and rank2 == 3 and position.get_piece(BoardSquare(file2, 2)) == '': 
            return True
    elif (rank2 - rank1 == 1 and abs(file2 - file1) == 1):
        if position.get_piece(move.target_square) != '': 
            return True
        elif move.target_square == position.en_passant: 
            return True
    return False

def ismovable_knight(position: Position, move: BoardMove) -> bool:
    file1, rank1, file2, rank2 = move
    if ((abs(file2 - file1) == 1 and abs(rank2 - rank1) == 2) or 
        (abs(rank2 - rank1) == 1 and abs(file2 - file1) == 2)):
        return True
    return False

def ismovable_bishop(position: Position, move: BoardMove) -> bool:
    file1, rank1, file2, rank2 = move
    if abs(file2 - file1) != abs(rank2 - rank1): 
        return False
    x_direction = int(copysign(1, file2-file1))
    y_direction = int(copysign(1, rank2-rank1))
    for x, y in zip(range(file1 + x_direction, file2, x_direction), 
                    range(rank1 + y_direction, rank2, y_direction)):
        if position.get_piece(BoardSquare(x, y)) != '': 
            return False
    return True

def ismovable_rook(position: Position, move: BoardMove) -> bool:
    file1, rank1, file2, rank2 = move
    if file1 == file2:
        y_direction = int(copysign(1, rank2-rank1))
        for y in range(rank1 + y_direction, rank2, y_direction):
            if position.get_piece(BoardSquare(file1, y)) != '': 
                return False
        return True
    elif rank1 == rank2:
        x_direction = int(copysign(1, file2-file1))
        for x in range(file1 + x_direction, file2, x_direction):
            if position.get_piece(BoardSquare(x, rank1)) != '': 
                return False
        return True
    return False

def ismovable_queen(position: Position, move: BoardMove) -> bool:
    return(position.ismovable_rook(move) or 
           position.ismovable_bishop(move))

def ismovable_king(position: Position, move: BoardMove) -> bool:
    file1, rank1, file2, rank2 = move
    if (-1 <= file2 - file1 <= 1) and (-1 <= rank2 - rank1 <= 1): 
        return True
    if position.isattacked(move.start_square):
        return False
    if position.is_white_to_move and position.get_piece(BoardSquare(4, 7)) == 'K' and rank2 == 7:
        if (file2 == 2 and position.castles['Q'] and position.get_piece(BoardSquare(0, 7)) == 'R' and 
            position.get_piece(BoardSquare(1, 7)) == '' and position.get_piece(BoardSquare(3, 7)) == '' and
            not(position.isattacked(BoardSquare(3, 7)))): 
            return True
        if (file2 == 6 and position.castles['K'] and position.get_piece(BoardSquare(7, 7)) == 'R' and 
                position.get_piece(BoardSquare(5, 7)) == '' and
                not(position.isattacked(BoardSquare(5, 7)))): 
            return True
    elif not(position.is_white_to_move) and position.get_piece(BoardSquare(4, 0)) == 'k' and rank2 == 0:
        if (file2 == 2 and position.castles['q'] and position.get_piece(BoardSquare(0, 0)) == 'r' and
            position.get_piece(BoardSquare(1, 0)) == '' and position.get_piece(BoardSquare(3, 0)) == '' and
            not(position.isattacked(BoardSquare(3, 0)))): 
            return True
        if (file2 == 6 and position.castles['k'] and position.get_piece(BoardSquare(7, 0)) == 'r' and 
                position.get_piece(BoardSquare(5, 0)) == '' and 
                not(position.isattacked(BoardSquare(5, 0)))): 
            return True
    return False

"'isatacked' functions return True if the given square is attacked by an enemy piece, False otherwise"
def isattacked(position: Position, square: BoardSquare) -> bool:
    return (position.isattacked_by_pawn(square) or 
            position.isattacked_by_knight(square) or 
            position.isattacked_by_bishop_queen(square) or 
            position.isattacked_by_rook_queen(square) or 
            position.isattacked_by_king(square))

def isattacked_by_pawn(position: Position, square: BoardSquare) -> bool:
    if position.is_white_to_move:
        return position.isattacked_by_bpawn(square)
    else:
        return position.isattacked_by_wpawn(square)

def isattacked_by_wpawn(position: Position, square: BoardSquare) -> bool:
    if square.rank == 7:
        return False
    if square.file - 1 >= 0 and position.get_piece(BoardSquare(square.file-1, square.rank+1)) == 'P':
        return True
    if square.file + 1 <= 7 and position.get_piece(BoardSquare(square.file+1, square.rank+1)) == 'P':
        return True
    return False

def isattacked_by_bpawn(position: Position, square: BoardSquare) -> bool:
    if square.rank == 0:
        return False
    if square.file - 1 >= 0 and position.get_piece(BoardSquare(square.file-1, square.rank-1)) == 'p':
        return True
    if square.file + 1 <= 7 and position.get_piece(BoardSquare(square.file+1, square.rank-1)) == 'p':
        return True
    return False

def isattacked_by_knight(position: Position, square: BoardSquare) -> bool:
    if position.is_white_to_move:
        knight = 'n'
    else:
        knight = 'N'
    for dy in [-2, -1, 1, 2]:
        for dx in [-2, -1, 1, 2]:
            if (abs(dx) != abs(dy) and 
                0 <= square.file + dx < 8 and 0 <= square.rank + dy < 8 and
                position.get_piece(BoardSquare(square.file + dx, square.rank + dy)) == knight):
                return True
    return False

def isattacked_by_bishop_queen(position: Position, square: BoardSquare) -> bool:
    if position.is_white_to_move:
        bishop = 'b'
        queen = 'q'
    else:
        bishop = 'B'
        queen = 'Q'
    for x, y in zip(range(square.file-1, -1, -1), 
                    range(square.rank-1, -1, -1)):
        piece = position.get_piece(BoardSquare(x, y))
        if piece == bishop or piece == queen:
            return True
        elif piece != '':
            break
    for x, y in zip(range(square.file+1, 8, 1), 
                    range(square.rank-1, -1, -1)):
        piece = position.get_piece(BoardSquare(x, y))
        if piece == bishop or piece == queen:
            return True
        elif piece != '':
            break
    for x, y in zip(range(square.file-1, -1, -1), 
                    range(square.rank+1, 8, 1)):
        piece = position.get_piece(BoardSquare(x, y))
        if piece == bishop or piece == queen:
            return True
        elif piece != '':
            break
    for x, y in zip(range(square.file+1, 8, 1), 
                    range(square.rank+1, 8, 1)):
        piece = position.get_piece(BoardSquare(x, y))
        if piece == bishop or piece == queen:
            return True
        elif piece != '':
            break
    return False

def isattacked_by_rook_queen(position: Position, square: BoardSquare) -> bool:
    if position.is_white_to_move:
        rook = 'r'
        queen = 'q'
    else:
        rook = 'R'
        queen = 'Q'
    for y in range(square.rank+1, 8, 1):
        piece = position.get_piece(BoardSquare(square.file, y))
        if piece == rook or piece == queen:
            return True
        elif piece != '':
            break
    for y in range(square.rank-1, -1, -1):
        piece = position.get_piece(BoardSquare(square.file, y))
        if piece == rook or piece == queen:
            return True
        elif piece != '':
            break
    for x in range(square.file+1, 8, 1):
        piece = position.get_piece(BoardSquare(x, square.rank))
        if piece == rook or piece == queen:
            return True
        elif piece != '':
            break
    for x in range(square.file-1, -1, -1):
        piece = position.get_piece(BoardSquare(x, square.rank))
        if piece == rook or piece == queen:
            return True
        elif piece != '':
            break
    return False

def isattacked_by_king(position: Position, square: BoardSquare) -> bool:
    if position.is_white_to_move:
        king = 'k'
    else:
        king = 'K'
    for y in range(max(0, square.rank-1), min(square.rank + 1, 7) + 1):
        for x in range(max(0, square.file-1), min(square.file + 1, 7) + 1):
            if position.get_piece(BoardSquare(x, y)) == king:
                return True
    return False