import pygame
from .chessman import *
from .board import *
from .gui_chessman import *
from ..const import *
from ..gui_const import *
from ..type_defs import *


def draw_text(screen: pygame.Surface, text: str, 
              center_x: int,          center_y: int, 
              fontSize: int,          Fontcolor: "ColorType", 
              background_color: Optional["ColorType"] = None) \
              -> pygame.Surface:

    font = pygame.font.Font(None, fontSize)
    text_surface = font.render(f"{text}", True, Fontcolor)
    text_rect = text_surface.get_rect()
    text_rect.center = (center_x, center_y)
    if background_color: screen.fill(background_color, text_rect)
    screen.blit(text_surface, text_rect)

    return text_rect

class GuiBoardCell(pygame.sprite.Sprite):

    def __init__(self, cell_x: int, cell_y: int, color: "ColorType") -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((CELL_SIDE_LENGTH, CELL_SIDE_LENGTH))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 1)

        self.rect.x = INIT_X + CELL_SIDE_LENGTH * cell_x
        self.rect.y = INIT_Y + CELL_SIDE_LENGTH * cell_y

    def set_color(self, color: "ColorType") -> None:
        self.image.fill(color)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 1)
    
class GuiBoard:
    
    @staticmethod
    def get_click_cell(pos: "CoordinateType") -> "CellPosType":
        return ((pos[0] - INIT_X) // CELL_SIDE_LENGTH, 
                (pos[1] - INIT_Y) // CELL_SIDE_LENGTH)

    def __init__(self) -> None:
        self.board = list()
        self.boardcell_sprite = pygame.sprite.Group()

        for i in range(len(ROW_VALUE_RANGE)):
            self.board.append(list())
            color_idx = i % 2
            for j in range(len(COL_VALUE_RANGE)):
                cell = GuiBoardCell(j, i, BOARDCELL_COLORS[(color_idx + j) % 2])
                self.board[i].append(cell)
                self.boardcell_sprite.add(cell)

    def refresh_board(self) -> None:

        for i in range(len(ROW_VALUE_RANGE)):
            color_idx = i % 2
            for j in range(len(COL_VALUE_RANGE)):
                self.board[i][j].set_color(BOARDCELL_COLORS[(color_idx + j) % 2])
        
    def paint_move_area(self, current_turn: Team, valid_moves: set["MoveType"]) -> None:
        
        for action, pos in valid_moves:
            cell_x, cell_y = GuiChessman.calc_cell_x_y(pos[0], pos[1], current_turn)

            if action == "Move":
                self.board[cell_y][cell_x].set_color(MOVE_COLOR)
            elif action == "Attack":
                self.board[cell_y][cell_x].set_color(ATTACK_COLOR)
            elif action == "Promotion":
                self.board[cell_y][cell_x].set_color(PROMOTION_COLOR)
            elif action == "Castling":
                self.board[cell_y][cell_x].set_color(CASTLING_COLOR)
    
    def draw_board(self, screen: pygame.Surface, current_turn: Team) -> None:
        self.get_bordcell_sprite().draw(screen)

        if current_turn == Team.WHITE: order = 1
        else:                          order = -1

        row_index_start_pos = (INIT_X + 8, INIT_Y + CELL_SIDE_LENGTH * 7 + 10)
        for i, row_index in enumerate(ROW_VALUE_RANGE[::order]):
            draw_text(screen, f"{row_index}", row_index_start_pos[0], row_index_start_pos[1] - CELL_SIDE_LENGTH * i, 25, GREEN if i % 2 == 0 else FRESH_GREEN)

        col_index_start_pos = (INIT_X + CELL_SIDE_LENGTH - 8, INIT_Y + CELL_SIDE_LENGTH * 8 - 10)
        for i, col_index in enumerate(COL_VALUE_RANGE[::order]):
            draw_text(screen, f"{col_index}", col_index_start_pos[0] + CELL_SIDE_LENGTH * i, col_index_start_pos[1], 25, GREEN if i % 2 == 0 else FRESH_GREEN)

    def get_bordcell_sprite(self) -> pygame.sprite.Group:
        return self.boardcell_sprite
