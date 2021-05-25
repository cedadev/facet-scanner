Configuration
==============

The configuration for the facet scanner is held in a config file. There are two
main sections in the configuration:

- elasticsearch
- facet_scanner

Elasticsearch
--------------

+-----------------------+----------------------------------------------+
| Option                | Description                                  |
+=======================+==============================================+
| api_key               | Elasticsearch API to give write access       |
+-----------------------+----------------------------------------------+
| target_index          | Index to write the facets to                 |
+-----------------------+----------------------------------------------+
| collection_index      | Index to aggregate the collections to        |
+-----------------------+----------------------------------------------+


Facet Scanner
-------------

+-----------------------+-------------------------------------------------------------------------+
| Option                | Description                                                             |
+=======================+=========================================================================+
| moles_mapping         | File path to cache of MOLES mapping to reduce load on the api server    |
+-----------------------+-------------------------------------------------------------------------+
| facet_json            | File path to cache of the facets to reduce load on the vocab server.    |
+-----------------------+-------------------------------------------------------------------------+

Download the moles_mapping cache:

::

    curl -fsSL -o moles_mapping.json http://api.catalogue.ceda.ac.uk/api/v0/obs/all

Export the facet_json:

::

    python cci_tagger/scripts/dump_facet_object.py facet_json.json

Example Config File
--------------------

::

    [elasticsearch]
    api_key = ****
    target_index = file-index
    collection_index = collection-index

    [facet_scanner]
    moles_mapping = moles_mapping_20210525.json
    facet_json = facets_json_20210525.json

