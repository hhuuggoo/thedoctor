from . import ValidationError, _postprocess, _dict_validate
def check_type(types):
    """Returns a function that checks whether an object matches types
    """
    def checktype(x):
        if not isinstance(x, types):
            raise ValidationError("Not a member of %s", str(types))
    return checktype

def true(val, message):
    """returns a function which returns a validation error with message
    if func returns False
    """
    if not val:
        raise ValidationError(message)

def broadcastable(*names):
    """returns a function - this function takes a dict of args
    (should be used in _all validator)
    asserts that every array in that list is broadcastable
    """
    ## todo - do we check whether these are numpy objs first?
    ## cause you can write numpy funcs on lists sometimes
    import numpy as np
    def _broadcastable(all_args):
        arrs = [all_args[x] for x in names]
        try:
            np.broadcast(*arrs)
        except ValueError as e:
            raise ValidationError("Cannot broadcast %s with shapes %s",
                                  names,
                                  [getattr(x, 'shape', 'no shape') for x in arrs])
    return _broadcastable

def nonsingular(matrix):
    """checks whether a matrix is singular
    """
    import numpy as np
    if np.linalg.matrix_rank(matrix) == 0:
        raise ValidationError("Matrix is singular")

def has(*names):
    """checks whether a dict or dataframe has certain fields (names)
    """
    def _has(obj):
        for n in names:
            if n not in obj:
                raise ValidationError("Value missing %s field", n)
    return _has

def dict_validator(validators):
    for k in validators.keys():
        validators[k] = _postprocess(validators[k])
    msg = "Error validating key: %s, value: %s"
    def _dict_validator(input_dict):
        _dict_validate(validators, input_dict, msg)
    return _dict_validator
