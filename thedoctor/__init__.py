from functools import wraps
import inspect
import warnings

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

def validate(**validators):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            #validate here
            return func(*args, **kwargs)
        return wrapper
    return decorator
