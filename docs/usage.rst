Useage
======

.. warning::
    This code base has been developed to work with the JASMIN Lotus cluster
    and will need adaptation to work in any other environment.

The command line tool expects you to run from within a *collection* i.e. a group
of files which share a common structure or processing class. The facet scanner
maps file paths to handlers, these handlers know how to interact with the files
to extract facets which will be useful when searching the data.


The command line entry point:

.. program-output:: facet_scanner -h


The script works by:

1. Run elasticsearch query to return all the files under the given path
2. Save each page (size given by :code:`--num-files`) into an intermediate directory :code:`processing_path`
3. Once this process has completed, each page file is submitted to lotus using :code:`facet_scanner/scripts/lotus_facet_scanner.py`
4. This runs the facet extraction on the files listed in the page file using lotus, writing to elasticsearch

There may be some files which do not complete in lotus. The lotus script deletes the page file on successful completion
of the facet extraction.

On completion of all the scheduled jobs, checking the intermediate directory will show you which files did not run. In most
cases, a simple re-run of the :code:`facet_scanner` script with the :code:`--rerun` flag will clear them. This :code:`--rerun`
flag ignores the step 1 and 2 above and skips to sending the jobs to lotus.