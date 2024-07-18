import pytest
from minishogi import Position

def test_inout_fen():
    p = Position()
    assert p.fen() == 'rbsgk/4p/5/P4/KGSBR[] w 0 1'
    for fen in ['1bs1k/4g/5/P4/KGSB1[Prr] w 0 2', '1bs1k/4g/5/P4/KGSB1[Prr] b 0 2']:
        print(Position(fen).fen(), fen)
        assert Position(fen).fen() == fen

def test_legal_pawn_positions():
    # 行き場のない歩
    for p in ['Pbsgk/4p/5/4P/KGSBR[r] w 0 1', 'Pbsgk/4p/5/4P/KGSBR[r] b 0 1', 
              '1bsgk/p4/5/P4/KGSBp[rr] w 0 1', '1bsgk/p4/5/P4/KGSBp[rr] b 0 1']:
        assert not Position(p).legal_pawn_positions()
    # 二歩
    for p in ['1bsgk/4p/4p/5/KGSBR[r] w 0 1', '1bsgk/4p/4p/5/KGSBR[r] w 0 1', 
              '1bsgk/4P/4P/5/KGSBR[r] w 0 1', '1bsgk/4P/4P/5/KGSBR[r] w 0 1']:
        assert not Position(p).legal_pawn_positions()

