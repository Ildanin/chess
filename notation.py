from typing import Any, Iterator


class BoardSquare:
    def __init__(self, file: int, rank: int) -> None:
        self.file = file
        self.rank = rank
        self.id = file + 8*rank
    
    def __str__(self) -> str:
        return f'{self.file} {self.rank}'

    def __iter__(self) -> Iterator[int]:
        return iter((self.file, self.rank))
    
    def __eq__(self, square: object) -> bool:
        if square == None:
            return False
        elif type(square) != BoardSquare:
            raise ValueError(f"BoardSquare object cannot be compared with {type(square)} object")
        return (self.file == square.file and self.rank == square.rank)

    def isinrange(self, lower_bound: int = 0, upper_bound: int = 8) -> bool:
        return(lower_bound <= self.file < upper_bound and 
               lower_bound <= self.rank < upper_bound)

    def shift(self, dx: int = 0, dy: int = 0):
        return BoardSquare(self.file + dx, self.rank + dy)
    
    def get_algebraic(self) -> str:
        x_comp = 'abcdefgh'[self.file]
        y_comp = str(8 - self.rank)
        return x_comp + y_comp

class BoardMove:
    def __init__(self, start_square: BoardSquare, target_square: BoardSquare) -> None:
        self.start_square = start_square
        self.target_square = target_square
        self.dx = None
        self.dy = None
    
    def __iter__(self) -> Iterator[int]:
        return iter((*self.start_square, *self.target_square))
    
    def get_dx(self) -> int:
        if self.dx == None:
            self.dx = self.target_square.file - self.start_square.file
        return self.dx
    
    def get_dy(self) -> int:
        if self.dy == None:
            self.dy = self.target_square.rank - self.start_square.rank
        return self.dy

def algebraic_to_board(algebraic: str) -> BoardSquare:
    x_comp = algebraic[0]
    y_comp = algebraic[1]
    file = 'abcdefgh'.index(x_comp)
    rank = 8 - int(y_comp)
    return BoardSquare(file, rank)


class ForsythEdwardsNotation:
    def __init__(self, FEN: str = "nbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
        self.string = FEN
        self.list = FEN.split()
    
    def __str__(self) -> str:
        return self.string
    
    def get_FEN(self) -> str:
        return self.string
    
    def get_position_array(self) -> list[str]:
        position: list[str] = []
        for c in self.list[0]:
            if c.isdigit():
                position += ['' for _ in range(int(c))]
            elif c != '/':
                position.append(c)
        return(position)
    
    def get_is_white_to_move(self) -> bool:
        return self.list[1] == 'w'
    
    def get_castles(self) -> dict[str, bool]:
        return {'K': 'K' in self.list[2], 
                'Q': 'Q' in self.list[2], 
                'k': 'k' in self.list[2], 
                'q': 'q' in self.list[2]}
    
    def get_en_passant(self) -> BoardSquare | None:
        if self.list[3] != '-':
            return algebraic_to_board(self.list[3])
    
    def get_halfmove_clock(self) -> int:
        return int(self.list[4])
    
    def get_fullmove_number(self) -> int:
        return int(self.list[5])

#pgn notation
#1. e4 e6 2. d4 b6 3. a3 Bb7 4. Nc3 Nh6 5. Bxh6 gxh6 6. Be2 Qg5 7. Bg4 h5 8. Nf3 Qg6 9. Nh4 Qg5 10. Bxh5 Qxh4 11. Qf3 Kd8 12. Qxf7 Nc6 13. Qe8# 1-0
class PortableGameNotation:
    def __init__(self, PGN: str, init_position: ForsythEdwardsNotation = ForsythEdwardsNotation()) -> None:
        self.string = PGN
        self.init_position = init_position
    
    def __str__(self) -> str:
        return self.string

    def append(self, move) -> None:
        pass
    
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


    '''def get_position_array(self, move: int) -> list[str]:
        pass

    def get_position_array_list(self) -> list[list[str]]:
        position_array = self.init_position.get_position_array()'''


    '''def as_FEN_list(self) -> list[ForsythEdwardsNotation]: #todo
        pass

    def as_FEN(self, move: int) -> ForsythEdwardsNotation: #todo
        pass'''

'''pgn = PortableGameNotation("1. e4 e6 2. d4 b6 3. a3 Bb7 4. Nc3 Nh6 5. Bxh6 gxh6 6. Be2 Qg5 7. Bg4 h5 8. Nf3 Qg6 9. Nh4 Qg5 10. Bxh5 Qxh4 11. Qf3 Kd8 12. Qxf7 Nc6 13. Qe8# 1-0")
print(pgn.get_move_list())
print(pgn.get_formatted_move_list())'''