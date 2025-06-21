


# row value range:    [1, 8]
# column value range: ['a', 'h']

ROW_VALUE_RANGE = tuple(range(1, 9))
COL_VALUE_RANGE = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

CHESSMAN_TYPE_NAMES = ("King", "Queen", "Rook", "Bishop", "Knight", "Pawn")

CASTLING_POS = (
    (1, 'g'),   # white short castling
    (1, 'c'),   # white long  castling
    (8, 'g'),   # black short castling
    (8, 'c')    # black long  castling
)