import sys
from minishogi import Position, WHITE
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
    file_OK = f'{filename}_OK.txt' if parfile else 'king_OK.txt'
    file_NG = f'{filename}_NG.txt' if parfile else 'king_NG.txt'
    with open(filename) as f:
        with open(file_OK, 'w') as wf1:
            with open(file_NG, 'w') as wf2:
                for fen in f.readlines():
                    pos = Position.from_fen(fen)
                    assert pos.side_to_move == WHITE, f'pos={pos.fen()}'
                    if not pos.can_capture_op_king():
                        assert pos.side_to_move == WHITE, f'pos={pos.fen()}'
                        wf1.write(pos.fen() + '\n')
                    else:
                        assert pos.side_to_move == WHITE, f'pos={pos.fen()}'
                        wf2.write(pos.fen() + '\n')

def main():
    assert len(sys.argv) == 2
    process_file(sys.argv[1], False)

if __name__ == "__main__":
    main()