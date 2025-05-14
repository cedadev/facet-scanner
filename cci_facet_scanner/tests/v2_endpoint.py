import requests
from tqdm import tqdm

def request():
    url = 'https://catalogue.ceda.ac.uk/api/v2/observations.json?fields=uuid,title,result_field&page=1&per_page=100&discoveryKeywords__name=ESACCI&publicationState__in=citable,published'
    collections = []
    moles_datasets = []
    found_all = False
    page = 0
    while not found_all:
        print(f'Page: {page}')
        r = requests.get(url)

        moles_datasets += r.json()['results']
        if r.json()['next']:
            url = r.json()['next']
        else:
            found_all = True
        page += 1

    for dataset in tqdm(moles_datasets, desc='Looping MOLES datasets'):

        if dataset.get('publicationState',None) not in ['published', 'citable']:
            # Skip non-published/citable records
            continue

        metadata = {
            'collection_id': dataset['uuid'],
            'parent_identifier': None,
            'title': dataset['title'],
            'path': dataset['result_field']['dataPath'],
            'is_published': True,
            '__id': dataset['uuid']
        }

        collections.append(metadata)

request()