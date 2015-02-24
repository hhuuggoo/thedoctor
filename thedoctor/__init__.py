from functools import wraps
import inspect
import warnings
import logging
import os

logger = logging.getLogger(__name__)
class ValidationError(Exception):
    pass

def arg_dict(func, args, kwargs):
    all_args = {}
    arg_names, vararg_name, keyword_name, defaults = inspect.getargspec(func)
    arg_names_set = set(arg_names)
    for name, value in zip(arg_names, args):
        all_args[name] = value
    #handle keyword arguments
    for name, value in kwargs.items():
        if name in all_args:
            warnings.warn("duplicate value for %s" % name)
            warnings.warn("skipping validation, %s will thrown an exception" % func.__name__)
            return None

        if name not in arg_names_set and not keyword_name:
            warnings.warn("function does not take parameter %s" % name)
            warnings.warn("skipping validation, %s will thrown an exception" % func.__name__)
            return None
        if name not in arg_names_set and keyword_name:
            continue
        all_args[name] = value

    #populate defaults
    if defaults is not None:
        for name, value in zip(arg_names[-len(defaults):], defaults):
            if name not in all_args:
                all_args[name] = value

    if len(args) > len(arg_names) and not vararg_name:
        warnings.warn("improper number of args")
        warnings.warn("skipping validation, %s will thrown an exception" % func.__name__)
        return

    if set(all_args.keys()) != arg_names_set:
        warnings.warn("improper number of args")
        warnings.warn("skipping validation, %s will thrown an exception" % func.__name__)
        return

    #handle *args
    if vararg_name:
        varargs = args[len(arg_names):]
        all_args[vararg_name] = varargs

    #handle **kwargs
    if keyword_name:
        kw_args = {}
        for k,v in kwargs.iteritems():
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

def validate(**validators):
    def passthrough(func):
        return func
    if os.environ.get('NO_DOCTOR'):
        return passthrough

    for k in validators.keys():
        validators[k] = _postprocess(validators[k])
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            all_args = arg_dict(func, args, kwargs)
            if all_args is None:
                #should return an exception
                #all_args is None if the call sig is wrong
                return func(*args, **kwargs)
            all_validator = validators.get('_all', [])
            return_validator = validators.get('_return', [])
            #TODO refactor this func callling code
            for k,v in validators.items():
                if k in {'_all', '_return'}:
                    continue
                for validator in v:
                    try:
                        validator(all_args[k])
                    except ValidationError as e:
                        logger.error("Error validating arg: %s, value: %s, on function %s",
                                     k, niceprint(all_args[k]), func.__name__)
                        logger.exception(e)
                        raise
            for validator in all_validator:
                try:
                    validator(all_args)
                except Exception as e:
                    logger.error("Error validating all args of %s", func.__name__)
                    logger.exception(e)
                    raise
            retval = func(*args, **kwargs)
            for validator in return_validator:
                try:
                    validator(retval)
                except Exception as e:
                    logger.error("Error validating return value of %s", func.__name__)
                    logger.exception(e)
                    raise
            return retval
        return wrapper
    return decorator
