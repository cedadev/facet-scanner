# CEDA Facet Scanner

![Static Badge](https://img.shields.io/badge/cci%20tagger%20workflow-8AD6F6)
![GitHub Release](https://img.shields.io/github/v/release/cedadev/facet-scanner)
[![PyPI version](https://badge.fury.io/py/cci-facet-scanner.svg)](https://pypi.python.org/pypi/cci-facet-scanner/)


Takes datasets and extracts the facets from the files/filepath.
The scanner works to map a file path to the specific handler for that collection of files. For example, ESA CCI datasets are scanned by the cci handler. This is because each collection of datasets will have different characteristics and will need to be treated in a different way.

[ReadTheDocs Documentation](https://facet-scanner.readthedocs.io/en/latest/index.html)

## Installation

Create a Python virtual environment:
**Must be Python 3**

```bash
python -m venv venv
source venv/bin/activate
```

This package can be installed with the following:
```bash
git clone https://github.com/facet-scanner
cd facet-scanner
pip install -e .
```

NOTE: As of 22nd Jan 2025 the `facet-scanner` repository has been upgraded for use with Poetry version 2. This requires the use of an additional `requirements_fix.txt` patch while a solution for poetry dependencies in github is worked on. The above installation MUST be supplemented with:

```bash
pip install -r requirements_fix.txt
```
This is a temporary fix and will be removed when poetry is patched.



## Running the code

`facet_scanner (path_to_scan) [--conf <path_to_config.ini>]`

Required:

| Argument   | Description |
| ------------ | ------------ |
| path_to_scan | File path in the archive to use as the basis of the scan. The scanner will take this path and retrieve all the files in the elasticsearch index at this point. |



Optional:

| Option   | No. Arguments | Description |
| -------- | :-------------------: | ------ |
| `--conf` | 1                   | Allows you to set a different location for the config file.This defaults to `../conf/facet_scanner.ini` relative to the script. |


## Adding a new Collection

[Adding a Handler Documentation](https://facet-scanner.readthedocs.io/en/latest/adding_a_handler.html)

## Facet Indexing with Rabbit

This repo also provides the code to read from the rabbit queue and process updates
to the files index, adding facets.

Watched events:
- DEPOSIT

Exposed Queue Consumer Classes:
- `rabbit_facet_indexer.queue_consumers.FacetScannerQueueConsumer`

## Configuration

Configuration is handled using a YAML file. The full configuration options 
are described in the [rabbit_indexer repo](https://github.com/cedadev/rabbit-index-ingest/blob/master/README.md#rabbit_event_indexer)

This process also requires an environment variable `JSON_TAGGER_ROOT`. This should be set to
the `json` directory which contains the tagging json.

The required sections for the facet indexer are:
- rabbit_server
- indexer
- logging
- moles
- elasticsearch
- files_index

An example YAML file (secrets noted by ***** ): 

```yaml

---
rabbit_server:
  name: "*****"
  user: "*****"
  password: "*****"
  vhost: "*****"
  source_exchange:
    name: deposit_logs
    type: fanout
  dest_exchange:
    name: fbi_fanout
    type: fanout
  queues:
    - name: elasticsearch_update_queue_opensearch_tags_test
      kwargs:
        auto_delete: false
    - name: elasticsearch_update_queue_opensearch_tags_test
      bind_kwargs:
        routing_key: opensearch.tagger.cci
indexer:
  queue_consumer_class: rabbit_facet_indexer.queue_consumers.FacetScannerQueueConsumer
  path_filter:
    paths:
      - /neodc/esacci
    filter_policy: 2
logging:
  log_level: info
moles:
  moles_obs_map_url: http://api.catalogue.ceda.ac.uk/api/v2/observations.json/?publicationState__in=citable,published,preview,removed&fields=publicationState,result_field,title,uuid
elasticsearch:
  es_api_key: "*****"
files_index:
  name: ceda-fbi
  calculate_md5: false
  scan_level: 2
```

## Running

The indexer can be run using the helper script provided by [rabbit_indexer repo](https://github.com/cedadev/rabbit-index-ingest/blob/master/README.md#configuration).
This uses an entry script and parses the config file to run your selected queue_consumer_class: 

`rabbit_event_indexer --conf <path_to_configuration_file>`
