import inspect
import logging
import os
import warnings
from functools import wraps


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def _postprocess(obj):
    """We support convenient ways of specifying dependencies.
    field=[func1, func2, func3]
    field=(type1, type2)
    field = [(type1, type2), func2]
    field=func1
    this function converts all specifications of deps into a list of functions
    """
    from .validators import typechecker
    if not isinstance(obj, list):
        obj = [obj]
    callbacks = []
    for spec in obj:
        if hasattr(spec, '__call__') and not isinstance(spec, type):
            callbacks.append(spec)
            continue
        if isinstance(spec, (tuple, type)):
            callbacks.append(typechecker(spec))
        else:
            raise ValidationError("unknown specification %s" % spec)
    return callbacks


def niceprint(obj, limit=1000):
    return str(obj)[:limit]


def run_validate(func, arg, msg, msg_params):
    try:
        func(arg)
    except ValidationError as e:
        logger.error(msg, *msg_params)
        logger.exception(e)
        raise


def _dict_validate(validators, inputs, msg):
    """validators - dict of validator function lists
    msg - logger message, containing 2 %s for k,v
    """
    for k, v in validators.items():
        for validator in v:
            value = inputs.get(k)
            run_validate(validator, value, msg, (k, niceprint(value)))


def validate(**validators):

    def passthrough(func):
        return func
    if os.environ.get('NO_DOCTOR'):
        return passthrough

    for k in validators.keys():
        validators[k] = _postprocess(validators[k])
    all_validator = validators.pop('_all', [])
    return_validator = validators.pop('_return', [])

    def decorator(func):
        dict_error_message = \
            "Error validating arg: %%s, value: %%s, on function %s"
        dict_error_message = dict_error_message % func.__name__
        sig = inspect.signature(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            call = sig.bind(*args, **kwargs)
            call.apply_defaults()
            all_args = call.arguments
            if all_args is None:
                # should return an exception
                # all_args is None if the call sig is wrong
                return func(*args, **kwargs)
            _dict_validate(validators, all_args, dict_error_message)
            for validator in all_validator:
                run_validate(validator, all_args,
                             "Error validating all args of %s",
                             (func.__name__,))
            retval = func(*args, **kwargs)
            for validator in return_validator:
                run_validate(
                    validator, retval,
                    "Error validating return value of %s, on function %s",
                    (niceprint(retval), func.__name__))
            return retval
        return wrapper
    return decorator
