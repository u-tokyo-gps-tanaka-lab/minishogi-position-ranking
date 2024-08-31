from minishogi import Position, Move, generate_previous_moves, generate_previous_positions

def test_generate_previous_moves():
    pos = Position.from_fen('r2gk/P4/5/5/KG2R[Pssbb] w')
    moves = set(generate_previous_moves(pos))
    #print(f'moves={moves}')
    moves_str = 'c5a5 b5a5 c5d5 d4d5 d4e5 e4e5 R@a5 G@d5'
    moves1 = set(Move.from_uci(x) for x in moves_str.split())
    for m in moves:
        assert m in moves1
    for m in moves1:
        assert m in moves
    pos = Position.from_fen('r2gk/P4/5/3+s+r/KG3[Psbb] w')
    moves = set(generate_previous_moves(pos))
    #print(f'moves={moves}')
    moves_str = 'c5a5 b5a5 c5d5 d4d5 d4e5 e4e5 c3d2 c2d2 d1d2 d3d2 e3d2 c1d2+ e1d2+ d1e2 d3e2 e1e2 e3e2 e4e2 e1e2+ R@a5 G@d5'
    moves1 = set(Move.from_uci(x) for x in moves_str.split())
    for m in moves:
        assert m in moves1
    for m in moves1:
        assert m in moves
    # 直前の手が打ち歩詰めになる手は生成しない
    pos = Position.from_fen('r2gk/P4/1+r3/p2+s1/K1G2[sbb] w')
    moves = set(generate_previous_moves(pos))
    #print(f'moves={moves}')
    assert Move.from_uci('P@a2') not in moves
    # 探索中に見つかったもの
    pos = Position.from_fen('SR1+r1/BSk1G/5/b1K+pG/+p4[] w')
    moves = set(generate_previous_moves(pos))
    print(f'moves={moves}')
    assert Move.from_uci('a2a1+') not in moves

def test_generate_previous_positions():
    pos = Position.from_fen('r2gk/P4/5/3+s+r/KG3[Psbb] w')
    poslist = [pos1.fen() for pos1 in generate_previous_positions(pos)]
    poslist1 = [
        '1r1gk/P4/5/3+s+r/KG3[Psbb] b',
        'r2gk/P4/5/4+r/KGs2[Psbb] b',
        'r2gk/P4/5/3S+r/KGs2[Pbb] b',
        'r2gk/P4/5/3+S+r/KGs2[Pbb] b',
    ]
    #print(f'poslist={poslist}')
    for pos1 in poslist1:
        assert pos1 in poslist
    pos = Position.from_fen('+P2gk/5/5/3+s+r/KG3[PsbbR] b')
    poslist = [pos1.fen() for pos1 in generate_previous_positions(pos)]
    poslist1 = [
        'r2gk/P4/5/3+s+r/KG3[Psbb] w',
    ]
    #print(f'poslist={poslist}')
    for pos1 in poslist1:
        assert pos1 in poslist
def test_do_undo():
    posstr = 'r2gk/P4/5/3+s+r/KG3[Psbb] w'
    pos = Position.from_fen(posstr)
    assert pos.is_consistent()
    moves = pos.plm(pos.side_to_move)
    for m in moves:
        pos1 = pos.apply_move(pos.side_to_move, m)
        if not pos1.is_consistent():
            continue
        poslist = [pos2.fen() for pos2 in generate_previous_positions(pos1)]
        print(f'm={m}, pos1={pos1.fen()}, poslist={poslist}')
        assert posstr in poslist



