import requests
from tqdm import tqdm
from cci_facet_scanner.collection_handlers.cci import get_version_status_for_uuid

def main():

    fields             = ['uuid', 'title', 'result_field','status','dataPublishedTime']
    page               = {'page': 1, 'per_page': 100}
    discovery_keywords = {'discoveryKeywords__name': 'ESACCI'}
    publication_filter = {'publicationState__in': 'citable,published'}

    url = 'https://catalogue.ceda.ac.uk/api/v3/observations/?'
    url += f'fields={",".join(fields)}&'
    url += '&'.join(f'{k}={v}' for k,v in page.items())
    url += '&'
    url += '&'.join(f'{k}={v}' for k,v in discovery_keywords.items())
    url += '&'
    url += '&'.join(f'{k}={v}' for k,v in publication_filter.items())

    # Find all datasets across all pages
    moles_datasets = []
    found_all = False
    page = 0
    while not found_all:
        page += 1
        r = requests.get(url)

        # Capture datasets
        moles_datasets += r.json()['results']

        # Check next page exists.
        if r.json()['next']:
            url = r.json()['next']
        else:
            found_all = True

    superseded = []
    must_correct = []
    for dataset in tqdm(moles_datasets, desc='Looping MOLES datasets'):
        uuid = dataset['uuid']
        out = get_version_status_for_uuid(uuid, find_incorrect=True)
        if isinstance(out, tuple):
            if out[1]:
                superseded.append(uuid)
            else:
                must_correct.append(uuid)
    
    print("Results:")
    print(f'> Correct relation: {len(superseded)}')
    print(f'> Incorrect relation: {len(must_correct)}')

if __name__ == "__main__":
    main()