#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import pytz
from tzlocal import get_localzone

utc = pytz.utc
local = get_localzone()


def tz(name):
    """Returns a tzinfo object with the given name."""
    if name == 'utc':
        return pytz.utc
    elif name == 'local':
        return get_localzone()
    else:
        return pytz.timezone(name)


def ts(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    """
    >>> ts(year=1970, month=1, day=1)
    0.0

    >>> ts(year=2011, month=5, day=31, hour=19, minute=0, second=1)
    1306868401.0
    """
    t0 = time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))
    t1 = time.mktime((year, month, day, hour,
                      minute, second, microsecond,
                      0, 0))
    return t1 - t0


def dt(days=0, hours=0, minutes=0, seconds=0, miliseconds=0, microseconds=0):
    """
    >>> dt(days=2, hours=1, minutes=30, seconds=12, miliseconds=32,
    ...    microseconds=123)
    178212.032123

    >>> dt(minutes=2, seconds=66) == 2 * 60 + 66
    True
    """
    hours += days * 24
    minutes += hours * 60
    seconds += minutes * 60

    microseconds += miliseconds * 1000
    seconds += microseconds / 1e6

    return seconds


def now():
    """
    >>> now() # doctest: +SKIP
    1425131462.31405
    """
    return time.time()


def strptime(text, format, timezone):
    if isinstance(timezone, str):
        timezone = tz(timezone)
    elif not isinstance(timezone, datetime.tzinfo):
        raise ValueError("Unknown timezone.")

    dt = datetime.datetime.strptime(text, format)
    return datetime_to_timestamp(dt, timezone)


def strftime(timestamp, format, timezone):
    if isinstance(timezone, str):
        timezone = tz(timezone)
    elif not isinstance(timezone, datetime.tzinfo):
        raise ValueError("Unknown timezone.")

    dt = timestamp_to_datetime(timestamp, timezone)
    return dt.strftime(format)


def datetime_to_timestamp(dt, timezone=None):
    """Converts a datetime object to UTC timestamp"""

    if dt.tzinfo is None:
        if isinstance(timezone, str):
            timezone = tz(timezone)
        dt = dt.replace(tzinfo=timezone)

    t0 = time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))
    t1 = time.mktime(dt.utctimetuple())
    return t1 - t0


def timestamp_to_datetime(ts, timezone):
    if isinstance(timezone, str):
        timezone = tz(timezone)
    elif not isinstance(timezone, datetime.tzinfo):
        raise ValueError("Unknown timezone.")

    return datetime.datetime.fromtimestamp(ts, timezone)


def now_datetime(timezone):
    if isinstance(timezone, str):
        timezone = tz(timezone)
    elif not isinstance(timezone, datetime.tzinfo):
        raise ValueError("Unknown timezone.")

    return datetime.datetime.fromtimestamp(time.time(), timezone)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
