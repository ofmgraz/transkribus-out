#!/usr/bin/env python
import os
from pathlib import Path
import glob
import requests
from saxonche import PySaxonProcessor
from concurrent.futures import ThreadPoolExecutor

# Constants
XSLT_URL = "https://csae8092.github.io/page2tei/page2tei-0.xsl"
LOCAL_XSLT = "page2tei-0.xsl"
METS_DIR = Path("./data/mets")
TEI_DIR = Path("./data/editions")
col_id = "216937"

# Download the main XSLT file if not already downloaded
if not os.path.exists(LOCAL_XSLT):
    response = requests.get(XSLT_URL)
    with open(LOCAL_XSLT, "wb") as f:
        f.write(response.content)

# Update the LOCAL_XSLT file to reference local copies of the included XSLT files
with open(LOCAL_XSLT, "r") as f:
    xslt_content = f.read()

xslt_content = xslt_content.replace('href="tokenize.xsl"', 'href="./tokenize.xsl"')
xslt_content = xslt_content.replace(
    'href="combine-continued.xsl"', 'href="./combine-continued.xsl"'
)
xslt_content = xslt_content.replace(
    'href="string-pack.xsl"', 'href="./string-pack.xsl"'
)

with open(LOCAL_XSLT, "w") as f:
    f.write(xslt_content)


# Download and save the other XSLT files locally
def download_xslt(url, local_path):
    if not os.path.exists(local_path):
        response = requests.get(url)
        with open(local_path, "wb") as f:
            f.write(response.content)


download_xslt("https://csae8092.github.io/page2tei/tokenize.xsl", "tokenize.xsl")
download_xslt(
    "https://csae8092.github.io/page2tei/combine-continued.xsl", "combine-continued.xsl"
)
download_xslt("https://csae8092.github.io/page2tei/string-pack.xsl", "string-pack.xsl")

# Prepare directories and files
files = glob.glob(f"{METS_DIR}/{col_id}/*_mets.xml")
os.makedirs(TEI_DIR, exist_ok=True)


def transform_file(file):
    try:
        tail = os.path.split(file)[-1]
        doc_id = tail.split("_")[0]
        tei_file = f"{doc_id}.xml"
        tei_path = os.path.join(TEI_DIR, tei_file)
        print(f"Transforming METS: {file} to {tei_path}")

        document = proc.parse_xml(xml_file_name=file)
        output = executable.transform_to_string(xdm_node=document)
        output = output.replace(' type=""', "")

        # Write the output to a TEI file
        with open(tei_path, "w") as f:
            f.write(output)

    except Exception as e:
        print(f"Error processing {file}: {e}")


# Initialize the processor and XSLT once
with PySaxonProcessor(license=False) as proc:
    xsltproc = proc.new_xslt30_processor()
    xsltproc.set_parameter("combine", proc.make_boolean_value(True))
    xsltproc.set_parameter("ab", proc.make_boolean_value(True))

    executable = xsltproc.compile_stylesheet(stylesheet_file=LOCAL_XSLT)

    # Parallel processing
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(transform_file, files)
