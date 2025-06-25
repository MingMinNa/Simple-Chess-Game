import pygame

from .chessman import *
from .board import *
from .game import *
from .gui_chessman import *
from .gui_board import *
from ..const import *
from ..gui_const import *


class PanelChessman(pygame.sprite.Sprite):

    def __init__(self, x: int, y:int, team: Team, chessman_type_name:str, chessman_images, side_length: int = CHESSMAN_SIDE_LENGTH) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(chessman_images[team][chessman_type_name], (side_length, side_length))
        self.image.set_colorkey(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = chessman_type_name

    def get_pos(self):
        return (self.rect.x, self.rect.y)

class PromotionPanel(pygame.sprite.Sprite):

    def __init__(self, team: Team, chessman_images) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.__promotion_panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT - 150))
        self.__promotion_panel.fill(GRAY)
        self.__rect = self.__promotion_panel.get_rect()
        self.__rect.center = (WIDTH // 2, HEIGHT // 2)

        self.chessman_types = list()
        self.chessman_sprite = pygame.sprite.Group()

        for i, chessman_type_name in enumerate(CHESSMAN_TYPE_NAMES[1: 5]):
            panel_chessman = PanelChessman(170 + (100 * i), 320 , team, chessman_type_name, chessman_images)
            self.chessman_sprite.add(panel_chessman)
            self.chessman_types.append(panel_chessman)
        
    def choose(self, mouse_pos):

        for chessman_type in self.chessman_types:
            if chessman_type.rect.x <= mouse_pos[0] <= chessman_type.rect.x + CHESSMAN_SIDE_LENGTH and \
               chessman_type.rect.y <= mouse_pos[1] <= chessman_type.rect.y + CHESSMAN_SIDE_LENGTH:
                return chessman_type.name
        return None
    
    def draw(self, screen):
        pygame.draw.rect(self.__promotion_panel, BLACK, self.__promotion_panel.get_rect(), 1)
        screen.blit(self.__promotion_panel, self.__rect)
        self.chessman_sprite.draw(screen)

class DeadChessmanPanel(pygame.sprite.Sprite):

    def __init__(self, chessman_images):
        pygame.sprite.Sprite.__init__(self)
        self.__chessman_panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT - 50))
        self.__chessman_panel_rect = self.__chessman_panel.get_rect()
        self.__chessman_panel_rect.center = (WIDTH // 2, HEIGHT // 2)
        self.__chessman_panel.fill(GRAY)

        self.__white_chessmen = dict()
        self.__black_chessman = dict()

        self.chessman_sprite = pygame.sprite.Group()

        for i, chessman_name in enumerate(CHESSMAN_TYPE_NAMES):
            white_chessman = PanelChessman(WIDTH // 2 - 160 + i * 55, HEIGHT // 2 - 60, Team.WHITE, chessman_name, chessman_images, side_length = 50)
            black_chessman = PanelChessman(WIDTH // 2 - 160 + i * 55, HEIGHT // 2 + 5, Team.BLACK, chessman_name, chessman_images, side_length = 50)
            self.chessman_sprite.add(white_chessman)
            self.chessman_sprite.add(black_chessman)
            self.__white_chessmen[chessman_name] = white_chessman
            self.__black_chessman[chessman_name] = black_chessman

    def draw(self, screen, dead_chessmen):
        pygame.draw.rect(self.__chessman_panel, BLACK, self.__chessman_panel.get_rect(), 1)
        screen.blit(self.__chessman_panel, self.__chessman_panel_rect)
        self.chessman_sprite.draw(screen)

        for chessman_name in CHESSMAN_TYPE_NAMES:
            white_chessman_pos = self.__white_chessmen[chessman_name].get_pos()
            black_chessman_pos = self.__black_chessman[chessman_name].get_pos()

            white_dead_count = dead_chessmen["White"][chessman_name]
            black_dead_count = dead_chessmen["Black"][chessman_name]

            draw_text(screen, str(white_dead_count), white_chessman_pos[0], white_chessman_pos[1] + 50, 20, WHITE)
            draw_text(screen, str(black_dead_count), black_chessman_pos[0], black_chessman_pos[1] + 50, 20, BLACK)

class GameEndPanel(pygame.sprite.Sprite):

    def __init__(self, winner: Team):
        pygame.sprite.Sprite.__init__(self)
        self.__end_panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
        self.__end_panel.fill(GRAY)
        self.__rect = self.__end_panel.get_rect()
        self.__rect.center = (WIDTH // 2, HEIGHT // 2)
        self.__winner = winner

    def draw(self, screen):
        pygame.draw.rect(self.__end_panel, BLACK, self.__end_panel.get_rect(), 1)
        screen.blit(self.__end_panel, self.__rect)
        foreground_color = WHITE if self.__winner == Team.WHITE else BLACK
        draw_text(screen, f"Winner: {self.__winner.name.title()}", WIDTH // 2, HEIGHT // 2 - 20, 75, foreground_color)
        draw_text(screen, f"Press any to continue", WIDTH // 2, HEIGHT // 2 + 40, 40, foreground_color)