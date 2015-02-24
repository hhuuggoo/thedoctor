def raises(err, lamda, *args, **kwargs):
    try:
        lamda(*args, **kwargs)
        return False
    except err:
        return True
