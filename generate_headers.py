#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
from os import path, mkdir
from sys import argv

source_directory = "./data/editions"
source_table = "Quellen_OFM_Graz.csv"
schema_file = "tei_ms.xsd"
output_directory = "./tei_headers"
template = "template.xml"


i = 1
test = False

if not path.isdir(output_directory):
    mkdir(output_directory)

if len(argv) > 1:
    test = True
log = maketei.Log("0make_tei")

for input_file in glob.glob(path.join(source_directory, "*.xml")):
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
    output_file = path.join(output_directory, input_file.split('/')[-1])
    if tei_source:
        with open(output_file, "w") as f:
            f.write(tei_source.printable)
