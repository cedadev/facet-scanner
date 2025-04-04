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
from typing import Optional, Tuple
from cci_facet_scanner.collection_handlers.base import CollectionHandler
import logging

from cci_facet_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

class FacetFactory:
    """
    Factory Class to return the correct collection handler based on the
    given filepath.
    """

    def __init__(self):
        self.map = COLLECTION_MAP

    def get_collection_map(self, path):
        """
        Takes an arbitrary path and returns a collection path

        :param path: Path to the data of interest
        :type path: str
        :return: The value from the map object
        :rtype: str, str
        """

        if not path.endswith('/'):
            path += '/'

        while path not in self.map and path != '/':
            path = os.path.dirname(path)

        # No match has been found
        if path == '/':
            return None, None

        return self.map[path], path

    def get_handler(self, path: str) -> Tuple[Optional[CollectionHandler], Optional[str]]:
        """
        Takes a system path and returns the correct handler for the collection.

        :param path: Filepath
        :type path: str

        :return: handler class, collection path
        :rtype: CollectionHandler, str
        """

        logger.debug('Locating collection details')
        collection_details, collection_path = self.get_collection_map(path)
        if collection_details is not None:
            return locate(collection_details['handler']), collection_path

        return None, None
