from notation.pgn import PortableGameNotation
from positionClass import Position
import numpy as np
import os
datasets_path = os.path.dirname(__file__)

def position_encode(position: Position) -> np.ndarray:
    encoded = []
    if position.white_move:
        for piece in position.pos_array:
            match piece:
                case '':  encoded += [0,0,0,0,0,0,0,0,0,0,0]
                case 'P': encoded += [0,0,0,0,0,0,0,0,0,0,1]
                case 'N': encoded += [0,0,0,0,0,0,0,0,0,1,0]
                case 'B': encoded += [0,0,0,0,0,0,0,0,1,0,0]
                case 'R': encoded += [0,0,0,0,0,0,0,1,0,0,0]
                case 'Q': encoded += [0,0,0,0,0,0,0,1,1,0,0]
                case 'K': encoded += [0,0,0,0,0,0,1,0,0,0,0]
                case 'p': encoded += [0,0,0,0,0,1,0,0,0,0,0]
                case 'n': encoded += [0,0,0,0,1,0,0,0,0,0,0]
                case 'b': encoded += [0,0,0,1,0,0,0,0,0,0,0]
                case 'r': encoded += [0,0,1,0,0,0,0,0,0,0,0]
                case 'q': encoded += [0,1,1,0,0,0,0,0,0,0,0]
                case 'k': encoded += [1,0,0,0,0,0,0,0,0,0,0]
    else:
        for piece in position.pos_array:
            match piece:
                case '':  encoded += [0,0,0,0,0,0,0,0,0,0]
                case 'p': encoded += [0,0,0,0,0,0,0,0,0,1]
                case 'n': encoded += [0,0,0,0,0,0,0,0,1,0]
                case 'b': encoded += [0,0,0,0,0,0,0,1,0,0]
                case 'r': encoded += [0,0,0,0,0,0,1,0,0,0]
                case 'q': encoded += [0,0,0,0,0,0,1,1,0,0]
                case 'k': encoded += [0,0,0,0,0,1,0,0,0,0]
                case 'P': encoded += [0,0,0,0,1,0,0,0,0,0]
                case 'N': encoded += [0,0,0,1,0,0,0,0,0,0]
                case 'B': encoded += [0,0,1,0,0,0,0,0,0,0]
                case 'R': encoded += [0,1,0,0,0,0,0,0,0,0]
                case 'Q': encoded += [0,1,1,0,0,0,0,0,0,0]
                case 'K': encoded += [1,0,0,0,0,0,0,0,0,0]
    return np.array(encoded)

def get_data(filename: str, start: int, stop: int) -> tuple[list[np.ndarray], list[np.ndarray]]:
    file = open(os.path.join(datasets_path, filename))
    positions: list[np.ndarray] = []
    resulting_moves: list[np.ndarray] = [] 
    for i, game in enumerate(file):
        if i < start:
            continue
        elif i >= stop:
            break 
        position = Position()
        moves = PortableGameNotation(game).get_moves()
        for move in moves:
            positions.append(position_encode(position))
            resulting_moves.append(np.array([int(bit) for bit in move.encode()]))
            position.move(move, skip_check=True)
    file.close()
    return positions, resulting_moves