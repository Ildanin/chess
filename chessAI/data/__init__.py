from notation.pgn import PortableGameNotation
from positionClass import Position
import numpy as np
import os
datasets_path = os.path.dirname(__file__)

def position_encode(position: Position) -> str:
    encoded = ''
    if position.white_move:
        for piece in position.pos_array:
            match piece:
                case '':  encoded += '00000000000'
                case 'P': encoded += '00000000001'
                case 'N': encoded += '00000000010'
                case 'B': encoded += '00000000100'
                case 'R': encoded += '00000001000'
                case 'Q': encoded += '00000001100'
                case 'K': encoded += '00000010000'
                case 'p': encoded += '00000100000'
                case 'n': encoded += '00001000000'
                case 'b': encoded += '00010000000'
                case 'r': encoded += '00100000000'
                case 'q': encoded += '01100000000'
                case 'k': encoded += '10000000000'
    else:
        for piece in position.pos_array:
            match piece:
                case '':  encoded += '0000000000'
                case 'P': encoded += '0000000001'
                case 'N': encoded += '0000000010'
                case 'B': encoded += '0000000100'
                case 'R': encoded += '0000001000'
                case 'Q': encoded += '0000001100'
                case 'K': encoded += '0000010000'
                case 'p': encoded += '0000100000'
                case 'n': encoded += '0001000000'
                case 'b': encoded += '0010000000'
                case 'r': encoded += '0100000000'
                case 'q': encoded += '0110000000'
                case 'k': encoded += '1000000000'
    return encoded

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
            positions.append(np.array([int(bit) for bit in position_encode(position)]))
            resulting_moves.append(np.array([int(bit) for bit in move.encode()]))
            position.move(move, skip_check=True)
    file.close()
    return positions, resulting_moves

def get_games(filename: str, start: int = 0, stop: int | None = None) -> list[PortableGameNotation]:
    games = []
    with open(os.path.join(datasets_path, filename)) as file:
        for i, line in enumerate(file):
            if start > i:
                continue
            if stop != None and stop <= i:
                break
            games.append(PortableGameNotation(line))
    return games