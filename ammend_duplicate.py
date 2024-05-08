#!/usr/bin/env python3
import re
##############################################
# Solve duplicate xml:ids
with open("data/editions/1499840.xml") as f:
    text = f.read()
xmlids = re.findall(r'xml:id=(\S+)', text)
counter = 0
xmlids.sort()
ant = ''
for i in xmlids:
    if i == ant:
        counter += 1
    else:
        counter = 0
    re.sub(f'"{i}"', f'"{i}_{counter}"', text, count=1)
    ant = i
with open("data/editions/1499840.xml", 'w') as file:
    file.write(text)
