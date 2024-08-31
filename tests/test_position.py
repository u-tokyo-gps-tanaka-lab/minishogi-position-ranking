import pytest
from minishogi import Position, Move, GOLD, BLANK, SILVER, king_checkmate_pawn, BLACK, WHITE

def test_inout_fen():
    p = Position.from_fen()
    assert p.fen() == 'rbsgk/4p/5/P4/KGSBR[] w'
    for fen in ['1bs1k/4g/5/P4/KGSB1[Prr] w', '1bs1k/4g/5/P4/KGSB1[Prr] b']:
        print(Position.from_fen(fen).fen(), fen)
  
def test_position_equal():
    fens = ['1bs1k/4g/5/P4/KGSB1[Prr] w', '1bs1k/4g/5/P4/KGSB1[Prr] b']
    for fen in fens:
        assert Position.from_fen(fen) == Position.from_fen(fen)

def test_position_in_dict():
    fens = ['1bs1k/4g/5/P4/KGSB1[Prr] w', '1bs1k/4g/5/P4/KGSB1[Prr] b']
    d = {}
    for fen in fens:
        pos = Position.from_fen(fen)
        d[pos] = 1
    for fen in fens:
        assert Position.from_fen(fen) in d

def test_is_consistent():
    p = Position.from_fen('rbsgk/4p/5/P4/KGSBR[] w')
    assert p.is_consistent()
    p = Position.from_fen('rbsgk/4p/5/PP3/KGSBR[] w')
    assert not p.is_consistent()
    p = Position.from_fen('rbsgk/4p/5/+P4/KGSBR[] w')
    assert p.is_consistent()
    p = Position.from_fen('rbsgk/4p/5/+P4/KGSBR[p] w')
    assert not p.is_consistent()

def test_legal_pawn_positions():
    # 行き場のない歩
    for p in ['Pbsgk/4p/5/4P/KGSBR[r] w', 'Pbsgk/4p/5/4P/KGSBR[r] b', 
              '1bsgk/p4/5/P4/KGSBp[rr] w', '1bsgk/p4/5/P4/KGSBp[rr] b']:
        assert not Position.from_fen(p).legal_pawn_positions()
    # 二歩
    for p in ['1bsgk/4p/4p/5/KGSBR[r] w', '1bsgk/4p/4p/5/KGSBR[r] w', 
              '1bsgk/4P/4P/5/KGSBR[r] w', '1bsgk/4P/4P/5/KGSBR[r] w']:
        assert not Position.from_fen(p).legal_pawn_positions()



def test_ptype_moves():
    pos = Position.from_fen('r2gk/P4/5/5/KG2R[Pbbss] w')
    moves = []
    pos.plm_piece(moves, WHITE, GOLD, 4, 1)
    print([m.to_uci() for m in moves])
    assert Move.from_uci('b1a2') in moves

def test_in_check():
    pos = Position.from_fen('r2gk/P4/5/5/KG2R[Pbbss] w')
    assert pos.in_check(BLACK)
    assert not pos.in_check(WHITE)
    pos = Position.from_fen('r2g1/P3k/5/5/KG1R1[Pbbss] w')
    assert not pos.in_check(BLACK)
    assert not pos.in_check(WHITE)
    pos = Position.from_fen('r2gk/P4/1+r3/p2+s1/K1G2[bbs] w')
    assert not pos.in_check(BLACK)
    assert pos.in_check(WHITE)

def test_apply_move():
    pos = Position.from_fen('r2g1/P3k/5/5/KG1R1[Pssbb] w')
    pos1 = pos.apply_move(WHITE, Move.from_uci('a1a2'))
    fen1 = pos1.fen()
    assert fen1 == 'r2g1/P3k/5/K4/1G1R1[Pssbb] b'

def test_apply_unmove():
    pos = Position.from_fen('r2gk/P4/5/3+s+r/KG3[Psbb] w')
    pos1 = pos.apply_unmove(BLACK, Move.from_uci('b5a5'), BLANK)
    fen1 = pos1.fen()
    assert fen1 == '1r1gk/P4/5/3+s+r/KG3[Psbb] b'
    pos = Position.from_fen('r2gk/P4/5/3+s+r/KG3[Psbb] w')
    pos1 = pos.apply_unmove(BLACK, Move.from_uci('c1d2+'), SILVER.to_piece(WHITE))
    fen1 = pos1.fen()
    assert fen1 == 'r2gk/P4/5/3S+r/KGs2[Pbb] b'

def test_checkmate():
    pos = Position.from_fen('r2gk/P4/1+r3/p2+s1/K1G2[sbb] w')
    assert pos.in_checkmate()
    pos = Position.from_fen('3g1/4k/p4/g4/KGrR1[Pssbb] w')
    assert pos.in_checkmate()
    pos = Position.from_fen('3g1/p3k/5/g4/KGrR1[Pssbb] w')
    assert not pos.in_checkmate()
    pos = Position.from_fen('3g1/4k/p4/g4/KGRr1[Pssbb] w')
    assert not pos.in_checkmate()


def test_king_checkmate_pawn():
    pos = Position.from_fen('r2gk/P4/1+r3/p2+s1/K1G2[sbb] w')
    assert king_checkmate_pawn(pos, 3, 0)