import os
datasets_path = os.path.dirname(__file__)

def generate_games_file(input_filename: str, output_filename: str | None = None, elo_threshold: int | None = None) -> str:
    "Generates the file with games in descending average ELO order"
    if output_filename == None:
        output_filename = input_filename.partition('.')[0] + '.txt'
    data: list[tuple] = []
    with open(os.path.join(datasets_path, input_filename)) as inp_file:
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
                if elo_threshold != None and avg_elo < elo_threshold:
                    continue
            elif line.split()[0] == '1.':
                game = remove_evaluations(line)
                game = remove_assessments(game)
                data.append((avg_elo, game))
    with open(os.path.join(datasets_path, output_filename), 'w') as out_file:
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

if __name__ == '__main__':
    from time import perf_counter

    database = "lichess_db_standard_rated_2013-01.pgn"
    filename = "data.txt"
    threshold = None

    inp_database = input(f"Database: (default={database})")
    inp_filename = input(f"Filename: (default={filename})")
    inp_threshold = input(f"threshold: (default={None})")
    
    if inp_database != "":
        database = inp_database
    if inp_filename != "":
        filename = inp_filename
    if inp_threshold != "":
        threshold = inp_threshold
    
    t1 = perf_counter()
    generate_games_file("lichess_db_standard_rated_2013-01.pgn", "data.txt")
    t2 = perf_counter()
    print('======================================')
    print(f"Finished in {round(t2-t1, 2)} seconds")