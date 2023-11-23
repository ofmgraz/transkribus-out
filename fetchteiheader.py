#!/usr/bin/env python3
import os
from lxml  import etree
#from lxml.etree import parse
from datetime import datetime
import requests

nsmap = {None: 'http://www.tei-c.org/ns/1.0',
         'wib': 'https://wibarab.acdh.oeaw.ac.at/langDesc',
         'xi': 'http://www.w3.org/2001/XInclude',
         'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
         'tei': 'http://www.tei-c.org/ns/1.0',
         'mets': 'http://www.loc.gov/METS/v2',
         'mod': 'http://www.loc.gov/mods/v3',
         'xml': ''
         }


#parser = etree.XMLParser(recover=True)
source_directory = 'teitest'
logn = 'fetchteiheader'


def log(logname, filename, arg='could not be parsed'):
    now = datetime.now()
    with open(f'{logname}.log', 'a') as f:
        f.write(f'{now.strftime("%Y/%m/%d %H:%M:%S")}\t'
                f'File `{filename}` {arg}\n')


def checkremote(filename):
    root = content = False
    try:
        content = getxml(filename)
    except Exception:
        log(logn, filename, 'could not be retrieved')
    if content:
        tree = etree.fromstring(content)
        # root = tree.getroot()
#        try:
            #    tree = ElementTree.fromstring(content)
 #           print(tree)
            # tree = parse(response, parser)
  #          print('AAAAA')
 #           root = tree.getroot()
  #      except Exception:
   #         log(logn, filename)
    return tree


def getheader(root):
    # stub
    return root.xpath('.//mets:dmdSec', namespaces=nsmap)


def getxml(docid):
    url = f'https://viewer.acdh.oeaw.ac.at/viewer/sourcefile?id={docid}'
    response = requests.get(url)
    return response.content


directorycontents = os.listdir(source_directory)

for filename in directorycontents:
    filename = 'A63_51.xml'
    if xmlmets := checkremote(filename.rstrip('.xml')):
        header = getheader(xmlmets)
        print(header)
        break  # print(xmlmets)
