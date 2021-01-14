.. CEDA Facet Scanner documentation master file, created by
   sphinx-quickstart on Fri Dec 18 16:24:08 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CEDA Facet Scanner's documentation!
==============================================

This documentation describes the CEDA facet scanner. This is the package which is used
to extract facets from collections of datasets which can then be fed into OpenSearch.

The extracted data is fed into elasticsearch.

Installation
============
Install the requirements::

   pip install -r requirements.txt


Install the library::

   pip install git+https://github.com/cedadev/facet-scanner


Basic Usage
===========

This code can be used to bulk process a dataset for testing and initialisation:

.. program-output:: facet_scanner -h

The script uses your supplied path and queries elasticsearch for all the files under this point. The :code:`--num-files`
flag sets the page size and determines how many files end up in each lotus batch job.



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   adding_a_handler

.. toctree::
   :maxdepth: 4
   :caption: API:

   api/collection_handlers
   api/scripts


Indices and table
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
