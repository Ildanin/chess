from notation.fen import ForsythEdwardsNotation
from notation.square import BoardMove
from positionClass import Position

#pgn notation
#1. e4 e6 2. d4 b6 3. a3 Bb7 4. Nc3 Nh6 5. Bxh6 gxh6 6. Be2 Qg5 7. Bg4 h5 8. Nf3 Qg6 9. Nh4 Qg5 10. Bxh5 Qxh4 11. Qf3 Kd8 12. Qxf7 Nc6 13. Qe8# 1-0
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