#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
import os
from sys import argv
from acdh_baserow_pyutils import BaseRowClient

if len(argv) > 1:
    test = True
else:
    test = False
if not test:
    BASEROW_DB_ID = 488
    BASEROW_URL = "https://baserow.acdh-dev.oeaw.ac.at/api/"
    BASEROW_TOKEN = "ZZlOZUBpKlBapPL09wQyuwKrdgCjrJnP"
    BASEROW_USER = os.environ.get("BASEROW_USER")
    BASEROW_PW = os.environ.get("BASEROW_PW")
    br_client = BaseRowClient(BASEROW_USER, BASEROW_PW, BASEROW_TOKEN, br_base_url=BASEROW_URL)
    jwt_token = br_client.get_jwt_token()
    os.makedirs("tmp", exist_ok=True)
    files = br_client.dump_tables_as_json(BASEROW_DB_ID, folder_name="tmp")
source_directory = "./data/editions"
source_table = os.path.join("tmp", "InputData.json")
schema_file = "tei_ms.xsd"
output_directory = "./data/constants/tei_headers"
template = "./data/constants/template.xml"

i = 1

if not os.path.isdir(output_directory):
    os.mkdir(output_directory)

if len(argv) > 1:
    test = True
log = maketei.Log("0make_tei")

for input_file in glob.glob(os.path.join(source_directory, "*.xml")):
    print(f"{i}\t\tParsing {input_file}")
    i += 1
    if test:
        tei_source = maketei.TeiHeader(input_file, template, source_table)
    else:
        try:
            tei_source = maketei.TeiHeader(input_file, template, source_table)
        except Exception as e:
            error = f"{type(e).__name__} {__file__} {e.__traceback__.tb_lineno}"
            log.print_log(input_file, error, stdout=True)
    output_file = os.path.join(output_directory, input_file.split('/')[-1])
    if tei_source:
        with open(output_file, "wb") as f:
            f.write(tei_source.printable)
#[os.remove(os.path.join("json", f)) for f in os.listdir("json")]
#os.rmdir("json")
