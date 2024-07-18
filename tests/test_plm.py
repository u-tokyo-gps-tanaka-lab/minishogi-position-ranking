import sys
from minishogi import Position

def test_plm():
    pos = Position('r2gk/4p/P4/5/KG2R[bbss] w 0 1')
    moves = pos.plm(1)
    assert moves == []
