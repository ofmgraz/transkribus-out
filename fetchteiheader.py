#!/usr/bin/env python3
import glob
from lxml import etree
from urllib.request import urlopen
from datetime import datetime
import json
import os

source_directory = 'teitest'
logn = 'fetchteiheader'

with open('mets2tei.json', 'r') as f:
    dictionary = json.load(f)

nsmap = {"tei": "http://www.tei-c.org/ns/1.0",
         "mets": "http://www.loc.gov/METS/",
         "mods": "http://www.loc.gov/mods/v3",
         "dv": "http://dfg-viewer.de/"}


def log(logname, filename, arg='could not be parsed'):
    now = datetime.now()
    with open(f'{logname}.log', 'a') as f:
        f.write(f'{now.strftime("%Y/%m/%d %H:%M:%S")}\t'
                f'File `{filename}` {arg}\n')


def getxml(docid):
    root = False
    url = f'https://viewer.acdh.oeaw.ac.at/viewer/sourcefile?id={docid}'
    parser = etree.XMLParser()
    try:
        print(url)
        with urlopen(url) as u:
            tree = etree.parse(u, parser)
            root = tree.getroot()
    except Exception:
        log(logn, url)
    return root


def printtree(tree):
    print(etree.tostring(tree, pretty_print=True, encoding=str))


def mets2tei(tei, metshdr, trs=dictionary):
    for i in dictionary:
        print(i, dictionary[i])
        value = metshdr.xpath(f'.//{i}', namespaces=nsmap)[0].text
        print(value)


for filename in glob.glob(os.path.join(source_directory, '*.xml')):
    # filename = 'A63_51.xml'
    print(filename)
    if xmlmets := getxml(os.path.basename(filename).rstrip('.xml')):
        mets2tei(filename, xmlmets, dictionary)
        break   # For testing purposes
