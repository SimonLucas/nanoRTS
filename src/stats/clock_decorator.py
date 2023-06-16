import time
from functools import wraps


def clock(func):
    @wraps(func)
    def clocked(*args):
        t0 = time.time()
        result = func(*args)
        elapsed = time.time() - t0
        name = func.__name__
        arg_str = ', '.join(repr(arg) for arg in args)
        print('[%0.8fs] %s(%s) -> %r' %
              (elapsed, name, arg_str, result))
        return result

    return clocked


# Example use
if __name__ == '__main__':
    @clock
    def snooze(seconds):
        time.sleep(seconds)


    for i in range(3):
        snooze(.123)
