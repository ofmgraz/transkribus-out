# ofmgraz  transkribus-export

Automagically export and upconvert data from [Transkribus](https://readcoop.eu/) collections into TEI/XML using [page2tei](https://github.com/dariok/page2tei) from @dariok and [acdh-transkribus-pyutils](https://github.com/acdh-oeaw/acdh-transkribus-utils).

## Run workflow

* add the Transkribus collection IDs to `./col_ids.txt` (each ID on a new line)

### Option A: Locally
* create a virtual environment `python -m venv venv`
* update pip to latest version and install needed python packages `pip install -U pip && pip install -r requirements.txt`
* copy/rename `dummy.env` to `secret.env` and add your Transkribus and Baserow credentials  
* run `source ./secret.env` to set your Transkribus credentials as environment variables.
* run `shellscripts/full_workflow.sh`

### Option B: As a GitHub Action
* Set the GH secrets `TR_USER` and `TR_PASSWORD` for your GitHub Actions with your Transkribus credentials
* Set the GH secrets `BASEROW_USER`, `BASEROW_PW`, and `BASEROW_READ_TOKEN` with your Baserow credentials
* run Action [Download and Transform](https://github.com/ofmgraz/transkribus-out/actions/workflows/download_collection.yml)


-----
created with [transkribus-export-cookiecutter](https://github.com/acdh-oeaw/transkribus-export-cookiecutter)
