#!/usr/bin/env python
import os
import glob
from saxonche import PySaxonProcessor

XSLT = "https://csae8092.github.io/page2tei/page2tei-0.xsl"
METS_DIR = glob.glob("./mets")
TEI_DIR = glob.glob("./data/editions")
col_id = "216937"
files = glob.glob(f"{METS_DIR}/{col_id}/*_mets.xml")
os.makedirs(TEI_DIR, exist_ok=True)

for x in files:
    tail = os.path.split(x)[-1]
    doc_id = tail.split("_")[0]
    tei_file = f"{doc_id}.xml"
    print(f"transforming mets: {x} to {tei_file}")
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        xsltproc.set_parameter("combine", proc.make_boolean_value(True))
        xsltproc.set_parameter("ab", proc.make_boolean_value(True))
        document = proc.parse_xml(xml_file_name=x)
        executable = xsltproc.compile_stylesheet(stylesheet_file=XSLT)
        output = executable.transform_to_string(xdm_node=document)
        output = output.replace(' type=""', "")
        with open(os.path.join(TEI_DIR, tei_file), "w") as f:
            f.write(output)
