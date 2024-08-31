from itertools import combinations
from collections import defaultdict, Counter
import random

from rank import kpos_rank2pos, comb, comb_table_pre, piece_rank2pos, pt2comblist, basic_ptype_rank2pos, pos_x, pos_y, canpromote2comb_table, nopromote2comb_table, rank2l, l2pos, pos2rank, l2key, pos2l, rank2pos
from minishogi import Position, H, W, KING, WHITE, BLACK, PAWN, SILVER, GOLD, BISHOP, ROOK


def test_l2key():
    fen = '4+b/1sP1k/+S3G/1b1g1/K1r+pR[] w'
    pos = Position.from_fen(fen) 
    l =  pos2l(pos)
    key = l2key(l)
    assert key == ((), ((4, 2), (6, 2), (5, 2), (2, 2), (3, 2)))
    fen = 'kS2+B/1rr2/1P3/1K2+p/+S2+b1[Gg] w'
    pos = Position.from_fen(fen) 
    l =  pos2l(pos)
    #print(f'l={l}')
    key = l2key(l)
    assert key == (((4, 2),), ((6, 2), (5, 2), (2, 2), (3, 2)))

def test_pos2rank():
    # ggKK positions
    for fen in ['2k2/2G2/5/5/1GK2[ppssrrbb] w', '4k/2g2/5/5/Kg3[ppssrrbb] w']:
        pos = Position.from_fen(fen)
        rank = pos2rank(pos)
        pos1 = rank2pos(rank)
        if pos != pos1:
            print(f'rank={rank}, pos={pos.fen()}, pos1={pos1.fen()}')
        assert pos == pos1
    # error 'SR1+r1/BSk1G/5/b1K+pG/+p4[] w'
    for fen in ['SR1+r1/BSk1G/5/b1K+pG/+p4[] w']:
    #for fen in []:
        pos = Position.from_fen(fen)
        rank = pos2rank(pos)
        pos1 = rank2pos(rank)
        if pos != pos1:
            print(f'rank={rank}, pos={pos.fen()}, pos1={pos1.fen()}')
        assert pos == pos1
    # sSgGKK positions
    for fen in ['3sk/2g2/5/5/KGS2[pprrbb] w','3+sk/2g2/5/5/KG+S2[pprrbb] w']:
        pos = Position.from_fen(fen)
        rank = pos2rank(pos)
        pos1 = rank2pos(rank)
        if pos != pos1:
            print(f'rank={rank}, pos={pos.fen()}, pos1={pos1.fen()}')
        assert pos == pos1
    # gGKK positions
    for fen in ['4k/2g2/5/5/KG3[ppssrrbb] w','2k2/2g2/5/5/1GK2[ppssrrbb] w']:
        pos = Position.from_fen(fen)
        rank = pos2rank(pos)
        pos1 = rank2pos(rank)
        if pos != pos1:
            print(f'rank={rank}, pos={pos.fen()}, pos1={pos1.fen()}')
        assert pos == pos1

    # gKK positions
    for fen in ['4k/2g2/5/5/K4[Gppssrrbb] w','2k2/5/5/5/1GK2[Gppssrrbb] w']:
        pos = Position.from_fen(fen)
        rank = pos2rank(pos)
        pos1 = rank2pos(rank)
        if pos != pos1:
            print(f'rank={rank}, pos={pos.fen()}, pos1={pos1.fen()}')
        assert pos == pos1


    # KK positions
    for fen in ['4k/5/5/5/K4[ggppssrrbb] w','4k/5/5/5/K4[GGppsSRRbB] w', 'k4/5/2K2/5/5[GGppsSRRbB] w', '2k2/5/2K2/5/5[GGppsSRRbB] w']:
        pos = Position.from_fen(fen)
        rank = pos2rank(pos)
        pos1 = rank2pos(rank)
        if pos != pos1:
            print(f'rank={rank}, pos={pos.fen()}, pos1={pos1.fen()}')
        assert pos == pos1
    fen = 'kS2+B/1rr2/1P3/1K2+p/+S2+b1[Gg] w'
    pos = Position.from_fen(fen)
    rank = pos2rank(pos)
    pos1 = rank2pos(rank)
    if pos != pos1:
        print(f'rank={rank}, pos={pos.fen()}, pos1={pos1.fen()}')
    assert pos == pos1

def test_pos2rank_from_file():
    with open('checkOK.txt') as f:
        for lno in range(1000):
            l = f.readline()
            fen = ' '.join(l.split()[:2])
            print(f'fen={fen}')
            pos = Position.from_fen(fen)
            rank = pos2rank(pos)
            print('pos={pos}, rank={rank}')
            pos1 = rank2pos(rank)
            assert pos == pos1

def test_rank2pos_from_file():
    with open('RN100M.txt') as f:
        for lno in range(1000):
            l = f.readline()
            rank = int(l)
            pos = rank2pos(rank)
            rank1 = pos2rank(pos)
            assert rank == rank1
