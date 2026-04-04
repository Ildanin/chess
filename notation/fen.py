from notation.square import BoardSquare, algebraic_to_board

class ForsythEdwardsNotation:
    def __init__(self, FEN: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
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
    
    def get_white_move(self) -> bool:
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