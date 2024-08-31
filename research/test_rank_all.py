from minishogi import Ptype

from rank_all import count2N, count_ptype
from rank import canpromote2comb_table, nopromote2comb_table

def test_count2N():
    c =[[[6, 1], [4, 2]], [[6, 1], [5, 2], [3, 2], [2, 2]]]
    c = [[(Ptype(pt), v) for pt, v in c[0]], [(Ptype(pt), v) for pt, v in c[1]]]
    ans = count2N(c)
    print(ans)
    assert ans == (4706713151078400, ([2, 3], [92, 3696, 3040, 2448]))

def test_count2N_table():
    for n_empty in [10, 15, 20]:
        for pti, v in [[6, 2], [5, 2], [4, 2], [3, 2], [2, 2]]:
            pt = Ptype(pti)
            if pt.can_promote():
                ans0, combs, _ = canpromote2comb_table[n_empty][v]
            else:
                ans0, combs, _ = nopromote2comb_table[n_empty][v]
            ans1 = count_ptype(pt, n_empty, v)
            assert ans0 == ans1
