# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '29 May 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import sys
import itertools
from collections import OrderedDict
import logging

from cci_facet_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """

    # If the programme is being run non-interactively, assume true
    if not sys.stdin.isatty():
        return True

    valid = {'yes': True, 'y': True,
             'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError(f'invalid default answer: "{default}"')

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write('Please respond with "yes" or "no" '
                             '(or "y" or "n").\n')


def generator_grouper(n, it):
    """
    Slices an iterator into smaller iterators of length n

    :param n: Number of items to return
    :param it: Generator
    :return: Returns an iterator of n items
    """

    while True:
        chunk_it = itertools.islice(it, n)

        # Check if we have reached the end of the iterator
        try:
            first_element = next(chunk_it)
        except StopIteration:
            return

        # Join the first element back onto the next n elements
        yield itertools.chain((first_element,), chunk_it)


def split_outside_quotes(s, delim):
    """
    Split a string s by character delim, but only when delim is not enclosed
    in double quotes.

    Return a list of the split parts (including quotes if present)
    """
    parts = []
    in_quotes = False
    temp = ""

    for char in s:
        if not in_quotes and char == delim:
            parts.append(temp)
            temp = ""
            continue

        temp += char
        if char == '"':
            in_quotes = not in_quotes

    if temp:
        parts.append(temp)
    return parts


def remove_quotes(s):
    """
    Return a string s with enclosing double quotes removed.
    """
    if not s.startswith('"') or not s.endswith('"'):
        raise ValueError("String '{}' is not wrapped in quotes".format(s))
    return s[1:-1]


def parse_key(key):
    """
    Convert a bucket key from the ES aggregation response to a dictionary.
    The format is as follows:
        - All keys and values are enclosed in double quotes (")
        - key-value pairs are separated by ','
        - key and value are separated by ':'
        - if key is 'names' then value is a list separated with ';'
    """
    err_msg = "Invalid key '{}'".format(key)

    d = {}
    pairs = split_outside_quotes(key, ",")
    for pair in pairs:

        try:
            label, val_str = split_outside_quotes(pair, ":")
        except ValueError:
            raise ValueError("{}: must be exactly 1 colon in key-value pair".format(err_msg))

        try:
            label = remove_quotes(label)
            # Split val_str by ; to get list of values, remove quotes for each,
            # and filter out empty values
            val_list = [_f for _f in map(remove_quotes, split_outside_quotes(val_str, ";")) if _f]

        except ValueError as ex:
            raise ValueError("{}: {}".format(err_msg, ex))

        if label == "names":
            # Remove any duplicate names; can't use set() as we need
            # to preserve the order for later comparison with CMMS content
            # otherwise, if we use 'names' in the future as the display name
            # this might alter
            val_list = list(OrderedDict((x, True) for x in val_list).keys())

            d[label] = val_list
        else:
            if len(val_list) > 1:
                raise ValueError("{}: only 'names' can contains multiple values".format(err_msg))
            if not val_list:
                continue
            d[label] = val_list[0]
    return d


class Singleton(type):
    _instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is  None:
            self._instance = super().__call__(*args, **kwargs)

        return self._instance
