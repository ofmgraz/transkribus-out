#!/usr/bin/env python
import fetchteiheader
import glob
from os import path

source_directory = "testdir"
log_file_name = "fetchteiheader"
source_table = "../../goobi-processing/001_src/Quellen_OFM_Graz.xlsx"


for input_file in glob.glob(path.join(source_directory, "*.xml")):
    print(f"Parsing {input_file}")
    tei_source = fetchteiheader.TeiTree(input_file, source_table)
    with open(f'{input_file.rstrip(".xml")}_m2t.xml', "w") as f:
        f.write(fetchteiheader.ET.tostring(tei_source.tei.tree, pretty_print=True, encoding="unicode"))
