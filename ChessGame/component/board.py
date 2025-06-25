from enum import Enum, auto
from copy import deepcopy
from .chessman import *
from ..const import *

class SpecialMove(Enum):
    PROMOTION = auto()
    EN_PASSANT = auto()
    LONG_CASTLING = auto()
    SHORT_CASTLING = auto()

class ChessBoard:

    @staticmethod
    def is_board_in_check(board: "ChessBoard", team: Team):
        
        enemy_team = Team.BLACK if team == Team.WHITE else Team.WHITE
        team_attack_area = get_all_team_attack_area(enemy_team, board.get_entire_board())

        for pos in team_attack_area:
            pos_chessman = board.get_chessman(pos[0], pos[1])

            if isinstance(pos_chessman, King) and \
                pos_chessman.get_team() == team:
                return True
            
        return False
    
    @staticmethod
    def is_board_checkmate(board: "ChessBoard", team: Team):

        is_check = ChessBoard.is_board_in_check(board, team)
        no_valid_moves = ChessBoard.is_board_no_valid_moves(board, team)
        return is_check and no_valid_moves

    def is_board_no_valid_moves(board: "ChessBoard", team: Team):
        
        for row in ROW_VALUE_RANGE:
            for col in COL_VALUE_RANGE:
                curr_chessman = board.get_chessman(row, col)
                if curr_chessman is not None and \
                   curr_chessman.get_team() == team:
                    
                    # try all the valid moves of the chessman
                    valid_moves = board.get_valid_moves(curr_chessman)
                    
                    for action, pos in valid_moves:
                        next_board = board.peak_move(curr_chessman, pos)
                        in_check = ChessBoard.is_board_in_check(next_board, team)
                        del next_board

                        if not in_check:  return False
        return True

    def __init__(self):
        self.reset_board()

    def reset_board(self):
        self.__board = dict()

        for row in ROW_VALUE_RANGE:
            self.__board[row] = dict()
            for col in COL_VALUE_RANGE:
                self.__board[row][col] = None
        
        # set the chessmen
        chessman_type_in_order = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)
        for col, chessman_class in zip(COL_VALUE_RANGE, chessman_type_in_order):
            self.__board[1][col] = chessman_class(1, col, Team.WHITE)
            self.__board[2][col] = Pawn(2, col, Team.WHITE)
            
            self.__board[7][col] = Pawn(7, col, Team.BLACK)
            self.__board[8][col] = chessman_class(8, col, Team.BLACK)

    def print_text_board(self):

        print(" " * 8, end = "")
        for col_name in COL_VALUE_RANGE:
            print(f"{col_name:8s}", end = "")
        print()

        for row in ROW_VALUE_RANGE: 
            print(f"{str(row):^8s}", end = "")
            for col in COL_VALUE_RANGE:
                chessman = self.get_chessman(row, col)
                if chessman:    print(f"\033[{chessman.get_team().value}m{type(chessman).__name__:8s}\033[0m", end = "")
                else:           print(f"----    ", end = "")
            print()
    
    def print_graphic_board(self):

        print(" " * 5, end = "")
        for col_name in COL_VALUE_RANGE:
            print(f"{col_name:^5s}", end = "")
        print()

        for row in ROW_VALUE_RANGE: 
            print(f"{str(row):^5s}", end = "")
            for col in COL_VALUE_RANGE:
                chessman = self.get_chessman(row, col)
                if chessman:    print(f"\033[{chessman.get_team().value}m{chessman.unicode():^5s}\033[0m", end = "")
                else:           print(f"  -  ", end = "")
            print()

    def get_chessman(self, row, col):
        return self.__board[row][col]

    def get_entire_board(self):
        return self.__board

    def get_valid_moves(self, target_chessman):

        if target_chessman is None: return set()

        curr_row, curr_col = target_chessman.get_pos()

        if self.__board[curr_row][curr_col] is not target_chessman:
            raise ValueError
        
        chessman_moves = target_chessman.get_valid_moves(self.__board)
        
        valid_moves = set()
        # make sure the moves that can't make the king attacked
        for action, pos in chessman_moves:
            next_board = self.peak_move(target_chessman, pos)

            if not ChessBoard.is_board_in_check(next_board, target_chessman.get_team()):
                valid_moves.add((action, pos))
        return valid_moves
        
    def refresh_en_passant(self, turn: Team):

        for row in ROW_VALUE_RANGE:
            for col in COL_VALUE_RANGE:
                chessman = self.get_chessman(row, col)
                
                if isinstance(chessman, Pawn) and chessman.get_team() == turn:
                    chessman.clear_en_passant()

    def chessman_move(self, target_chessman, dest_pos):

        killed_enemy = None
        origin_pos = target_chessman.get_pos()
        self.__board[origin_pos[0]][origin_pos[1]] = None

        # special case I: promotion
        if isinstance(target_chessman, Pawn) and \
           (target_chessman.get_team() == Team.WHITE and dest_pos[0] == ROW_VALUE_RANGE[-1] or\
           target_chessman.get_team() == Team.BLACK and dest_pos[0] == ROW_VALUE_RANGE[0]):
            
            target_chessman.set_moved()
            target_chessman.set_pos(dest_pos)

            killed_enemy = self.__board[dest_pos[0]][dest_pos[1]]
            self.__board[dest_pos[0]][dest_pos[1]] = target_chessman

            return (SpecialMove.PROMOTION, killed_enemy)

        # special case II: en_passant
        elif isinstance(target_chessman, Pawn) and dest_pos in target_chessman.get_en_passant():

            target_chessman.set_moved()
            target_chessman.set_pos(dest_pos)
            
            if target_chessman.get_team() == Team.WHITE: _, enemy_pos = calc_position(dest_pos, -1, 0)
            else:                                        _, enemy_pos = calc_position(dest_pos, 1, 0)
            
            killed_enemy = self.__board[enemy_pos[0]][enemy_pos[1]]
            self.__board[enemy_pos[0]][enemy_pos[1]] = None
            self.__board[dest_pos[0]][dest_pos[1]] = target_chessman

            return (SpecialMove.EN_PASSANT, killed_enemy)
        
        # special case III: castling
        elif isinstance(target_chessman, King) and not target_chessman.get_moved() and dest_pos in CASTLING_POS:
            
            target_chessman.set_moved()
            target_chessman.set_pos(dest_pos)
            self.__board[dest_pos[0]][dest_pos[1]] = target_chessman

            # long castling
            if dest_pos[1] == 'c':
                return (SpecialMove.LONG_CASTLING, None)
            # short castling
            else:
                return (SpecialMove.SHORT_CASTLING, None)
        
        # Pawn special move: go forward 2 cells
        elif isinstance(target_chessman, Pawn) and not target_chessman.get_moved() and dest_pos[0] in (4, 5):
            target_chessman.set_moved()
            target_chessman.set_pos(dest_pos)
            self.__board[dest_pos[0]][dest_pos[1]] = target_chessman
            
            for delta_col in (-1, 1):
                valid, neighbor_pos = calc_position(dest_pos, 0, delta_col)
                
                if not valid: continue
                neighbor_chessman = self.get_chessman(neighbor_pos[0], neighbor_pos[1])

                if neighbor_chessman is not None and \
                    isinstance(neighbor_chessman, Pawn) and \
                    neighbor_chessman.get_team() != target_chessman.get_team():

                    advance_direction = 1 if neighbor_chessman.get_team() == Team.WHITE else -1
                    neighbor_chessman.add_en_passant(( dest_pos[0] + advance_direction, dest_pos[1]))
            return (None, killed_enemy)
        else:
            target_chessman.set_moved()
            target_chessman.set_pos(dest_pos)

            killed_enemy = self.__board[dest_pos[0]][dest_pos[1]]
            self.__board[dest_pos[0]][dest_pos[1]] = target_chessman

            return (None, killed_enemy)

    def promotion(self, target_pawn, new_chessman_type):
        
        curr_pos = target_pawn.get_pos()
        new_chessman = new_chessman_type(curr_pos[0], curr_pos[1], target_pawn.get_team())
        new_chessman.set_moved()
        self.__board[curr_pos[0]][curr_pos[1]] = new_chessman

    def peak_move(self, target_chessman, dest_pos):

        row, col = target_chessman.get_pos()
        copied_chess_board = deepcopy(self)
        copied_chess_board.chessman_move(copied_chess_board.get_chessman(row, col), dest_pos)

        return copied_chess_board