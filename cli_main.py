
from ChessGame import *
from ChessGame.cli import *

def main():
    chess_game = ChessGame()

    while not chess_game.get_game_end():

        # Show the board 
        chess_game.show_board()
        print(f"Current Turn: {chess_game.get_current_turn().name.title()}")

        # choose the chessman and the move
        chosen_chessman, chosen_move = cli_choose_chessman_and_moves(chess_game)
        
        state, _ = chess_game.chessman_move(chosen_chessman, chosen_move)

        if state == GameState.END:  break
        elif state == GameState.PROMOTION:
            cli_choose_promotion(chess_game, chosen_chessman)
        chess_game.update_in_check()
        chess_game.update_checkmate()
        chess_game.next_turn()
        
        if chess_game.get_checkmate():
            print("Checkmate !!")
            break
        elif chess_game.get_in_check():
            print("Check !!")
    
    print(f"End, the winner is {chess_game.get_winner().name.title()}")
    
    dead_chessmen = chess_game.get_dead_chessmen()

    for team in (Team.WHITE, Team.BLACK):
        print(f"[{team.name.title()}] dead chessmen: {dead_chessmen[team.name.title()]}")
        
    return 

if __name__ == "__main__":
    main()