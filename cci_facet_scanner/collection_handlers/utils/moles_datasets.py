# encoding: utf-8
"""
"""
__author__ = 'Richard Smith'
__date__ = '25 Jan 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import os
import requests
from json.decoder import JSONDecodeError
from requests.exceptions import Timeout
import json
import logging

from cci_facet_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

MOLES_MAPPING_FILE = os.environ.get('MOLES_MAPPING_FILE')


class CatalogueDatasets:
    """
    Class to map a filepath to the relate MOLES record

    :param moles_base: Base URL to the MOLES api server (default: http://api.catalogue.ceda.ac.uk).
    :type moles_base: str

    """
    
    def __init__(self, moles_base='http://api.catalogue.ceda.ac.uk'):
        """

        :param moles_base: The base URL for the MOLES API server
        :type moles_base: str
        """

        self.moles_base = moles_base
        
        self.moles_mapping_url = f'{moles_base}/api/v0/obs/all'

        # Try loading the mapping from disk
        if MOLES_MAPPING_FILE:
            with open(MOLES_MAPPING_FILE) as reader:
                self.moles_mapping = json.load(reader)
        else:
            try:
                self.moles_mapping = requests.get(self.moles_mapping_url).json()
            except JSONDecodeError as e:
                import sys
                raise ConnectionError(f'Could not connect to {self.moles_mapping_url} to get moles mapping') from e

    def get_moles_record_metadata(self, path):
        """
        Try and find metadata for a MOLES record associated with the path.

        Example API response::

            {
                "title": "ESA Fire Climate Change Initiative Project  (Fire CCI)",
                "url": "http://catalogue.ceda.ac.uk/uuid/6c3584d985bd484e8beb23ff0df91292",
                "record_type": "Project",
                "record_path": "",
                "publication_state": "published"
            }

        :param path: Directory path
        :type path: str

        :return: Dictionary containing MOLES title, url and record_type
        :rtype: dict
        """

        # Condition path - remove trailing slash
        if path.endswith('/'):
            path = path[:-1]

        # Check for path match in stored dictionary
        test_path = path
        while test_path != '/' and test_path:

            result = self.moles_mapping.get(test_path)

            # Try adding a slash to see if it matches. Some records in MOLES are stored
            # with a slash, others are not
            if not result:
                result = self.moles_mapping.get(test_path + '/')

            if result is not None:
                return result

            # Shrink the path down until a match is found
            test_path = os.path.dirname(test_path)

        # No match has been found
        # Search MOLES API for path match
        url = f'{self.moles_base}/api/v0/obs/get_info{path}'
        try:
            response = requests.get(url, timeout=10)
        except Timeout:
            return {}

        # Update moles mapping
        if response:
            self.moles_mapping[path] = response.json()
            return response.json()

