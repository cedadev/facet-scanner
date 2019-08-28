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
import os
import subprocess
import json
import importlib.util
from tqdm import tqdm
from facet_scanner.util import generator_grouper
import time


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

    def __init__(self, host, http_auth, conf, **kwargs):
        """
        Create the elasticsearch connection
        :param host: Elasticsearch Host
        :param args: args to pass into the Elasticsearch connection class
        :param kwargs: kwargs to pass into the Elasticsearch connection class
        """
        self.es = ElasticsearchConnection(host=host, http_auth=http_auth, **kwargs)
        self.conf = conf

    @abstractmethod
    def get_facets(self, path):
        """
        Each collection handler must specify the method for extracting the facets
        :param path: File path
        :return: dict Facet:value pairs
        """
        pass

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
                print('Pausing for 1 mins')
                time.sleep(60)

            script_path = importlib.util.find_spec('facet_scanner.scripts.lotus_facet_scanner').origin
            task = f'python {script_path} {filepath}'
            command = f'bsub -W 24:00 -e errors/{file}.err {task}'

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

        # Remove file once processed
        if os.path.exists(path):
            os.remove(path)
