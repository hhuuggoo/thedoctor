from .. import _postprocess


def test_postprocess():
    val = _postprocess((int, dict, tuple))
    assert len(val) == 1
    assert val[0].__name__ == "checktype"

    def func(x):
        return x

    val = _postprocess(func)
    assert val == [func]
    val = _postprocess([(int, dict, tuple), func])
    assert val[0].__name__ == "checktype"
    assert val[1] == func
    val = _postprocess(int)
    assert val[0].__name__ == "checktype"
