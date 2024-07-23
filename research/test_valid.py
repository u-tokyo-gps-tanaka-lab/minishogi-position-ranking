from minishogi import Position, generate_previous_positions, BLANK, KING, ZONE_Y_AXIS
from heapq import heappush, heappop
from collections import defaultdict

def distance_to_KK(pos):
    ans = 0
    kings = []
    for y in range(5):
        for x in range(5):
            piece = pos.board[y][x]
            if piece != BLANK:
                ptype = piece.ptype()
                if ptype == KING:
                    kings.append((y, x))
                else:
                    ans += 10
                    if ptype.is_promoted():
                        ans += 10
                        pl = piece.player()
                        ans += abs(ZONE_Y_AXIS[pl.value] - y)
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

pos = Position.from_fen('+p+P2G/k4/2+SS+R/1K2+B/1B3[Rg] w')
poslist = generate_previous_positions(pos)
print([pos1.fen() for pos1 in poslist])

