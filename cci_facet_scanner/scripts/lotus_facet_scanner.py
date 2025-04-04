# encoding: utf-8
"""

Lotus Facet Scanner MRO
------------------------

1. cci_facet_scanner.scripts.lotus_facet_scanner.LotusFacetScanner.process_path
2. cci_facet_scanner.core.facet_scanner.FacetScanner.get_handler
3. cci_facet_scanner.collection_handlers.utils.facet_factory.FacetFactory.get_handler
4. cci_facet_scanner.collection_handlers.base.CollectionHandler.update_facets
5. cci_facet_scanner.collection_handlers.base.CollectionHandler._facet_generator
6. cci_facet_scanner.collection_handlers.base.CollectionHandler.get_facets

"""
__author__ = 'Richard Smith'
__date__ = '30 May 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from cci_facet_scanner.scripts.facet_scanner_cmd import FacetExtractor
import argparse
import os
import json

import logging
from cci_facet_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False


class LotusFacetScanner(FacetExtractor):

    def process_path(self, cmd_args):
        """
        Open the page file, extract the list of file paths and process
        each one to extract the facets.

        :param cmd_args: Arguments from the command line
        :type cmd_args: argparse.Namespace
        """

        # Get first item in processing file to extract path to get handler
        with open(cmd_args.path) as reader:
            first_line = reader.readline()
        dataset_path = json.loads(first_line)['_source']['info']['directory']

        print(f'Dataset path: {dataset_path}')

        print('Getting handler...')
        handler = self.get_handler(dataset_path, headers={'x-api-key': self.es_password}, facet_json=self.facet_json)
        print(handler)

        print('Retrieving facets...')
        handler.update_facets(cmd_args.path, self.index)

        # Remove file once processed
        if os.path.exists(cmd_args.path):
            os.remove(cmd_args.path)
        else:
            print(f'{cmd_args.path} does not exist')

    @staticmethod
    def _get_command_line_args():
        """
        Get the command line arguments and return parsed args
        :return: Parsed args
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(description='Process path for facets and update the index. This script is designed'
                                                     ' to be run as a batch process on lotus')
        parser.add_argument('path', type=str, help='Path to page file for processing')
        parser.add_argument('--conf', dest='conf',
                            default=os.path.join(os.path.dirname(__file__), '../conf/cci_facet_scanner.ini'))

        return parser.parse_args()


if __name__ == '__main__':
    LotusFacetScanner.main()