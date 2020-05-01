# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from pydoc import locate
from .collection_map import COLLECTION_MAP
import os


class FacetFactory:

    def __init__(self):
        self.map = COLLECTION_MAP

    def get_handler(self, path):
        """
        Takes a system path and returns the file extensions to look for and
        the correct handler for the collection.

        :param path:
        :return: granule extension, handler class
        """

        collection_details, collection_path = self.get_collection_map(path)
        if collection_details is not None:
            return locate(collection_details['handler']), collection_path

    def get_collection_map(self, path):
        """
        Takes an arbitrary path and returns a collection path
        :param path: Path to the data of interest
        :return: The value from the map object
        """

        if not path.endswith('/'):
            path += '/'

        while path not in self.map and path != '/':
            path = os.path.dirname(path)

        # No match has been found
        if path == '/':
            return None, None

        return self.map[path], path

