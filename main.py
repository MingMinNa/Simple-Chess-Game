import pygame
from ChessGame import *


def main() -> None:
    init_pygame()
    while True:
        gui_state = main_screen_state()
        if gui_state == GuiState.QUIT: break
        gui_state = game_state()
        if gui_state == GuiState.QUIT: break
    pygame.quit()

if __name__ == '__main__':
    main()