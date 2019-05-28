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
from configparser import RawConfigParser


class FacetScanner:

    def __init__(self, conf):
        self.handler_factory = FacetFactory()

        self.es_host = conf.get("elasticsearch", "host")
        self.es_user = conf.get('elasticsearch', 'es_user')
        self.es_password = conf.get('elasticsearch', 'es_password')
        self.index = conf.get('elasticsearch', 'target_index')

    def get_handler(self, path):

        handler = self.handler_factory.get_handler(path)

        return handler(
            host=self.es_host,
            http_auth=(self.es_user, self.es_password)
        )

    def process_path(self, path):

        handler = self.get_handler(path)

        handler.update_facets(path, self.index)

    @classmethod
    def main(cls):
        # Get command line arguments
        parser = argparse.ArgumentParser(description='Process path for facets and update the index')
        parser.add_argument('path', type=str, help='Path to process')
        parser.add_argument('--conf', dest='conf', default='../conf/facet_scanner.ini')

        args = parser.parse_args()

        # Load config file
        conf = RawConfigParser(args.conf)
        conf.read()

        # Initialise scanner
        scanner = cls(conf)

        # Run scanner
        scanner.process_path(args.path)

if __name__ == '__main__':

    FacetScanner.main()






