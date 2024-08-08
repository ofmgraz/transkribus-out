#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
from os import path
from sys import argv
from acdh_tei_pyutils.tei import TeiReader, ET

tkb_directory = "./data/editions"
headers_directory = "./tei_headers"
schema_file = "tei_ms.xsd"
i = 1
test = False
if len(argv) > 1:
    test = True
log = maketei.Log("0generate_body")

prev_filepath = ""

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
    xml_current_root = tei_source.tei.tree.getroot()
    if prev_filepath:
        prev = prev_filepath.split("/")[-1]
        xml_current_root.attrib['prev'] = prev
        xml_prev = TeiReader(prev_filepath)
        xml_prev_root = xml_prev.tree.getroot()
        xml_prev_root.attrib['next'] = filename
        with open(prev_filepath, "w") as f:
            f.write(ET.tostring(xml_prev_root, pretty_print=True, encoding="unicode"))
    prev_filepath = tkb_file
    with open(tkb_file, "w") as f:
        f.write(ET.tostring(xml_current_root, pretty_print=True, encoding="unicode"))
