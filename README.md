# CEDA Facet Scanner

Takes datasets and extracts the facets from the files/filepath.


## Running the code

``

parser = argparse.ArgumentParser(description='Process path for facets and update the index')
    parser.add_argument('path', type=str, help='Path to process')
    parser.add_argument('--conf', dest='conf', default='../conf/facet_scanner.