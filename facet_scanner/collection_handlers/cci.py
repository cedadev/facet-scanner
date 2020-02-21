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
from cci_tagger.conf.constants import PROCESSING_LEVEL
from .util import CatalogueDatasets
import requests
from facet_scanner.util import parse_key

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
    collection_id = 'cci'
    collection_title = 'CCI'

    project_name = 'opensearch'

    extensions = ['.nc']

    filters = []

    facets = {
            'institute': 'institution',
            'productVersion': 'product_version',
            'productString': 'product_string',
            'processingLevel': 'processing_level',
            'dataType': 'data_type',
            'ecv': None,
            'sensor': None,
            'platform': None,
            'frequency': 'time_coverage_resolution'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pds = ProcessDatasets(suppress_file_output=True)

        self.catalogue = CatalogueDatasets()


        if kwargs['collection_root'] is not None:
            self.collection_root = kwargs['collection_root']
        else:
            raise TypeError('Collection root is None. '
                            'Collection root cannot be None. '
                            'Check handler factory')

    def get_facets(self, path):
        """
        Extract the facets from the file path
        :param path: File path
        :return: Dict  Facet:value pairs
        """

        tagged_dataset = self.pds.get_file_tags(path)

        # Translate between output from tagging code to map to named facets
        mapped_facets = {}
        for tag_name, tag_value in tagged_dataset.labels.items():

            # Get facet name
            for facet, tag_name_mapping in self.facets.items():

                if tag_name == tag_name_mapping:
                    mapped_facets[facet] = tag_value

                if tag_name == facet and tag_name_mapping is None:
                    mapped_facets[facet] = tag_value

        # Get MOLES catalogue
        moles_info = self.catalogue.get_moles_record_metadata(path)

        mapped_facets['drsId'] = tagged_dataset.drs

        if moles_info:
            mapped_facets['datasetId'] = moles_info['url'].split('uuid/')[-1]

        return mapped_facets

    @staticmethod
    def _get_temporal(results):
        """
        Get start and end date for collection
        :return:
        """

        temporal = {}

        for key in ('start_date', 'end_date'):
            time = nested_get(('aggregations', key, 'value_as_string'), results)
            if time is not None:
                temporal[key] = time

        # Generate date_range
        start_date = nested_get(('aggregations', 'start_date', 'value_as_string'), results)
        end_date = nested_get(('aggregations', 'end_date', 'value_as_string'), results)

        dates = (start_date, end_date)

        if not any(dates):
            return {}

        if all(dates):
            temporal['time_frame'] = {
                'gte': start_date,
                'lte': end_date
            }
        else:
            val = [x for x in dates if x == True]

            temporal['time_frame'] = {
                'gte': val,
                'lte': val
            }
        return temporal

    @staticmethod
    def _get_geospatial(results):
        """
        Get bounding box from Elasticsearch aggregation response
        :param results: Elasticsearch response
        :return: Geospatial bbox dictionary
        """
        """
        Get the bounding box
        :param path:
        :return:
        """

        geospatial = {}

        top_left_lon = nested_get(('aggregations','bbox','bounds','top_left','lon'), results)
        top_left_lat = nested_get(('aggregations','bbox','bounds','top_left','lat'), results)
        bottom_right_lon = nested_get(('aggregations','bbox','bounds','bottom_right','lon'), results)
        bottom_right_lat = nested_get(('aggregations','bbox','bounds','bottom_right','lat'), results)

        if results['aggregations']['bbox']:
            geospatial = {
                'bbox': {
                    'type': 'envelope',
                    'coordinates': [[top_left_lon, top_left_lat], [bottom_right_lon, bottom_right_lat]]
                }
            }

        return geospatial

    @staticmethod
    def _get_file_formats(results):

        facets = {}
        values = nested_get(('aggregations', 'file_format', 'buckets'), results)

        if values:
            facets['fileFormat'] = [x['key'] for x in values]

    def _get_collection_facets(self, results):
        """
        Extracts the facet values from the elasticsearch response
        :param results: Elasticsearch response json
        :return: Dictionary of facet values
        """

        facets = {}

        for facet in self.facets:
            key = ('aggregations', facet, 'buckets')

            values = nested_get(key, results)

            if values:
                facets[facet] = [x['key'] for x in values]

        return facets

    @staticmethod
    def _get_collection_variables(results):
        """
        Convert the aggreation into a dictionary of variables for opensearch
        :param results:
        :return:
        """
        response = {}
        variables = []

        # Get the aggregation buckets
        key = ('aggregations', 'variables', 'buckets')
        variable_buckets = nested_get(key, results)

        for bucket in variable_buckets:
            variable_dict = parse_key(bucket["key"])
            variables.append(variable_dict)

        if variables:
            response['variables'] = variables

        return response

    def get_elasticsearch_aggregation(self, path):
        """
        Repeated action of getting the aggregations at different levels depending on the specified file path
        :param path: File path
        :return: metadata dictionary representative of dataset. If all data found, gives:

        {
            'start_date': ...,
            'end_date': ...,
            'bbox': ...,
            'facet1': ...,
            'facet2': ...,
        }
        """

        metadata = {}

        query = {
            'query': {
                'match_phrase_prefix': {
                    'info.directory.analyzed': path
                }
            },
            'size': 0,
            'aggs': {
                'bbox': {
                    'geo_bounds': {
                        'field': 'info.spatial.coordinates.coordinates'
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
                },
                'file_format': {
                    'terms': {
                        'field': 'info.type.keyword'
                    }
                },
                'variables': {
                    'terms': {
                        'field': 'info.phenomena.agg_string',
                        'size': 1000
                    }
                }
            }
        }

        # Add the facet aggregations
        for facet in self.facets:
            query['aggs'][facet] = {'terms':{'field':f'projects.{self.project_name}.{facet}.keyword', 'size':1000}}

        result = self.es.search(index='opensearch-cci-test-2', body=query)

        metadata.update(self._get_temporal(result))
        metadata.update(self._get_geospatial(result))
        metadata.update(self._get_collection_facets(result))
        metadata.update(self._get_collection_variables(result))

        return metadata

    def _generate_collections(self, index):
        """
        Collection level metadata is generated to map to MOLES datasets
        :param path: File path
        :return: None
        """

        collections = []

        # Create top level collection
        root_collection = {
            'collection_id': self.collection_id,
            'title': self.collection_title,
            'path': self.collection_root
        }

        root_collection.update(self.get_elasticsearch_aggregation(self.collection_root))

        collections.append(root_collection)

        # Create moles level collections
        # Get the moles datasets for the given path
        moles_datasets = requests.get(f'http://api.catalogue.ceda.ac.uk/api/v1/observations.json?dataPath_prefix={self.collection_root}&discoveryKeyword=ESACCI').json()

        for dataset in moles_datasets:
            metadata = {
                'collection_id': dataset['uuid'],
                'parent_identifier': self.collection_id,
                'title': dataset['title'],
                'path': dataset['result_field']['dataPath']
            }

            metadata.update(self.get_elasticsearch_aggregation(dataset['result_field']['dataPath']))
            collections.append(metadata)

        # Generate elasticsearch indexing metadata
        for collection in collections:
            yield {
                '_index': index,
                '_type': 'collection',
                '_source': collection
            }


