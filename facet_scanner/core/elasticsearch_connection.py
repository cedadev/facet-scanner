# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk, parallel_bulk


class ElasticsearchConnection:

    def __init__(self, host, *args, **kwargs):
        self.es = Elasticsearch([host], *args, **kwargs)

    def get_hits(self, index, query=None):
        return scan(self.es, query=query, index=index)

    def get_query(self, extensions, path, excludes=[]):
        query_base = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase_prefix": {
                                "info.directory.analyzed": path
                            }
                        }
                    ],
                    "must_not":[],
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