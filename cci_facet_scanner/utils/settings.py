import os

ES_HOSTS = os.environ.get("ES_HOSTS",None) or ['https://elasticsearch.ceda.ac.uk']