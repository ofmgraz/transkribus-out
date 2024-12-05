#!/usr/bin/env python
# Executable file that calls library maketei
import maketei
import glob
from os import path
from sys import argv
from acdh_tei_pyutils.tei import ET
from concurrent.futures import ThreadPoolExecutor, as_completed

tkb_directory = "./data/editions"
headers_directory = "./data/constants/tei_headers"
schema_file = "tei_ms.xsd"
test = len(argv) > 1
log = maketei.Log("0generate_body")

prev_filepath = ""


def process_file(tkb_file):
    filename = path.basename(tkb_file)
    header_file = path.join(headers_directory, filename)
    try:
        tei_source = maketei.TeiBody(tkb_file, header_file)
    except Exception as e:
        error = f"{type(e).__name__} {__file__} {e.__traceback__.tb_lineno}"
        log.print_log(filename, error, stdout=True)
        return None, None, None

    xml_current_root = tei_source.tei.tree.getroot()
    return tkb_file, filename, xml_current_root


def update_links_and_write(prev_filepath, prev_filename, prev_xml_root, curr_filename, curr_xml_root):
    curr_xml_root.attrib['prev'] = f"https://id.acdh.oeaw.ac.at/ofmgraz/teidocs/{prev_filename}"
    prev_xml_root.attrib['next'] = f"https://id.acdh.oeaw.ac.at/ofmgraz/teidocs/{curr_filename}"
    print(f"update_links_and_write filepath {prev_filepath}")
    print(f"update_links_and_write filename {curr_filename}")

    with open(prev_filepath, "w") as f:
        f.write(ET.tostring(prev_xml_root, pretty_print=True, encoding="unicode"))

    with open(f"./data/editions/{curr_filename}", "w") as f:
        f.write(ET.tostring(curr_xml_root, pretty_print=True, encoding="unicode"))


tkb_files = glob.glob(path.join(tkb_directory, "*.xml"))

with ThreadPoolExecutor() as executor:
    future_to_file = {executor.submit(process_file, tkb_file): tkb_file for tkb_file in tkb_files}

    prev_filepath = None
    prev_filename = None
    prev_xml_root = None

    for future in as_completed(future_to_file):
        tkb_file, filename, xml_current_root = future.result()
        if tkb_file is None:
            continue

        if prev_filepath:
            update_links_and_write(prev_filepath, prev_filename, prev_xml_root, filename, xml_current_root)

        prev_filepath = tkb_file
        prev_filename = filename
        prev_xml_root = xml_current_root

    # Handle the last file
    if prev_filepath:
        with open(prev_filepath, "w") as f:
            f.write(ET.tostring(prev_xml_root, pretty_print=True, encoding="unicode"))
