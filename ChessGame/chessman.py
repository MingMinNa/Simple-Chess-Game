from enum import Enum, auto
from typing import override, overload
from .const import *



def check_valid_pos(pos):
    # pos = (row, col)
    if pos[0] in ROW_VALUE_RANGE and pos[1] in COL_VALUE_RANGE:
        return True
    return False

def calc_position(current_pos, row_move, col_move):

    def letter_to_int(col_alpha):
        return COL_VALUE_RANGE.index(col_alpha)
    
    def int_to_letter(col_idx):
        if col_idx >= len(COL_VALUE_RANGE) or col_idx < 0: return "#" # error chars
        return COL_VALUE_RANGE[col_idx]

    row_move_range = range(-len(ROW_VALUE_RANGE) + 1, len(ROW_VALUE_RANGE))
    col_move_range = range(-len(COL_VALUE_RANGE) + 1, len(COL_VALUE_RANGE))
    
    if not (check_valid_pos(current_pos) and row_move in row_move_range and col_move in col_move_range):    return False, None

    next_row = current_pos[0] + row_move
    next_col = int_to_letter(letter_to_int(current_pos[1]) + col_move)
    next_pos = (next_row, next_col)
    if not check_valid_pos(next_pos): return False, None

    return True, next_pos

def get_all_team_attack_area(team, board):
    team_attack_area = set()

    for row in ROW_VALUE_RANGE:
        for col in COL_VALUE_RANGE:
            chessman = board[row][col]

            if chessman is not None and chessman.get_team() == team:
                chessman_attack_area = chessman.get_attack_area(board)

                team_attack_area.update(chessman_attack_area)
                
    return team_attack_area

class Team(Enum):
    WHITE = 37 # for \033[37m ... \033[0m
    BLACK = 30 # for \033[30m ... \033[0m

class BaseChessman:
    def __init__(self, init_row: int, init_col: str, team: Team):
        if not check_valid_pos((init_row, init_col)):
            raise ValueError(f"Fail to initialize a chessman whose has wrong position ({init_row}, {init_col})")
        if not isinstance(team, Team):
            raise ValueError(f"Fail to initialize a chessman whose has a wrong Team value {init_col}")

        self.__current_row = init_row
        self.__current_col = init_col
        self.__team = team
        self.__has_moved = False

    def set_pos(self, next_row_pos: int, next_col_pos: str) -> None:
        if not check_valid_pos((next_row_pos, next_col_pos)):
            raise ValueError(f"Fail to set new position ({next_row_pos}, {next_col_pos})")
        
        self.__current_row = next_row_pos
        self.__current_col = next_col_pos
    
    def set_pos(self, next_pos: tuple[int, str]) -> None:
        self.__current_row = next_pos[0]
        self.__current_col = next_pos[1]
    
    def unicode(self):
        pass

    def get_valid_moves(self, board):
        pass

    def get_attack_area(self, board):
        pass

    def set_moved(self):
        self.__has_moved = True

    def get_pos(self):
        return (self.__current_row, self.__current_col)
    
    def get_team(self):
        return self.__team

    def get_moved(self):
        return self.__has_moved

class King(BaseChessman):

    def __init__(self, init_row: int, init_col: str, team: Team):
        super().__init__(init_row, init_col, team)
    
    @override
    def unicode(self):
        if self.get_team() == Team.WHITE: return "\u2654"
        else:                             return "\u265A"
    
    @override
    def get_valid_moves(self, board):

        def check_castling(start_row, board, all_enemy_attack_area, between_cells, king_pass_cells):

            target_rook = board[start_row][COL_VALUE_RANGE[0]]
            if isinstance(target_rook, Rook) and target_rook.get_moved() is False:
                # all the cells between the king and the rook are clear.
                for col in between_cells:
                    if board[start_row][col] is not None:
                        return False

                # the cells that the king passes through can't be attacked.
                for col in king_pass_cells:
                    if (start_row, col) in all_enemy_attack_area:
                        return False
                return True
            return False
        
        valid_moves = set()

        if self.get_team() == Team.BLACK:
            all_enemy_attack_area = get_all_team_attack_area(Team.WHITE, board)
        else:
            all_enemy_attack_area = get_all_team_attack_area(Team.BLACK, board)

        attack_area = self.get_attack_area(board)

        for pos in attack_area:
            if pos not in all_enemy_attack_area:
                chessman = board[pos[0]][pos[1]]
                if chessman is None:
                    valid_moves.add(("Move", pos))
                elif chessman.get_team() != self.get_team():
                    valid_moves.add(("Attack", pos))

        if self.get_moved() is True: 
            return valid_moves

        start_row = 1 if self.get_team() == Team.WHITE else ROW_VALUE_RANGE[-1]

        # long castling
        if check_castling(start_row, board, all_enemy_attack_area, ('b', 'c', 'd'), ('c', 'd', 'e')):
            valid_moves.add(('Castling', (start_row, 'c')))

        # short castling
        if check_castling(start_row, board, all_enemy_attack_area, ('f', 'g'), ('e', 'f', 'g')):
            valid_moves.add(('Castling', (start_row, 'g')))

        return valid_moves

    @override
    def get_attack_area(self, board):

        attack_area = set() # store the attackable position 

        # 8 directions 
        directions = [
            (-1, -1), (-1,  0), (-1,  1), 
            ( 0, -1),           ( 0,  1), 
            ( 1, -1), ( 1,  0), ( 1,  1)
        ]

        for dir in directions:
            delta_row, delta_col = dir[0], dir[1]

            valid, attack_pos = calc_position(self.get_pos(), delta_row, delta_col)

            if valid is True:
                attack_area.add(attack_pos)

        return attack_area

class Queen(BaseChessman):

    def __init__(self, init_row: int, init_col: str, team: Team):
        super().__init__(init_row, init_col, team)
    
    @override
    def unicode(self):
        if self.get_team() == Team.WHITE: return "\u2655"
        else:                             return "\u265B"

    @override
    def get_valid_moves(self, board):
        
        attack_area = self.get_attack_area(board)

        # remove the moves that touch the chessmen in the same team
        valid_moves = set()
        for pos in attack_area:
            chessman = board[pos[0]][pos[1]]
            
            if chessman is None:
                valid_moves.add(("Move", pos))
            elif chessman is not None and chessman.get_team() != self.get_team():
                valid_moves.add(("Attack", pos))
    
        return valid_moves

    @override
    def get_attack_area(self, board):
        
        attack_area = set() # store the attackable position 

        # 8 directions 
        directions = [
            (-1, -1), (-1,  0), (-1,  1), 
            ( 0, -1),           ( 0,  1), 
            ( 1, -1), ( 1,  0), ( 1,  1)
        ]

        for dir in directions:
            for delta in range(1, len(ROW_VALUE_RANGE)):
                delta_row, delta_col = dir[0] * delta, dir[1] * delta

                valid, attack_pos = calc_position(self.get_pos(), delta_row, delta_col)

                # out of bounds (attack_pos is not on the board)
                if valid is False:
                    break
                # touch other chessmen
                elif board[attack_pos[0]][attack_pos[1]] is not None:
                    attack_area.add(attack_pos)
                    break
                else:
                    attack_area.add(attack_pos)
        return attack_area

class Rook(BaseChessman):

    def __init__(self, init_row: int, init_col: str, team: Team):
        super().__init__(init_row, init_col, team)

    @override
    def unicode(self):
        if self.get_team() == Team.WHITE: return "\u2656"
        else:                             return "\u265C"
    
    @override
    def get_valid_moves(self, board):
        
        attack_area = self.get_attack_area(board)

        # remove the moves that touch the chessmen in the same team
        valid_moves = set()
        for pos in attack_area:
            chessman = board[pos[0]][pos[1]]
            
            if chessman is None:
                valid_moves.add(("Move", pos))
            elif chessman is not None and chessman.get_team() != self.get_team():
                valid_moves.add(("Attack", pos))
    
        return valid_moves

    @override
    def get_attack_area(self, board):
        
        attack_area = set() # store the attackable position 

        # 4 directions 
        directions = [
                      (-1,  0), 
            ( 0, -1),           ( 0,  1), 
                      ( 1,  0), 
        ]

        for dir in directions:
            for delta in range(1, len(ROW_VALUE_RANGE)):
                delta_row, delta_col = dir[0] * delta, dir[1] * delta

                valid, attack_pos = calc_position(self.get_pos(), delta_row, delta_col)

                # out of bounds (attack_pos is not on the board)
                if valid is False:
                    break
                # touch other chessmen
                elif board[attack_pos[0]][attack_pos[1]] is not None:
                    attack_area.add(attack_pos)
                    break
                else:
                    attack_area.add(attack_pos)
        return attack_area

class Bishop(BaseChessman):

    def __init__(self, init_row: int, init_col: str, team: Team):
        super().__init__(init_row, init_col, team)

    @override
    def unicode(self):
        if self.get_team() == Team.WHITE: return "\u2657"
        else:                             return "\u265D"

    @override
    def get_valid_moves(self, board):
        
        attack_area = self.get_attack_area(board)

        # remove the moves that touch the chessmen in the same team
        valid_moves = set()
        for pos in attack_area:
            chessman = board[pos[0]][pos[1]]

            if chessman is None:
                valid_moves.add(("Move", pos))
            elif chessman is not None and chessman.get_team() != self.get_team():
                valid_moves.add(("Attack", pos))
    
        return valid_moves

    @override
    def get_attack_area(self, board):
        
        attack_area = set() # store the attackable position 

        # 4 directions 
        directions = [
            (-1, -1),           (-1,  1), 
             
            ( 1, -1),           ( 1,  1)
        ]

        for dir in directions:
            for delta in range(1, len(ROW_VALUE_RANGE)):
                delta_row, delta_col = dir[0] * delta, dir[1] * delta

                valid, attack_pos = calc_position(self.get_pos(), delta_row, delta_col)

                # out of bounds (attack_pos is not on the board)
                if valid is False:
                    break
                # touch other chessmen
                elif board[attack_pos[0]][attack_pos[1]] is not None:
                    attack_area.add(attack_pos)
                    break
                else:
                    attack_area.add(attack_pos)
        return attack_area

class Knight(BaseChessman):

    def __init__(self, init_row: int, init_col: str, team: Team):
        super().__init__(init_row, init_col, team)

    @override
    def unicode(self):
        if self.get_team() == Team.WHITE: return "\u2658"
        else:                             return "\u265E"

    @override
    def get_valid_moves(self, board):
        
        attack_area = self.get_attack_area(board)

        # remove the moves that touch the chessmen in the same team
        valid_moves = set()
        for pos in attack_area:
            chessman = board[pos[0]][pos[1]]
            
            if chessman is None:
                valid_moves.add(("Move", pos))
            elif chessman is not None and chessman.get_team() != self.get_team():
                valid_moves.add(("Attack", pos))
    
        return valid_moves

    @override
    def get_attack_area(self, board):
        
        attack_area = set() # store the attackable position 

        # 8 directions 
        directions = [
            ( 2,  1), ( 2, -1),
            ( 1,  2), ( 1, -2), 
            (-2,  1), (-2, -1),
            (-1,  2), (-1, -2)
        ]

        for dir in directions:
            delta_row, delta_col = dir[0], dir[1]

            valid, attack_pos = calc_position(self.get_pos(), delta_row, delta_col)

            # out of bounds (attack_pos is not on the board)
            if valid is False:
                continue

            attack_area.add(attack_pos)
    
        return attack_area

class Pawn(BaseChessman):

    def __init__(self, init_row: int, init_col: str, team: Team):
        super().__init__(init_row, init_col, team)

        self.__en_passant = list()
        self.__advance_direction = 1 if self.get_team() == Team.WHITE else -1

    @override
    def unicode(self):
        if self.get_team() == Team.WHITE: return "\u2659"
        else:                             return "\u265F"

    @override
    def get_valid_moves(self, board):

        valid_moves = set()

        # the pawn has not moved yet: the pawn can go forward 2 cells 
        if not self.get_moved():
            for delta in range(1, 3):
                valid, next_pos = calc_position(self.get_pos(), delta * self.__advance_direction, 0)

                if not valid or board[next_pos[0]][next_pos[1]] is not None: break
                valid_moves.add(("Move", next_pos))
        # normal move: the pawn can only go forward 1 cell 
        else:
            valid, next_pos = calc_position(self.get_pos(), self.__advance_direction, 0)

            if valid and board[next_pos[0]][next_pos[1]] is None: valid_moves.add(("Move", next_pos))

        
        # add en_passant moves
        for pos in self.get_en_passant():
            valid_moves.add(("Attack", pos))

        # add attack_area
        attack_area = self.get_attack_area(board)
        
        for pos in attack_area:
            chessman = board[pos[0]][pos[1]]
            
            if chessman is not None and chessman.get_team() != self.get_team():
                valid_moves.add(("Attack", pos))
        
        return valid_moves

    @override
    def get_attack_area(self, board):
        
        attack_area = set() # store the attackable position 

        directions = [ (self.__advance_direction, 1), (self.__advance_direction, -1)]

        for dir in directions:
            delta_row, delta_col = dir[0], dir[1]

            valid, attack_pos = calc_position(self.get_pos(), delta_row, delta_col)

            if valid is True:
                attack_area.add(attack_pos)
    
        return attack_area

    def clear_en_passant(self):
        self.__en_passant.clear()

    def add_en_passant(self, pos):
        self.__en_passant.append(pos)

    def get_en_passant(self):
        return self.__en_passant
    