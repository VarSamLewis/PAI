import pytest
from PAI.tools.tool_store import sum2num


def test_tool_store_sum2num_1():
    assert sum2num(1, 2) == 3

    with pytest.raises(TypeError):
        sum2num("4", 4)
