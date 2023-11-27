#!/usr/bin/env python3
import glob
from urllib.request import urlopen
from datetime import datetime
from acdh_tei_pyutils.tei import TeiReader, TeiEnricher
from lxml import etree as ET
import json
import os
import re

source_directory = 'testdir'
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
    print(url)
    try:
        root = TeiReader(url)
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
        year = re.sub('x+', '00', date).lstrip('~').split()[0]
        year = int(year.split('-')[0].strip('.'))
    except Exception:
        log(logn, date, 'is not a valid date')
        year = 'nan'
    ddate = {'when': f'{year}'}
    if date.startswith('~'):
        ddate = {'notBefore': f'{year - 20}', 'notAfter': f'{year + 20}'}
    elif date.endswith('Jh.'):
        ddate = {'notBefore': f'{(year - 1) * 100}', 'notAfter':  f'{(year - 1) * 100 + 99}'}
    elif date.endswith('x'):
        ddate = {'notBefore': f'{year}', 'notAfter': f'{year + 99}'}
    elif re.findall(r'^\d{2}\-\d(?:/\d)*', date):
        second = date.split('-')[1]
        if second in '12':
            factor = 100 / int(second)
            nb = year * 100 - factor
            na = nb + 50
        else:
            factor = int(second.split('/')[0]) * 100 / int(second.split('/')[1])
            na = year * 100 + factor
            nb = year * 100 + factor - 25
        ddate = {'notBefore': f'{nb}', 'notAfter': f'{na}'}
    return ddate


def mets2tei(tei, metshdr, trs=dictionary):
    teidoc = TeiEnricher(tei)
    for i in dictionary:
        add_nodes(teidoc.tree, dictionary[i].split('/'), metshdr.tree.xpath(f'//{i}', namespaces=nsmap)[0].text)
    return teidoc


def add_nodes(teitree, nodes, value):
    new_node = parseattributes(ET.Element('{http://www.tei-c.org/ns/1.0}' + nodes[0]), '')
    if len(nodes) > 1:
        if parent := teitree.xpath(f'//tei:{nodes[0]}', namespaces=nsmap):
            parent = parent[0]
        else:
            teitree.append(new_node)
            parent = teitree.xpath(f'//tei:{nodes[0]}', namespaces=nsmap)[0]
        add_nodes(parent, nodes[1:], value)
    else:
        new_node = parseattributes(new_node, value)
        teitree.append(new_node)
    return teitree


for filename in glob.glob(os.path.join(source_directory, '*.xml')):
    log(logn, filename, 'Parsing')
    # filename = 'A63_51.xml'
    print(os.path.basename(filename).rstrip('.xml'))
    if xmlmets := getxml(os.path.basename(filename).rstrip('.xml')):
        a = mets2tei(filename, xmlmets, dictionary)
        a.tree_to_file(f'{filename}_m2t.xml')
        # break
