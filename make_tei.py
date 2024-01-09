#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
from os import path
from sys import argv

source_directory = "tei"
source_table = "Quellen_OFM_Graz.csv"
schema_file = "tei_ms.xsd"
i = 1
test = False
if len(argv) > 1:
    test = True
log = maketei.Log("0make_tei")

for input_file in glob.glob(path.join(source_directory, "*.xml")):
    print(f"{i}\t\tParsing {input_file}")
    i += 1
    if test:
        tei_source = maketei.TeiTree(source_table, input_file)
        with open(input_file, "w") as f:
            f.write(tei_source.printable)
    else:
        try:
            tei_source = maketei.TeiTree(source_table, input_file)
            with open(input_file, "w") as f:
                f.write(tei_source.printable)
        except Exception as e:
            error = f"{type(e).__name__} {__file__} {e.__traceback__.tb_lineno}"
            log.print_log(input_file, error, stdout=True)
