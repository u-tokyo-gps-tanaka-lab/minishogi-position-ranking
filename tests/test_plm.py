import sys
from minishogi import Position, Move, BLACK, WHITE, PAWN

def test_plm_piece():
    pos = Position.from_fen('r2gk/P4/5/5/KG2R[Pbbss] w')
    moves = []
    pos.plm_piece(moves, WHITE, PAWN, 1, 0)
    assert 'a4a5+' in [m.to_uci() for m in moves]
    assert 'a4a5' not in [m.to_uci() for m in moves]

def test_plm():
    pos = Position.from_fen('r2gk/P4/5/5/KG2R[Pbbss] w')
    moves_str = 'e1c1 e1d1 e1e2 e1e3 e1e4 e1e5 e1e5+ a1b2 a4a5+ b1c1 b1a2 b1b2 b1c2 P@c1 P@d1 P@b2 P@c2 P@d2 P@e2 P@b3 P@c3 P@d3 P@e3 P@b4 P@c4 P@d4 P@e4 a1a2'
    sf_moves = set(Move.from_uci(x) for x in moves_str.split())
    moves = set(pos.plm(WHITE))
    print([m.to_uci() for m in moves])
    for m in sf_moves:
        assert m in moves
    for m in moves:
        assert m in sf_moves
    pos = Position.from_fen('r2gk/P4/5/5/KGR2[Pbbss] b')
    moves_str = 'a5a4 a5b5 a5c5 d5c4 d5d4 d5e4 d5c5 B@d1 B@e1 B@a2 B@b2 B@c2 B@d2 B@e2 B@a3 B@b3 B@c3 B@d3 B@e3 B@b4 B@c4 B@d4 B@e4 B@b5 B@c5 S@d1 S@e1 S@a2 S@b2 S@c2 S@d2 S@e2 S@a3 S@b3 S@c3 S@d3 S@e3 S@b4 S@c4 S@d4 S@e4 S@b5 S@c5 e5d4 e5e4'
    sf_moves = set(Move.from_uci(x) for x in moves_str.split())
    moves = set(pos.plm(BLACK))
    for m in sf_moves:
        assert m in moves
    for m in moves:
        assert m in sf_moves
    # 二歩を生成しない
    pos = Position.from_fen('r2gk/p4/5/5/KGR2[pbbss] b')
    moves_str = 'a5b5 a5c5 a4a3 d5c4 d5d4 d5e4 d5c5 B@d1 B@e1 B@a2 B@b2 B@c2 B@d2 B@e2 B@a3 B@b3 B@c3 B@d3 B@e3 B@b4 B@c4 B@d4 B@e4 B@b5 B@c5 S@d1 S@e1 S@a2 S@b2 S@c2 S@d2 S@e2 S@a3 S@b3 S@c3 S@d3 S@e3 S@b4 S@c4 S@d4 S@e4 S@b5 S@c5 e5e4 e5d4 P@b2 P@c2 P@d2 P@e2 P@b3 P@c3 P@d3 P@e3 P@b4 P@c4 P@d4 P@e4 P@b5 P@c5'
    sf_moves = set(Move.from_uci(x) for x in moves_str.split())
    moves = set(pos.plm(BLACK))
    for m in sf_moves:
        assert m in moves
    for m in moves:
        assert m in sf_moves