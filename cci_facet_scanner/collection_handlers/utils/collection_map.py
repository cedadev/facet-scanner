# encoding: utf-8
"""
A Python dictionary which contains the mapping from path to collection handler.py

The key pairs are formed::

    '/path/to/dataset: dict(handler='cci_facet_scanner.collection_handlers.<handler_module>.<handler_class>')

"""
__author__ = 'Richard Smith'
__date__ = '26 Mar 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

COLLECTION_MAP = {
    '/badc/cmip5/data': dict(handler='cci_facet_scanner.collection_handlers.cmip5.CMIP5'),
    '/neodc/esacci': dict(handler='cci_facet_scanner.collection_handlers.cci.CCI')
}