from math import comb
import json
from minishogi import Ptype, KING, BLACK, WHITE, ptype_counts, H, W, KING, GOLD, PAWN, SILVER, ROOK, BISHOP, ptype_order

# ptype_order = [KING, GOLD, KNIGHT, LANCE, PAWN, SILVER, ROOK, BISHOP, Ptype.BLANK]
# (handcounts, boardcounts) を返す．
# handcounts, boardcounts は
#　(piece count) のpair
def make_count_sub(i):
    if i >= len(ptype_order) or ptype_order[i] == Ptype.BLANK:
        return [([], [])]
    pt = Ptype(ptype_order[i])
    l2 = make_count_sub(i + 1)
    if pt == KING:
        return l2
    l1 = []
    rest = ptype_counts[pt]
    for bc in range(rest + 1):
        hc = rest - bc
        l1add = [[], []]
        if hc > 0:
            l1add[0].append((pt, hc))
        if bc > 0:
            l1add[1].append((pt, bc))
        l1.append(l1add)
    ans = []                            
    for hc1, bc1 in l1:
        for hc2, bc2 in l2:
            ans.append((hc1 + hc2, bc1 + bc2))
    print(f'make_count_sub(i={i}) return len(ans)={len(ans)}')
    return ans            
countall = make_count_sub(0)
countall.sort()
KPOS_COUNT = H * (W // 2) * (H * W - 1) + H * (H * (W + 1) // 2 - 1)
def count_ptype(pt, n_empty, v):
    x = 0
    for pb0 in range(v + 1 if pt.can_promote() else 1):
        v0 = v - pb0
        for pb1 in range(v0 + 1 if pt.can_promote() else 1):
            v1 = v0 - pb1
            for b0 in range(v1 + 1):
                b1 = v1 - b0
                xadd = comb(n_empty, pb0) * comb(n_empty - pb0, pb1) * comb(n_empty - pb0 - pb1, b0) * comb(n_empty - pb0 - pb1 - b0, b1)
                x += xadd
    return x            

def count2N(c):
    hc, bc = c
    hcmult = 1
    hcl = []
    for pt, v in hc:
        hcmult *= (v + 1)
        hcl.append(v + 1)
    bcl = []
    bcmult = KPOS_COUNT # KING position
    #print(f'bcmult={bcmult}')
    n_empty = H * W - 2
    for pt, v in bc:
        x = count_ptype(pt, n_empty, v)        
        bcmult *= x
        bcl.append(x)
        n_empty -= v                            
    return hcmult * bcmult, (hcl, bcl)

def main():
    count2num = []
    rank2count = []
    countsum = 0
    for i in range(len(countall)):
        c = countall[i]
        if len(c) != 2:
            print(f'i={i}, c={c}')
        s, l = count2N(c)
        rank2count.append((countsum, c, l))
        countsum += s

    print(countsum)
    with open('count2i.json', 'w') as wf:
        json_str = json.dumps({'sum' : countsum, 'rank2count' : rank2count})
        wf.write(json_str)

if __name__ == "__main__":
    main()
