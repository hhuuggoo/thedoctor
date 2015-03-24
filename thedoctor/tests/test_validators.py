import numpy as np

import pandas as pd

from .utils import raises
from .. import ValidationError
from ..validators import broadcastable, check_type, dict_validator, has, \
    nonsingular, true


class A(object):
    pass


def test_check_type():
    func = check_type(A)
    a = A()
    func(a)
    assert raises(ValidationError, func, 1)
    func = check_type((dict, list))
    assert raises(ValidationError, func, (1, 2))
    func([1, 2])
    func({'a': 1})


def test_nonsingular():
    assert raises(ValidationError, nonsingular, [[0, 0], [0, 0]])
    nonsingular([[0, 1], [1, 0]])


def test_broadcastable():
    data = {'a': np.random.random((2, 1)),
            'b': np.random.random((3, 1)),
            'c': 3}
    func = broadcastable('a', 'b')
    assert raises(ValidationError, func, data)
    func = broadcastable('a', 'c')
    func(data)


def test_has():
    data = pd.DataFrame({'a': [1, 2, 3, 4, 5],
                         'b': [1, 2, 3, 4, 5],
                         'c': [1, 2, 3, 4, 5]})
    func = has('a', 'b')
    func(data)
    func = has('a', 'dd')
    assert raises(ValidationError, func, data)


def test_dict_validator():
    good_dict = {'a': 1, 'b': 2, 'c': [1, 2, 3, 4]}
    bad_dict = {'a': 1, 'c': [1, 2, 3, 4]}
    validators = dict(b=lambda x: true(x is not None, "must be present"))
    func = dict_validator(validators)
    func(good_dict)
    assert raises(ValidationError, func, bad_dict)
