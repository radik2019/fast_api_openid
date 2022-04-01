from loguru import logger
from functools import wraps



def dbg(*args):
    for i in args: logger.debug(f"\n\n\n{i}\n\n\n")


def dbg_func(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        logger.debug(f"Calling: <{func.__qualname__}> with params: {args} and {kwargs} --->> {output}")
        return output
    return wrapper
