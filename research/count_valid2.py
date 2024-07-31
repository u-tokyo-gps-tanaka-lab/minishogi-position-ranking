from minishogi import Ptype, KING, BLACK, WHITE, ptype_counts, Position

H, W = Position.H, Position.W
# (handcounts, boardcounts) を返す．
# handcounts, boardcounts は
#　(piece count) のpair
def make_count_sub(i):
    if i > Ptype.BASIC_MAX.value:
        return [([], [])]
    pt = Ptype(i)
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
countall = make_count_sub(Ptype.BASIC_MIN.value)
countall.sort()
print(f'len(countall)={len(countall)}, countall[100]{countall[100]}')
#print(f'countall={countall}')

def comb(n, m):
    if n < m:
        return 0
    m = min(m, n - m)
    ans = 1
    for i in range(m):
        ans = ans * (n - i) // (i + 1)
    return ans

def count2N(c):
    hc, bc = c
    hcmult = 1
    for pt, v in hc:
        hcmult *= (v + 1)
    bcmult = H * (W // 2) * (H * W - 1) + H * (H * (W + 1) // 2 - 1) # KING position
    #print(f'bcmult={bcmult}')
    rest = H * W - 2
    for pt, v in bc:
        x = 0
        for pb0 in range(v + 1 if pt.can_promote() else 1):
            v0 = v - pb0
            for pb1 in range(v0 + 1 if pt.can_promote() else 1):
                v1 = v0 - pb1
                for b0 in range(v1 + 1):
                    b1 = v1 - b0
                    xadd = comb(rest, pb0) * comb(rest - pb0, pb1) * comb(rest - pb0 - pb1, b0) * comb(rest - pb0 - pb1 - b0, b1)
                    x += xadd
        #print(f'pt={pt}, v={v}, x={x}')
        bcmult *= x
        rest -= v                            
    return hcmult * bcmult
print(f'count2N(countall[100]){count2N(countall[100])}')
ansall = sum(count2N(c) for c in countall)
print(ansall)