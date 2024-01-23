#!/usr/bin/env python3
import glob
import os
from lxml import etree as ET
from maketei import Log
import re

directory = "./data/editions"
log = Log("0simplifytkb")


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


for filename in glob.glob(os.path.join(directory, "*.xml")):
    pass
