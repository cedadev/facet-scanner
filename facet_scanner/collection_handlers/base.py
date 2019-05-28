# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '30 Apr 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from facet_scanner.core.elasticsearch_connection import ElasticsearchConnection
from abc import ABC, abstractmethod
from tqdm import tqdm


class CollectionHandler(ABC):

    @property
    @abstractmethod
    def project_name(self):
        """
        Make the setting of a project name mandatory.
        Abstract property for name of the project eg. opensearch
        """
        pass

    # File extensions to include
    extensions = []

    # List if filters to add to the query. These filters are added in the
    # must_not clause of the query to exclude documents in the index. e.g:
    #  {
    #       "match": {
    #           "info.directory.analyzed": "derived"
    #       }
    #   }
    filters = []

    def __init__(self, host, *args, **kwargs):
        """
        Create the elasticsearch connection
        :param host: Elasticsearch Host
        :param args: args to pass into the Elasticsearch connection class
        :param kwargs: kwargs to pass into the Elasticsearch connection class
        """
        self.es = ElasticsearchConnection(host=host, *args, **kwargs)

    @abstractmethod
    def get_facets(self, path):
        """
        Each collection handler must specify the method for extracting the facets
        :param path: File path
        :return: dict Facet:value pairs
        """
        pass

    def update_facets(self, path, index):
        """
        Adds the facets to the index
        :param path: directory root of the collection
        :param index: index to add the facets to
        """
        self.es.bulk(self._facet_generator, path, index, generator=True)

    def _facet_generator(self, path, index):
        """
        Generator method which takes a path and elasticsearch index name
        :param path: Directory root of the collection
        :param index: index to use as source and destination for facets
        :return: generator
        """
        query = self.es.get_query(self.extensions, path, excludes=self.filters)

        count = self.es.count(index=index, body=query)

        matches = self.es.get_hits(index=index, query=query)

        for match in tqdm(matches, total=count, desc='Generate facets for documents'):
            match_path = match['_source']['info']['directory']
            id = match['_id']

            facets = self.get_facets(match_path)
            project = {
                'application_id': self.project_name,
            }

            project.update(facets)

            yield {
                '_index': index,
                '_op_type': 'update',
                '_id': id,
                '_type': 'file',
                'script': {
                    'source': """
                        if (ctx._source.containsKey(\"projects\")){

                            for (proj in ctx._source.projects){
                                if (proj.project_id == params.project.project_id){
                                    params.exists = true;
                                    break;
                                }
                            }
                            if (!params.exists){
                                ctx._source.projects.addAll([params.project]);
                            }
                        }
                        else {
                            ctx._source.projects = [params.project]
                        }
                      """,
                    'params': {
                        'project': project,
                        'exists': False
                    }
                }
            }