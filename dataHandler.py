def file_transform(input_filename: str, output_filename: str | None = None) -> str:
    if output_filename == None:
        out_file = open(input_filename.partition('.')[0] + 'txt', 'w')
    else:
        out_file = open(output_filename, 'w')
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
                out_file.write("LobbyElo " + str((black_elo + white_elo) // 2) + '\n')
            elif line.split()[0] == '1.':
                pgn_string = remove_evaluations(line)
                pgn_string = remove_assessments(pgn_string)
                out_file.write(pgn_string)
    out_file.close()
    return out_file.name

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

def data_load(filename: str) -> list:
    data: list[list] = [[]]
    with open(filename) as file:
        for line in file:
            if line.split()[0][1:] in ["WhiteElo", "BlackElo"]:
                data[-1].append(int(line.split()[-1]))
            elif line.split()[0] == '1.':
                data[-1].append(line)
                data.append([])
    return data[:-1]

if __name__ == '__main__':
    FILENAME = "lichess_db_standard_rated_2013-01.pgn"
    file_transform(FILENAME)