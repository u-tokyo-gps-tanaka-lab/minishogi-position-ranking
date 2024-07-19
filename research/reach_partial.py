from minishogi import Position, generate_previous_positions, BLANK, KING, is_promoted, piece2ptype, ZONE_Y_AXIS
from heapq import heappush, heappop
from collections import defaultdict
import sys

def distance_to_KK(pos):
    ans = 0
    kings = []
    for y in range(5):
        for x in range(5):
            piece = pos.board[y][x]
            if piece != BLANK:
                ptype = piece2ptype(piece)
                if ptype == KING:
                    kings.append((y, x))
                else:
                    ans += 10
                    if is_promoted(ptype):
                        ans += 10
                        pl = 1 if piece > 0 else -1
                        ans += abs(ZONE_Y_AXIS[pl] - y)
    assert len(kings) == 2
    if abs(kings[0][0] - kings[1][0]) + abs(kings[0][1] - kings[1][1]) <= 2:
        ans += 10
    return ans        

def can_reach_KK(pos):
    prev = {}
    q = [(distance_to_KK(pos), pos)]
    prev[pos] = None
    distance = defaultdict(int)
    distance[pos] = 0
    i = 0
    while len(q) > 0:
        d, pos1 = heappop(q)
        #if i % 1000 == 0:
        #    print(f'len(q)={len(q)}, d={d}, pos1={pos1.fen()}')
        i += 1
        #print(f'd={d}, pos1={pos1.fen()}')
        if d == 0:
            ans = [pos1]
            while pos1 != pos:
                pos1 = prev[pos1]
                ans.append(pos1)
            ans.append(pos)
            #print(f'len(prev)={len(prev)}')
            return (True, [pos.fen() for pos in ans])
        for pos2 in generate_previous_positions(pos1):
            if pos2 not in prev:
                prev[pos2] = pos1
                distance[pos2] = distance[pos1] + 1
                heappush(q, (distance_to_KK(pos2), pos2))
    maxd = max((v, k) for k, v in distance.items())
    return (False, (maxd[0], maxd[1].fen()))

assert len(sys.argv) == 2
infname = sys.argv[1]
prevOK = []
with open(infname, 'r') as rf:
    for l in rf.readlines():
        prevOK.append(Position(l))

reachOK = []
reachNG = []
okcount = defaultdict(int)
ngcount = defaultdict(int)
i = 0
for pos in prevOK:
    ans = can_reach_KK(pos)
    if ans[0] == True:
        #if i % 100 == 0:
        #    print(ans[1])
        reachOK.append(pos)        
        okcount[len(ans[1])] += 1
    else:
        #if i % 100 == 0:
        #    print(ans[1])
        reachNG.append(pos)
        ngcount[ans[1]] += 1
print(f'reachNG={len(reachNG)}, reachOK={len(reachOK)}')
print(f'reachNG[:10] = {[pos.fen() for pos in reachNG[:10]]}') 
print(f'reachOK[:10] = {[pos.fen() for pos in reachOK[:10]]}') 

with open(f'reachOK.{infname}.txt', 'w') as wf:
    for pos in reachOK:
        wf.write(pos.fen() + '\n')
with open(f'reachNG.{infname}.txt', 'w') as wf:
    for pos in reachNG:
        wf.write(pos.fen() + '\n')
