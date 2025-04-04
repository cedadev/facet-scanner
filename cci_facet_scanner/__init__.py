# encoding: utf-8

__author__ = 'Daniel Westwood'
__date__ = '28 Oct 2024'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'daniel.westwood@stfc.ac.uk'

# Logger setup
import logging

logging.basicConfig(level=logging.DEBUG)
logstream = logging.StreamHandler()

formatter = logging.Formatter('%(levelname)s [%(name)s]: %(message)s')
logstream.setFormatter(formatter)

