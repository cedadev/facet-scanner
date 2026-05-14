
class TestConsistency:

    def test_collection_handlers(self):

        from cci_facet_scanner.collection_handlers.base import \
            CollectionHandler
        from cci_facet_scanner.collection_handlers.cci import (
            CCI, extract_variables, nested_get)
        from cci_facet_scanner.collection_handlers.cmip5 import CMIP5
        from cci_facet_scanner.collection_handlers.utils.collection_map import \
            COLLECTION_MAP
        from cci_facet_scanner.collection_handlers.utils.facet_factory import \
            FacetFactory
        from cci_facet_scanner.collection_handlers.utils.moles_datasets import \
            CatalogueDatasets

        assert 1==1,"Import collection handlers successful"

    def test_file_handlers(self):
        from cci_facet_scanner.file_handlers.base import FileHandler
        from cci_facet_scanner.file_handlers.handler_factory import HandlerFactory
        from cci_facet_scanner.file_handlers.netcdf import NetcdfHandler

        assert 1==1,"Import file handlers successful"

    def test_core(self):
        from cci_facet_scanner.core.facet_scanner import FacetScanner

        assert 1==1, "Import core successful"

    def test_scripts(self):
        from cci_facet_scanner.scripts.facet_scanner_cmd import FacetExtractor
        from cci_facet_scanner.scripts.lotus_facet_scanner import \
            LotusFacetScanner
        from cci_facet_scanner.scripts.check_json import \
            TextColours, TestJSONFile, TestResults, test_results
        from cci_facet_scanner.scripts.check_tags import \
            Dataset, main
        from cci_facet_scanner.scripts.command_line_client import \
            CCITaggerCommandLineClient, get_datasets_from_file, \
            get_logging_level, read_json_file
        from cci_facet_scanner.scripts.dump_facet_object import \
            get_args, main

        assert 1==1, "Import scripts successful"

    def test_tagging(self):
        from cci_facet_scanner.tagging.dataset import Dataset
        from cci_facet_scanner.tagging.facets import Concept, Facets
        from cci_facet_scanner.tagging.tagger import ProcessDatasets

        assert 1==1, "Import tagging classes successful"

    def test_utils(self):
        from cci_facet_scanner.utils import constants
        from cci_facet_scanner.utils import dataset_jsons
        from cci_facet_scanner.utils import decorators
        from cci_facet_scanner.utils import elasticsearch
        from cci_facet_scanner.utils import settings
        from cci_facet_scanner.utils import snippets

        assert 1==1, "Import utils successful"