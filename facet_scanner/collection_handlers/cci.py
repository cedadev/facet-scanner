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
from .util import CatalogueDatasets

def nested_get(key_list, input_dict):
    """
    Takes an iterable of keys and returns none if not found or the value
    :param key_list:
    :return:

    """

    last_key = key_list[-1]
    dict_nest = input_dict

    for key in key_list:
        if key != last_key:
            dict_nest = dict_nest.get(key, {})
        else:
            return dict_nest.get(key)


class CCI(CollectionHandler):
    """
    """

    project_name = 'opensearch'

    extensions = ['.nc']

    filters = []

    facets = [
            'institution',
            'product_version',
            'product_string',
            'processing_level',
            'data_type',
            'ecv',
            'sensor',
            'platform',
            'time_coverage_resolution'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vocab_file = self.conf.get('cci', 'vocab_file')

        self.pds = ProcessDatasets(suppress_file_output=True, filepath=vocab_file)

        self.catalogue = CatalogueDatasets()

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

        # Get MOLES catalogue
        moles_info = self.catalogue.get_moles_record_metadata(path)

        if moles_info:
            facets['dataset_id'] = moles_info['url'].split('uuid/')[-1]

        return facets

    def get_temporal(self, results):
        """
        Get start and end date for collection
        :return:
        """

        temporal = {}

        for key in ('start_date', 'end_date'):
            time = nested_get(('aggregations', key, 'value_as_string'), results)
            if time is not None:
                temporal[key] = time

        return temporal

    def get_geospatial(self, results):
        """
        Get the bounding box
        :param path:
        :return:
        """

        top_left_lon = nested_get(('aggregations','bbox','bounds','top_left','lon'), results)
        top_left_lat = nested_get(('aggregations','bbox','bounds','top_left','lat'), results)
        bottom_right_lon = nested_get(('aggregations','bbox','bounds','bottom_right','lon'), results)
        bottom_right_lat = nested_get(('aggregations','bbox','bounds','bottom_right','lat'), results)

        if results['aggregations']['bbox']:
            return {
                'type': 'envelope',
                'coordinates': [[top_left_lon, top_left_lat],[bottom_right_lon, bottom_right_lat]]
            }

        return {}

    def get_collection_facets(self):


        pass

    def generate_collections(self, path):

        query = {
            "query": {
                "match_phrase_prefix": {
                    "info.directory.analyzed": path
                }
            },
            "size": 0,
            "aggs": {
                "bbox": {
                    "geo_bounds": {
                        "field": "info.spatial.coordinates.coordinates"
                    }
                },
                'start_date': {
                    'min': {
                        'field': 'info.temporal.start_time'
                    }
                },
                'end_date': {
                    'max': {
                        'field': 'info.temporal.end_time'
                    }
                }
            }
        }

        # Add the facet aggregations
        for facet in self.facets:
            query['aggs'][facet] = {'terms': f'project.opensearch.{facet}', 'size':1000}

        print(query)

        # result = self.es.search(index='', query=query)
        #
        # # Create top level collection
        # top_collection = {
        #     'collection_id': 'cci',
        #     'title': 'CCI',
        # }
        #
        # top_collection.update(self.get_temporal(result))
        # top_collection.update(self.get_geospatial(result))
        #
        # # Create moles level collections



