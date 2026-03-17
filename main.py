from chessBoard import *
from settings import WIN_WIDTH, WIN_HEIGHT
from time import perf_counter
from random import randrange

screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
clock = pg.Clock()
board = ChessBoard(screen, BOARD_X, BOARD_Y)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            #t1 = perf_counter()
            board.process_left_click(*pg.mouse.get_pos())
            #t2 = perf_counter()
            #print(round(10**6 * (t2-t1), 7))
            board.draw()
        elif event.type == pg.KEYDOWN:
            key = event.key
            if key == pg.K_SPACE:
                #board.reset()
                pass
    
    '''possible_moves = board.position_handler.get_possible_moves()
    if board.move_piece(*possible_moves[randrange(0, len(possible_moves))]):
        board.draw()
    if board.position_handler.is_checkmate():
        print('Checkmate')
        print(board.history[-1])
        exit()
    elif board.position_handler.is_draw():
        print('Draw')
        print(board.history[-1])
        exit()'''
    
    pg.display.flip()

    clock.tick(1000)