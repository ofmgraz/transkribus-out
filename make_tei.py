#!/usr/bin/env python
import maketei
import glob
from os import path

source_directory = "testdir"
log_file_name = "fetchteiheader"
source_table = "../../goobi-processing/001_src/Quellen_OFM_Graz.xlsx"
schema_file = "tei_ms.xsd"


for input_file in glob.glob(path.join(source_directory, "*.xml")):
    print(f"Parsing {input_file}")
    tei_source = maketei.TeiTree(source_table, input_file)
    # fetchteiheader.TEIValidator(tei_source, schema_file)
    with open(f'{input_file.rstrip(".xml")}_m2t.xml', "w") as f:
        f.write(
            maketei.ET.tostring(
                tei_source.tei.tree, pretty_print=True, encoding="unicode"
            )
        )
