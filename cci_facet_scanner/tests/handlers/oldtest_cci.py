# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '22 May 2019'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import unittest
from cci_facet_scanner.collection_handlers.cci import CCI


class TestCCIHandler(unittest.TestCase):

    def setUp(self):
        self.cci_handler = CCI(host="https://jasmin-es1.ceda.ac.uk:443", http_auth=('richard', 'blah'))
        self.path = '/neodc/esacci/aerosol/data/ATSR2_ORAC/L3/v3.02/DAILY/1995/08/19950801-ESACCI-L3C_AEROSOL-AER_PRODUCTS-ATSR2-ERS2-ORAC-DAILY-fv03.02.nc'

    # def test_get_frequency(self):
    #
    #     frequency = self.cci_handler.get_frequency(self.path)
    #
    #     self.assertEqual(frequency, 'day')
    #
    # def test_get_processing_level(self):
    #
    #     level = self.cci_handler.get_processing_level(self.path)
    #
    #     self.assertEqual(level,3)

    def test_get_facets(self):

        facets = self.cci_handler.get_facets('../data/199701-ESACCI-L3C_AEROSOL-AER_PRODUCTS-ATSR2-ERS2-ORAC-MONTHLY-fv03.02.nc')
        print(facets)

if __name__ == '__main__':
    unittest.main()