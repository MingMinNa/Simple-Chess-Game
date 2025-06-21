

from .const import *
from .chessman import *
from .board import *
from .game import *

def read_valid_cell():

    choice = input("Please input the chosen cells (e.g. 1a): ").strip().lower()

    if choice.lower() == "return":
        return True, None, None

    if len(choice) != 2 or not choice[0].isdigit(): 
        print(f"\nInvalid input \"{choice}\"\n"); return False, None, None
    
    row, col = int(choice[0]), choice[1]

    if not check_valid_pos((row, col)): 
        print(f"\nInvalid input \"{choice}\"\n"); return False, None, None

    return True, row, col

def cli_choose_chessman_and_moves(chess_game):
    
    print("\n---- [Chose Chessman] ----")
    while True:
        valid, row, col = read_valid_cell()
        
        if not valid: continue

        chosen_chessman = chess_game.get_chessman(row, col)
        if chosen_chessman is None or chosen_chessman.get_team() != chess_game.get_current_turn(): 
            print(f"\nPlease choose a {chess_game.get_current_turn().name.lower()} team chessman\n"); continue
        
        valid_moves = chess_game.get_valid_moves(chosen_chessman)
        moves_pos = {move[1] for move in valid_moves}
        
        print("\n---- [Chose Move] ----")
        while True:
            print(f"Vaid moves: {valid_moves}")
            print("To choose other chessman, please input \"return\"")
            valid, row, col = read_valid_cell()

            if valid and row is None and col is None:
                print("\n---- [Chose Chessman] ----")
                break
            if not valid: continue

            pos = (row, col)
            
            if pos in moves_pos: return chosen_chessman, pos
            else:                print(f"\nInvalid Move {pos} \n")

def cli_choose_promotion(chess_game, pawn_chessman):

    chessman_type_classes = (None, Queen, Rook, Bishop, Knight, None)
    while True:
        choice = input("Please input a new chessman type in the list [\"Queen\", \"Rook\", \"Bishop\", \"Knight\"]: ").strip()

        # Note: CHESSMAN_TYPE_NAMES = ("King", "Queen", "Rook", "Bishop", "Knight", "Pawn")
        if choice not in CHESSMAN_TYPE_NAMES[1:5]: continue

        chess_game.promotion(pawn_chessman, chessman_type_classes[CHESSMAN_TYPE_NAMES.index(choice)])
        break
