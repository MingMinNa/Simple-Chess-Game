from __future__ import annotations
import pygame
from typing import Optional
from .chessman import *
from .board import *
from .game import *
from .gui_chessman import *
from .gui_board import *
from ..const import *
from ..gui_const import *
from ..type_defs import *


class PanelChessman(pygame.sprite.Sprite):

    def __init__(
            self, 
            x                  : int, 
            y                  : int, 
            team               : Team, 
            chessman_type_name : str, 
            chessman_images    : ImageDictType, 
            side_length        : int = CHESSMAN_SIDE_LENGTH
        ) -> None:

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(chessman_images[team][chessman_type_name], (side_length, side_length))
        self.image.set_colorkey(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = chessman_type_name

    def get_pos(self) -> CoordinateType:
        return (self.rect.x, self.rect.y)

class PromotionPanel(pygame.sprite.Sprite):

    def __init__(self, team: Team, chessman_images: ImageDictType) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.__promotion_panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT - 150))
        self.__promotion_panel.fill(GRAY)
        self.__rect = self.__promotion_panel.get_rect()
        self.__rect.center = (WIDTH // 2 - 150, HEIGHT // 2)

        self.chessman_types = list()
        self.chessman_sprite = pygame.sprite.Group()

        for i, chessman_type_name in enumerate(CHESSMAN_TYPE_NAMES[1: 5]):
            panel_chessman = PanelChessman(170 + (100 * i), 320 , team, chessman_type_name, chessman_images)
            self.chessman_sprite.add(panel_chessman)
            self.chessman_types.append(panel_chessman)
        
    def choose(self, mouse_pos: CoordinateType) -> Optional[str]:

        for chessman_type in self.chessman_types:
            if chessman_type.rect.x <= mouse_pos[0] <= chessman_type.rect.x + CHESSMAN_SIDE_LENGTH and \
               chessman_type.rect.y <= mouse_pos[1] <= chessman_type.rect.y + CHESSMAN_SIDE_LENGTH:
                return chessman_type.name
        return None
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(self.__promotion_panel, BLACK, self.__promotion_panel.get_rect(), 1)
        screen.blit(self.__promotion_panel, self.__rect)
        self.chessman_sprite.draw(screen)

class InfoPanel(pygame.sprite.Sprite):

    def __init__(self, chessman_images: ImageDictType) -> None:
        
        pygame.sprite.Sprite.__init__(self)
        self.__main_panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT - 35))
        self.__main_panel_rect = self.__main_panel.get_rect()
        self.__main_panel_rect.center = (WIDTH // 2, HEIGHT // 2 + 15)
        self.__main_panel.fill(GRAY)

        self.__exit_panel = pygame.Surface((80, 30))
        self.__exit_panel_rect = self.__exit_panel.get_rect()
        self.__exit_panel_rect.center = (WIDTH // 2, HEIGHT // 2 + 90)
        self.__exit_panel.fill(WHITE)

        self.__white_chessmen = dict()
        self.__black_chessman = dict()

        self.chessman_sprite = pygame.sprite.Group()

        for i, chessman_type_name in enumerate(CHESSMAN_TYPE_NAMES):
            white_chessman = PanelChessman(WIDTH // 2 - 160 + i * 55, HEIGHT // 2 - 60, Team.WHITE, chessman_type_name, chessman_images, side_length = 50)
            black_chessman = PanelChessman(WIDTH // 2 - 160 + i * 55, HEIGHT // 2 + 5, Team.BLACK, chessman_type_name, chessman_images, side_length = 50)
            self.chessman_sprite.add(white_chessman)
            self.chessman_sprite.add(black_chessman)
            self.__white_chessmen[chessman_type_name] = white_chessman
            self.__black_chessman[chessman_type_name] = black_chessman

    def draw(self, screen: pygame.Surface, dead_chessmen: DeadChessmenType) -> None:
        
        pygame.draw.rect(self.__main_panel, BLACK, self.__main_panel.get_rect(), 1)
        screen.blit(self.__main_panel, self.__main_panel_rect)
        
        pygame.draw.rect(self.__exit_panel, BLACK, self.__exit_panel.get_rect(), 1)
        screen.blit(self.__exit_panel, self.__exit_panel_rect)

        self.chessman_sprite.draw(screen)

        for chessman_type_name in CHESSMAN_TYPE_NAMES:
            white_chessman_pos = self.__white_chessmen[chessman_type_name].get_pos()
            black_chessman_pos = self.__black_chessman[chessman_type_name].get_pos()

            white_dead_count = dead_chessmen["White"][chessman_type_name]
            black_dead_count = dead_chessmen["Black"][chessman_type_name]

            draw_text(screen, str(white_dead_count), white_chessman_pos[0], white_chessman_pos[1] + 50, 20, WHITE)
            draw_text(screen, str(black_dead_count), black_chessman_pos[0], black_chessman_pos[1] + 50, 20, BLACK)

        draw_text(screen, "Exit", self.__exit_panel_rect.center[0], self.__exit_panel_rect.center[1], 30, BLACK)

    def is_in_exit_button(self, mouse_pos: CoordinateType) -> bool:

        x, y = mouse_pos[0], mouse_pos[1]

        if self.__exit_panel_rect.x <= x <= self.__exit_panel_rect.x + self.__exit_panel.get_width() and \
           self.__exit_panel_rect.y <= y <= self.__exit_panel_rect.y + self.__exit_panel.get_height():
            return True
        return False

class GameEndPanel(pygame.sprite.Sprite):

    def __init__(self, winner: Optional[Team]) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.__end_panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
        self.__end_panel.fill(GRAY)
        self.__rect = self.__end_panel.get_rect()
        self.__rect.center = (WIDTH // 2, HEIGHT // 2)
        self.__winner = winner

    def get_x(self) -> int:
        return self.__rect.x
    
    def get_y(self) -> int:
        return self.__rect.y

    def get_width(self) -> int:
        return self.__end_panel.get_width()
    
    def get_height(self) -> int:
        return self.__end_panel.get_height()
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(self.__end_panel, BLACK, self.__end_panel.get_rect(), 1)
        screen.blit(self.__end_panel, self.__rect)

        foreground_color = BLACK if self.__winner == Team.BLACK else WHITE

        if self.__winner is not None:
            draw_text(screen, f"Winner: {self.__winner.name.title()}", WIDTH // 2, HEIGHT // 2 - 20, 75, foreground_color)
        else:
            draw_text(screen, f"Draw", WIDTH // 2, HEIGHT // 2 - 20, 75, foreground_color)
        draw_text(screen, f"Press any to continue", WIDTH // 2, HEIGHT // 2 + 40, 40, foreground_color)

class RecordPanel(pygame.sprite.Sprite):

    def __init__(self) -> None:
        pygame.sprite.Sprite.__init__(self)

        self.__max_round = 0
        self.__max_display_count = 15
        self.__start_round = 1
        self.__end_round = self.__max_display_count
        self.__latest = True
        
        self.__record_cells = dict()
        self.__record_cells_rect = dict()
        start_x, start_y = INIT_X + CELL_SIDE_LENGTH * 8 + 70, INIT_Y + 30
        for i in range(self.__max_display_count):
            self.__record_cells[i] = dict()
            self.__record_cells_rect[i] = dict()

            panel, panel_rect = self.__generate_cell(RECORD_CELL_WITDH, RECORD_CELL_HEIGHT, start_x, start_y + RECORD_CELL_HEIGHT * i, FRESH_GREEN)
            self.__record_cells[i][Team.WHITE] = panel
            self.__record_cells_rect[i][Team.WHITE] = panel_rect
            
            panel, panel_rect = self.__generate_cell(RECORD_CELL_WITDH, RECORD_CELL_HEIGHT, start_x + RECORD_CELL_WITDH, start_y + RECORD_CELL_HEIGHT * i, FRESH_GREEN)
            self.__record_cells[i][Team.BLACK] = panel
            self.__record_cells_rect[i][Team.BLACK] = panel_rect

    def draw(
            self, 
            screen          : pygame.Surface, 
            rounds          : int, 
            chess_notations : NotationType
        ) -> None:

        self.__max_round = max(self.__max_round, rounds)

        if self.__latest: 
            self.__end_round = self.__max_round
            self.__start_round = max(1, self.__end_round - self.__max_display_count + 1)

        draw_text(screen, "White", INIT_X + CELL_SIDE_LENGTH * 8 + 70 + 60, INIT_Y + 5, 40, WHITE)
        draw_text(screen, "Black", INIT_X + CELL_SIDE_LENGTH * 8 + 70 + 120 + 60, INIT_Y + 5, 40, GRAY)
        
        for i in range(self.__max_display_count):
            round_index = i + self.__start_round
            draw_text(screen, str(round_index), self.__record_cells_rect[i][Team.WHITE].x - 30, self.__record_cells_rect[i][Team.WHITE].center[1], 40, WHITE)

            for team in (Team.WHITE, Team.BLACK):
                pygame.draw.rect(self.__record_cells[i][team], BACKGROUND_COLOR, self.__record_cells[i][team].get_rect(), 2)
                screen.blit(self.__record_cells[i][team], self.__record_cells_rect[i][team])
            
            if round_index > rounds: continue

            for team, color in zip((Team.WHITE, Team.BLACK), \
                                   (     WHITE,      BLACK)):
                if team not in chess_notations[round_index]: continue
                center_x, center_y = self.__record_cells_rect[i][team].center
                draw_text(screen, chess_notations[round_index][team], center_x, center_y, 35, color)

    def set_latest(self) -> None:
        self.__latest = True

    def scroll_up(self) -> None:

        self.__latest = False
        if self.__start_round > 1:
            self.__end_round -= 1
            self.__start_round -= 1

    def scroll_down(self) -> None:

        self.__latest = False
        if self.__end_round < self.__max_round:
            self.__end_round += 1
            self.__start_round += 1

    def __generate_cell(
            self, 
            width  : int, 
            height : int, 
            x      : int, 
            y      : int, 
            color  : ColorType
        ) -> Tuple[pygame.Surface, pygame.Rect]:
        
        panel = pygame.Surface((width, height))
        panel_rect = panel.get_rect()
        panel_rect.x = x
        panel_rect.y = y
        panel.fill(color)
        return panel, panel_rect