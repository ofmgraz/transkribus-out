#!/usr/bin/env python3
import glob
import os
from datetime import datetime
from acdh_tei_pyutils.tei import TeiReader

directory = "tei"
logn = "renamefiles"


# The first mandatory argument is the name of the log file, the second one is the file mentioned in the log entry.
def log(logname, filename, arg="could not be parsed"):
    now = datetime.now()
    with open(f"{logname}.log", "a") as f:
        f.write(f'{now.strftime("%Y/%m/%d %H:%M:%S")}\tFile `{filename}` {arg}\n')


def checkfile(filename):
    tree = False
    try:
        tree = TeiReader(filename)
    except Exception:
        log(logn, filename)
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
    if xmltei := checkfile(filename):
        new_name = os.path.join(directory, f"{getname(xmltei)}.xml")
        os.rename(filename, new_name)
