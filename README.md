# CEDA Facet Scanner

Takes datasets and extracts the facets from the files/filepath.


## Running the code

`facet_scanner (path_to_scan) [--conf <path_to_config.ini>]`

Required:

| Argument   | Description |
| ------------ | ------------ |
| path_to_scan | File path in the archive to use as the basis of the scan. The scanner will take this path and retrieve all the files in the elasticsearch index at this point. |



Optional:

| Option   | Number of Arguments | Description |
| -------- | :-------------------: | ------ |
| `--conf` | 1                   | Allows you to set a different location for the config file.This defaults to `../conf/facet_scanner.ini` relative to the script. |
