import os

ES_HOSTS = os.environ.get("ES_HOSTS",None) or ['https://elasticsearch.ceda.ac.uk']

SPARQL_HOST_NAME = 'vocab.ceda.ac.uk'

ESGF_DRS_FILE = 'esgf_drs.json'
MOLES_TAGS_FILE = 'moles_tags.csv'
MOLES_ESGF_MAPPING_FILE = 'moles_esgf_mapping.csv'
ERROR_FILE = 'error.log'
LOG_FORMAT = '%(name)s - %(levelname)s - %(message)s'