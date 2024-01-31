#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
from os import path
from sys import argv

tkb_directory = "./data/editions"
headers_directory = "./tei_headers"
schema_file = "tei_ms.xsd"
i = 1
test = False
if len(argv) > 1:
    test = True
log = maketei.Log("0generate_body")

for tkb_file in glob.glob(path.join(tkb_directory, "*.xml")):
    print(f"{i}\t\tParsing {tkb_file}")
    filename = tkb_file.split("/")[-1]
    header_file = path.join(headers_directory, filename)
    i += 1
    if test:
        tei_source = maketei.TeiBody(tkb_file, header_file)
    else:
        try:
            tei_source = maketei.TeiBody(tkb_file, header_file)
        except Exception as e:
            error = f"{type(e).__name__} {__file__} {e.__traceback__.tb_lineno}"
            log.print_log(filename, error, stdout=True)
    with open(tkb_file, "w") as f:
        f.write(tei_source.printable)
