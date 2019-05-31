# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '30 May 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from facet_scanner.scripts.facet_scanner_cmd import FacetScanner
import argparse
import os


class LotusFacetScanner(FacetScanner):

    def process_path(self, cmd_args):
        """

        :param cmd_args: Arguments from the command line
        """
        print('Getting handler...')
        handler = self.get_handler(cmd_args.path)
        print(handler)

        print('Retrieving facets...')
        handler.update_facets(cmd_args.path, self.index, cmd_args.processing_path)

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