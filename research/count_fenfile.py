import sys
from collections import defaultdict
from minishogi import Position, BLANK
H = 5
W = 5

def count_fenfile(fname):
    with open(fname, 'r') as f:
        p2pos = {}
        piececount = defaultdict(int)
        lno = 1
        while True:
            l = f.readline()
            l = l.rstrip()
            if not l:
                break
            # print(f'lno={lno}, l={l}', file=sys.stderr)
            lno += 1
            pos = Position.from_fen(l)
            for y in range(H):
                for x in range(W):
                    piece = pos.board[y][x]
                    if piece != BLANK:
                        if piece not in p2pos:
                            p2pos[piece] = [[0] * W for _ in range(H)]
                        p2pos[piece][y][x] += 1
                        piececount[piece] += 1
        for k, v in sorted(p2pos.items()):
            print(k)
            for y in range(H):
                print(' '.join(str(p2pos[k][y][x]) for x in range(W)))
            print('\n')                
            print(piececount[k])

def main():
    for fname in sys.argv[1:]:
        count_fenfile(fname)

if __name__ == '__main__':
    main()
