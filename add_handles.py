#!/usr/bin/env python3
import csv
import sys
from acdh_tei_pyutils.tei import TeiReader, ET

input_files = sys.argv
if len(input_files) > 1:
    d = {}
    with open('handles.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            d[row["file"]] = row["handle_id"]
    for filename in input_files[1:]:
        print(filename)
        tree = TeiReader(filename)
        basename = filename.split('/')[-1]
        if len(tree.any_xpath('.//tei:publicationStmt/tei:idno[@type="handle"]')) < 1:
            pubstmt = tree.any_xpath('.//tei:publicationStmt')[0]
            print(pubstmt)
            ET.SubElement(pubstmt, "idno", attrib={"type": "handle"}).text = d[basename]
            tree.tree_to_file(filename)
