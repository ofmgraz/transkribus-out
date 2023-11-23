#!/usr/bin/env python3
import os
from lxml import etree
from lxml.etree import parse
from datetime import datetime

nsmap = {None: 'http://www.tei-c.org/ns/1.0',
         'wib': 'https://wibarab.acdh.oeaw.ac.at/langDesc',
         'xi': 'http://www.w3.org/2001/XInclude',
         'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
         'tei': 'http://www.tei-c.org/ns/1.0',
         'xml': ''
         }
parser = etree.XMLParser(recover=True)
directory = 'tei'


def log(filename, arg='could not be parsed'):
    now = datetime.now()
    with open('renamefiles.log', 'a') as f:
        f.write(f'{now.strftime("%Y/%m/%d %H:%M:%S")}\t'
                f'File `{filename}` {arg}\n')


def checkfile(filename):
    root = False
    if os.path.exists(filename):
        try:
            tree = parse(filename, parser)
            root = tree.getroot()
        except Exception:
            log(filename)
    else:
        log(filename, 'does not exist')
    return root


def getname(root):
    name = False
    docids = root.findall('.//tei:title[@type="main"]', namespaces=nsmap)
    for i in docids:
        parts = i.text.split('_')
        if len(parts) > 2:
            name = f'{parts[1]}_{parts[2]}'
            break
    return name


directorycontents = os.listdir(directory)

for filename in directorycontents:
    old_name = f'{directory}/{filename}'
    if xmltei := checkfile(old_name):
        new_name = f'{directory}/{getname(xmltei)}.xml'
        os.rename(old_name, new_name)
