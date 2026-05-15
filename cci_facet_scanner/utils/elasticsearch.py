# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__   = '16 Sept 2025'
__copyright__ = 'Copyright 2025 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

def es_connection_kwargs(hosts, api_key, **kwargs):
    """
    Determine Elasticsearch connection kwargs
    """
    if isinstance(hosts, list):
        hosts = hosts[0]

    # All APIs for Elasticsearch should now work with this method
    return {
        'hosts':[hosts],
        'api_key':api_key,
        **kwargs
    }
    
class ElasticsearchConnection:
    """
    Elasticsearch Connection class.

    :param index: files index (default: settings.ELASTICSEARCH_INDEX)
    :type index: str

    """

    def __init__(self, host: str | list, api_key, index=None, collection_index=None, connection_params=None):
        self.index = index
        self.collection_index = collection_index

        connection_params = connection_params or {}

        if isinstance(host, str):
            host = [host]

        if isinstance(api_key,str):
            api_key = api_key.rstrip()

        self.es = Elasticsearch(
            **es_connection_kwargs(
                hosts=host,
                api_key=api_key,
                **connection_params
            )
        )

    def get(self, *args, **kwargs):
        """Get Query"""
        return self.es.get(*args, **kwargs)

    def search(self, query):
        """
        Search the files index

        :param query: Elasticsearch file query
        :type query: dict

        :return: Elasticsearch response
        :rtype: dict
        """
        try:
            return self.es.search(index=self.index, body=query)
        except:
            print(None)
            raise ValueError()

    def search_collections(self, query):
        """
        Search the collections index

        :param query: Elasticsearch collection query
        :type query: dict

        :return: Elasticsearch response
        :rtype: dict
        """
        return self.es.search(index=self.collection_index, body=query)

    def count(self, query):
        """
        Return the hit count from the current file query

        :param query: Elasticsearch file query
        :type query: dict

        :return: Elasticsearch count response
        :rtype: dict
        """
        return self.es.count(index=self.index, body=query)

    def count_collections(self, query):
        """
        Return the hit count from the current collection query

        :param query: Elasticsearch collection query
        :type query: dict

        :return: Elasticsearch count response
        :rtype: dict
        """
        return self.es.count(index=self.collection_index, body=query)
    
class ElasticsearchBulkConnection(ElasticsearchConnection):
    """
    Wrapper class to handle the connection with Elasticsearch.

    Specifically replicated to handle bulk queries etc.
    """

    def get_hits(self, index, query=None):
        return scan(self.es, query=query, index=index)

    def get_query(self, extensions, path, excludes=[]):
        query_base = {
            "_source": {
                "exclude": ["info.phenomena"]
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase_prefix": {
                                "info.directory.analyzed": path
                            }
                        }
                    ],
                    "must_not": [],
                    "filter": []
                }
            }
        }

        for ext in extensions:
            filter = {
                "term": {
                    "info.type.keyword": ext
                }
            }

            query_base["query"]["bool"]["filter"].append(filter)

        for exclusion in excludes:
            query_base["query"]["bool"]["must_not"].append(exclusion)

        return query_base

    def bulk(self, iterator, *args, generator=False):
        if generator:
                bulk(self.es, iterator(*args), refresh=True)
        else:
            bulk(self.es, iterator, refresh=True)

    def mget(self, *args, **kwargs):
        return self.es.mget(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self.es.search(*args, **kwargs)

    def create_collections_index(self, index):
        
        return self.es.indices.create(index=index, ignore=400, body={
            "mappings": {
                "properties": {
                    "time_frame": {
                        "type": "date_range"
                    },
                    "bbox": {
                        "properties": {
                            "coordinates": {
                                "type": "geo_point"
                            }
                        }
                    }
                }
            }
        })
