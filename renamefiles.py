#!/usr/bin/env python3
import glob
import os
from acdh_tei_pyutils.tei import TeiReader
from maketei import Log
import re

directory = "tei"
log = Log("0rename")


def checkfile(filename):
    tree = False
    try:
        tree = TeiReader(filename)
    except Exception as e:
        log.print_log(filename, e, True)
    return tree


def getname(root):
    name = False
    regex = re.compile(r'A-Gf_(\w)_*(\d{1,2}_\S{2,3})_.*')
    docid = root.any_xpath('//tei:teiHeader//tei:title[@type="main"]')[0].text
    name = re.sub(regex, r'\g<1>\g<2>', docid)
    return name


for filename in glob.glob(os.path.join(directory, "*.xml")):
    try:
        xmltei = checkfile(filename)
        new_name = os.path.join(directory, f"{getname(xmltei)}.xml")
        os.rename(filename, new_name)
        print(f"{filename}\t->\t{new_name}")
    except Exception as e:
        log.print_log(filename, e, True)
