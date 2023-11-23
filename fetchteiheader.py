#!/usr/bin/env python3
import glob
from lxml import etree
from urllib.request import urlopen
from datetime import datetime

source_directory = 'teitest'
logn = 'fetchteiheader'


nspaces = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "mets": "http://www.loc.gov/METS/"}


def log(logname, filename, arg='could not be parsed'):
    now = datetime.now()
    with open(f'{logname}.log', 'a') as f:
        f.write(f'{now.strftime("%Y/%m/%d %H:%M:%S")}\t'
                f'File `{filename}` {arg}\n')


def getheader(tree):
    header = tree.xpath('//mets:dmdSec', namespaces=nspaces)
    return header[0]


def getxml(docid):
    tree = False
    url = f'https://viewer.acdh.oeaw.ac.at/viewer/sourcefile?id={docid}'
    parser = etree.XMLParser()
    with urlopen(url) as u:
        tree = etree.parse(u, parser)
        root = tree.getroot()
    return root


for filename in glob.glob(f'{source_directory}/*.xml'):
    filename = 'A63_51.xml'
    if xmlmets := getxml(filename.rstrip('.xml')):
        header = getheader(xmlmets)
        print(header.tostring())
        break  # print(xmlmets)
