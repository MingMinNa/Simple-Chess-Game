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
        # for captured chessman display
        self.__move_lst = list()        # (team, chessman_type_name, case, source_pos, dest_pos, killed_enemy_pos, is_check, is_checkmate)
        self.__promotion_info = dict()  # key: move_lst_index, value: chessman_type_name

        # for threefold repetition rule
        self.__board_lst = list()       # (board_representation, white_long_castling, white_short_castling, black_long_castling, black_short_castling)
        self.__repetition_count = 0      

    def add_move(self, team, case, chessman_type_name, source_pos, dest_pos, killed_enemy_pos = None, in_check = False, is_checkmate = False):
        self.__move_lst.append((team, case, chessman_type_name, source_pos, dest_pos, killed_enemy_pos, in_check, is_checkmate))

    def add_promotion_info(self, chessman_type_name):
        self.__promotion_info[len(self.__move_lst) - 1] = chessman_type_name

    def add_board(self, chess_board: ChessBoard):
        
        # white_long_castling, white_short_castling, black_long_castling, black_short_castling)
        long_short = [False, False, False, False]
        
        for i, _ in enumerate((Team.WHITE, Team.BLACK)):
            row = (i * (-1) + len(ROW_VALUE_RANGE)) % len(ROW_VALUE_RANGE) + 1
            
            king_chessman, rook_chessman = chess_board.get_chessman(row, 'e'), chess_board.get_chessman(row, 'a')
            if isinstance(king_chessman, King) and isinstance(rook_chessman, Rook) and \
               king_chessman.get_moved() == False and rook_chessman.get_moved() == False:
                long_short[2 * i] = True
            
            king_chessman, rook_chessman = chess_board.get_chessman(row, 'e'), chess_board.get_chessman(row, 'h')
            if isinstance(king_chessman, King) and isinstance(rook_chessman, Rook) and \
               king_chessman.get_moved() == False and rook_chessman.get_moved() == False:
                long_short[2 * i + 1] = True

        board_str = ""

        name_abbr = {
            "King":   'K',
            "Queen":  'Q',
            "Rook":   'R',
            "Bishop": 'B',
            "Knight": 'N',
            "Pawn":   '', # 'P' or ''
        }
        
        for row in ROW_VALUE_RANGE:
            for col in COL_VALUE_RANGE:
                chessman = chess_board.get_chessman(row, col)
                
                if chessman is None:                 board_str += "n,"
                elif not isinstance(chessman, Pawn): board_str += f"{name_abbr[type(chessman).__name__]},"
                else:
                    board_str += 'P'
                    for pos in chessman.get_en_passant():
                        board_str += f"({pos[0]}{pos[1]})"
                    board_str += ','
        board_representation = (board_str, *long_short)
        self.__repetition_count = max(self.__repetition_count, self.__board_lst.count(board_representation) + 1)
        self.__board_lst.append(board_representation)

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

    def get_repetitions(self):
        return self.__repetition_count

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

        self.record_board()

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
        self.record_move(target_chessman.get_team(), case, type(target_chessman).__name__, source_pos, dest_pos, 
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

        # 三次重複局面 threefold repetition rule
        if self.__record.get_repetitions() >= 3:
            self.__draw = True
            return 

        # 50個回合內，雙方既沒有棋子被吃掉，也沒有士兵被移動過 50-move rule
        if self.__rule_50_counter == 50: 
            self.__draw = True
            return 
        
    def record_move(self, team, case, chessman_type_name, source_pos, dest_pos, killed_enemy_pos = None, in_check = False, is_checkmate = False):
        self.__record.add_move(team, case, chessman_type_name, source_pos, dest_pos, killed_enemy_pos, in_check, is_checkmate)

    def record_promotion_info(self, chessman_type_name):
        self.__record.add_promotion_info(chessman_type_name)

    def record_board(self):
        self.__record.add_board(self.__chess_board)