Adding a Handler
================

Expanding the coverage of the facet scanner involves adding the dataset to the collection map
and creating a new handler class.

1. Collection Map (:code:`facet_scanner/collection_handlers/util/collection_map.py`
2. Handler Class (:code:`facet_scanner/collection_handlers/.`)


Collection Map
--------------

.. automodule:: facet_scanner.collection_handlers.util.collection_map
    :noindex:

The :code:`<module>.<handler_class>` variables are substituted to match the new collection handler.

Handler Class
-------------

The handler class does all the work of extracting the facets from the specified files in the :code:`COLLECTION_MAP`

All handler classes should inherit from the :doc:`api/collection_handlers`

MRO
----

When the :code:`facet_scanner` is run, the methods are called in the following order:

.. automodule:: facet_scanner.scripts.facet_scanner_cmd

.. automodule:: facet_scanner.scripts.lotus_facet_scanner

