import sys
import json
from math import comb
from bisect import bisect_left, bisect_right
from functools import reduce
from operator import mul
from minishogi import Ptype, WHITE, BLACK, KING, H, W, Position, BLANK

COUNT2I_JSON = 'count2i.json'
def read_count2i(filename):
    with open(filename) as f:
        return json.load(f)

counts = read_count2i(COUNT2I_JSON)
countsum, rank2count = counts['sum'], counts['rank2count']
# print(f'countsum={countsum}, len(count2offset)={len(count2offset)}')

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
                x += xadd
    return x, rank2comb           

canpromote2comb_table = [[pt2comblist(True, n_empty, allcount) for allcount in range(18 + 1)] for n_empty in range(H * W + 1)]
nopromote2comb_table = [[pt2comblist(False, n_empty, allcount) for allcount in range(18 + 1)] for n_empty in range(H * W + 1)]

def basic_ptype_rank2pos(onboards, pt, empties, n_pieces, j):
    n_empty = len(empties)
    if pt.can_promote():
        combsall = canpromote2comb_table[n_empty][n_pieces]
    else:
        combsall = nopromote2comb_table[n_empty][n_pieces]
    #print(f'basic_ptype_rankpos(pt={pt}, n_empty={n_empty}, n_pieces = {n_pieces}), combsall = {combsall}, j ={j}')
    assert j < combsall[0]
    k = bisect_left(combsall[1], (j, (0, 0, 0, 0)))
    if len(combsall[1]) <= k or combsall[1][k][0] > j:
        k -= 1
    #print(f'k={k}')
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
    #print(f'o, cs, ms = {(o, cs, ms)}')
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
    #print(f'hands={hands}, x = {x}, mult = {mult}')            
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
        #rest = len(empties)
        #x1, rank2comb = pt2comblist(pt, rest, v)
        #
        #assert j < x1
        #print(f'x1={x1}, rank2comb={rank2comb}')
        #k = bisect_left(rank2comb, (j, (0, 0, 0, 0)))
        #if not(k < len(rank2comb) and rank2comb[k][0] == j):
        #    k -= 1
        #j -= rank2comb[k][0]
        basic_ptype_rank2pos(onboards, pt, empties, v, j)
        #print(f'pt={pt}, i={i}, v={v}, x={x}, j={j}, x1={x1}, rank2comb={rank2comb}')
    return (hands, onboards)

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