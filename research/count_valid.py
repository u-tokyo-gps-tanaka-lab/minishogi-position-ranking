from minishogi import Position, generate_previous_positions, BLANK, KING, is_promoted, piece2ptype, ZONE_Y_AXIS
from heapq import heappush, heappop
from collections import defaultdict

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

random1M = []
with open('../data/random1M.txt') as f:
    for fen in f.readlines():
        pos = Position(fen)
        random1M.append(pos)
        #if len(random1M) > 100:
        #    break
#
print(f'random1M.size() = {len(random1M)}')
pawnOK = []
pawnNG = []
for pos in random1M:
    if pos.legal_pawn_positions():
        pawnOK.append(pos)
    else:
        pawnNG.append(pos)
print(f'pawnNG={len(pawnNG)}, pawnOK={len(pawnOK)}')
print(f'pawnNG[:10] = {[pos.fen() for pos in pawnNG[:10]]}')        
#
checkOK = []
checkNG = []
for pos in pawnOK:
    if pos.can_capture_op_king():
        checkNG.append(pos)
    else:
        checkOK.append(pos)
print(f'checkNG={len(checkNG)}, checkOK={len(checkOK)}')
print(f'checkNG[:10] = {[pos.fen() for pos in checkNG[:10]]}')     

with open('checkOK.txt', 'w') as wf:
    for pos in checkOK:
        wf.write(pos.fen() + '\n')
with open('checkNG.txt', 'w') as wf:
    for pos in checkNG:
        wf.write(pos.fen() + '\n')

# no prev state
prevOK = []
prevNG = []
prevNGnocheck = []
for pos in checkOK:
    poslist = generate_previous_positions(pos)
    if len(poslist) == 0:
        prevNG.append(pos)
        if not pos.in_check(pos.side_to_move):
            prevNGnocheck.append(pos)
    else:
        prevOK.append(pos)
print(f'prevNG={len(prevNG)}, prevOK={len(prevOK)}')
print(f'prevNG[:10] = {[pos.fen() for pos in prevNG[:10]]}') 
print(f'prevOK[:10] = {[pos.fen() for pos in prevOK[:10]]}') 

print(f'prevNGnocheck={len(prevNGnocheck)}')
print(f'prevNGnocheck[:10] = {[pos.fen() for pos in prevNGnocheck[:10]]}') 

with open('prevOK.txt', 'w') as wf:
    for pos in prevOK:
        wf.write(pos.fen() + '\n')
with open('prevNG.txt', 'w') as wf:
    for pos in prevNG:
        wf.write(pos.fen() + '\n')


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

with open('reachOK.txt', 'w') as wf:
    for pos in reachOK:
        wf.write(pos.fen() + '\n')
with open('reachNG.txt', 'w') as wf:
    for pos in reachNG:
        wf.write(pos.fen() + '\n')
