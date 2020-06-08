# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from elasticsearch.helpers import scan, bulk
from ceda_elasticsearch_tools.elasticsearch import CEDAElasticsearchClient


class ElasticsearchConnection:

    def __init__(self, **kwargs):
        self.es = CEDAElasticsearchClient(**kwargs)

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
                bulk(self.es, iterator(*args))
        else:
            bulk(self.es, iterator)

    def count(self, *args, **kwargs):
        return self.es.count(*args, **kwargs).get('count')

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
