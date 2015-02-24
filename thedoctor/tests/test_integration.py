from .. import validate
from .utils import raises
from .. import ValidationError
from ..validators import true

def test_integration():
    @validate(a=int, b=int)
    def func(a,b):
        return (a,b)
    assert func(1,2) == (1,2)
    assert raises(ValidationError, func, 1, 'a')

    @validate(a=int)
    def func(a,b):
        return (a,b)
    assert func(1,'a') == (1,'a')
    assert raises(ValidationError, func, 'a', 1)

def test_return_validator():
    def return_validator(result):
        if result != 3:
            raise ValidationError('not 3')
    @validate(_return=[int, return_validator])
    def func(a,b):
        return a + b
    assert raises(ValidationError, func, 1, 3)
    assert raises(ValidationError, func, 'a', 'b')
    assert func(1, 2) == 3

    def sums_to_3(all_args):
        if all_args['a'] + all_args['b'] != 3:
            raise ValidationError('not sum to 3')
    @validate(_all=sums_to_3)
    def func(a,b):
        return a + b
    assert raises(ValidationError, func, 1, 3)
    assert func(1, 2) == 3


def test_lambda_validator():
    @validate(_all=true(lambda x : x['a'] + x['b'] == 3, "must sum to 3"))
    def func(a,b):
        return a + b
    assert raises(ValidationError, func, 1, 3)
    assert func(1, 2) == 3
