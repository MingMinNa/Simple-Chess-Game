import pygame
from enum import Enum, auto
from .game import ChessGame
from .chessman import *
from .board import *
from ..const import *
from ..gui_const import *
from ..type_defs import *


class GuiChessmanState(Enum):
    UP = auto()
    DOWN = auto()

class GuiChessman(pygame.sprite.Sprite):

    @staticmethod
    def repaint_chessmen(chess_game: ChessGame, chessman_bind: "ChessmanBindType") -> None:
        for r in ROW_VALUE_RANGE:
            for c in COL_VALUE_RANGE:
                chessman = chess_game.get_chessman(r, c)
                if chessman is not None:
                    c_x, c_y = GuiChessman.calc_cell_x_y(r, c, chess_game.get_current_turn())
                    chessman_bind[chessman].set_cell_x_y(c_x, c_y)  

    @staticmethod
    def calc_cell_x_y(row: int, col: str, current_turn: Team) -> "CellPosType":

        if current_turn == Team.BLACK:
            # (row, col) = (1, 'a') => (x, y) = (7, 0)
            # (row, col) = (8, 'h') => (x, y) = (0, 7)
            return (7 - COL_VALUE_RANGE.index(col), row - 1)
        else:
            # (row, col) = (1, 'a') => (x, y) = (0, 7)
            # (row, col) = (8, 'h') => (x, y) = (7, 0)
            return (COL_VALUE_RANGE.index(col), 7 - row + 1) 

    @staticmethod
    def calc_row_col(cell_x: int, cell_y: int, current_turn: Team) -> "BoardPosType":
        
        def int_to_letter(col_idx: int) -> str:
            if col_idx >= len(COL_VALUE_RANGE) or col_idx < 0: return "#" # error chars
            return COL_VALUE_RANGE[col_idx]

        if current_turn == Team.BLACK:
            # (row, col) = (1, 'a') <= (x, y) = (7, 0)
            # (row, col) = (8, 'h') <= (x, y) = (0, 7)
            return (cell_y + 1, int_to_letter(7 - cell_x))
        else:
            # (row, col) = (1, 'a') <= (x, y) = (0, 7)
            # (row, col) = (8, 'h') <= (x, y) = (7, 0)
            return (8 - cell_y, int_to_letter(cell_x))

    def __init__(self, cell_x: int, cell_y: int, team: Team, image: pygame.Surface) -> None:
        
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(image, (CHESSMAN_SIDE_LENGTH, CHESSMAN_SIDE_LENGTH))
        self.image.set_colorkey(RED)

        self.team = team
        self.cell_x = cell_x
        self.cell_y = cell_y

        # set the position
        self.rect = self.image.get_rect()
        self.rect.x = INIT_X + cell_x * CELL_SIDE_LENGTH + 10
        self.rect.y = INIT_Y + cell_y * CELL_SIDE_LENGTH + 10

        self.state = GuiChessmanState.DOWN

    def click(self) -> None:
        
        if self.state == GuiChessmanState.DOWN: self.__up()
        else:                                   self.__down()
    
    def __down(self) -> None:
        if self.state == GuiChessmanState.UP:
            self.rect.y += 10
        self.state = GuiChessmanState.DOWN

    def __up(self) -> None:
        if self.state == GuiChessmanState.DOWN:
            self.rect.y -= 10
        self.state = GuiChessmanState.UP

    def set_cell_x_y(self, cell_x: int, cell_y: int) -> None:
        self.cell_x = cell_x
        self.cell_y = cell_y

        self.rect.x = INIT_X + cell_x * CELL_SIDE_LENGTH + 10
        self.rect.y = INIT_Y + cell_y * CELL_SIDE_LENGTH + 10
    
    def get_cell_x_y(self) -> "CellPosType":
        return (self.cell_x, self.cell_y)
