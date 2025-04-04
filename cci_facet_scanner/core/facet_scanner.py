# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '01 May 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from cci_facet_scanner.collection_handlers.utils import FacetFactory
import logging
from typing import Union

from cci_facet_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False


class FacetScanner:
    """
    Base class for the facet scanner
    """

    def __init__(self, ontology_local: Union[str,None] = None):

        self._ontology_local = ontology_local
        self.handler_factory = FacetFactory()

    def get_handler(self, path, api_key: Union[str,None] = None,**kwargs):
        """
        Get the correct handler for the given path

        :param path: Filepath
        :type path: str
        :param kwargs:

        :return: Mapped collection handler
        :rtype: CollectionHandler
        """
        logger.debug("Obtaining handler")
        handler, collection_root = self.handler_factory.get_handler(path)

        logger.debug('Handler Obtainment complete')
        # Handle situation where handler not found
        if handler is None:
            logger.error(f'Unable to find a handler for: {path} in cci_facet_scanner.collection_handlers.utils.collection_map.'
                         ' Update mapping file')

        return handler(
            collection_root=collection_root, 
            ontology_local=self._ontology_local,
            api_key=api_key,
            **kwargs)

    def get_collection(self, path):
        """
        Take a file path and return the top level collection file path as defined in the collection map

        :param path: input filepath
        :type path: str

        :return: top level collection path
        :rtype: str
        """
        collection_details, collection_path = self.handler_factory.get_collection_map(path)

        return collection_path