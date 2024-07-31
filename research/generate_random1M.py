from minishogi import KING, Ptype, WHITE, BLACK
# 駒の数はそれぞれ2に固定

# (handcounts, boardcounts) を返す．
# handcounts, boardcounts は
#　(piece count) のpair
def make_count_sub(i):
    if i > Ptype.BASIC_MAX.value:
        return [([], [])]
    pt = Ptype(i)
    l2 = make_count_sub(i + 1)
    l1 = []
    for hc0 in range(1 if pt == KING else 3):
        rest = 2 - hc0
        for hc1 in range(1 if pt == KING else (rest + 1)):
            rest = 2 - hc0 - hc1
            for bc0 in range(1 if pt ==  KING else 0, 2 if pt == KING else (rest + 1)):
                bc1 = 2 - hc0 - hc1 - bc0
                pmax0 = bc0 if pt.can_promote() else 0
                pmax1 = bc1 if pt.can_promote() else 0
                for pbc0 in range(0, pmax0 + 1):
                    for pbc1 in range(0, pmax1 + 1):
                        l1add = ([], [])
                        if bc0 - pbc0 > 0:
                            l1add[1].append((pt.to_piece(WHITE), bc0 - pbc0))
                        if bc1 - pbc1 > 0:
                            l1add[1].append((pt.to_piece(BLACK), bc1 - pbc1))
                        if pbc0 > 0:
                            l1add[1].append((pt.promote().to_piece(WHITE), pbc0))
                        if pbc1 > 0:
                            l1add[1].append((pt.promote().to_piece(BLACK), pbc1))
                        if hc0 > 0:
                            l1add[0].append((pt.to_piece(WHITE), hc0))
                        if hc1 > 0:
                            l1add[0].append((pt.to_piece(BLACK), hc1))
                        l1.append(l1add)
    ans = []                            
    for hc1, bc1 in l1:
        for hc2, bc2 in l2:
            ans.append((hc1 + hc2, bc1 + bc2))
    return ans            
countall = make_count_sub(1)
countall.sort()
countall = [(tuple(x[0]), tuple(x[1])) for x in countall]
count2i = {x: i for i, x in enumerate(countall)}
print(f'len(countall)={len(countall)}, countall[100000]{countall[100000]}')
