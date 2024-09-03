#!/usr/bin/env python
import os
from pathlib import Path
import glob
from saxonche import PySaxonProcessor

# Constants
XSLT = "https://csae8092.github.io/page2tei/page2tei-0.xsl"
METS_DIR = Path("./data/mets")
TEI_DIR = Path("./data/editions")
col_id = "216937"

# Prepare directories and files
files = glob.glob(f"{METS_DIR}/{col_id}/*_mets.xml")
os.makedirs(TEI_DIR, exist_ok=True)

def transform_file(x):
    try:
        tail = os.path.split(x)[-1]
        doc_id = tail.split("_")[0]
        tei_file = f"{doc_id}.xml"
        tei_path = os.path.join(TEI_DIR, tei_file)
        print(f"Transforming METS: {x} to {tei_path}")

        # Initialize the processor and process one file at a time
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_parameter("combine", proc.make_boolean_value(True))
            xsltproc.set_parameter("ab", proc.make_boolean_value(True))

            document = proc.parse_xml(xml_file_name=x)
            executable = xsltproc.compile_stylesheet(stylesheet_file=XSLT)
            output = executable.transform_to_string(xdm_node=document)
            output = output.replace(' type=""', "")

            # Write the output to a TEI file
            with open(tei_path, "w") as f:
                f.write(output)

    except Exception as e:
        print(f"Error processing {x}: {e}")

# Sequential Processing
for file in files:
    transform_file(file)