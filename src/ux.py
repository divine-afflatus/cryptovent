#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
import gzip
import math
import io
import os
from clint.textui import progress
import codecs
from recordtype import recordtype


class SaveFilePos(object):
    __slots__ = ['saved_position', 'file_handle', 'should_reset']

    def __enter__(self):
        self.saved_position = self.file_handle.tell()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.should_reset:
            self.file_handle.seek(self.saved_position)

        # Not suppressing exceptions.
        return False

    def __init__(self, file_handle, should_reset=True):
        self.file_handle = file_handle
        self.should_reset = should_reset
        self.saved_position = None


def file_size(file_handle, reset_pos=True):
    """Returns the file size."""
    with SaveFilePos(file_handle, reset_pos):
        file_handle.seek(0, 2)
        return file_handle.tell()


def get_file_object(file_handle):
    """Returns the underlying file object."""
    while True:
        if isinstance(file_handle, gzip.GzipFile):
            file_handle = file_handle.myfileobj
        else:
            break
    return file_handle


LineLengthStats = recordtype(
    'LineLengthStats',
    ['count', 'sum', 'sum_of_squares'])
FileStats = recordtype(
    'FileStats',
    ['is_compressed',
     'underlying_file_size',
     'compressed_read_count',
     'decompressed_read_count'])


class CountIO(io.IOBase):
    def __init__(self, base):
        self.base = base
        self.base0 = get_file_object(base)

        self.last_line_extra = 0

        self.line_stats = LineLengthStats(
            count=0,
            sum=0,
            sum_of_squares=0)

        self.file_stats = FileStats(
            is_compressed=isinstance(base, gzip.GzipFile),
            underlying_file_size=file_size(self.base0),
            compressed_read_count=0,
            decompressed_read_count=0)

    def close(self):
        self.base.close()

    @property
    def closed(self):
        return self.base.closed

    def fileno(self):
        return self.base.fileno()

    def flush(self):
        self.base.flush()

    def isatty(self):
        return self.base.isatty

    def readable(self):
        return self.base.readable

    def writeable(self):
        return False

    def seekable(self):
        return False

    def update_stats(self, real_read, data):
        self.file_stats.compressed_read_count += real_read

        if data is not None:
            self.file_stats.decompressed_read_count += len(data)

            for char in data:
                self.last_line_extra += 1

                if char == '\n':
                    length = self.last_line_extra
                    self.line_stats.count += 1
                    self.line_stats.sum += length
                    self.line_stats.sum_of_squares += length * length
                    self.last_line_extra = 0

    def readline(self, limit=-1):
        pos0 = self.base0.tell()

        result = None
        try:
            result = self.base.readline(limit)
            return result
        finally:
            self.update_stats(self.base0.tell() - pos0, result)

    def read(self, limit=-1):
        pos0 = self.base0.tell()

        result = None
        try:
            result = self.base.read(limit)
            return result
        finally:
            self.update_stats(self.base0.tell() - pos0, result)

    @property
    def size(self):
        if not self.file_stats.is_compressed:
            return self.file_stats.underlying_file_size

        if self.file_stats.compressed_read_count == 0:
            return self.underlying_file_size

        compression_ratio = self.file_stats.decompressed_read_count / \
            self.file_stats.compressed_read_count
        return int(compression_ratio * self.file_stats.underlying_file_size)

    @property
    def line_count(self):
        if self.line_stats.count == 0:
            return 1

        line_length = self.line_stats.sum / self.line_stats.count
        return self.size / line_length


def read_file(path):
    _, ext = os.path.splitext(path)

    if ext == '.gz':
        return gzip.open(path, 'rb')
    else:
        return open(path, 'rb')


def line_reader(path, label='', width=32, hide=None, every=100, codec='utf-8',
                skip_empty=False):
    if label is None:
        label = path

    input_file = read_file(path)
    counter = CountIO(input_file)
    reader = codecs.iterdecode(counter, codec) \
        if codec is not None else counter

    with progress.Bar(label=label, width=width, hide=hide, every=every,
                      expected_size=counter.line_count) as bar:
        for i, line in enumerate(reader):
            bar.show(i + 1, counter.line_count)

            if skip_empty:
                if line.strip() == '':
                    continue

            yield line

    input_file.close()


class BiReader(io.IOBase):
    def __init__(self, base_stream, buffer_size=8196):
        self.base_stream = base_stream
        self.size = file_size(base_stream)
        self.buffer_size = buffer_size

        self.left = ""
        self.focus = 0
        self.center = 0
        self.right = ""

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_CUR:
            offset = self.focus + offset
            whence = io.SEEK_SET
        elif whence == io.SEEK_END:
            offset = self.size + offset
            whence = io.SEEK_SET

        assert whence == io.SEEK_SET
        assert 0 <= offset <= self.size

        buf_left = self.center - len(self.left)
        buf_right = self.center + len(self.right)

        if buf_left <= offset <= buf_right:
            self.focus = offset
        else:
            self.base_stream.seek(offset, whence)
            self.focus = offset

            self.right = ""
            self.left = ""
            self.center = offset

    def tell(self):
        return self.focus

    def _position(self, bias=1):
        pos = self.focus - self.center

        buf = 0
        if pos > 0 or (pos == 0 and bias == 1):
            buf = 1
            assert 0 <= pos <= len(self.right)
        elif pos < 0 or (pos == 0 and bias == -1):
            buf = -1
            pos += len(self.left)
            assert 0 <= pos <= len(self.left)

        return (buf, pos)

    def _move_right(self):
        assert self.focus - self.center == len(self.right)

        if self.focus == self.size:
            return False

        self.base_stream.seek(self.focus, 0)

        self.left = self.right if len(self.right) > 0 else self.left
        self.right = self.base_stream.read(self.buffer_size)
        self.center = self.focus

        return True

    def _move_left(self):
        assert self.center - self.focus == len(self.left)

        if self.focus == 0:
            return False

        seek_pos = max(self.focus - self.buffer_size, 0)
        read_size = min(self.focus, self.buffer_size)

        self.base_stream.seek(seek_pos, 0)

        self.right = self.left if len(self.left) > 0 else self.right
        self.left = self.base_stream.read(read_size)
        self.center = self.focus

        return True

    def readr(self, limit=-1):
        if limit == -1:
            limit = self.size - self.focus

        result = ""

        while limit > 0:
            buf, pos = self._position(bias=1)

            if buf == 1 and pos < len(self.right):
                length = min(len(self.right) - pos, limit)
                result += self.right[pos:pos+length]
                limit, self.focus = limit - length, self.focus + length
            elif buf == -1:
                length = min(len(self.left) - pos, limit)
                result += self.left[pos:pos+length]
                limit, self.focus = limit - length, self.focus + length
            elif buf == 1 and pos == len(self.right):
                if not self._move_right():
                    break

        assert(limit >= 0)
        return result

    def readliner(self, limit=-1):
        if limit == -1:
            limit = self.size - self.focus

        result = ""

        while limit > 0:
            buf, pos = self._position(bias=1)

            if buf == 1 and pos < len(self.right):
                length = min(len(self.right) - pos, limit)

                index = self.right.find('\n', pos)
                if index != -1:
                    length = min(length, index + 1 - pos)

                result += self.right[pos:pos+length]
                limit, self.focus = limit - length, self.focus + length

                if index != -1:
                    break
            elif buf == -1:
                length = min(len(self.left) - pos, limit)

                index = self.left.find('\n', pos)
                if index != -1:
                    length = min(length, index + 1 - pos)

                result += self.left[pos:pos+length]
                limit, self.focus = limit - length, self.focus + length

                if index != -1:
                    break
            elif buf == 1 and pos == len(self.right):
                if not self._move_right():
                    break

        assert(limit >= 0)
        return result

    def readl(self, limit=-1):
        if limit == -1:
            limit = self.focus

        result = ""

        while limit > 0:
            buf, pos = self._position(bias=-1)

            if buf == -1 and pos > 0:
                length = min(pos, limit)
                result = self.left[pos-length:pos] + result
                limit, self.focus = limit - length, self.focus - length
            elif buf == 1:
                length = min(pos, limit)
                result = self.right[pos-length:pos] + result
                limit, self.focus = limit - length, self.focus - length
            elif buf == -1 and pos == 0:
                if not self._move_left():
                    break

        assert(limit >= 0)
        return result

    def readlinel(self, limit=-1, greedy=True):
        if limit == -1:
            limit = self.focus

        result = ""

        while limit > 0:
            buf, pos = self._position(bias=-1)

            if buf == -1 and pos > 0:
                length = min(pos, limit)

                index = 0
                if len(result) == 0 and self.left[pos - 1] == '\n' and greedy:
                    index = self.left.rfind('\n', 0, pos - 1)
                else:
                    index = self.left.rfind('\n', 0, pos)

                if index != -1:
                    length = min(length, pos - (index + 1))

                result = self.left[pos-length:pos] + result
                limit, self.focus = limit - length, self.focus - length

                if index != -1:
                    break
            elif buf == 1:
                length = min(pos, limit)

                index = 0
                if len(result) == 0 and self.right[pos - 1] == '\n' and greedy:
                    index = self.right.rfind('\n', 0, pos - 1)
                else:
                    index = self.right.rfind('\n', 0, pos)

                if index != -1:
                    length = min(length, pos - (index + 1))

                result = self.right[pos-length:pos] + result
                limit, self.focus = limit - length, self.focus - length

                if index != -1:
                    break
            elif buf == -1 and pos == 0:
                if not self._move_left():
                    break

        assert(limit >= 0)
        return result

    def read(self, limit=-1):
        return self.readr(limit)

    def readline(self, limit=-1):
        return self.readliner(limit)

    def close(self):
        self.base.close()

    @property
    def closed(self):
        return self.base.closed

    def fileno(self):
        return self.base.fileno()

    def flush(self):
        self.base.flush()

    def isatty(self):
        return self.base.isatty

    def readable(self):
        return self.base.readable

    def writeable(self):
        return False

    def seekable(self):
        return self.base.seekable

    def eof(self):
        return self.focus == self.size


class BiReaderSearch(object):
    def __init__(self, reader, key_func):
        self.reader = reader
        self.key_func = key_func

        with SaveFilePos(self.reader):
            self.reader.seek(0, io.SEEK_SET)
            self.first = (0, self.key_func(self.reader.readliner()))

            self.reader.seek(0, io.SEEK_END)
            line = self.reader.readlinel()
            self.last = (self.reader.tell(), self.key_func(line))

    def _read_key(self):
        pos = self.reader.tell()
        key = self.key_func(self.reader.readliner())
        return pos, key

    def linearr(self, key):
        _, last_key = self._read_key()
        assert last_key < key

        while True:
            if self.reader.eof():
                return

            current, current_key = self._read_key()

            if current_key >= key:
                self.reader.seek(current)
                return

    def binaryr(self, key):
        left = self.first[0]
        left_key = self.first[1]
        right = self.last[0]
        right_key = self.last[1]

        # Invariant: left_key < key <= right_key
        if not (left_key < key):
            self.reader.seek(0, io.SEEK_SET)
            return
        elif not (key <= right_key):
            self.reader.seek(0, io.SEEK_END)
            return

        while True:
            assert left_key < key <= right_key

            middle = (left + right) // 2
            self.reader.seek(middle)
            self.reader.readlinel(greedy=False)
            middle = self.reader.tell()

            if middle == left:
                return self.linearr(key)

            middle_key = self.key_func(self.reader.readliner())
            if middle_key < key:
                left = middle
                left_key = middle_key
            elif key <= middle_key:
                right = middle
                right_key = middle_key
            else:
                assert False, "Should be unreachable."


def estimate_compression_ratio(input_file, max_error=0.001, probability=0.999,
                               buf_size=1 * 1024 * 1024,
                               bootstrap=16 * 1024 * 1024,
                               reset_pos=True):
    if not isinstance(input_file, gzip.GzipFile):
        raise ValueError("gzip_file")

    with SaveFilePos(input_file, reset_pos):
        input_file.seek(0)

        initial_pos = input_file.myfileobj.tell()
        compressed = 0
        decompressed = 0
        ratio = 0
        k = 1 / math.sqrt(1 - probability)

        try:
            while True:
                decompressed += len(input_file.read(buf_size))
                compressed = input_file.myfileobj.tell() - initial_pos
                ratio = compressed / decompressed
                err = k * ratio * (1 - ratio) / decompressed
                if err <= max_error and decompressed >= bootstrap:
                    return ratio
        except EOFError:
            return compressed / decompressed


def estimate_file_size(input_file, max_error=0.001, probability=0.999,
                       reset_pos=True):
    with SaveFilePos(input_file, reset_pos):
        if isinstance(input_file, gzip.GzipFile):
            size = file_size(input_file.myfileobj)
            ratio = estimate_compression_ratio(
                input_file, max_error, probability, reset_pos=False)
            return int(size / ratio)
        else:
            return file_size(input_file, reset_pos=False)


def estimate_line_length(input_file, max_error=0.001, probability=0.999,
                         bootstrap_lines=100000,
                         reset_pos=True):
    with SaveFilePos(input_file, reset_pos):
        input_file.seek(0)

        stats = LineLengthStats(0, 0, 0)
        k = 1 / math.sqrt(1 - probability)

        for i, line in enumerate(input_file):
            line_length = len(line)
            stats.count += 1
            stats.sum += line_length
            stats.sum_of_squares += line_length * line_length

            if i < bootstrap_lines:
                continue

            variance = stats.sum_of_squares / stats.count - \
                (stats.sum / stats.count)**2
            sigma_squared = variance / stats.count
            if k * sigma_squared < max_error:
                return stats.sum / stats.count

        return 0 if stats.sum == 0 else stats.sum / stats.count


def estimate_line_count(input_file, max_error=0.001, probability=0.999,
                        bootstrap_lines=10000, reset_pos=True):
    with SaveFilePos(input_file, reset_pos):
        input_file.seek(0)

        e0 = max_error / 2
        p0 = 1 - math.sqrt(1 - probability)

        size = estimate_file_size(input_file, max_error=e0, probability=p0)
        line_len = estimate_line_length(input_file, max_error=e0,
                                        probability=p0,
                                        bootstrap_lines=bootstrap_lines,
                                        reset_pos=False)
        return int(size / line_len)
