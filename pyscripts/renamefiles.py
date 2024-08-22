#!/usr/bin/env python3
import glob
import os
from acdh_tei_pyutils.tei import ET
from maketei import Log
import re

directory = "./data/editions"
log = Log("0rename")


def checkfile(filename):
    parser = ET.XMLParser(recover=True)
    tree = False
    try:
        tree = ET.parse(filename)
    except Exception:
        try:
            tree = ET.parse(filename, parser=parser)
        except Exception as e:
            log.print_log(filename, e, True)
    return tree.getroot()


def getname(root):
    name = False
    regex = re.compile(r'A-Gf_(\w)_*(\d{1,2}_\S{2,3})_.*')
    docid = root.xpath('//tei:teiHeader//tei:title[@type="main"]',
                       namespaces={"tei": "http://www.tei-c.org/ns/1.0"})[0].text
    name = re.sub(regex, r"\g<1>\g<2>", docid)
    if name[0] in '0123456789':
        name = re.sub(r"^(\d+_)", r"A\g<1>", name)
    return name


for current_filepath in glob.glob(os.path.join(directory, "*.xml")):
    try:
        xmltei = checkfile(current_filepath)
        current_file = f"{getname(xmltei)}.xml"
        new_filepath = os.path.join(directory, current_file)
        os.rename(current_filepath, new_filepath)
        print(f"{current_filepath}\t->\t{new_filepath}")
    except Exception as e:
        log.print_log(current_filepath, e, True)
