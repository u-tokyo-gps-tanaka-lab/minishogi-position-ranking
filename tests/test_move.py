from minishogi import Move, PAWN, SILVER, GOLD, BISHOP, ROOK

def test_drop_move():
    for piece in [PAWN, SILVER, GOLD, BISHOP, ROOK]:
        for y in range(5):
            for x in range(5):
                m = Move.make_drop_move(piece, (y, x))
                assert m.is_drop()
                m = Move.make_drop_move(-piece, (y, x))
                assert m.is_drop()
                
