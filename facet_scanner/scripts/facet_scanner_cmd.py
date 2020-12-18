# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import argparse
import os
from configparser import RawConfigParser
from facet_scanner.util import query_yes_no
from facet_scanner.core.facet_scanner import FacetScanner


class FacetExtractor(FacetScanner):

    def __init__(self, conf):

        super().__init__()

        self.es_password = conf.get('elasticsearch', 'api_key')
        self.index = conf.get('elasticsearch', 'target_index')
        self.facet_json = conf.get('facet_scanner', 'facet_json', fallback=None)
        self.moles_mapping = conf.get('facet_scanner', 'moles_mapping', fallback=None)

        print(
            f'Index: {self.index} '
            f'Password: {"*******" if self.es_password is not None else None}'
        )

        query_yes_no('Check the above variables. Ready to continue?')

    def process_path(self, cmd_args):
        """

        :param cmd_args: Arguments from the command line
        """
        print('Getting handler...')
        handler = self.get_handler(cmd_args.path, headers={'x-api-key': self.es_password}, facet_json=self.facet_json)
        print(handler)

        print('Retrieving facets...')
        handler.export_facets(cmd_args.path, self.index, cmd_args.processing_path, rerun=cmd_args.rerun, batch_size=cmd_args.num_files, lotus=cmd_args.no_run)

    @staticmethod
    def _get_command_line_args():
        # Get command line arguments
        parser = argparse.ArgumentParser(description='Process path for facets and update the index')
        parser.add_argument('path', type=str, help='Path to process')
        parser.add_argument('processing_path', type=str, help='Path to output intermediate files')
        parser.add_argument('--no-run', action='store_false', dest='no_run', help='Disables the run on lotus. Can be used just to build the output lists.')
        parser.add_argument('--rerun', action='store_true', help='Disable paging to disk on rerun')
        parser.add_argument('--num-files', dest='num_files', type=int, help='Number of files per lotus job',
                            default=500)
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
        scanner.process_path(args)


if __name__ == '__main__':
    FacetExtractor.main()
