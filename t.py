#!/usr/bin/env python3
import os
import maketei

BASEROW_USER = os.environ.get("BASEROW_USER")
BASEROW_PW = os.environ.get("BASEROW_PW")
BASEROW_TOKEN = "ZZlOZUBpKlBapPL09wQyuwKrdgCjrJnP"

template = "template.xml"
output_directory = "./tei_headers"
schema_file = "tei_ms.xsd"
source_table = "json/InputData.json"
source_directory = "./data/editions"
source_file = 'S1_74.xml'

output_file = os.path.join(output_directory, source_file)
input_file = os.path.join(source_directory, source_file)

tei_source = maketei.TeiHeader(input_file, template, source_table)
