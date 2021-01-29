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
from cci_tagger.tagger import ProcessDatasets
from .utils import CatalogueDatasets
import requests
from facet_scanner.utils import parse_key
from tqdm import tqdm
import hashlib
from facet_scanner.collection_handlers.utils import generate_id


def nested_get(key_list, input_dict, default=None):
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
            return dict_nest.get(key, default)


class CCI(CollectionHandler):
    """
    Collection Handler for the CCI project

    Parameters:
    -----------

    :param collection_root: Used when building the root object for this collection
    :param moles_mapping: A JSON file use to reduce the load on the api server
    compared to being requested by each lotus job.
    :param facet_json: Used by the cci_tagger ProcessDatasets to initialise the lookup
    rather than requesting from the vocab server for each lotus job.

    :attr collection_id: The collection id for root collection
    :attr collection_title: The collection Title for root collection
    :attr project_name: The project to attach the metadata to a
    :attr extensions: File extension filters
    :attr filters: Additional filters
    :attr facets: Facet mappings for use in get_facets method

    """

    collection_id = 'cci'
    collection_title = 'CCI'

    project_name = 'opensearch'

    extensions = []

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
        'platformGroup': 'platform_group',
        'frequency': 'time_coverage_resolution',
        'drsId': None
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.catalogue = CatalogueDatasets(moles_mapping=kwargs.pop('moles_mapping', None))

        self.pds = ProcessDatasets(suppress_file_output=True, **kwargs)

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

        if tagged_dataset.drs:
            mapped_facets['drsId'] = tagged_dataset.drs
            mapped_facets['datasetId'] = [generate_id(tagged_dataset.drs)]

        if moles_info:
            # Get any ids which already exist from drs
            dsid = mapped_facets.get('datasetId',[])
            moles_uuid = moles_info["url"].split("uuid/")[-1]
            dsid.extend([moles_uuid])
            mapped_facets['datasetId'] = dsid

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

        top_left_lon = nested_get(('aggregations', 'bbox', 'bounds', 'top_left', 'lon'), results)
        top_left_lat = nested_get(('aggregations', 'bbox', 'bounds', 'top_left', 'lat'), results)
        bottom_right_lon = nested_get(('aggregations', 'bbox', 'bounds', 'bottom_right', 'lon'), results)
        bottom_right_lat = nested_get(('aggregations', 'bbox', 'bounds', 'bottom_right', 'lat'), results)

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
        values = nested_get(('aggregations', 'fileFormat', 'buckets'), results)

        if values:
            facets['fileFormat'] = [x['key'] for x in values]

        return facets

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
        key = ('aggregations', 'variable', 'buckets')
        variable_buckets = nested_get(key, results)

        if variable_buckets:
            for bucket in variable_buckets:
                variable_dict = parse_key(bucket['key'])
                variable_dict['agg_string'] = bucket['key']
                variables.append(variable_dict)

            if variables:
                response['variable'] = variables

        return response

    def _get_dataset_aggregations(self, results):

        aggregations = []

        # Get DRS IDs
        key = ('aggregations', 'drsId', 'buckets')
        drs_ids = nested_get(key, results)

        if drs_ids:

            # Generate a list of hashes to query the aggregation state store
            ids = [generate_id(id['key']) for id in drs_ids]

            # Query the state store for the current aggregations
            agg_state = self.es.mget(index='opensearch-aggregation-state', body={'ids': ids}, _source=True)

            # Check the results to see which drs appear in the state store
            for doc in agg_state['docs']:
                if doc['found']:
                    agg = {
                        'id': doc['_source']['id'],
                        'services': [
                            'opendap'
                        ]
                    }

                    if doc['_source']['wms']:
                        agg['services'].extend(['wms', 'wcs'])

                    aggregations.append(agg)

        return {'aggregations': aggregations}

    def _get_elasticsearch_aggregation(self, path, file_index, variables=True, aggregations=True, extra_query_clauses=None):
        """
        Repeated action of getting the aggregations at different levels depending on the specified file path

        :param path: File path
        :param file_index: The name of the index containing the files
        :param variables: Whether or not to aggregate variables
        :param aggregations: Whether or not to build aggregation list
        :param extra_query_clauses: Any extra query segments to be added to bool query

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
                'bool': {
                    'must': [
                        {
                            'match_phrase_prefix': {
                                'info.directory.analyzed': path
                            }
                        }
                    ]
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
                'fileFormat': {
                    'terms': {
                        'field': 'info.type.keyword'
                    }
                }
            }
        }

        if variables:
            query['aggs']['variable'] = {
                'terms': {
                    'field': 'info.phenomena.agg_string',
                    'size': 1000
                }
            }

        # Add any extra query clauses
        if extra_query_clauses:
            for clause in extra_query_clauses:
                query['query']['bool']['must'].append(clause)

        # Add the facet aggregations
        for facet in self.facets:
            query['aggs'][facet] = {'terms': {'field': f'projects.{self.project_name}.{facet}.keyword', 'size': 1000}}

        result = self.es.search(index=file_index, body=query, request_timeout=60)

        metadata.update(self._get_temporal(result))
        metadata.update(self._get_geospatial(result))
        metadata.update(self._get_collection_facets(result))
        metadata.update(self._get_file_formats(result))
        metadata.update(self._get_collection_variables(result))

        if aggregations:
            metadata.update(self._get_dataset_aggregations(result))

        return metadata

    def _generate_collections(self, collection_index, file_index):
        """
        Collection level metadata is generated to map to MOLES datasets

        :param collection_index: index to put the collections in
        :param file_index: Index to use as source for aggregations
        """

        collections = []

        # Create moles level collections
        # Get the moles datasets for the given path
        r = requests.get(f'http://api.catalogue.ceda.ac.uk/api/v1/observations.json?discoveryKeyword=ESACCI&limit=300')

        moles_datasets = r.json()['results']

        for dataset in tqdm(moles_datasets, desc='Looping MOLES datasets'):
            metadata = {
                'collection_id': dataset['uuid'],
                'parent_identifier': self.collection_id,
                'title': dataset['title'],
                'path': dataset['result_field']['dataPath'],
                'is_published': True,
                '__id': dataset['uuid'],
                'links': {
                    'describedby': [
                        {
                            'title': 'ISO19115',
                            'href': f'https://catalogue.ceda.ac.uk/export/xml/{dataset["uuid"]}.xml'
                        },
                        {
                            'title': 'Dataset Information',
                            'href': f'https://catalogue.ceda.ac.uk/uuid/{dataset["uuid"]}'
                        }
                    ]
                }
            }

            metadata.update(
                self._get_elasticsearch_aggregation(
                    dataset['result_field']['dataPath'],
                    file_index
                )
            )
            collections.append(metadata)

            # Get drs datasets within MOLES datasets
            drs_datasets = metadata.get('drsId', [])

            # If we are adding another level, then need to add a "collection" for all files
            if drs_datasets:
                drs_datasets.append('_all')

            for drs in drs_datasets:

                # Need to make a unique identifier for _all collection
                if drs == '_all':
                    id = f'{dataset["uuid"]}.all'
                else:
                    id = generate_id(drs)

                metadata = {
                    'collection_id': id,
                    'parent_identifier': dataset['uuid'],
                    'title': drs if drs != '_all' else 'All Files',
                    'path': dataset['result_field']['dataPath'],
                    'is_published': True,
                    '__id': id,
                    'links': {
                        'describedby': [
                            {
                                'title': 'Dataset Information',
                                'href': f'https://catalogue.ceda.ac.uk/uuid/{dataset["uuid"]}'
                            }
                        ]
                    }
                }

                # Don't want a drs filter on the files when doing _all
                if drs != '_all':
                    metadata.update(
                        self._get_elasticsearch_aggregation(
                            dataset['result_field']['dataPath'],
                            file_index,
                            extra_query_clauses=[
                                {'term': {f'projects.{self.project_name}.drsId.keyword': drs}}
                            ]
                        )
                    )
                else:
                    metadata.update(
                        self._get_elasticsearch_aggregation(
                            dataset['result_field']['dataPath'],
                            file_index
                        )
                    )
                collections.append(metadata)

        # Generate elasticsearch indexing metadata
        for collection in collections:
            id = collection.pop('__id')
            yield {
                '_index': collection_index,
                '_id': id,
                '_source': collection

            }

    def _generate_root_collections(self, collection_index):
        # Create top level collection
        root_collections = []

        root_collection = {
            'collection_id': self.collection_id,
            'title': self.collection_title,
            'path': self.collection_root,
            '__id': hashlib.sha1(self.collection_id.encode()).hexdigest()
        }

        metadata = {}

        query = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'term': {
                                'is_published': True
                            }
                        }
                    ],
                    'must_not': [
                        {
                            'term': {
                                'collection_id.keyword': 'cci'
                            }
                        }
                    ]
                }
            },
            'size': 0,
            'aggs': {
                'bbox': {
                    'geo_bounds': {
                        'field': 'bbox.coordinates'
                    }
                },
                'start_date': {
                    'min': {
                        'field': 'start_date'
                    }
                },
                'end_date': {
                    'max': {
                        'field': 'end_date'
                    }
                }
            }
        }

        # Add the facet aggregations
        for facet in self.facets:
            query['aggs'][facet] = {'terms': {'field': f'{facet}.keyword', 'size': 1000}}

        result = self.es.search(index=collection_index, body=query, request_timeout=60)

        metadata.update(self._get_temporal(result))
        metadata.update(self._get_geospatial(result))
        metadata.update(self._get_collection_facets(result))
        metadata.update(self._get_collection_variables(result))

        root_collection.update(metadata)

        root_collections.append(root_collection)

        for collection in root_collections:
            id = collection.pop('__id')
            yield {
                '_index': collection_index,
                '_id': id,
                '_source': collection

            }
