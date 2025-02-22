#!/usr/bin/env python3
import re
##############################################
# Solve duplicate xml:ids
with open("data/editions/1499840.xml") as f:
    text = f.read()
xmlids = re.findall(r'xml:id="(\S+)"', text)
xmlids.sort()
counter = 0
ant = ''
for i in xmlids:
    if i == ant:
        counter += 1
    else:
        counter = 0
        text = re.sub(f'"#({i})"', r'"#\1_0"', text)
    text = re.sub(f'"({i})"', fr'"\1_{counter}"', text, count=1)
    ant = i
with open("data/editions/1499840.xml", "w") as f:
    f.write(text)
