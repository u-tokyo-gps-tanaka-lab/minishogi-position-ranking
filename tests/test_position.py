import pytest
from minishogi import Position, Move, GOLD

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

def test_ptype_moves():
    pos = Position('r2gk/P4/5/5/KG2R[Pbbss] w 0 1')
    moves = []
    pos.plm_piece(moves, 1, GOLD, 4, 1)
    assert Move.from_uci('b1a2') in moves

def test_in_check():
    pos = Position('r2gk/P4/5/5/KG2R[Pbbss] w 0 1')
    assert pos.in_check(-1)
    assert not pos.in_check(1)
    pos = Position('r2g1/P3k/5/5/KG1R1[Pbbss] w 0 1')
    assert not pos.in_check(-1)
    assert not pos.in_check(1)

def test_apply_move():
    pos = Position('r2g1/P3k/5/5/KG1R1[Pbbss] w 0 1')
    pos1 = pos.apply_move(1, Move.from_uci('a1a2'))
    fen1 = pos1.fen()
    assert fen1 == 'r2g1/P3k/5/K4/1G1R1[Pbbss] b 0 2'


def test_checkmate():
    pos = Position('3g1/4k/p4/g4/KGrR1[Pbbss] w 0 1')
    assert pos.in_checkmate()
    pos = Position('3g1/p3k/5/g4/KGrR1[Pbbss] w 0 1')
    assert not pos.in_checkmate()
    pos = Position('3g1/4k/p4/g4/KGRr1[Pbbss] w 0 1')
    assert not pos.in_checkmate()