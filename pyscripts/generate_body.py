#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
from os import path
from sys import argv
from acdh_tei_pyutils.tei import TeiReader, ET

# Directory paths
tkb_directory = "./data/editions"
headers_directory = "./data/constants/tei_headers"
schema_file = "tei_ms.xsd"
log = maketei.Log("0generate_body")

# Check if running in test mode
test = len(argv) > 1

# Initialize previous file path
prev_filepath = ""

# Cache TeiReader objects to minimize repeated file reads
tei_cache = {}

# Process each XML file in the directory
for i, tkb_file in enumerate(glob.glob(path.join(tkb_directory, "*.xml")), start=1):
    print(f"{i}\t\tParsing {tkb_file}")
    filename = path.basename(tkb_file)
    header_file = path.join(headers_directory, filename)
    
    # Process the TEI body
    try:
        if test:
            tei_source = maketei.TeiBody(tkb_file, header_file)
        else:
            if filename not in tei_cache:
                tei_cache[filename] = maketei.TeiBody(tkb_file, header_file)
            tei_source = tei_cache[filename]
    except Exception as e:
        error = f"{type(e).__name__} {__file__} {e.__traceback__.tb_lineno}"
        log.print_log(filename, error, stdout=True)
        continue

    xml_current_root = tei_source.tei.tree.getroot()

    # Link previous and next files
    if prev_filepath:
        prev = path.basename(prev_filepath)
        xml_current_root.attrib['prev'] = f"https://id.acdh.oeaw.ac.at/ofmgraz/teidocs/{prev}"

        # Reuse TeiReader from cache if available
        if prev not in tei_cache:
            xml_prev = TeiReader(prev_filepath)
            tei_cache[prev] = xml_prev
        else:
            xml_prev = tei_cache[prev]
        
        xml_prev_root = xml_prev.tree.getroot()
        xml_prev_root.attrib['next'] = f"https://id.acdh.oeaw.ac.at/ofmgraz/teidocs/{filename}"
        
        with open(prev_filepath, "w") as f:
            f.write(ET.tostring(xml_prev_root, pretty_print=True, encoding="unicode"))
    
    prev_filepath = tkb_file
    
    with open(tkb_file, "w") as f:
        f.write(ET.tostring(xml_current_root, pretty_print=True, encoding="unicode"))