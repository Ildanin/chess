import pygame as pg
from config import *
from positionClass import Position
from notation import ForsythEdwardsNotation, BoardSquare, BoardMove
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

        self.prev_square: BoardSquare | None = None
        self.higlighted_squares: list[BoardSquare] | None = None
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

    def get_square(self, mouse_x: int, mouse_y: int) -> BoardSquare: #add flip
        "Returns the coordinates of the square relative to its position on the screen"
        file = (mouse_x-self.x) // self.square_size
        rank = (mouse_y-self.y) // self.square_size
        return BoardSquare(file, rank)

    def get_piece(self, square: BoardSquare) -> str:
        "Returns the piece located in the given coordinates"
        if square.isinrange():
            return self.position.get_piece(square)
        return ''
    
    def process_left_click(self, mouse_x: int, mouse_y: int) -> None:
        "Handles user's lmb press"
        square = self.get_square(mouse_x, mouse_y)
        if not(square.isinrange()):
            return None
        if self.prev_square == None:
            self.pick(square)
        elif self.promotion != None:
            self.pick_promotion(square)
            self.unpick()
        elif square == self.prev_square:
            self.unpick()
        elif self.position.is_move_possible(BoardMove(self.prev_square, square), self.higlighted_squares):
            if self.position.ispromotion(square.rank, self.get_piece(self.prev_square)):
                self.position.set_piece(self.prev_square, '')
                self.promotion = square
                self.higlighted_squares = [self.promotion]
            else:
                self.position.move(BoardMove(self.prev_square, square), available_squares=self.higlighted_squares)
                self.unpick()
        else:
            self.pick(square)
    
    def pick(self, square: BoardSquare) -> None:
        self.prev_square = square
        if self.higlight_moves:
            self.higlighted_squares = self.position.get_highlights(square)

    def unpick(self) -> None:
        self.prev_square = None
        self.higlighted_squares = None

    def pick_promotion(self, square: BoardSquare) -> None:
        "Handles user's clicks on the screen during a pawn promotion"
        if self.promotion == None or self.prev_square == None:
            raise ValueError("no pawn promotion is present")
        if self.promotion.rank == 0:
            if self.promotion.file == square.file and (0 <= square.rank < 4):
                self.position.move(BoardMove(self.prev_square, self.promotion), ['Q', 'N', 'R', 'B'][square.rank], self.higlighted_squares)
            else:
                self.position.set_piece(self.prev_square, 'P')
        elif self.promotion.rank == 7:
            if self.promotion.file == square.file and (4 <= square.rank < 8):
                self.position.move(BoardMove(self.prev_square, self.promotion), ['q', 'n', 'r', 'b'][7 - square.rank], self.higlighted_squares)
            else:
                self.position.set_piece(self.prev_square, 'p')
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
        for rank in range(0, 8):
            for file in range(0, 8):
                if (rank + file)%2 == 0:
                    pg.draw.rect(self.screen, 
                                 self.white_color, 
                                 pg.Rect(self.square_size * file + self.x, 
                                         self.square_size * rank + self.y, 
                                         self.square_size, self.square_size))
                else:
                    pg.draw.rect(self.screen, 
                                 self.black_color, 
                                 pg.Rect(self.square_size * file + self.x, 
                                         self.square_size * rank + self.y, 
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
        if self.promotion.file == 0:
            pg.draw.rect(self.screen, (255, 255, 255), 
                            pg.Rect(self.x + self.promotion.file * self.square_size, 
                                    self.y + self.promotion.rank * self.square_size, 
                                    self.square_size, 4*self.square_size))
            for y, piece in zip(range(self.promotion.rank, self.promotion.rank +4, 1), ['Q', 'N', 'R', 'B']):
                self.screen.blit(self.piece_assets[piece], 
                                (self.x + self.promotion.file * self.square_size, 
                                    self.y + y * self.square_size))
        elif self.promotion.file == 7:
            pg.draw.rect(self.screen, (255, 255, 255), 
                            pg.Rect(self.x + self.promotion.file * self.square_size, 
                                    self.y + (self.promotion.file - 3) * self.square_size, 
                                    self.square_size, 4*self.square_size))
            for y, piece in zip(range(self.promotion.file, self.promotion.file -4, -1), ['q', 'n', 'r', 'b']):
                self.screen.blit(self.piece_assets[piece], 
                                (self.x + self.promotion.rank * self.square_size, 
                                    self.y + y * self.square_size))

    def ischekmate(self) -> bool:
        "Returns True if position is a checkmate, False otherwise"
        return self.position.ischeckmate()
    
    def isdraw(self) -> bool:
        "Returns True if position is a draw, False otherwise"
        return self.position.isdraw()