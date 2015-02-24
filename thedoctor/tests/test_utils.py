from .. import arg_dict
from functools import wraps

##TODO better test names, splitting up test cases
def get_template(func, *args, **kwargs):
    return arg_dict(func, args, kwargs)

def get_actual(func, *args, **kwargs):
    return func(*args, **kwargs)

def func1(a, b):
    return locals()

def test_arg_dict1():
    template = get_template(func1, 1, 2)
    actual = get_actual(func1, 1, 2)
    assert template == actual

    template = get_template(func1, **dict(a=1, b=2))
    actual = get_actual(func1, **dict(a=1, b=2))
    assert template == actual

    template = get_template(func1, *[1,2])
    actual = get_actual(func1, *[1,2])
    assert template == actual

    template = get_template(func1, 1, **dict(b=2))
    actual = get_actual(func1, 1, **dict(b=2))
    assert template == actual

    #bad function call, too many args
    template = get_template(func1, 1, 2, 3)
    assert template == None

    #bad function call, too many args
    template = get_template(func1, 1)
    assert template == None

def func2(a, b, c='foo'):
    return locals()

def test_arg_dict2():
    template = get_template(func2, 1, 2)
    actual = get_actual(func2, 1, 2)
    assert template == actual

    template = get_template(func2, 1, 2, c='bar')
    actual = get_actual(func2, 1, 2, c='bar')
    assert template == actual

    template = get_template(func2, *[1,2,'bar'])
    actual = get_actual(func2, *[1,2,'bar'])
    assert template == actual

    template = get_template(func2, *[1], **dict(b=2, c='bar'))
    actual = get_actual(func2, *[1], **dict(b=2, c='bar'))
    assert template == actual

    # this is an bad functional call
    template = get_template(func2, 1, 2, 3, c='bar')
    assert template is None

def func3(*args, **kwargs):
    return locals()

def test_arg_dict3():
    template = get_template(func3, 1, 2, foo='bar')
    actual = get_actual(func3, 1, 2, foo='bar')
    assert template == actual

def func4(a, b, c='foo', *args):
    return locals()

def func5(a, b, c='foo', **kwargs):
    return locals()

def func6(a, b, c='foo', *args, **kwargs):
    return locals()

def test_advanced4():
    template = get_template(func4, 1, 2, 3, 4, 5)
    actual = get_actual(func4, 1, 2, 3, 4, 5)
    assert template == actual

def test_advanced5():
    template = get_template(func5, 1, 2, 3, 4, 5)
    assert template is None

    template = get_template(func5, 1, 2, d='foo', c='foo', e='bar')
    actual = get_template(func5, 1, 2, d='foo', c='foo', e='bar')
    assert template == actual

def test_advanced6():
    template = get_template(func6, 1, 2, 3, 4, 5, d='foo', e='bar')
    actual = get_actual(func6, 1, 2, 3, 4, 5, d='foo', e='bar')
    assert template == actual

from .. import _postprocess

def test_postprocess():
    val = _postprocess((int, dict, tuple))
    assert len(val) == 1
    assert val[0].__name__ == "checktype"
    func = lambda x : x
    val = _postprocess(func)
    assert val == [func]
    val = _postprocess([(int, dict, tuple), func])
    assert val[0].__name__ == "checktype"
    assert val[1] == func
    val = _postprocess(int)
    assert val[0].__name__ == "checktype"
