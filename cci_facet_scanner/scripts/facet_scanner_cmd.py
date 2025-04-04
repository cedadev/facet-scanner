# encoding: utf-8
"""

Facet Scanner CMD MRO
---------------------

1. cci_facet_scanner.scripts.cci_facet_scanner_cmd.FacetExtractor.process_path
2. cci_facet_scanner.core.cci_facet_scanner.FacetScanner.get_handler
3. cci_facet_scanner.collection_handlers.utils.facet_factory.FacetFactory.get_handler
4. cci_facet_scanner.collection_handlers.base.CollectionHandler.export_facets
5. facets_scanner.core.elasticsearch_connection.ElasticsearchConnection.get_query
6. facets_scanner.core.elasticsearch_connection.ElasticsearchConnection.get_hits
7. cci_facet_scanner.collection_handlers.base.CollectionHandler.lotus_submit

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import argparse
import os
from configparser import RawConfigParser
from cci_facet_scanner.utils import query_yes_no
from cci_facet_scanner.core.facet_scanner import FacetScanner
import logging

from cci_facet_scanner import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False


class FacetExtractor(FacetScanner):

    def __init__(self, conf):

        super().__init__()

        self.es_password = conf.get('elasticsearch', 'api_key')
        self.index = conf.get('elasticsearch', 'target_index')
        self.facet_json = conf.get('cci_facet_scanner', 'facet_json', fallback=None)

        print(
            f'Index: {self.index} '
            f'Password: {"*******" if self.es_password is not None else None}'
        )

        query_yes_no('Check the above variables. Ready to continue?')

    def process_path(self, cmd_args):
        """
        Main routine for processing a path from the command line arguments

        :param cmd_args: Arguments from the command line
        :type cmd_args: argparse.Namespace
        """
        print('Getting handler...')
        handler = self.get_handler(cmd_args.path, api_key=self.es_password, facet_json=self.facet_json)

        print('Retrieving facets...')
        handler.export_facets(cmd_args.path, self.index, cmd_args.processing_path, rerun=cmd_args.rerun, batch_size=cmd_args.num_files)

        # try:
        #     handler.export_collections(cmd_args.path)
        # except NotImplementedError:
        #     print(f'Collection generator not implemented for {handler}')

    @staticmethod
    def _get_command_line_args():
        """
        Defines the command line arguments and handles their extraction

        :return: Parsed arguments
        :rtype: argparse.Namespace
        """

        parser = argparse.ArgumentParser(description='Process path for facets and update the index')
        parser.add_argument('path', type=str, help='Path to process')
        parser.add_argument('processing_path', type=str, help='Path to output intermediate files')
        parser.add_argument('--rerun', action='store_true', help='Disable paging to disk on rerun')
        parser.add_argument('--num-files', dest='num_files', type=int, help='Number of files per lotus job',
                            default=500)
        parser.add_argument('--conf', dest='conf',
                            default=os.path.join(os.path.dirname(__file__), '../conf/cci_facet_scanner.ini'))

        return parser.parse_args()

    @classmethod
    def main(cls):
        """
        Main routine. Extracts the command line options,
        loads the configuration file and initiaises the scanner before calling
        cls.process_path

        """
        args = cls._get_command_line_args()

        # Load config file
        print('Loading config...')
        conf = RawConfigParser()
        conf.read(args.conf)
        print(f'Analysis path: {args.path}')

        # Initialise scanner
        scanner = cls(conf)

        # Run scanner
        scanner.process_path(args)


if __name__ == '__main__':
    FacetExtractor.main()
