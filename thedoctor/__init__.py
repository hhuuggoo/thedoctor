import inspect
import logging
import os
import warnings
from functools import wraps


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def arg_dict(func, args, kwargs):
    """Given a function and the args/kwargs that it is called with,
    construct the dictionary mapping arument names to argument values
    """

    skip_validation = \
        "skipping validation, %s will throw an exception" % func.__name__
    all_args = {}
    arg_names, vararg_name, keyword_name, defaults = inspect.getargspec(func)
    arg_names_set = set(arg_names)
    for name, value in zip(arg_names, args):
        all_args[name] = value
    # handle keyword arguments
    for name, value in kwargs.items():
        if name in all_args:
            warnings.warn("duplicate value for %s" % name)
            warnings.warn(skip_validation)
            return None

        if name not in arg_names_set and not keyword_name:
            warnings.warn("function does not take parameter %s" % name)
            warnings.warn(skip_validation)
            return None
        if name not in arg_names_set and keyword_name:
            continue
        all_args[name] = value

    # populate defaults
    if defaults is not None:
        for name, value in zip(arg_names[-len(defaults):], defaults):
            if name not in all_args:
                all_args[name] = value

    if len(args) > len(arg_names) and not vararg_name:
        warnings.warn("improper number of args")
        warnings.warn(skip_validation)
        return

    if set(all_args.keys()) != arg_names_set:
        warnings.warn("improper number of args")
        warnings.warn(skip_validation)
        return

    # handle *args
    if vararg_name:
        varargs = args[len(arg_names):]
        all_args[vararg_name] = varargs

    # handle **kwargs
    if keyword_name:
        kw_args = {}
        for k, v in kwargs.items():
            if k not in all_args:
                kw_args[k] = v
        all_args[keyword_name] = kw_args

    return all_args


def _postprocess(obj):
    """We support convenient ways of specifying dependencies.
    field=[func1, func2, func3]
    field=(type1, type2)
    field = [(type1, type2), func2]
    field=func1
    this function converts all specifications of deps into a list of functions
    """
    from .validators import check_type
    if not isinstance(obj, list):
        obj = [obj]
    callbacks = []
    for spec in obj:
        if hasattr(spec, '__call__') and not isinstance(spec, type):
            callbacks.append(spec)
            continue
        if isinstance(spec, (tuple, type)):
            callbacks.append(check_type(spec))
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

        @wraps(func)
        def wrapper(*args, **kwargs):
            all_args = arg_dict(func, args, kwargs)
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
