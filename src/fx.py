#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools


chain = itertools.chain
empty = iter([])


def peek(iterable, n=1):
    if n <= 0:
        return iterable

    iterable = iter(iterable)

    elements = []
    try:
        for i in xrange(n):
            elements.append(iterable.next())
    except:
        return elements[:], iter(elements)
    else:
        return elements[:], chain(iter(elements), iterable)


def groupby(iterable, keyfunc):
    """
    >>> groupby(['abc', 'acd', 'dsa', 'dw', 'd', 'k'], lambda w: w[0])
    ... # doctest: +NORMALIZE_WHITESPACE
    {'a': ['abc', 'acd'], 'k': ['k'], 'd': ['dsa', 'dw', 'd']}
    """
    result = {}
    for value in iterable:
        key = keyfunc(value)
        if key not in result:
            result[key] = []
        result[key].append(value)
    return result


def countwhile(list, predicate):
    for i, v in enumerate(list):
        if not predicate(v):
            return i
    return len(list)


def windowdiffs(sorted_iterable, key_func,
                window_size,
                window_step=None,
                window_start=None):
    """
    >>> list(windowdiffs([0, 1, 1, 2, 2, 2.4, 2.9, 3.5,
    ...                   4, 4.1, 4.2, 4.3, 5], lambda k: k, 2, 1))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(0, 2, 0, [0, 1, 1]),
     (1, 3, 1, [2, 2, 2.4, 2.9]),
     (2, 4, 2, [3.5]),
     (3, 5, 4, [4, 4.1, 4.2, 4.3]),
     (4, 6, 1, [5])]
    """
    values = iter(sorted_iterable)

    old_keys = []
    new_keys = []
    new_values = []

    # If window_step is not specified, assume that
    # the step is equal to the size.
    if window_step is None:
        window_step = window_size

    # If window_start is not specified, assume that
    # we start with the first item.
    if window_start is None:
        new_values.append(values.next())
        window_start = key_func(new_values[0])
        new_keys.append(window_start)

    for value in values:
        key = key_func(value)

        if key < window_start + window_size:
            new_keys.append(key)
            new_values.append(value)
            continue

        while key >= window_start + window_size:
            new_window_start = window_start + window_step

            remove = countwhile(old_keys, lambda k: k < window_start)
            del old_keys[:remove]
            old_keys.extend(new_keys)

            yield (window_start, window_start + window_size,
                   remove, new_values)

            new_keys = []
            new_values = []
            window_start = new_window_start

        new_keys.append(key)
        new_values.append(value)

    remove = countwhile(old_keys, lambda k: k < window_start)
    yield (window_start, window_start + window_size,
           remove, new_values)


def windows(sorted_iterable, key_func,
            window_size,
            window_step=None,
            window_start=None):
    """
    >>> list(windows([0, 1, 1, 2, 2, 2.4, 2.9, 3.5,
    ...               4, 4.1, 4.2, 4.3, 5], lambda k: k, 2, 1))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(0, 2, [0, 1, 1]),
     (1, 3, [1, 1, 2, 2, 2.4, 2.9]),
     (2, 4, [2, 2, 2.4, 2.9, 3.5]),
     (3, 5, [3.5, 4, 4.1, 4.2, 4.3]),
     (4, 6, [4, 4.1, 4.2, 4.3, 5])]
    """
    diffs = windowdiffs(sorted_iterable, key_func,
                        window_size, window_step, window_start)

    items = []
    for t0, t1, remove, add in diffs:
        del items[:remove]
        items += add
        yield (t0, t1, items[:])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
