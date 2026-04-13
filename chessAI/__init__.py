from network import Network, load
from positionClass import Position
from notation.square import BoardMove, move_decode
from chessAI.data import position_encode

class ChessAI(Network):    
    def get_move(self, position: Position) -> BoardMove:
        move = super().process(position_encode(position))
        return move_decode(''.join(str(round(bit)) for bit in move))
    
    def move(self, position: Position, skip_check: bool = False) -> None:
        move = self.get_move(position)
        position.move(move, skip_check=skip_check)


def load_chessAI(filename: str) -> ChessAI:
    ai = ChessAI([], 'linear')
    ai.load(filename)
    return ai