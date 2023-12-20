#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
from os import path

source_directory = "tei"
source_table = "../../goobi-processing/001_src/Quellen_OFM_Graz.xlsx"
schema_file = "tei_ms.xsd"
i = 1

log = maketei.Log("0make_tei")

for input_file in glob.glob(path.join(source_directory, "*.xml")):
    print(f"{i}\t\tParsing {input_file}")
    i += 1
    try:
        tei_source = maketei.TeiTree(source_table, input_file)
        with open(input_file, "w") as f:
            f.write(tei_source.printable)
    except Exception as e:
        log.print_log(input_file, e, stdout=True)
