import pygame

from .chessman import *
from .board import *
from .game import *
from .gui_chessman import *
from .gui_board import *
from ..const import *
from ..gui_const import *


def draw_promotion_panel(current_turn, chessman_images):

    panel_sprite = pygame.sprite.Group()
    panel = PromotionPanel(current_turn, chessman_images)
    panel_sprite.add(panel)
    return panel, panel_sprite

class PanelChessman(pygame.sprite.Sprite):

    def __init__(self, x: int, y:int, team: Team, chessman_type_name:str, chessman_images) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(chessman_images[team][chessman_type_name], (CHESSMAN_SIDE_LENGTH, CHESSMAN_SIDE_LENGTH))
        self.image.set_colorkey(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = chessman_type_name

class PromotionPanel(pygame.sprite.Sprite):

    def __init__(self, team: Team, chessman_images) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = PANEL_INIT_X
        self.rect.y = PANEL_INIT_Y

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
    
    def draw(self, sprite, screen):
        sprite.draw(screen)
        self.chessman_sprite.draw(screen)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 1)
