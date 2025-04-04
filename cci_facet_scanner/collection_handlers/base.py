# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '30 Apr 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from cci_facet_scanner.core.elasticsearch_connection import ElasticsearchConnection
import os
import subprocess
import json
import importlib.util
from tqdm import tqdm
from cci_facet_scanner.utils import generator_grouper, Singleton
import time

from typing import Union

from cci_facet_scanner import logstream
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False


class CollectionHandler(metaclass=Singleton):
    """
    Base Class for all collection handlers.

    :param kwargs: Passed to ElasticsearchConnection class

    :attr extensions:
        File extensions to include. If none provided will default to all
    :type extensions:
        list

    :attr filters:
        Additional filters to go as part of the must_not clause of the elasticsearch query
        when retrieving the initial file list.
    :type filters:
        list

    """

    @property
    def project_name(self):
        """
        Make the setting of a project name mandatory.
        Abstract property for name of the project eg. opensearch
        """
        raise NotImplementedError

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

    def __init__(self, api_key: Union[str,None] = None,**kwargs):
        """
        Create the elasticsearch connection

        :param kwargs: kwargs to pass into the Elasticsearch connection class
        """
        # clean out extra arguments if they are there
        kwargs.pop('collection_root')
        kwargs.pop('facet_json', None)
        kwargs.pop('moles_mapping', None)

        self.es = ElasticsearchConnection(api_key=api_key, **kwargs)

    def get_facets(self, path):
        """
        Each collection handler must specify the method for extracting the facets

        :param path: File path
        :return: dict Facet:value pairs
        """
        raise NotImplementedError

    def export_facets(self, path, index, processing_path, lotus=True, rerun=False, batch_size=500):
        """
        Dumps the list of files to process and calls lotus to add to index

        :param path: directory root of the collection
        :param index: index to add the facets to
        :param processing_path: directory to place the elasticsearch pages for processing by lotus
        :param lotus: Boolean. True will set processes to run on lotus
        :param batch_size: Size of pages to send for processing
        """

        query = self.es.get_query(self.extensions, path, excludes=self.filters)

        matches = self.es.get_hits(index=index, query=query)

        if not rerun:
            print('Outputting pages to file...')
            for i, page in enumerate(generator_grouper(batch_size, matches)):
                filepath = os.path.join(processing_path, f'results_page_{i}.json')

                with open(filepath, 'w') as writer:
                    writer.writelines(map(lambda x: f'{json.dumps(x)}\n', page))

        if lotus:
            self.lotus_submit(processing_path)

    @staticmethod
    def lotus_submit(processing_directory):

        for i, file in enumerate(os.listdir(processing_directory)):

            filepath = os.path.join(processing_directory, f'{file}')

            # Pause every 10 so as to not overwhelm the API
            if i and not i % 10:
                print('Pausing for 20 seconds')
                time.sleep(20)

            script_path = os.path.dirname(
                importlib.util.find_spec('cci_facet_scanner.scripts.lotus_cci_facet_scanner').origin

            )

            task = f'{script_path}/lotus_worker.sh {script_path} {filepath}'
            command = f'sbatch -t 06:00:00 -e errors/{file}.err {task}'

            subprocess.run(command, shell=True)

    def update_facets(self, path, index):
        """
        Take a file containing elasticsearch documents and update the index with
        facets at these locations

        :param path: Path to elasticsearch input file
        :param index: Index to update
        """

        self.es.bulk(self._facet_generator, path, index, generator=True)

    def _facet_generator(self, path, index):
        """
        Generator method which reads a file containing a list of elasticsearch documents

        :param path: Path to input file
        :param index: index to use as destination for facets
        :return: generator to use with elasticsearch bulk helper
        """

        # Load items from file
        with open(path) as reader:

            for line in tqdm(reader, desc='Gathering facets'):
                match = json.loads(line.strip())

                match_dir = match['_source']['info']['directory']
                match_filename = match['_source']['info']['name']

                data_path = os.path.join(match_dir, match_filename
                                         )
                id = match['_id']

                facets = self.get_facets(data_path)
                project = {
                    self.project_name: facets
                }

                yield {
                    '_index': index,
                    '_op_type': 'update',
                    '_id': id,
                    'doc': {'projects': project},
                    'doc_as_upsert': True

                }

    def _generate_collections(self, collection_index, file_index):
        """
        Optional handle to enable different handling of collections between datasets.
        Returns None and handles indexing of the relevant metadata.

        :param collection_index: Name of the collection index
        :param file_index: Name of the file index
        """
        raise NotImplementedError

    def _generate_root_collections(self, collection_index):
        """
        Optional handle to enable different handling of collections between datasets.
        Returns None and handles indexing of the relevant metadata.

        :param collection_index: Name of the collection index
        """
        raise NotImplementedError

    def export_collections(self, collection_index, file_index):

        # Make sure the collections index exists with the date range mapping
        self.es.create_collections_index(collection_index)

        self.es.bulk(self._generate_collections, collection_index, file_index, generator=True)
        self.es.bulk(self._generate_root_collections, collection_index, generator=True)



