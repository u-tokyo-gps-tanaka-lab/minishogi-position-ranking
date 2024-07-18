from minishogi import Position, showstate

def test_images():
    pos = Position('+B+b3/4+R/G1k2/P+SsP1/2K+R1[G] w 0 1')
    print(pos.fen())
    showstate(pos)