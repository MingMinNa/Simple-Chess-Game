from enum import Enum, auto
from .board import *
from .chessman import *
from ..const import *

class GameState(Enum):
    END = auto()
    NEXT_TURN = auto()
    PROMOTION = auto()

class Record:
    
    def __init__(self):
        self.__move_lst = list()        # (team, chessman_type_name, case, source_pos, dest_pos, killed_enemy_pos, is_check, is_checkmate)
        self.__promotion_info = dict()  # key: move_lst_index, value: chessman_type_name

    def add_move(self, team, case, chessman_type_name, source_pos, dest_pos, killed_enemy_pos = None, in_check = False, is_checkmate = False):
        self.__move_lst.append((team, case, chessman_type_name, source_pos, dest_pos, killed_enemy_pos, in_check, is_checkmate))

    def add_promotion_info(self, chessman_type_name):
        self.__promotion_info[len(self.__move_lst) - 1] = chessman_type_name

    # long algebraic notation
    def get_chess_notation(self):
        name_abbr = {
            "King":   'K',
            "Queen":  'Q',
            "Rook":   'R',
            "Bishop": 'B',
            "Knight": 'N',
            "Pawn":   '', # 'P' or ''
        }
        round = 0
        notations = dict()
        pos_to_str = lambda pos: pos[1] + str(pos[0])
        for i, move in enumerate(self.__move_lst):
            team, case, chessman_type_name, source_pos, dest_pos, killed_enemy_pos, in_check, is_checkmate = move
            source_pos_str, dest_pos_str = pos_to_str(source_pos), pos_to_str(dest_pos)

            round = (i // 2) + 1

            notation = name_abbr[chessman_type_name]
            
            if case == SpecialMove.EN_PASSANT:
                notation += source_pos_str + 'x' + dest_pos_str + " e.p."
            elif case == SpecialMove.LONG_CASTLING:
                notation = "0-0-0"
            elif case == SpecialMove.SHORT_CASTLING:
                notation = "0-0"
            elif killed_enemy_pos is None:
                notation += source_pos_str + dest_pos_str
            else:   # killed_enemy_pos is not None
                notation += source_pos_str + 'x' + dest_pos_str

            if case == SpecialMove.PROMOTION and i in self.__promotion_info:
                notation += name_abbr[self.__promotion_info[i]]

            if is_checkmate:
                notation += '#'
            elif in_check:
                notation += '+'
            
            notations.setdefault(round, dict())
            notations[round][team] = notation
        return round, notations

class ChessGame: 

    def __init__(self):
        self.__chess_board = ChessBoard()
        self.__current_turn = Team.WHITE
        self.__dead_white_count = dict()
        self.__dead_black_count = dict()
        self.__record = Record()
        self.__game_end = False
        self.__winner = None

        self.__in_check = False
        self.__checkmate = False
        self.__draw = False
        self.__rule_50_counter = 0

        self.__round_record = {
            "Pawn Move": False,
            "Chessman Killed": False
        }

        for chessman_type_name in CHESSMAN_TYPE_NAMES:
            self.__dead_white_count[chessman_type_name] = 0
            self.__dead_black_count[chessman_type_name] = 0

    def next_turn(self):

        self.__chess_board.refresh_en_passant(self.get_current_turn())
        self.__current_turn = Team.BLACK if self.get_current_turn() == Team.WHITE else Team.WHITE

        # check round_info
        if self.get_current_turn() == Team.WHITE:
            if self.__round_record["Pawn Move"] is False and self.__round_record["Chessman Killed"] is False:
                self.__rule_50_counter += 1
            else:
                self.__rule_50_counter = 0
            self.__round_record = {
                "Pawn Move": False,
                "Chessman Killed": False
            }
        
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

    def get_draw(self):
        return self.__draw

    def promotion(self, target_pawn, new_chessman_type):
        self.__chess_board.promotion(target_pawn, new_chessman_type)

    def chessman_move(self, target_chessman, dest_pos):
        source_pos = target_chessman.get_pos()
        case, killed_enemy = self.__chess_board.chessman_move(target_chessman, dest_pos)
        
        if isinstance(target_chessman, Pawn): self.__round_record["Pawn Move"] = True

        ret_state = GameState.NEXT_TURN

        if killed_enemy is not None:
            self.__round_record["Chessman Killed"] = True
            if killed_enemy.get_team() == Team.WHITE: self.__dead_white_count[f"{type(killed_enemy).__name__}"] += 1
            else:                                     self.__dead_black_count[f"{type(killed_enemy).__name__}"] += 1

            if isinstance(killed_enemy, King): 
                self.__game_end = True
                if killed_enemy.get_team() == Team.WHITE: self.__winner = Team.BLACK
                else:                                       self.__winner = Team.WHITE
                ret_state = GameState.END

        if case == SpecialMove.PROMOTION:
            ret_state = GameState.PROMOTION
        elif case == SpecialMove.LONG_CASTLING:
            _, _ = self.__chess_board.chessman_move(self.get_chessman(dest_pos[0], 'a'), (dest_pos[0], 'd'))
        elif case == SpecialMove.SHORT_CASTLING:
            _, _ = self.__chess_board.chessman_move(self.get_chessman(dest_pos[0], 'h'), (dest_pos[0], 'f'))

        enemy_team = Team.BLACK if self.get_current_turn() == Team.WHITE else Team.WHITE
        self.__record.add_move(target_chessman.get_team(), case, type(target_chessman).__name__, source_pos, dest_pos, 
                               killed_enemy_pos = None if killed_enemy is None else killed_enemy.get_pos(), \
                               in_check = ChessBoard.is_board_in_check(self.__chess_board, enemy_team), \
                               is_checkmate = ChessBoard.is_board_checkmate(self.__chess_board, enemy_team))
        return ret_state, killed_enemy
    
    def show_board(self):
        self.__chess_board.print_text_board()

    def update_in_check(self):
        self.__in_check = ChessBoard.is_board_in_check(self.__chess_board, self.get_current_turn())
    
    def update_checkmate(self):

        if ChessBoard.is_board_checkmate(self.__chess_board, self.get_current_turn()):
            self.__checkmate = True
            self.__winner = Team.BLACK if self.get_current_turn() == Team.WHITE else Team.WHITE 
        else:
            self.__checkmate = False
        return 
    
    def update_draw(self):
        
        self.__draw = False

        # 逼和 stalemate
        self.update_in_check()
        if not self.get_in_check() and \
           ChessBoard.is_board_no_valid_moves(self.__chess_board, self.get_current_turn()):
            self.__draw = True
            return 

        # 三次重複局面 


        # 50個回合內，雙方既沒有棋子被吃掉，也沒有士兵被移動過
        if self.__rule_50_counter == 50: 
            self.__draw = True
            return 