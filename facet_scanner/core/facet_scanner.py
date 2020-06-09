# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '01 May 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from facet_scanner.collection_handlers.util import FacetFactory
import logging

logger = logging.getLogger(__name__)


class FacetScanner:

    def __init__(self):
        self.handler_factory = FacetFactory()

    def get_handler(self, path, **kwargs):
        """
        Get the correct handler for the given path
        :param path:
        :param kwargs:
        :return:
        """
        handler, collection_root = self.handler_factory.get_handler(path)

        # Handle situation where handler not found
        if handler is None:
            logger.error(f'Unable to find a handler for: {path} in facet_scanner.collection_handlers.util.collection_map.'
                         ' Update mapping file')

        return handler(collection_root=collection_root, **kwargs)

    def get_collection(self, path):
        """
        Take a file path and return the top level collection file path as defined in the collection map
        :param path: input filepath
        :return: top level collection path
        """
        collection_details, collection_path = self.handler_factory.get_collection_map(path)

        return collection_path