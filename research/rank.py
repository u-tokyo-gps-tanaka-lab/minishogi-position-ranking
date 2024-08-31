import sys
import json
from math import comb
from bisect import bisect_left, bisect_right
from functools import reduce
from operator import mul
from collections import defaultdict

from minishogi import Ptype, WHITE, BLACK, KING, H, W, Position, BLANK, ptype_order, Piece

COUNT2I_JSON = 'count2i.json'
def read_count2i(filename):
    with open(filename) as f:
        return json.load(f)

counts = read_count2i(COUNT2I_JSON)
countsum, rank2count = counts['sum'], counts['rank2count']
# print(f'countsum={countsum}, len(count2offset)={len(count2offset)}')
hb2oms = {}
for o, hbc, ms in rank2count:
    hbc = (tuple(map(tuple, hbc[0])), tuple(map(tuple, hbc[1])))
    #print(hbc)
    hb2oms[hbc] = (o, ms)

def pos_x(pos):
    return pos // H
def pos_y(pos):
    return pos % H

KPOS_COUNT = H * (W // 2) * (H * W - 1) + H * (H * (W + 1) // 2 - 1)

def kpos_rank2pos(onboards, j, empties):
    """
    WHITE, BLACKのkingのpositionの組のうち，j番目の要素を onboards に追加する．
    Add the j-th element of the set of positions of WHITE and BLACK kings to onboards.
    
    元の盤面とその左右を反転した盤のうち、小さい方の組み合わせしか生成しない．emptiesのサイズは，H * Wのサイズに限る．
    Generate only the smaller combinations of the original board and its left-right reversed board. The size of empties is limited to H * W.

    空きマスのリスト empties からkingを置いた場合は削除する．
    If a king from the list of empty squares 'empties', remove it.

    座標 pos はx * H + y で計算される非負整数 0 <= pos < H * W 
    The cordinate 'pos' is calculated by x * H + y, where 0 <= pos < H * W.

    Args:
        onboards (list[Tuple[Piece, int]]): The target to add the tuple (piece, pos)
        j (int): The j-th element
        empties (list[int]): A list of empty squares of size H * W, which decreases by 2 when executed
    Returns: None    
    """
    assert len(empties) == H * W
    assert W % 2 == 1
    assert j < H * (W // 2) * (H * W - 1) + H * (H * W - 1)
    if j < H * (W // 2) * (H * W - 1):
        j0 = j % (H * (W // 2))
        k0 = empties.pop(j0)        
        j1 = j // (H * (W // 2))
        k1 = empties.pop(j1)
    else:
        j -= H * (W // 2) * (H * W - 1)
        j0 = j % H 
        k0 = empties.pop(H * (W // 2) + j0)
        j1 = j // H 
        k1 = empties.pop(j1)
    onboards.append((KING.to_piece(WHITE), k0))
    onboards.append((KING.to_piece(BLACK), k1))

# rest個の空マスから n_pieces を選ぶ時，最小のインデックスを i個にする組み合わせの数
# When selecting 'n_pieces' from 'rest' empty squares, how many combinations are there when the smallest index is 'i'?
comb_table = [[[0] * rest for n_pieces in range(19)] for rest in range(H * W + 1)]
for rest in range(1, H * W + 1):
    for n_pieces in range(1, min(rest, 18) + 1):
        for i in range(rest):
            comb_table[rest][n_pieces][i] = comb(rest - 1 - i, n_pieces - 1)

# rest個の空マスから n_pieces を選ぶ時，最小のインデックスが i個未満の組み合わせの数は?
# When selecting 'n_pieces' from 'rest' empty squares, how many combinations are there when the smallest index is less than 'i'?
comb_table_pre = [[[0] * (rest + 1) for n_pieces in range(19)] for rest in range(H * W + 1)]        
for rest in range(1, H * W + 1):
    for n_pieces in range(1, min(rest, 18) + 1):
        for i in range(rest):
            comb_table_pre[rest][n_pieces][i + 1] = comb_table_pre[rest][n_pieces][i] + comb_table[rest][n_pieces][i] 

def piece_rank2pos(onboards, piece, j, n_pieces, empties):
    """
    pieceがn_piecesあるとき，小さい順に並んだ座標のリストのうち，j番目の要素を onboards に追加する．
    When there are n_pieces of piece, add the j-th element of the list of coordinates arranged in ascending order to onboards.
    
    空きマスのリスト empties から削除する．
    Remove it from the list of empty squares 'empties'.

    Args:
        onboards (list[Tuple[Piece, int, int]]): (piece, y, x) を追加する対象
        piece (Piece): 
        j (int): j番目の要素
        empties (list[int]): H * W のサイズの空きマスのリスト，実行すると2つ減る
    Returns: None            
    """
    rest = len(empties)
    empty_base = 0
    while n_pieces > 0:
        i = bisect_right(comb_table_pre[rest][n_pieces], j) - 1
        j -= comb_table_pre[rest][n_pieces][i]
        rest = rest - 1 - i
        pi = empties.pop(empty_base + i)
        empty_base += i
        onboards.append((piece, pi))
        n_pieces -= 1


def pt2comblist(canp, n_empty, allcount):
    if n_empty < allcount:
        return (0, [])
    rank2comb = []
    comb2rank = {}
    x = 0
    for pb0 in range(allcount + 1 if canp else 1):
        v0 = allcount - pb0
        n_empty_1 = n_empty - pb0
        for pb1 in range(v0 + 1 if canp else 1):
            v1 = v0 - pb1
            n_empty_2 = n_empty_1 - pb1
            for b0 in range(v1 + 1):
                n_empty_3 = n_empty_2 - b0
                b1 = v1 - b0
                xadd = comb(n_empty, pb0) * comb(n_empty_1, pb1) * comb(n_empty_2, b0) * comb(n_empty_3, b1)
                rank2comb.append((x, (pb0, pb1, b0, b1)))
                comb2rank[(pb0, pb1, b0, b1)] = x
                x += xadd
    return x, rank2comb, comb2rank           
canpromote2comb_table = [[pt2comblist(True, n_empty, allcount) for allcount in range(18 + 1)] for n_empty in range(H * W + 1)]
nopromote2comb_table = [[pt2comblist(False, n_empty, allcount) for allcount in range(18 + 1)] for n_empty in range(H * W + 1)]

def basic_ptype_rank2pos(onboards, pt, empties, n_pieces, j):
    n_empty = len(empties)
    if pt.can_promote():
        combsall = canpromote2comb_table[n_empty][n_pieces]
    else:
        combsall = nopromote2comb_table[n_empty][n_pieces]
    assert j < combsall[0]
    k = bisect_left(combsall[1], (j, (0, 0, 0, 0)))
    if len(combsall[1]) <= k or combsall[1][k][0] > j:
        k -= 1
    j -= combsall[1][k][0]
    combs = combsall[1][k][1]        
    for i, x in enumerate(combs):
        if x != 0:
            rest = len(empties)
            v = comb(rest, x)
            cur = j % v
            j //= v
            piece = pt.to_piece(WHITE if i % 2 == 0 else BLACK)
            if i & 2 == 0:
                piece = piece.promote()
            piece_rank2pos(onboards, piece, cur, x, empties)

def rank2l(x):
    j = bisect_left(rank2count, [x, [], []])
    if not (j < len(rank2count) and rank2count[j][0] == x):
        j -= 1
    o, cs, ms = rank2count[j]
    x -= o
    mult = KPOS_COUNT * reduce(mul, ms[0], 1) * reduce(mul, ms[1], 1)
    assert x < mult
    hands = [[], []]
    for i, (pti, v) in enumerate(cs[0]):
        pt = Ptype(pti)
        assert mult % ms[0][i] == 0
        mult //= ms[0][i]
        j = x % ms[0][i]
        x //= ms[0][i]
        for _ in range(j):
            hands[0].append(pt)
        for _ in range(v - j):
            hands[1].append(pt)
    onboards = []
    assert mult % KPOS_COUNT == 0
    mult //= KPOS_COUNT
    j = x % KPOS_COUNT
    x //= KPOS_COUNT
    empties = list(range(H * W))
    kpos_rank2pos(onboards, j, empties)
    for i, (pti, v) in enumerate(cs[1]):
        pt = Ptype(pti)
        assert mult % ms[1][i] == 0
        mult //= ms[1][i]
        j = x % ms[1][i]
        x //= ms[1][i]
        basic_ptype_rank2pos(onboards, pt, empties, v, j)
    return (hands, onboards)

def l2key(l):
    hands, onboard = l
    pts = defaultdict(int)
    for p in range(2):
        for pt in hands[p]:
            pts[pt] += 1
    hc = []
    for pt in ptype_order:
        if pt in pts:
            hc.append((int(pt), pts[pt]))
    p2pos = defaultdict(list)
    for piece, pos in onboard:
        p2pos[piece].append(pos)
    pt2count = defaultdict(int)        
    for piece, xs in p2pos.items():
        pt = piece.ptype().unpromote_if()
        pt2count[pt] += len(xs)
    bc = []        
    for pt in ptype_order:
        if pt != KING and pt in pt2count:
            bc.append((int(pt), pt2count[pt]))
    return (tuple(hc), tuple(bc))

def piece_pos2rank(pc, empties, posls):
    ans = 0
    rest = len(empties)
    n_pieces = len(posls)
    empty_base = 0
    while n_pieces > 0:
        j = empties.index(posls[-n_pieces])
        v = comb_table_pre[rest - empty_base][n_pieces][j - empty_base]
        ans += v
        empties.pop(j)
        rest -= 1
        #print(f'rest={rest}, empty_base={empty_base}, n_pieces={n_pieces}, j={j}, v={v}, comb_table_pre[rest - empty_base][n_pieces] = {comb_table_pre[rest - empty_base][n_pieces]}')
        #ans += comb_table_pre[rest - empty_base][n_pieces][j - empty_base]
        
        empty_base = j
        n_pieces -= 1
    return ans

def l2rank(l):
    hands, onboards = l
    hands0 = defaultdict(int)
    for pt in hands[0]:
        hands0[pt] += 1
    pc2pos = defaultdict(list)
    for pc, pos in onboards:
        pc2pos[pc].append(pos)
    hbc = l2key(l)
    o, ms = hb2oms[hbc]
    ans = 0
    base = 1
    # hands
    for i in range(len(hbc[0])):
        pt, cnt = hbc[0][i]
        cnt1 = hands0.get(Ptype(pt), 0)
        ans += base * cnt1
        base *= (cnt + 1)
    # kpos
    empties = list(range(H * W))
    j0 = pc2pos[Piece.W_KING][0]
    empties.pop(j0)
    j1 = empties.index(pc2pos[Piece.B_KING][0])
    empties.pop(j1)
    kpos = 0
    if j0 < H * (W // 2):
        kpos = j0 + j1 * H * (W // 2)
    elif j0 < H * (W // 2 + 1):
        kpos = H * (W // 2) * (H * W - 1) + (j0 % H) + j1 * H
    else:
        print(f'pc2pos={pc2pos}, j0={j0}, j1={j1}')
        raise ValueError(f'invalid king positions ')
    ans += base * kpos
    base *= KPOS_COUNT
    for i in range(len(hbc[1])):
        pt, cnt = hbc[1][i]
        pt = Ptype(pt)
        ptcounts = []
        posls = []
        for j in range(0, 2): # j == 0 promoted, 1 not promoted
            for p in range(0, 2): # p == 0 white, 1 black
                if j == 0 and not pt.can_promote():
                    ptcounts.append(0)
                    posls.append([])
                else:
                    pc = pt.to_piece([WHITE, BLACK][p])
                    if j == 0:
                        pc = pc.promote()
                    posl = pc2pos.get(pc, [])
                    ptcounts.append(len(posl))
                    posls.append(posl[:])
        ptcounts = tuple(ptcounts)
        n_empty = len(empties)
        if pt.can_promote():
            x, rank2comb, comb2rank = canpromote2comb_table[n_empty][cnt]
        else:
            x, rank2comb, comb2rank = nopromote2comb_table[n_empty][cnt]                            
        rank = comb2rank[ptcounts]
        in_rank = 0
        in_rank_base = 1
        for j in range(0, 2): # j == 0 promoted, 1 not promoted
            for p in range(0, 2): # p == 0 white, 1 black
                if ptcounts[j * 2 + p] == 0:
                    continue
                n_empty = len(empties)
                pc = pt.to_piece([WHITE, BLACK][p])
                if j == 0:
                    pc = pc.promote()
                v = piece_pos2rank(pc, empties, posls[j * 2 + p])
                in_rank += in_rank_base * v
                in_rank_base *= comb(n_empty, len(posls[j * 2 + p]))
        ans += base * (rank + in_rank)
        base *= x
    return ans + o

def l2pos(l):
    hands, onboards = l
    board = [[BLANK] * W for _ in range(H)]
    for piece, pos in onboards:
        #print(f'piece={piece}, pos={pos}, W={W}, H={H}')
        y, x = pos % H, pos // H
        board[y][x] = piece
    return Position(WHITE, board, hands)        

def pos2l(pos):
    hands = pos.hands
    onboards = []
    for y in range(H):
        for x in range(W):
            if pos.board[y][x] != BLANK:
                onboards.append((pos.board[y][x], x * H + y))
    onboards.sort()
    return (hands, onboards)

def rank2pos(x):
    return l2pos(rank2l(x))

def pos2rank(pos):
    l = pos2l(pos)
    #print(f'pos.board={pos.board}, l={l}')
    return l2rank(l)