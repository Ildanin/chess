import pygame as pg
from settings import *
from positionClass import Position
from notation import ForsythEdwardsNotation, PortableGameNotation
import os


BB = pg.image.load(os.path.join("assets", "black_bishop.png "))
BK = pg.image.load(os.path.join("assets", "black_king.png "))
BN = pg.image.load(os.path.join("assets", "black_knight.png "))
BP = pg.image.load(os.path.join("assets", "black_pawn.png "))
BQ = pg.image.load(os.path.join("assets", "black_queen.png "))
BR = pg.image.load(os.path.join("assets", "black_rook.png "))

WB = pg.image.load(os.path.join("assets", "white_bishop.png "))
WK = pg.image.load(os.path.join("assets", "white_king.png "))
WN = pg.image.load(os.path.join("assets", "white_knight.png "))
WP = pg.image.load(os.path.join("assets", "white_pawn.png "))
WQ = pg.image.load(os.path.join("assets", "white_queen.png "))
WR = pg.image.load(os.path.join("assets", "white_rook.png"))

class ChessBoard:
    def __init__(self, screen: pg.Surface, x: int, y: int, size: int = BOARD_SIZE, position: Position = Position(ForsythEdwardsNotation(INIT_POSITION)),
                 white_color: tuple = WHITE_COLOR, black_color: tuple = BLACK_COLOR, highlight_clor: tuple = HIGHLIGHT_COLOR, higlight_moves: bool = HIGHLIGHT_MOVES) -> None:
        self.screen = screen
        self.x = x
        self.y = y
        self.square_size = size//8
        self.size = self.square_size*8
        self.white_color = white_color
        self.black_color = black_color
        self.highlight_clor = highlight_clor
        self.higlight_moves = higlight_moves

        self.position = position

        self.prev_pos: tuple[int, int] | None = None
        self.higlighted_squares: list[tuple[int, int]] | None = None
        self.promotion = None

        self.piece_assets = {
            'b': pg.transform.scale(BB.convert_alpha(), (self.square_size, self.square_size)),
            'k': pg.transform.scale(BK.convert_alpha(), (self.square_size, self.square_size)),
            'n': pg.transform.scale(BN.convert_alpha(), (self.square_size, self.square_size)),
            'p': pg.transform.scale(BP.convert_alpha(), (self.square_size, self.square_size)),
            'q': pg.transform.scale(BQ.convert_alpha(), (self.square_size, self.square_size)),
            'r': pg.transform.scale(BR.convert_alpha(), (self.square_size, self.square_size)),

            'B': pg.transform.scale(WB.convert_alpha(), (self.square_size, self.square_size)),
            'K': pg.transform.scale(WK.convert_alpha(), (self.square_size, self.square_size)),
            'N': pg.transform.scale(WN.convert_alpha(), (self.square_size, self.square_size)),
            'P': pg.transform.scale(WP.convert_alpha(), (self.square_size, self.square_size)),
            'Q': pg.transform.scale(WQ.convert_alpha(), (self.square_size, self.square_size)),
            'R': pg.transform.scale(WR.convert_alpha(), (self.square_size, self.square_size))
            }
        self.draw()

    def get_square(self, mouse_x: int, mouse_y: int) -> tuple[int, int]: #add flip
        "Returns the coordinates of the square relative to its position on the screen"
        board_x = (mouse_x-self.x) // self.square_size
        board_y = (mouse_y-self.y) // self.square_size
        return board_x, board_y

    def get_piece(self, board_x: int, board_y: int) -> str:
        "Returns the piece located in the given coordinates"
        if 0 <= board_x < 8 and 0 <= board_y < 8:
            return self.position.get_piece(board_x, board_y)
        return ''
    
    def process_left_click(self, mouse_x: int, mouse_y: int) -> None:
        "Handles user's lmb press"
        board_x, board_y = self.get_square(mouse_x, mouse_y)
        if not(0 <= board_x < 8 and 0 <= board_y < 8):
            return None
        if self.prev_pos == None:
            self.pick(board_x, board_y)
        elif self.promotion != None:
            self.pick_promotion(board_x, board_y)
            self.unpick()
        elif (board_x, board_y) == self.prev_pos:
            self.unpick()
        elif self.position.is_move_possible(*self.prev_pos, board_x, board_y, self.higlighted_squares):
            if self.position.ispromotion(board_y, self.get_piece(*self.prev_pos)):
                self.position.set_piece(*self.prev_pos, '')
                self.promotion = (board_x, board_y)
                self.higlighted_squares = [self.promotion]
            else:
                self.position.move(*self.prev_pos, board_x, board_y, available_squares=self.higlighted_squares)
                self.unpick()
        else:
            self.pick(board_x, board_y)
    
    def pick(self, board_x: int, board_y: int) -> None:
        self.prev_pos = (board_x, board_y)
        if self.higlight_moves:
            self.higlighted_squares = self.position.get_highlights(board_x, board_y)

    def unpick(self) -> None:
        self.prev_pos = None
        self.higlighted_squares = None

    def pick_promotion(self, board_x: int, board_y: int) -> None:
        "Handles user's clicks on the screen during a pawn promotion"
        if self.promotion == None or self.prev_pos == None:
            raise ValueError("no pawn promotion is present")
        if self.promotion[1] == 0:
            if self.promotion[0] == board_x and (0 <= board_y < 4):
                self.position.move(*self.prev_pos, *self.promotion, ['Q', 'N', 'R', 'B'][board_y], self.higlighted_squares)
            else:
                self.position.set_piece(*self.prev_pos, 'P')
        elif self.promotion[1] == 7:
            if self.promotion[0] == board_x and (4 <= board_y < 8):
                self.position.move(*self.prev_pos, *self.promotion, ['q', 'n', 'r', 'b'][7 - board_y], self.higlighted_squares)
            else:
                self.position.set_piece(*self.prev_pos, 'p')
        self.promotion = None        
    
    def draw(self) -> None: #add flip
        "Draws board with pieces to the screen"
        self.draw_board()
        self.draw_coordinates()
        self.higlight()
        self.draw_pieces()
        self.draw_promotion_screen()

    def draw_board(self) -> None: #add flip
        "Draws the board to the screen"
        for board_y in range(0, 8):
            for board_x in range(0, 8):
                if (board_x % 2 == 0) ^ (board_y % 2 == 0):
                    pg.draw.rect(self.screen, 
                                 self.black_color, 
                                 pg.Rect(self.square_size * board_x + self.x, 
                                         self.square_size * board_y + self.y, 
                                         self.square_size, self.square_size))
                else:
                    pg.draw.rect(self.screen, 
                                 self.white_color, 
                                 pg.Rect(self.square_size * board_x + self.x, 
                                         self.square_size * board_y + self.y, 
                                         self.square_size, self.square_size))
    
    def draw_coordinates(self) -> None: #add flip #todo
        pass

    def draw_pieces(self) -> None: #add flip
        "Draws pieces to the screen"
        for i, piece in enumerate(self.position):
            if piece != '':
                self.screen.blit(self.piece_assets[piece], 
                                 (self.x + (i%8)*self.square_size, 
                                  self.y + (i//8)*self.square_size))

    def higlight(self) -> None: #add flip
        "Highlights all the squares that can be accessed by the picked piece"
        if self.higlighted_squares == None:
            return None
        for x, y in self.higlighted_squares:
            pg.draw.rect(self.screen, self.highlight_clor, 
                        pg.Rect(self.x + x * self.square_size, 
                                self.y + y * self.square_size, 
                                self.square_size, self.square_size))
    
    def draw_promotion_screen(self) -> None: #add flip
        if self.promotion == None:
            return None
        if self.promotion[1] == 0:
            pg.draw.rect(self.screen, (255, 255, 255), 
                            pg.Rect(self.x + self.promotion[0]*self.square_size, 
                                    self.y + self.promotion[1]*self.square_size, 
                                    self.square_size, 4*self.square_size))
            for y, piece in zip(range(self.promotion[1], self.promotion[1]+4, 1), ['Q', 'N', 'R', 'B']):
                self.screen.blit(self.piece_assets[piece], 
                                (self.x + self.promotion[0]*self.square_size, 
                                    self.y + y*self.square_size))
        elif self.promotion[1] == 7:
            pg.draw.rect(self.screen, (255, 255, 255), 
                            pg.Rect(self.x + self.promotion[0]*self.square_size, 
                                    self.y + (self.promotion[1] - 3)*self.square_size, 
                                    self.square_size, 4*self.square_size))
            for y, piece in zip(range(self.promotion[1], self.promotion[1]-4, -1), ['q', 'n', 'r', 'b']):
                self.screen.blit(self.piece_assets[piece], 
                                (self.x + self.promotion[0]*self.square_size, 
                                    self.y + y*self.square_size))

    def ischekmate(self) -> bool:
        "Returns True if position is a checkmate, False otherwise"
        return self.position.ischeckmate()
    
    def isdraw(self) -> bool:
        "Returns True if position is a draw, False otherwise"
        return self.position.isdraw()
    
'''    def reset(self) -> list[str]:
        "Returns the board to its originall state"
        out = self.history.copy()
        self.history.clear()
        self.position = self.get_position(self.init_FEN_position)
        self.position_handler.__init__(self.position)
        self.prev_pos = None
        self.higlighted_squares = None
        self.draw()
        return(out)'''