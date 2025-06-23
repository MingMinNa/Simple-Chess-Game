from enum import Enum, auto
from .board import *
from .chessman import *
from ..const import *

class GameState(Enum):
    END = auto()
    NEXT_TURN = auto()
    PROMOTION = auto()

class ChessGame: 

    def __init__(self):
        self.__chess_board = ChessBoard()
        self.__current_turn = Team.WHITE
        self.__dead_white_count = dict()
        self.__dead_black_count = dict()
        self.__record = list()
        self.__game_end = False
        self.__winner = None

        self.__in_check = False
        self.__checkmate = False

        for chessman_type_name in CHESSMAN_TYPE_NAMES:
            self.__dead_white_count[chessman_type_name] = 0
            self.__dead_black_count[chessman_type_name] = 0

    def next_turn(self):
        self.__chess_board.refresh_en_passant(self.get_current_turn())
        self.__current_turn = Team.BLACK if self.get_current_turn() == Team.WHITE else Team.WHITE
        
    def get_current_turn(self):
        return self.__current_turn

    def get_game_end(self):
        return self.__game_end
    
    def get_chessman(self, row, col):
        return self.__chess_board.get_chessman(row, col)

    def get_entire_board(self):
        return self.__chess_board.get_entire_board()
    
    def get_winner(self):
        return self.__winner
    
    def get_record(self):
        return self.__record
    
    def get_valid_moves(self, target_chessman):
        return self.__chess_board.get_valid_moves(target_chessman)
    
    def get_dead_chessmen(self):
        return {
            "White": self.__dead_white_count, 
            "Black": self.__dead_black_count
        }
    
    def get_in_check(self):
        return self.__in_check

    def get_checkmate(self):
        return self.__checkmate

    def promotion(self, target_pawn, new_chessman_type):
        self.__chess_board.promotion(target_pawn, new_chessman_type)

    def chessman_move(self, target_chessman, dest_pos):
        source_pos = target_chessman.get_pos()
        case, killed_enemy = self.__chess_board.chessman_move(target_chessman, dest_pos)
        
        self.__record.append((type(target_chessman).__name__, source_pos, dest_pos, case))
        
        if killed_enemy is not None:
            if killed_enemy.get_team() == Team.WHITE: self.__dead_white_count[f"{type(killed_enemy).__name__}"] += 1
            else:                                     self.__dead_black_count[f"{type(killed_enemy).__name__}"] += 1

            if isinstance(killed_enemy, King): 
                self.__game_end = True
                if killed_enemy.get_team() == Team.WHITE: self.__winner = Team.BLACK
                else:                                       self.__winner = Team.WHITE
                return GameState.END, killed_enemy
        

        if case == SpecialMove.PROMOTION:
            return GameState.PROMOTION, killed_enemy
        elif case == SpecialMove.LONG_CASTLING:
            _, _ = self.__chess_board.chessman_move(self.get_chessman(dest_pos[0], 'a'), (dest_pos[0], 'd'))
        elif case == SpecialMove.SHORT_CASTLING:
            _, _ = self.__chess_board.chessman_move(self.get_chessman(dest_pos[0], 'h'), (dest_pos[0], 'f'))
        return GameState.NEXT_TURN, killed_enemy
    
    def show_board(self):
        self.__chess_board.print_text_board()

    def update_in_check(self):
        self.__in_check = ChessBoard.is_board_in_check(self.__chess_board, self.get_current_turn())
    
    def update_checkmate(self):

        self.update_in_check()
        if self.get_in_check() is False: 
            self.__checkmate = False
            return

        for row in ROW_VALUE_RANGE:
            for col in COL_VALUE_RANGE:
                curr_chessman = self.get_chessman(row, col)
                if curr_chessman is not None and \
                   curr_chessman.get_team() == self.__current_turn:
                    
                    # try all the valid moves of the chessman
                    valid_moves = self.get_valid_moves(curr_chessman)
                    
                    for action, pos in valid_moves:
                        next_board = self.__chess_board.peak_move(curr_chessman, pos)
                        in_check = ChessBoard.is_board_in_check(next_board, self.get_current_turn())
                        del next_board

                        if not in_check:    
                            self.__checkmate = False
                            return

        self.__checkmate = True
        self.__winner = Team.BLACK if self.get_current_turn() == Team.WHITE else Team.WHITE 
        return 