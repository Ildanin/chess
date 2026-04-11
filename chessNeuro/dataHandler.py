from notation.pgn import PortableGameNotation
from config import UNTRANSFORMED

def get_games(input_filename: str, output_filename: str | None = None) -> str:
    "Returns the file with games in descending average ELO order"
    if output_filename == None:
        output_filename = input_filename.partition('.')[0] + '.txt'
    data: list[tuple] = []
    with open(input_filename) as inp_file:
        for line in inp_file:
            if line == '\n':
                pass
            elif line.split()[0][1:] == "WhiteElo":
                if line.split('"')[1] != '?':
                    white_elo = int(line.split('"')[1])
                else:
                    white_elo = 1000
            elif line.split()[0][1:] == "BlackElo":
                if line.split('"')[1] != '?':
                    black_elo = int(line.split('"')[1])
                else:
                    black_elo = 1000
                avg_elo = (black_elo + white_elo) // 2
            elif line.split()[0] == '1.':
                game = remove_evaluations(line)
                game = remove_assessments(game)
                data.append((avg_elo, game))
    with open(output_filename, 'w') as out_file:
        for avg_elo, game in sorted(data, reverse=True):
            out_file.write(game)
    return output_filename

def remove_evaluations(pgn_string: str) -> str:
    while pgn_string.count('{') > 0:
        start = pgn_string.index('{')
        stop = pgn_string.index('}')
        pgn_string = pgn_string[:start-1] + pgn_string[stop+1:]
    while pgn_string.count('...') > 0:
        start = pgn_string.index('...')
        pgn_string = pgn_string[:start-2] + pgn_string[start+3:]
    return pgn_string

def remove_assessments(pgn_string: str) -> str:
    pgn_string = pgn_string.replace('?', '')
    pgn_string = pgn_string.replace('!', '')
    return pgn_string

def data_load(filename: str, start: int = 0, stop: int | None = None) -> list[tuple[int, PortableGameNotation]]:
        data: list[tuple] = []
        with open(filename) as file:
            for i, line in enumerate(file):
                if start > i//2 or (stop != None and i//2 >= stop):
                    continue
                if line.split()[0] == "LobbyElo":
                    elo = int(line.split()[-1])
                elif line.split()[0] == '1.':
                    pgn = PortableGameNotation(line[:-1])
                    data.append((elo, pgn))
        return data[:-1]

if __name__ == '__main__':
    get_games("lichess_db_standard_rated_2013-01.pgn", "dataset.txt")