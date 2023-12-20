#!/usr/bin/env python3
import glob
import os
from acdh_tei_pyutils.tei import TeiReader
from maketei import Log

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
    docids = root.any_xpath('//tei:teiHeader//tei:title[@type="main"]')
    for i in docids:
        parts = i.text.split("_")
        # Not being sure of whether the content of each element <title type="main"> is what we are looking for, we get
        # the first one that follows the format we're expecting to find to improve our chances
        if len(parts) > 2:
            name = f"{parts[1]}_{parts[2]}"
            break
    return name


for filename in glob.glob(os.path.join(directory, "*.xml")):
    try:
        xmltei = checkfile(filename)
        new_name = os.path.join(directory, f"{getname(xmltei)}.xml")
        os.rename(filename, new_name)
        print(f"{filename}\t->\t{new_name}")
    except Exception as e:
        log.print_log(filename, e, True)
