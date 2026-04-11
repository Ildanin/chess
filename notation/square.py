from typing import Iterator

class BoardSquare:
    def __init__(self, file: int, rank: int) -> None:
        self.file = file
        self.rank = rank
        self.id = file + 8*rank
    
    def __str__(self) -> str:
        return self.get_algebraic()

    def __iter__(self) -> Iterator[int]:
        return iter((self.file, self.rank))
    
    def __eq__(self, square: object) -> bool:
        if square == None:
            return False
        elif type(square) == tuple:
            return(self.file == square[0] and self.rank == square[1])
        elif type(square) != BoardSquare:
            raise ValueError(f"BoardSquare object cannot be compared with {type(square)} object")
        return(self.file == square.file and self.rank == square.rank)
    
    def encode(self) -> str:
        if not self.isinrange():
            raise ValueError("Cannot encode a square that is outside of the board")
        rank = bin(self.rank)[2:].zfill(3)
        file = bin(self.file)[2:].zfill(3)
        return file + rank
    
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
    def __init__(self, start: BoardSquare, target: BoardSquare, promote_to: str = 'Q') -> None:
        self.start = start
        self.target = target
        self.file1 = start.file
        self.rank1 = start.rank
        self.file2 = target.file
        self.rank2 = target.rank
        self.promote_to = promote_to
        self.dx = None
        self.dy = None
    
    def __str__(self) -> str:
        return self.start.get_algebraic() + self.target.get_algebraic()
    
    def __iter__(self) -> Iterator[int]:
        return iter((*self.start, *self.target))
    
    def __eq__(self, move: object) -> bool:
        if move == None:
            return False
        elif type(move) != BoardMove:
            raise ValueError(f"BoardSquare object cannot be compared with {type(move)} object")
        return(self.start == move.start and self.target == move.target)
    
    def encode(self) -> str:
        return self.start.encode() + self.target.encode()
    
    def get_dx(self) -> int:
        if self.dx == None:
            self.dx = self.target.file - self.start.file
        return self.dx
    
    def get_dy(self) -> int:
        if self.dy == None:
            self.dy = self.target.rank - self.start.rank
        return self.dy

def algebraic_to_board(algebraic: str) -> BoardSquare:
    x_comp = algebraic[0]
    y_comp = algebraic[1]
    file = 'abcdefgh'.index(x_comp)
    rank = 8 - int(y_comp)
    return BoardSquare(file, rank)