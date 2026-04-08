from notation.fen import ForsythEdwardsNotation
from notation.square import BoardMove
from positionClass import Position

#pgn notation
#Pe4 pe6 Pd4 pb6 Pa3 Bb7 Nc3 Nh6 Bh6 gh6 Be2 Qg5 Bg4 ph5 Nf3 Qg6 Nh4 Qg5 Bh5 Qh4 Qf3 Kd8 Qf7 Nc6 Qe8
#Pe4 pc5 Nc3 pd6 Pd4 cd4 Nb5 pe5 Pc3 dc3 Nc3 Nc6 Pf4 Nf6 Nf3 Be7 fe5 de5 Bg5 Bg4 Qb3 O-O Rd1 Qa5 Bd2 Qc7 Nd5 Nd5 ed5 Nd4 Nd4 Bd1 Nb5 Bb3 Nc7 Ba2 Na8 Ra8 Bd3 Bd5 O-O Bc5 Kh1 pg6 Bg5 pf5 Rd1 pe4 Bb5 Bc6 Bc6 bc6 Rc1 Bb6 Rc6 Re8 Pg3 pe3 Kg2 pe2 Bd2 e1=Q Be1 Re1 Kh3 Re2 Rc8 Kg7 Rb8 Rb2 Rb7 Kh6 Pg4 Rb3 Kg2 fg4 Kf1 Rb2
#Pc4 pf5 Nc3 Nf6 Pg3 pd6 Bg2 pg6 Pe4 fe4 Ne4 Nbd7 Ng5 Ne5 Pb3 ph6 Pd4 Nc6 Pd5 Nb4 Pa3 hg5 ab4 pg4 Ne2 Bf5 Nd4 Qd7 O-O Bg7 Re1 Rh5 Ra2 O-O-O Ra7 Kb8 Ra4 Rdh8 Bh6 Rh8h6 Qa1 Qa4 Qa4 Rh2 Nc6 bc6 dc6



def get_board_move(alg_move: str, position: Position) -> BoardMove:
    if alg_move == 'O-O':
        if position.white_move:
            return BoardMove(WHITE_KING_SQUARE, BoardSquare(5, WHITE_BACK_RANK))
        else:
            return BoardMove(BLACK_KING_SQUARE, BoardSquare(5, BLACK_BACK_RANK))
    if alg_move == 'O-O-O':
        if position.white_move:
            return BoardMove(WHITE_KING_SQUARE, BoardSquare(3, WHITE_BACK_RANK))
        else:
            return BoardMove(BLACK_KING_SQUARE, BoardSquare(3, BLACK_BACK_RANK))
    if alg_move[-2] == '=':
        promote_to = alg_move[-1]
        alg_move = alg_move[:-2]
    else:
        promote_to = 'Q'
    target = algebraic_to_board(alg_move[-2:])
    add_info = alg_move[1:-2]
    if len(add_info) == 2:
        return BoardMove(algebraic_to_board(add_info), target)
    legal_starts = list(position.getcandidates(target, alg_move[0]))
    if len(legal_starts) == 0:
        if position.white_move:
            legal_starts = list(position.getcandidates(target, 'P'))
        else:
            legal_starts = list(position.getcandidates(target, 'p'))
    if len(legal_starts) == 1:
        return BoardMove(legal_starts[0], target, promote_to)
    if add_info.isdigit():
        rank = 8 - int(add_info)
        for start in legal_starts:
            if start.rank == rank:
                return BoardMove(start, target)
    else:
        file = 'abcdefgh'.index(add_info)
        for start in legal_starts:
            if start.file == file:
                return BoardMove(start, target)
    raise ValueError("Incorrect algebraic notation")



class PortableGameNotation:
    def __init__(self, PGN: str, init_position: ForsythEdwardsNotation = ForsythEdwardsNotation()) -> None:
        self.string = PGN
        self.init_position = init_position
        self.position = Position(init_position)
    
    def __str__(self) -> str:
        return self.string
    
    def get_results(self) -> str:
        return self.string.split()[-1]

    def get_move_list(self) -> list[str]:
        unfiltered_list = self.string.split()
        filtered_list: list[str] = []
        for move in unfiltered_list[:-1]:
            if not(move[0].isdigit()):
                filtered_list.append(move)
        return filtered_list
    
    def get_formatted_move_list(self) -> list[str]:
        formatted_move_list: list[str] = []
        for i, move in enumerate(self.get_move_list()):
            move = move.replace('x', '')
            move = move.replace('+', '')
            move = move.replace('#', '')
            if len(move) == 2:
                if i%2 == 0:
                    move = 'P' + move
                else:
                    move = 'p' + move
            formatted_move_list.append(move)
        return formatted_move_list