# encoding: utf-8
"""
Handler to generate facets for the CMIP5 project
"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from cci_facet_scanner.collection_handlers.base import CollectionHandler
import os
import logging

from cci_facet_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

class CMIP5(CollectionHandler):
    project_name = 'opensearch'
    keys = ['project', 'product', 'institute',
            'model', 'experiment', 'timeFrequency',
            'realm', 'cmipTable', 'ensemble',
            'version', 'variable'
            ]
    extensions = ['.nc']

    filters = [
        {
            "match": {
                "info.directory.analyzed": "derived"
            }
        },
        {
            "match": {
                "info.directory.analyzed": "retracted"
            }
        },
        {
            "match": {
                "info.directory.analyzed": "mnj_wrk"
            }
        },
        {
            "match": {
                "info.directory.analyzed": "obsolete"
            }
        }
    ]

    def get_facets(self, path):
        """
        Extract the facets from the file path
        :param path: File path
        :return: Dict  Facet:value pairs
        """

        facets = {}

        # Turn filepath into directory
        dir_path = os.path.dirname(path)

        path_components = path.split('/')

        for segment, key in zip(path_components[4:], self.keys):
            facets[key] = segment

        return facets


