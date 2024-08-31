from itertools import combinations
from collections import defaultdict, Counter
import random

from rank import kpos_rank2pos, comb, comb_table_pre, piece_rank2pos, pt2comblist, basic_ptype_rank2pos, pos_x, pos_y, canpromote2comb_table, nopromote2comb_table, rank2l, l2pos, pos2rank, l2key, pos2l
from minishogi import Position, H, W, KING, WHITE, BLACK, PAWN, SILVER, GOLD, BISHOP, ROOK


def test_kpos_rank2pos():
    combs = set()
    for j in range(H * (W // 2) * (H * W - 1) + H * (H * (W + 1) // 2 - 1)):
        onboards, empties = [], list(range(H * W))
        kpos_rank2pos(onboards, j, empties)
        assert len(empties) == H * W - 2
        assert len(onboards) == 2
        assert onboards[0][0] == KING.to_piece(WHITE)
        assert onboards[1][0] == KING.to_piece(BLACK)
        pos1, pos2 = onboards[0][1], onboards[1][1]
        combs.add((pos1, pos2))
    assert len(combs) == H * (W // 2) * (H * W - 1) + H * (H * (W + 1) // 2 - 1)
    #print(f'combs={combs}')
    for pos1, pos2 in combs:
        #print(f'pos1={pos1}, pos2={pos2}')
        assert pos1 != pos2
        assert pos_x(pos1) < (W + 1) // 2
        if pos_x(pos1) == W // 2:
            assert pos_x(pos2) < (W + 1) // 2

def test_comb_table():
    for n_pieces in range(1, 19):
        for rest in range(n_pieces, H * W + 1):
            assert len(comb_table_pre[rest][n_pieces]) == rest + 1
            assert comb_table_pre[rest][n_pieces][1] == comb(rest, n_pieces)

def test_piece_rank2pos():
    for rest, n_pieces in [(23, 1), (21, 2)]:
        combs = set()
        for j in range(comb(rest, n_pieces)):
            empties = list(range(rest))
            onboards = []
            piece_rank2pos(onboards, KING.to_piece(WHITE), j, n_pieces, empties)
            assert len(empties) == rest - n_pieces
            assert len(onboards) == n_pieces
            #print(f'onboards={onboards}')
            poslist = [x[1] for x in onboards]
            poslist1 = list(sorted([x for x in poslist], key=lambda p: (pos_x(p), pos_y(p))))
            assert poslist == poslist1
            combs.add(tuple(poslist))
        assert len(combs) == comb(rest, n_pieces)
        for cmb in combinations(range(rest), n_pieces):
            poslist = tuple(cmb)
            assert poslist in combs

def test_basic_pt2comblist():
    for (pt, n_empty, allcount), count0 in [((PAWN, 23, 1), 23 * 4)]:
        x, rank2comb, _ = pt2comblist(pt, n_empty, allcount)
        assert x == count0
        assert len(rank2comb) == 4
        for i, comb in rank2comb:
            assert sum(comb) == allcount

def test_comb_table():
    for ((n_empty, allcount), v) in [((23, 1), 23 * 4)]:
        x, rank2comb, comb2rank = canpromote2comb_table[n_empty][allcount]
        assert x == v
        assert len(rank2comb) == 4
        for i, comb in rank2comb:
            assert sum(comb) == allcount
            assert comb2rank[comb] == i
    for ((n_empty, allcount), v) in [((23, 1), 23 * 2)]:
        x, rank2comb, _ = nopromote2comb_table[n_empty][allcount]
        assert x == v
        assert len(rank2comb) == 2
        for i, comb in rank2comb:
            assert sum(comb) == allcount
            assert comb2rank[comb] == i
def test_basic_ptype_rank2pos():
    for pt, n_empty, n_pieces in [(PAWN, 23, 1), (GOLD, 22, 2), (SILVER, 10, 4), (ROOK, 15, 3)]:
        if pt.can_promote():
            combcount, combsall, _ = canpromote2comb_table[n_empty][n_pieces]
        else:
            combcount, combsall, _ = nopromote2comb_table[n_empty][n_pieces]
        pcmb2posl = defaultdict(list)
        for j in range(combcount):
            empties = list(range(n_empty))
            onboards = []
            basic_ptype_rank2pos(onboards, pt, empties, n_pieces, j)
            assert len(empties) == n_empty - n_pieces
            assert len(onboards) == n_pieces
            #print(f'onboards={onboards}')
            piece2posl = defaultdict(list)
            for piece, pos in onboards:
                piece2posl[piece].append(pos)
            kvs = list(sorted(piece2posl.items()))
            pcounts = tuple(sorted(Counter(x[0] for x in kvs).items()))
            posl = [x[1] for x in kvs]
            pcmb2posl[pcounts].append(posl)
        #print(f'pcmb2posl.items()={pcmb2posl.items()}')
        for k, v in pcmb2posl.items():
            assert len(v) == len(set(tuple(tuple(l) for l in v1) for v1 in v))

def test_basic_ptype_rank2pos_random():
    for pt, n_empty, n_pieces in [(PAWN, 23, 1), (GOLD, 22, 2), (SILVER, 10, 4), (ROOK, 15, 3)]:
    #for pt, n_empty, n_pieces in [(SILVER, 10, 4)]:
        if pt.can_promote():
            combcount, combsall, _ = canpromote2comb_table[n_empty][n_pieces]
        else:
            combcount, combsall,_ = nopromote2comb_table[n_empty][n_pieces]
        p2count = defaultdict(int)
        for _ in range(1000):
            j = random.randrange(0, combcount)
            empties = list(range(n_empty))
            onboards = []
            basic_ptype_rank2pos(onboards, pt, empties, n_pieces, j)
            for piece, pos in onboards:
                p2count[piece] += 1
        #print(p2count)

