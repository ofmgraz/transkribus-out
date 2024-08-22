# ofmgraz  transkribus-export

Automagically export and upconvert data from [Transkribus](https://readcoop.eu/) collections into TEI/XML using [page2tei](https://github.com/dariok/page2tei) from @dariok and [acdh-transkribus-pyutils](https://github.com/acdh-oeaw/acdh-transkribus-utils).

## initial (local) set up

* create a virtual environment `python -m venv venv`
* update pip to latest version and install needed python packages `pip install -U pip && pip install -r requirements.txt`
* copy/rename `dummy.env` to `secret.env` and add your Transkribus credentials

## export the data

* add the Transkribus collection IDs to `./col_ids.txt` (each ID on a new line)
run `source ./secret.env` to set your Transkribus credentials as environment variables.
* run `python download_and_transform.py`

## Rename files

* Renames Transkribus files to descriptive filenames to match their METS counterparts and the table
* Run `./renamefiles.py`

## Create TEI
* Creates TEI files with the required teiHeader
* Run `./make_tei.py`

## GitHub-Actions

* Create GitHub secrets called `TR_USER` and `TR_PW` and add your Transkribus credentials
* Go to GitHub Actions and start the workflow -> the exported METS and TEI/XML files will be checked into your repo

-----
created with [transkribus-export-cookiecutter](https://github.com/acdh-oeaw/transkribus-export-cookiecutter)
