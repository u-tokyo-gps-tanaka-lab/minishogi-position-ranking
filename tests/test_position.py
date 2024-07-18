import pytest
import minishogi

def test_inout_fen():
    p = minishogi.Position()
    assert p.fen() == 'rbsgk/4p/5/P4/KGSBR[] w 0 1'
    for fen in ['1bs1k/4g/5/P4/KGSB1[Prr] w 0 2', '1bs1k/4g/5/P4/KGSB1[Prr] b 0 2']:
        print(minishogi.Position(fen).fen(), fen)
        assert minishogi.Position(fen).fen() == fen
