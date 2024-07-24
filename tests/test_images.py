from minishogi import Position, showstate

def test_images():
    pos = Position.from_fen('+B+b3/4+R/G1k2/1+Ss2/2K+R1[Gpp] w')
    print(pos.fen())
    showstate(pos, filename='state.png')