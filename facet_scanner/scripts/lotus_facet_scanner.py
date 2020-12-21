# encoding: utf-8
"""

Lotus Facet Scanner MRO
------------------------

1. facet_scanner.scripts.lotus_facet_scanner.LotusFacetScanner.process_path
2. facet_scanner.core.facet_scanner.FacetScanner.get_handler
3. facet_scanner.collection_handlers.utils.facet_factory.FacetFactory.get_handler
4. facet_scanner.collection_handlers.base.CollectionHandler.update_facets
5. facet_scanner.collection_handlers.base.CollectionHandler._facet_generator
6. facet_scanner.collection_handlers.base.CollectionHandler.get_facets

"""
__author__ = 'Richard Smith'
__date__ = '30 May 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from facet_scanner.scripts.facet_scanner_cmd import FacetExtractor
import argparse
import os
import json


class LotusFacetScanner(FacetExtractor):

    def process_path(self, cmd_args):
        """

        :param cmd_args: Arguments from the command line
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

    @staticmethod
    def _get_command_line_args():
        # Get command line arguments
        parser = argparse.ArgumentParser(description='Process path for facets and update the index')
        parser.add_argument('path', type=str, help='Path to process')
        parser.add_argument('--conf', dest='conf',
                            default=os.path.join(os.path.dirname(__file__), '../conf/facet_scanner.ini'))

        return parser.parse_args()

if __name__ == '__main__':
    LotusFacetScanner.main()