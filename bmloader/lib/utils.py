import functools
import pickle
import errno
import time
import os
import hashlib

def timeit(func):
    def wrapper(*args, **kwrags):
        start = time.time()
        output = func(*args, **kwrags)
        end = time.time()
        print('{} sec'.format(end - start))
        return output

    return wrapper


def ensure_directory(directory):
    directory = os.path.expanduser(directory)
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e


def disk_cache(basename, directory, method=False):
    directory = os.path.expanduser(directory)
    ensure_directory(directory)

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = (args[0]._path, *tuple(args), *tuple(kwargs.items()))
            if method and key:
                key = key[1:]
            hash_input = []
            for k in key:
                if isinstance(k, str):
                    k = int(hashlib.sha1(k.encode('utf-8')).hexdigest(), 16) % (10 ** 8)
                hash_input.append(k)

            filename = '{}-{}.pickle'.format(basename, hash(tuple(hash_input)))
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as handle:
                    return pickle.load(handle)
            result = func(*args, **kwargs)
            with open(filepath, 'wb') as handle:
                pickle.dump(result, handle)
            return result

        return wrapped

    return wrapper
