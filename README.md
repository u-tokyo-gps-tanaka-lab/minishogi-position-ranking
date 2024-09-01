# minishogi-position-ranking

<!-- [![arXiv](https://img.shields.io/badge/arXiv-1234.56789-b31b1b.svg)](https://arxiv.org/abs/1234.56789) -->

cf. "Estimating the number of reachable positions in Minishogi"  http://id.nii.ac.jp/1001/00238391/ (in Japanese)

[Rye](https://rye.astral.sh/) is required to run these programs.

## Reproduce the experiments

### Setup

```bash
$ rye sync
$ cd research
```

Make sure that you are in `research` directory before you start the follwing experiments. Also, you need to have IPAGothic font in your system to visualize positions.

### 1. generate $S_{all}$ and rank its elements

```bash
$ rye run python rank_all.py
```

If the program works correctly, you should see the following outputs and get `count2i.json`. `16014219505238849250` is the number of elements in $S_{all}$.

```text
make_count_sub(i=5) return len(ans)=3
make_count_sub(i=4) return len(ans)=9
make_count_sub(i=3) return len(ans)=27
make_count_sub(i=2) return len(ans)=81
make_count_sub(i=1) return len(ans)=243
16014219505238849250
```

### 2. generate random integers (position ranks)

```bash
$ rye run python random_number_10K.py
$ rye run python random_number_100M.py # requires a few GB of storage
```

They will create `RN10K.txt` and `RN100M.txt` respectively. The former is for testing and the latter for the main experiment.

### 3. check the legality of the positions

```bash
$ rye run python rank_to_fen.py RN100M.txt
```

`rank_to_fen.py` reads the random ranks, generates pseudo-legal positions corresponding to them, and checks if they are identical when flipped horizontally. It creates `flipH_[OK,NG].txt` in default.

```bash
$ rye run python check_piece.py flipH_OK.txt
$ rye run python check_king.py piece_OK.txt
$ rye run python check_prev.py king_OK.txt
$ rye run python check_reach.py prev_OK.txt
```

After running these commands, you will be able to estimate the number of reachable positions in Minishogi using interval estimation of the population proportion of $S_{all}$.