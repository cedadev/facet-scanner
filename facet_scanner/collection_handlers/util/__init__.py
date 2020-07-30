# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from .facet_factory import FacetFactory
from .moles_datasets import CatalogueDatasets
from hashlib import sha1


def generate_id(string):
    """
    Generate sha1 hash of string
    :param string: input string
    :return: hex string
    """

    return sha1(string.encode('utf-8')).hexdigest()