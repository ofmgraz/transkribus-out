# ofmgraz  transkribus-export

Automagically export and upconvert data from [Transkribus](https://readcoop.eu/) collections into TEI/XML using [page2tei](https://github.com/dariok/page2tei) from @dariok and [acdh-transkribus-pyutils](https://github.com/acdh-oeaw/acdh-transkribus-utils).




## Run workflow as a GitHub Action

### Full run (It may take over an hour)
* run Action [Download and Transform](https://github.com/ofmgraz/transkribus-out/actions/workflows/download_collection.yml)


### Download sources
This action fetches MET files from Transkribus. It does not perform further actions, which should be done idependently nas described below.
* run Action [Download and Transform](https://github.com/ofmgraz/transkribus-out/actions/workflows/jusdownload.yml)

### Regenerate TEI
This action generates XML-TEI files from the header seeds and the METS files fetched from Transkribus. Note that it will replicate the original files if neither the METS files nor the headers seeds have been changed.
* run Action [Download and Transform](https://github.com/ofmgraz/transkribus-out/actions/workflows/justtransform.yml)

### Regenerate header seeds
After changing the Baserow table  where the metadata is fetched from, run the following action to regenerate the seeds used to create the TEI-files. This does not regenerate said TEI files, which has to be made with another action.
* run Action [Download and Transform](https://github.com/ofmgraz/transkribus-out/actions/workflows/regenerate_headers.yml)


## Run workflow Locally
* add the Transkribus collection IDs to `./col_ids.txt` (each ID on a new line)
* create a virtual environment `python -m venv venv`
* update pip to latest version and install needed python packages `pip install -U pip && pip install -r requirements.txt`
* copy/rename `dummy.env` to `secret.env` and add your Transkribus and Baserow credentials  
* run `source ./secret.env` to set your Transkribus credentials as environment variables.
* run `shellscripts/full_workflow.sh`


-----
created with [transkribus-export-cookiecutter](https://github.com/acdh-oeaw/transkribus-export-cookiecutter)
