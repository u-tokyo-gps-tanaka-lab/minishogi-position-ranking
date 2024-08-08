from rank import countsum, rank2l, l2pos

if __name__ == "__main__":
    print(f"countsum={countsum}")
    for rank in range(countsum):
        pos = l2pos(rank2l(rank))
        print(f"rank={rank}, fen={pos.fen()}")
