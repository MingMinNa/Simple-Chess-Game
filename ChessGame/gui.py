import os
import pygame

from enum import Enum, auto
from .const import *
from .component.chessman import *
from .component.board import *
from .component.game import *
from .component.gui_chessman import *
from .component.gui_board import *
from .component.gui_panel import *


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
        gui_board.refresh_board()
        return GuiState.CHESSMAN_CHOOSE
    
    game_state, killed_enemy = chess_game.chessman_move(chosen_chessman, dest_pos)    
    
    if killed_enemy is not None:
        chessman_sprite.remove(chessman_bind[killed_enemy])
        del chessman_bind[killed_enemy]
        
    chessman_bind[chosen_chessman].click()  # put down
    gui_board.refresh_board()

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

def gui_game_end(chess_game, screen, gui_board, chessman_sprite):
    end_panel = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
    end_panel_rect = end_panel.get_rect()
    end_panel_rect.center = (350, 350)
    end_panel.fill(GRAY)

    pygame.draw.rect(end_panel, BLACK, end_panel.get_rect(), 1)
    screen.blit(end_panel, end_panel_rect)
    foreground_color = WHITE if chess_game.get_winner() == Team.WHITE else BLACK
    draw_text(screen, f"Winner: {chess_game.get_winner().name.title()}", 350, 330, 75, foreground_color)
    draw_text(screen, f"Press any to continue", 350, 390, 40, foreground_color)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GuiState.QUIT
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                # hide the end panel
                gui_board.draw_board(screen, chess_game.get_current_turn())
                chessman_sprite.draw(screen)
                pygame.display.update()
            elif event.type == pygame.KEYUP and event.key == pygame.K_TAB:
                pygame.draw.rect(end_panel, BLACK, end_panel.get_rect(), 1)
                screen.blit(end_panel, end_panel_rect)
                draw_text(screen, f"Winner: {chess_game.get_winner().name.title()}", 350, 330, 75, foreground_color)
                draw_text(screen, f"Press any to continue", 350, 390, 40, foreground_color)
                pygame.display.update()
            elif event.type == pygame.KEYUP and event.key != pygame.K_TAB:
                return GuiState.MAIN

def init_pygame():
    pygame.init()
    pygame.display.set_caption("Simple Chess Game")
    screen = pygame.display.set_mode((INIT_WIDTH, INIT_HEIGHT))
    clock = pygame.time.Clock()
    clock.tick(FPS)
    load_assets()
    return

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

def main_screen_state():
    
    pygame.display.set_icon(scaled_icon)
    screen = pygame.display.set_mode((INIT_WIDTH, INIT_HEIGHT))
    clock = pygame.time.Clock()
    clock.tick(FPS)
    screen.blit(scaled_background, (0, 0))

    draw_text(screen, "Chess Game",        INIT_WIDTH // 2,     INIT_HEIGHT // 2 - 80,       100,  BLACK) # text "Chess Game" shadow
    draw_text(screen, "Press any to play", INIT_WIDTH // 2,     INIT_HEIGHT // 2 + 20,       70,   BLACK) # text "Press any to play" shadow
    draw_text(screen, "Chess Game",        INIT_WIDTH // 2 + 3, INIT_HEIGHT // 2 - 80 + 3,   100,  WHITE) 
    draw_text(screen, "Press any to play", INIT_WIDTH // 2 + 3, INIT_HEIGHT // 2 + 20 + 3,   70,   WHITE) 
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GuiState.QUIT
            elif event.type == pygame.KEYUP and event.key != pygame.K_ESCAPE:
                return GuiState.GAME

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
        screen.fill(BACKGROUND_COLOR)
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
                        panel, panel_sprite = draw_promotion_panel(chess_game.get_current_turn(), chessman_images)
                    if gui_state in [GuiState.PROMOTION, GuiState.NEXT_TURN]:
                        place_chessman_audio.play()

                elif gui_state == GuiState.PROMOTION:
                    gui_state = gui_choose_promotion(panel, mouse_pos, chosen_chessman, chess_game, gui_board, chessman_bind, chessman_sprite)

                    if gui_state == GuiState.NEXT_TURN:
                        del panel_sprite, panel
                        panel = panel_sprite = None
                
                if gui_state == GuiState.NEXT_TURN:  
                    chess_game.next_turn()
                    gui_board.refresh_board()
                    GuiChessman.repaint_chessmen(chess_game, chessman_bind)
                    gui_state = GuiState.CHESSMAN_CHOOSE

                    chess_game.update_in_check()
                    chess_game.update_checkmate()

        draw_text(screen, f"Turn: {chess_game.get_current_turn().name.title()}", 100, 15, 30, GRAY, BACKGROUND_COLOR)
        draw_text(screen, f"Press Esc to exit ", 600, 15, 30, GRAY, BACKGROUND_COLOR)

        if chess_game.get_checkmate():
            gui_state = GuiState.END
            draw_text(screen, "Checkmate", 350, 15, 30, RED, BACKGROUND_COLOR)
        elif chess_game.get_in_check():
            draw_text(screen, "Check", 350, 15, 30, RED, BACKGROUND_COLOR)
        
        gui_board.draw_board(screen, chess_game.get_current_turn())
        chessman_sprite.draw(screen)
        if panel is not None: panel.draw(panel_sprite, screen)  # promotion panel
        pygame.display.update()
        
        if gui_state == GuiState.END:  break
    
    return gui_game_end(chess_game, screen, gui_board, chessman_sprite)