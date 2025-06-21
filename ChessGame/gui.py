import os
import pygame

from enum import Enum, auto
from .const import *
from .chessman import *
from .board import *
from .game import *


# windows constants
INIT_WIDTH, INIT_HEIGHT = 700, 550
WIDTH, HEIGHT = 700, 700 
PANEL_WIDTH, PANEL_HEIGHT = 400, 250
CHESSMAN_SIDE_LENGTH = 60
CELL_SIDE_LENGTH = 80
INIT_X, INIT_Y = 30, 30
PANEL_INIT_X, PANEL_INIT_Y = 150, 225

FPS = 60

# color 
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
GRAY        = (125, 125, 125)
GREEN       = (0, 110, 0)
FRESH_GREEN = (99,211,108)
RED         = (255, 0, 0)
YELLOW      = (240, 230, 140)
BLUE        = (30, 144, 255)

BOARDCELL_COLORS = [GREEN, FRESH_GREEN]
BACKGROUND_COLOR = BLACK
ATTACK_COLOR = RED
MOVE_COLOR = GRAY
PROMOTION_COLOR = BLUE
CASTLING_COLOR = YELLOW


class GuiState(Enum):

    GAME = auto()
    MAIN = auto()
    QUIT = auto()

    CHESSMAN_CHOOSE = auto()
    MOVE_CHOOSE = auto()

    # the below are the same as the GameState
    END = auto()
    NEXT_TURN = auto()
    PROMOTION = auto()

class GuiChessmanState(Enum):
    UP = auto()
    DOWN = auto()

class GuiChessman(pygame.sprite.Sprite):

    
    @staticmethod
    def repaint_chessmen(chess_game, chessman_bind):
        for r in ROW_VALUE_RANGE:
            for c in COL_VALUE_RANGE:
                chessman = chess_game.get_chessman(r, c)
                if chessman is not None:
                    c_x, c_y = GuiChessman.calc_cell_x_y(r, c, chess_game.get_current_turn())
                    chessman_bind[chessman].set_cell_x_y(c_x, c_y)  

    @staticmethod
    def calc_cell_x_y(row, col, current_turn):
        
        if current_turn == Team.BLACK:
            # (row, col) = (1, 'a') => (x, y) = (7, 0)
            # (row, col) = (8, 'h') => (x, y) = (0, 7)
            return (7 - COL_VALUE_RANGE.index(col), row - 1)
        else:
            # (row, col) = (1, 'a') => (x, y) = (0, 7)
            # (row, col) = (8, 'h') => (x, y) = (7, 0)
            return (COL_VALUE_RANGE.index(col), 7 - row + 1) 

    @staticmethod
    def calc_row_col(cell_x, cell_y, current_turn):

        def int_to_letter(col_idx):
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

    def __init__(self, cell_x: int, cell_y: int, team: Team, image):
        
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

    def click(self):
        
        if self.state == GuiChessmanState.DOWN: self.__up()
        else:                                   self.__down()
    
    def __down(self):
        if self.state == GuiChessmanState.UP:
            self.rect.y += 10
        self.state = GuiChessmanState.DOWN

    def __up(self):
        if self.state == GuiChessmanState.DOWN:
            self.rect.y -= 10
        self.state = GuiChessmanState.UP

    def set_cell_x_y(self, cell_x, cell_y):
        self.cell_x = cell_x
        self.cell_y = cell_y

        self.rect.x = INIT_X + cell_x * CELL_SIDE_LENGTH + 10
        self.rect.y = INIT_Y + cell_y * CELL_SIDE_LENGTH + 10
    
    def get_cell_x_y(self):
        return (self.cell_x, self.cell_y)

class GuiBoardCell(pygame.sprite.Sprite):

    def __init__(self, cell_x: int, cell_y: int, color) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((CELL_SIDE_LENGTH, CELL_SIDE_LENGTH))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 1)

        self.rect.x = INIT_X + CELL_SIDE_LENGTH * cell_x
        self.rect.y = INIT_Y + CELL_SIDE_LENGTH * cell_y

    def set_color(self, color):
        self.image.fill(color)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 1)

class GuiBoard:
    
    @staticmethod
    def get_click_cell(pos):
        return ((pos[0] - INIT_X) // CELL_SIDE_LENGTH, 
                (pos[1] - INIT_Y) // CELL_SIDE_LENGTH)

    def __init__(self):
        self.board = list()
        self.boardcell_sprite = pygame.sprite.Group()

        for i in range(len(ROW_VALUE_RANGE)):
            self.board.append(list())
            color_idx = i % 2
            for j in range(len(COL_VALUE_RANGE)):
                cell = GuiBoardCell(j, i, BOARDCELL_COLORS[(color_idx + j) % 2])
                self.board[i].append(cell)
                self.boardcell_sprite.add(cell)

    def refresh_board(self, current_turn):

        for i in range(len(ROW_VALUE_RANGE)):
            color_idx = i % 2
            for j in range(len(COL_VALUE_RANGE)):
                self.board[i][j].set_color(BOARDCELL_COLORS[(color_idx + j) % 2])

    def paint_move_area(self, current_turn, valid_moves):
        
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
    
    def get_bordcell_sprite(self):
        return self.boardcell_sprite

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



# Load assets
scaled_icon = None
scaled_background = None
chessman_images = None

place_chessman_audio = None

def load_assets():
    global scaled_icon, scaled_background, chessman_images, place_chessman_audio
    icon_image = pygame.image.load(os.path.join(IMAGE_FOLDER, "icon.png")).convert()
    scaled_icon = pygame.transform.scale(icon_image, (25, 19))
    
    background_image = pygame.image.load(os.path.join(IMAGE_FOLDER, "background.png")).convert()
    scaled_background = pygame.transform.scale(background_image, (INIT_WIDTH, INIT_HEIGHT))

    place_chessman_audio = pygame.mixer.Sound(os.path.join(AUDIO_FOLDER, "placeChessman.mp3"))

    chessman_images = {Team.BLACK: dict(), Team.WHITE: dict()}
    for team in (Team.BLACK, Team.WHITE):
        for type_name in CHESSMAN_TYPE_NAMES:
            chessman_images[team][type_name] = pygame.image.load(os.path.join(IMAGE_FOLDER, "chessman", f"{type_name.title()}_{team.name.lower()}.png")).convert()

def pygame_init():
    pygame.init()
    pygame.display.set_caption("Simple Chess Game")
    screen = pygame.display.set_mode((INIT_WIDTH, INIT_HEIGHT))
    clock = pygame.time.Clock()
    clock.tick(FPS)
    load_assets()
    return

def screen_draw_text(screen: "pygame.Surface", text: str, center_x: int, center_y: int, fontSize: int, Fontcolor: tuple[int], background_color = None) -> None:

    font = pygame.font.Font(None, fontSize)
    text_surface = font.render(f"{text}", True, Fontcolor)
    text_rect = text_surface.get_rect()
    text_rect.center = (center_x, center_y)
    if background_color: screen.fill(background_color, text_rect)
    screen.blit(text_surface, text_rect)

    return text_rect

def draw_promotion_panel(current_turn):

    panel_sprite = pygame.sprite.Group()
    panel = PromotionPanel(current_turn, chessman_images)
    panel_sprite.add(panel)
    return panel, panel_sprite

def main_screen_state():
    
    pygame.display.set_icon(scaled_icon)
    screen = pygame.display.set_mode((INIT_WIDTH, INIT_HEIGHT))
    clock = pygame.time.Clock()
    clock.tick(FPS)
    screen.blit(scaled_background, (0, 0))

    screen_draw_text(screen, "Chess Game",        INIT_WIDTH // 2,     INIT_HEIGHT // 2 - 80,       100,  BLACK) # text "Chess Game" shadow
    screen_draw_text(screen, "Press any to play", INIT_WIDTH // 2,     INIT_HEIGHT // 2 + 20,       70,   BLACK) # text "Press any to play" shadow
    screen_draw_text(screen, "Chess Game",        INIT_WIDTH // 2 + 3, INIT_HEIGHT // 2 - 80 + 3,   100,  WHITE) 
    screen_draw_text(screen, "Press any to play", INIT_WIDTH // 2 + 3, INIT_HEIGHT // 2 + 20 + 3,   70,   WHITE) 
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GuiState.QUIT
            elif event.type == pygame.KEYUP and event.key != pygame.K_ESCAPE:
                return GuiState.GAME

def init_chessman_display(chess_game):
    chessman_bind = dict()
    chessman_sprite = pygame.sprite.Group()

    for row in ROW_VALUE_RANGE:
        for col in COL_VALUE_RANGE:
            chessman = chess_game.get_chessman(row, col)
            if chessman is not None:
                cell_x, cell_y = GuiChessman.calc_cell_x_y(row, col, chess_game.get_current_turn())
                gui_chessman = GuiChessman(cell_x, cell_y, chessman.get_team(), chessman_images[chessman.get_team()][type(chessman).__name__])
                chessman_bind[chessman] = gui_chessman
                chessman_sprite.add(gui_chessman)
    
    return chessman_bind, chessman_sprite

def gui_choose_chessman(chess_game, gui_board, chessman_bind, cell_x, cell_y):
    
    row, col = GuiChessman.calc_row_col(cell_x, cell_y, chess_game.get_current_turn())
    chessman = chess_game.get_chessman(row, col)

    if chessman is None or chessman.get_team() != chess_game.get_current_turn():
        return GuiState.CHESSMAN_CHOOSE, None, None
    
    chessman_bind[chessman].click()
    valid_moves = chess_game.get_valid_moves(chessman)
    gui_board.paint_move_area(chess_game.get_current_turn(), valid_moves)

    return GuiState.MOVE_CHOOSE, chessman, valid_moves

def gui_choose_moves(chess_game, gui_board, chessman_bind, chessman_sprite, chosen_chessman, valid_moves, cell_x, cell_y):
    
    row, col = GuiChessman.calc_row_col(cell_x, cell_y, chess_game.get_current_turn())
    dest_pos = (row, col)

    if dest_pos not in {pos for _, pos in valid_moves}:
        chessman_bind[chosen_chessman].click()  # put down
        gui_board.refresh_board(chess_game.get_current_turn())
        return GuiState.CHESSMAN_CHOOSE

    dest_chessman = chess_game.get_chessman(row, col)
    if dest_chessman is not None:
        chessman_sprite.remove(chessman_bind[dest_chessman])
        del chessman_bind[dest_chessman]
    
    game_state = chess_game.chessman_move(chosen_chessman, dest_pos)    
    chessman_bind[chosen_chessman].click()  # put down
    gui_board.refresh_board(chess_game.get_current_turn())

    GuiChessman.repaint_chessmen(chess_game, chessman_bind)

    if game_state == GameState.END: return GuiState.END
    elif game_state == GameState.PROMOTION: return GuiState.PROMOTION
    else:                                   return GuiState.NEXT_TURN

def gui_choose_promotion(panel, mouse_pos, pawn_chessman, chess_game, gui_board, chessman_bind, chessman_sprite):

    chosen_chessman_type_name = panel.choose(mouse_pos)

    if chosen_chessman_type_name is None:
        return GuiState.PROMOTION
    
    curr_pos, curr_team = pawn_chessman.get_pos(), pawn_chessman.get_team()
    cell_x, cell_y = GuiChessman.calc_cell_x_y(curr_pos[0], curr_pos[1], chess_game.get_current_turn())

    chessman_sprite.remove(chessman_bind[pawn_chessman])
    del chessman_bind[pawn_chessman]
    chessman_type_classes = (None, Queen, Rook, Bishop, Knight, None)
    chess_game.promotion(pawn_chessman, chessman_type_classes[CHESSMAN_TYPE_NAMES.index(chosen_chessman_type_name)])
    new_chessman = chess_game.get_chessman(curr_pos[0], curr_pos[1])
    new_gui_chessman = GuiChessman(cell_x, cell_y, curr_team, chessman_images[curr_team][chosen_chessman_type_name])
    chessman_bind[new_chessman] = new_gui_chessman
    chessman_sprite.add(new_gui_chessman)

    return GuiState.NEXT_TURN

def game_state():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BACKGROUND_COLOR)
    chess_game = ChessGame()
    gui_board = GuiBoard()
    chessman_bind, chessman_sprite = init_chessman_display(chess_game)
    panel, panel_sprite = None, None

    gui_state = GuiState.CHESSMAN_CHOOSE
    chosen_chessman = None
    valid_moves = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GuiState.QUIT
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                return GuiState.MAIN
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                cell_x, cell_y = GuiBoard.get_click_cell(mouse_pos)

                # click out of the board, nothing happens
                if cell_x not in range(8) or cell_y not in range(8): continue

                if gui_state == GuiState.CHESSMAN_CHOOSE:
                    gui_state, chosen_chessman, valid_moves = gui_choose_chessman(chess_game, gui_board, chessman_bind, cell_x, cell_y)
                elif gui_state == GuiState.MOVE_CHOOSE:
                    gui_state = gui_choose_moves(chess_game, gui_board, chessman_bind, chessman_sprite, chosen_chessman, valid_moves, cell_x, cell_y)

                    if gui_state == GuiState.PROMOTION:
                        panel, panel_sprite = draw_promotion_panel(chess_game.get_current_turn())
                    if gui_state in [GuiState.PROMOTION, GuiState.NEXT_TURN]:
                        place_chessman_audio.play()

                elif gui_state == GuiState.PROMOTION:
                    gui_state = gui_choose_promotion(panel, mouse_pos, chosen_chessman, chess_game, gui_board, chessman_bind, chessman_sprite)

                    if gui_state == GuiState.NEXT_TURN:
                        del panel_sprite, panel
                        panel = panel_sprite = None
                
                if gui_state == GuiState.NEXT_TURN:  
                    chess_game.next_turn()
                    gui_board.refresh_board(chess_game.get_current_turn())
                    GuiChessman.repaint_chessmen(chess_game, chessman_bind)
                    gui_state = GuiState.CHESSMAN_CHOOSE
        screen_draw_text(screen, f"Turn: {chess_game.get_current_turn().name.title()}   ", 100, 15, 30, GRAY, BACKGROUND_COLOR)
        screen_draw_text(screen, f"Press Esc to exit ", 600, 15, 30, GRAY, BACKGROUND_COLOR)

        if chess_game.is_check():
                screen_draw_text(screen, "Check", 350, 15, 30, RED,              BACKGROUND_COLOR)
        else:   screen_draw_text(screen, "Check", 350, 15, 30, BACKGROUND_COLOR, BACKGROUND_COLOR)
        
        gui_board.get_bordcell_sprite().draw(screen)
        chessman_sprite.draw(screen)
        if panel is not None: 
            panel.draw(panel_sprite, screen)
        pygame.display.update()
        
        if gui_state == GuiState.END:   break



