import sys
from minishogi import Position, generate_previous_positions, WHITE

def load_fen_list(fname):
    ans = []
    with open(fname) as f:
        for fen in f.readlines():
            fen = fen.rstrip()
            pos = Position.from_fen(fen)
            ans.append(pos)
    return ans
def save_fen_list(fname, ls):
    with open(fname, 'w') as wf:
        wf.write('\n'.join(pos.fen() for pos in ls))
        wf.write('\n')

def process_file(filename, parfile=False):
    file_OK = f'{filename}_OK.txt' if parfile else 'prev_OK.txt'
    file_NG = f'{filename}_NG.txt' if parfile else 'prev_NG.txt'
    file_NG_nocheck = f'{filename}_NG_nocheck.txt' if parfile else 'prev_NG_nocheck.txt'
    with open(filename) as f:
        with open(file_OK, 'w') as wf1:
            with open(file_NG, 'w') as wf2:
                with open(file_NG_nocheck, 'w') as wf3:
                    for fen in f.readlines():
                        pos = Position.from_fen(fen)
                        assert pos.side_to_move == WHITE, f'pos={pos.fen()}'
                        poslist = generate_previous_positions(pos)
                        if len(poslist) != 0:
                            assert pos.side_to_move == WHITE, f'pos={pos.fen()}'
                            wf1.write(pos.fen() + '\n')
                        else:
                            assert pos.side_to_move == WHITE, f'pos={pos.fen()}'
                            wf2.write(pos.fen() + '\n')
                            if not pos.in_check(pos.side_to_move):
                                wf3.write(pos.fen() + '\n')

def main():
    assert len(sys.argv) == 2
    process_file(sys.argv[1], False)

if __name__ == "__main__":
    main()
