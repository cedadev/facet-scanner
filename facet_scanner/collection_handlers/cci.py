# encoding: utf-8
"""
Handler to generate facets for the CCI project
"""
__author__ = 'Richard Smith'
__date__ = '30 Apr 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from facet_scanner.collection_handlers.base import CollectionHandler
import os
from cci_tagger.tagger import ProcessDatasets
from cci_tagger.constants import PROCESSING_LEVEL


class CCI(CollectionHandler):
    """
    """

    project_name = 'opensearch'

    extensions = ['.nc']

    filters = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vocab_file = self.conf.get('cci', 'vocab_file')

        self.pds = ProcessDatasets(suppress_file_output=True, filepath=vocab_file)

    def get_facets(self, path):
        """
        Extract the facets from the file path
        :param path: File path
        :return: Dict  Facet:value pairs
        """

        facets = {}

        # Extract facets from the filename
        drs, tags = self.pds._parse_file_name(os.path.dirname(path), path)
        facets.update(drs)


        # Extract facets from the file
        drs, tags = self.pds._scan_net_cdf_file(path, os.path.dirname(path), tags.get(PROCESSING_LEVEL))
        facets.update(drs)

        return facets
