
class TestConsistency:

    def test_collection_handlers(self):

        from facet_scanner.collection_handlers.utils.collection_map import COLLECTION_MAP
        from facet_scanner.collection_handlers.utils.facet_factory import FacetFactory
        from facet_scanner.collection_handlers.utils.moles_datasets import CatalogueDatasets

        from facet_scanner.collection_handlers.base import CollectionHandler
        from facet_scanner.collection_handlers.cci import (
            nested_get,
            extract_variables,
            CCI
        )
        from facet_scanner.collection_handlers.cmip5 import CMIP5

        assert 1==1,"Import collection handlers successful"

    def test_core(self):
        from facet_scanner.core.elasticsearch_connection import ElasticsearchConnection
        from facet_scanner.core.facet_scanner import FacetScanner

        assert 1==1, "Import core successful"

    def test_scripts(self):
        from facet_scanner.scripts.facet_scanner_cmd import FacetExtractor
        from facet_scanner.scripts.lotus_facet_scanner import LotusFacetScanner
        
        assert 1==1, "Import scripts successful"

    def test_utils(self):
        from facet_scanner.utils.snippets import (
            query_yes_no,
            generator_grouper,
            split_outside_quotes,
            remove_quotes,
            parse_key,
            Singleton
        )

        assert 1==1, "Import utils successful"