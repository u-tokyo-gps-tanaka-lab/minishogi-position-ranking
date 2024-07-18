from minishogi import Position, Move, generate_previous_moves

def test_generate_previous_moves():
    pos = Position('r2gk/P4/5/5/KG2R[Pbbss] w 0 1')
    moves = set(generate_previous_moves(pos))
    print(f'moves={moves}')
    moves_str = 'c5a5 b5a5 c5d5 d4d5 d4e5 e4e5 R@a5 G@d5'
    moves1 = set(Move.from_uci(x) for x in moves_str.split())
    for m in moves:
        assert m in moves1
    for m in moves1:
        assert m in moves
