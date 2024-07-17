import pytest
import minishogi

def test_inout_fen():
    p = Position()
    assert p.fen() == ''