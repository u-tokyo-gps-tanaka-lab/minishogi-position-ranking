from minishogi import Move, PAWN, SILVER, GOLD, BISHOP, ROOK, WHITE, BLACK

def test_move_equal():
    move1 = Move((4, 4), (4, 2), False)
    move2 = Move((4, 4), (4, 2), False)
    assert move1 == move2

def test_drop_move():
    for ptype in [PAWN, SILVER, GOLD, BISHOP, ROOK]:
        for y in range(5):
            for x in range(5):
                m = Move.make_drop_move(ptype.to_piece(WHITE), (y, x))
                assert m.is_drop()
                m = Move.make_drop_move(ptype.to_piece(BLACK), (y, x))
                assert m.is_drop()

def test_moves_uci():
    move = Move.from_uci('e1c1')
    assert move == Move((4, 4), (4, 2), False)
    move = Move.from_uci('e1e5+')
    assert move == Move((4, 4), (0, 4), True)
    move = Move.make_drop_move(PAWN, (4, 2))
    assert move == Move.from_uci('P@c1')
    movestrs = 'e1c1 e1d1 e1e2 e1e3 e1e4 e1e5 e1e5+ a1b2 a4a5+ b1c1 b1a2 b1b2 b1c2 P@c1 P@d1 P@b2 P@c2 P@d2 P@e2 P@b3 P@c3 P@d3 P@e3 P@b4 P@c4 P@d4 P@e4 a1a2'
    for s in movestrs.split():
        assert s == Move.from_uci(s).to_uci()

