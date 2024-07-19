import pytest
from minishogi import Position, Move, GOLD, BLANK, SILVER, king_checkmate_pawn

def test_inout_fen():
    p = Position()
    assert p.fen() == 'rbsgk/4p/5/P4/KGSBR[] w 0 1'
    for fen in ['1bs1k/4g/5/P4/KGSB1[Prr] w 0 2', '1bs1k/4g/5/P4/KGSB1[Prr] b 0 2']:
        print(Position(fen).fen(), fen)
  
def test_position_equal():
    fens = ['1bs1k/4g/5/P4/KGSB1[Prr] w 0 2', '1bs1k/4g/5/P4/KGSB1[Prr] b 0 2']
    for fen in fens:
        assert Position(fen) == Position(fen)

def test_position_in_dict():
    fens = ['1bs1k/4g/5/P4/KGSB1[Prr] w 0 2', '1bs1k/4g/5/P4/KGSB1[Prr] b 0 2']
    d = {}
    for fen in fens:
        pos = Position(fen)
        d[pos] = 1
    for fen in fens:
        assert Position(fen) in d

def test_is_consistent():
    p = Position('rbsgk/4p/5/P4/KGSBR[] w 0 1')
    assert p.is_consistent()
    p = Position('rbsgk/4p/5/PP3/KGSBR[] w 0 1')
    assert not p.is_consistent()
    p = Position('rbsgk/4p/5/+P4/KGSBR[] w 0 1')
    assert p.is_consistent()
    p = Position('rbsgk/4p/5/+P4/KGSBR[p] w 0 1')
    assert not p.is_consistent()

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

def test_apply_unmove():
    pos = Position('r2gk/P4/5/3+s+r/KG3[Pbbs] w 0 1')
    pos1 = pos.apply_unmove(-1, Move.from_uci('b5a5'), BLANK)
    fen1 = pos1.fen()
    assert fen1 == '1r1gk/P4/5/3+s+r/KG3[Pbbs] b 0 0'
    pos = Position('r2gk/P4/5/3+s+r/KG3[Pbbs] w 0 1')
    pos1 = pos.apply_unmove(-1, Move.from_uci('c1d2+'), SILVER)
    fen1 = pos1.fen()
    assert fen1 == 'r2gk/P4/5/3S+r/KGs2[Pbb] b 0 0'

def test_checkmate():
    pos = Position('3g1/4k/p4/g4/KGrR1[Pbbss] w 0 1')
    assert pos.in_checkmate()
    pos = Position('3g1/p3k/5/g4/KGrR1[Pbbss] w 0 1')
    assert not pos.in_checkmate()
    pos = Position('3g1/4k/p4/g4/KGRr1[Pbbss] w 0 1')
    assert not pos.in_checkmate()

def test_king_checkmate_pawn():
    pos = Position('r2gk/P4/1+r3/p2+s1/K1G2[bbs] w 0 1')
    assert king_checkmate_pawn(pos, 3, 0)