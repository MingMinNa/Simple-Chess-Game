import pygame
from typing import Union, Dict, Tuple, Literal, Type, TypeAlias
from .component import (chessman,  gui_chessman)

BoardPosType:   TypeAlias = Tuple[int, str]
CoordinateType: TypeAlias = Tuple[int, int]
CellPosType:    TypeAlias = Tuple[int, int]

BoardDictType: TypeAlias    =  Dict[int, Dict[str, chessman.BaseChessman]]
ActionType:    TypeAlias    = Literal["Move", "Attack", "Castling", "Promotion"]
MoveType:      TypeAlias    = Tuple[ActionType, BoardPosType]
PromotionType: TypeAlias    = Union[
                                Type[chessman.Queen], Type[chessman.Rook], 
                                Type[chessman.Bishop], Type[chessman.Knight]
                            ]
NotationType:     TypeAlias =    Dict[int, Dict[chessman.Team, str]] 
DeadChessmenType: TypeAlias =    Dict[str, Dict[str, int]]

ColorType:        TypeAlias = Tuple[int, int, int]
ChessmanBindType: TypeAlias =  Dict[chessman.BaseChessman, gui_chessman.GuiChessman]
ImageDictType:    TypeAlias =  Dict[chessman.Team, Dict[str, pygame.Surface]]
