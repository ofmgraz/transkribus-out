#!/usr/bin/env python3
import glob
from lxml import etree
from urllib.request import urlopen
from datetime import datetime
import json
import os
import re

source_directory = 'teitest'
logn = 'fetchteiheader'
parser = etree.XMLParser()

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
    try:
        with urlopen(url) as u:
            tree = etree.parse(u, parser)
            root = tree.getroot()
    except Exception:
        log(logn, url)
    return root


def parseattributes(element, value):
    if 'date' in element.tag:
        attr = normalisedate(value)
        for x in attr:
            element.attrib[x] = attr[x]
    element.text = value
    return element


def normalisedate(date):
    try:
        year = int(date.lstrip('~').replace('x', '0').split()[0].split('-')[0].strip('.'))
    except Exception:
        log(logn, date, 'is not a valid date')
        year = 'nan'
    ddate = {'when': f'{year}'}
    if date.startswith('~'):
        ddate = {'notBefore': f'{year - 20}', 'notAfter': f'{year + 20}'}
    elif date.endswith('Jh.'):
        ddate = {'notBefore': f'{(year - 1) * 100}', 'notAfter':  f'{(year - 1) * 100 + 99}'}
    elif date.endswith('xx'):
        ddate = {'notBefore': f'{year}', 'notAfter': '{year + 99}'}
    elif re.findall(r'^\d{2}\-\d(?:/\d)*', date):
        ddate = {'notBefore': f'{year * 100}', 'notAfter': '{year + 99}'}
        second = date.split('-')[1]
        if second == '1':
            nb = year * 100
            na = nb + 50
        elif second == '2':
            na = year * 100 + 100
            nb = na - 50
        else:
            factor = int(second.split('/')[0]) / int(second.split('/')[1])
            na = year * 100 + int(factor * 100)
            nb = year * 100 + int(factor * 100) - 25
        ddate = {'notBefore': f'{nb}', 'notAfter': f'{na}'}
    return ddate


def printtree(tree):
    print(etree.tostring(tree, pretty_print=True, encoding=str))


def mets2tei(tei, metshdr, trs=dictionary):
    tei = 'teitest/test.xml'
    doc = etree.parse(tei, parser)
    doc = doc.getroot()
    for i in dictionary:
        add_nodes(doc, dictionary[i].split('/'), metshdr.xpath(f'.//{i}', namespaces=nsmap)[0].text)
    return doc


def add_nodes(teitree, nodes, value):
    if parent := teitree.xpath(f'tei:{nodes[0]}', namespaces=nsmap):
        parent = parent[0]
    else:
        parent = etree.SubElement(teitree, nodes[0])
    if len(nodes) > 1:
        add_nodes(parent, nodes[1:], value)
    else:
        parent = parseattributes(parent, value)
    return teitree


for filename in glob.glob(os.path.join(source_directory, '*.xml')):
    log(logn, filename, 'Parsing')
    # filename = 'A63_51.xml'
    if xmlmets := getxml(os.path.basename(filename).rstrip('.xml')):
        a = mets2tei(filename, xmlmets, dictionary)
        printtree(a)
