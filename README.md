# ofmgraz  transkribus-export

Automagically export and upconvert data from [Transkribus](https://readcoop.eu/) collections into TEI/XML using [page2tei](https://github.com/dariok/page2tei) from @dariok and [acdh-transkribus-pyutils](https://github.com/acdh-oeaw/acdh-transkribus-utils).




## Run workflow as a GitHub Action

### Full run
This action runs the whole pipeline. It recreates everything from scratch and may take a while, depending on the load of both Transkribus and GitHub. It may be done as fast as in 15 minutes, but it may also take over an hour. 
* run Action [Download and Transform](https://github.com/ofmgraz/transkribus-out/actions/workflows/download_collection.yml)

### Running steps independently
#### Download sources
This action fetches MET files from Transkribus. It does not perform further actions, which should be done idependently as described below. This may take up to 45 min.
* run Action [Just download](https://github.com/ofmgraz/transkribus-out/actions/workflows/jusdownload.yml)

#### Regenerate XML-TEI files
This action generates XML-TEI files from the header seeds and the METS files fetched from Transkribus. It will replicate the original files if neither the METS files nor the headers seeds have been changed. This may take up to 20 min.
* run Action [Just transform](https://github.com/ofmgraz/transkribus-out/actions/workflows/justtransform.yml)

#### Regenerate header seeds
After changing the Baserow table  where the metadata is fetched from, run the following action to regenerate the seeds used to create the TEI files. This does not regenerate said TEI files, which has to be made with another action.
* run Action [Regenerate headers](https://github.com/ofmgraz/transkribus-out/actions/workflows/regenerate_headers.yml)


## Run workflow Locally
* add the Transkribus collection IDs to `./col_ids.txt` (each ID on a new line)
* create a virtual environment `python -m venv venv`
* update pip to latest version and install needed python packages `pip install -U pip && pip install -r requirements.txt`
* copy/rename `dummy.env` to `secret.env` and add your Transkribus and Baserow credentials  
* run `source ./secret.env` to set your Transkribus credentials as environment variables.
* run `shellscripts/full_workflow.sh`



-----
created with [transkribus-export-cookiecutter](https://github.com/acdh-oeaw/transkribus-export-cookiecutter)
