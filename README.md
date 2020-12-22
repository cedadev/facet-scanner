# CEDA Facet Scanner

Takes datasets and extracts the facets from the files/filepath.
The scanner works to map a file path to the specific handler for that collection of files. For example, ESA CCI datasets are scanned by the cci handler. This is because each collection of datasets will have different characteristics and will need to be treated in a different way.

[Documentation](https://facet-scanner.readthedocs.io/en/latest/index.html)


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
