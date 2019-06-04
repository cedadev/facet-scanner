# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from facet_scanner.collection_handlers.util.facet_factory import FacetFactory
import argparse
import os
from configparser import RawConfigParser
from facet_scanner.util.snippets import query_yes_no


class FacetScanner:

    def __init__(self, conf):
        self.handler_factory = FacetFactory()

        self.es_host = conf.get("elasticsearch", "host")
        self.es_user = conf.get('elasticsearch', 'es_user')
        self.es_password = conf.get('elasticsearch', 'es_password')
        self.index = conf.get('elasticsearch', 'target_index')

        print(
            f'Host: {self.es_host} '
            f'User: {self.es_user} '
            f'Index: {self.index} '
            f'Password: {"*******" if self.es_password is not None else None}'
        )

        query_yes_no('Check the above variables. Ready to continue?')

    def get_handler(self, path, conf):
        handler = self.handler_factory.get_handler(path)

        # Handle situation where handler not found
        if handler is None:
            raise NotImplementedError('The script was unable to find a match in facet_scanner.collection_handlers.util.collection_map.'
                                      'Please update the mapping file.')

        return handler(
            host=self.es_host,
            http_auth=(self.es_user, self.es_password),
            conf = conf

        )

    def process_path(self, cmd_args, conf):
        """

        :param cmd_args: Arguments from the command line
        """
        print('Getting handler...')
        handler = self.get_handler(cmd_args.path, conf)
        print(handler)

        print('Retrieving facets...')
        handler.export_facets(cmd_args.path, self.index, cmd_args.processing_path)

    @staticmethod
    def _get_command_line_args():
        # Get command line arguments
        parser = argparse.ArgumentParser(description='Process path for facets and update the index')
        parser.add_argument('path', type=str, help='Path to process')
        parser.add_argument('processing_path', type=str, help='Path to output intermediate files')
        parser.add_argument('--conf', dest='conf',
                            default=os.path.join(os.path.dirname(__file__), '../conf/facet_scanner.ini'))

        return parser.parse_args()

    @classmethod
    def main(cls):
        args = cls._get_command_line_args()

        # Load config file
        print('Loading config...')
        conf = RawConfigParser()
        conf.read(args.conf)
        print(f'Analysis path: {args.path}')

        # Initialise scanner
        scanner = cls(conf)

        # Run scanner
        scanner.process_path(args, conf)





if __name__ == '__main__':
    FacetScanner.main()

