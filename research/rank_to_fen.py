import sys
import json
from math import comb
from bisect import bisect_left, bisect_right
from functools import reduce
from operator import mul
from minishogi import Ptype, WHITE, BLACK, KING, H, W
from rank import countsum, rank2l, l2pos

flipH_OK = []
flipH_NG = []

def flipHpos(v):
    y, x = v % H, v // H 
    x = W - 1 - x
    return x * H + y

def flipH_onboards(xs):
    assert xs[0][0] == KING.to_piece(WHITE)
    assert xs[1][0] == KING.to_piece(BLACK)
    ans = []
    for piece, v in xs:
        ans.append((piece, flipHpos(v)))
    ans.sort()
    return ans        

def process_file(filename, parfile=False):
    file_OK = f'{filename}_OK.txt' if parfile else 'flipH_OK.txt'
    file_NG = f'{filename}_NG.txt' if parfile else 'flipH_NG.txt'
    with open(filename) as f:
        with open(file_OK, 'w') as wf1:
            with open(file_NG, 'w') as wf2:
                for l in f.readlines():
                    x = int(l)
                    assert x < countsum
                    (hands, onboards) = rank2l(x)
                    onboards1 = onboards[:]
                    onboards.sort()
                    #if onboards != onboards1:
                    #    print(f'onboards={onboards}, onbords1={onboards1}')
                    assert onboards == onboards1
                    pos = l2pos((hands, onboards))
                    if flipH_onboards(onboards) < onboards:
                        wf2.write(pos.fen() + '\n')
                    else:
                        wf1.write(pos.fen() + '\n')
def main():
    assert len(sys.argv) == 2
    process_file(sys.argv[1], False)

if __name__ == "__main__":
    main()