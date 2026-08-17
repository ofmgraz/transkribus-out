#!/usr/bin/env python3
import glob
import re


def repair_file(filename):
    with open(filename) as source:
        text = source.read()

    seen = {}

    def replace_id(match):
        value = match.group(1)
        occurrence = seen.get(value, 0)
        seen[value] = occurrence + 1
        if occurrence == 0:
            return match.group(0)
        return f'xml:id="{value}_{occurrence}"'

    repaired = re.sub(r'xml:id="([^\"]+)"', replace_id, text)
    if repaired != text:
        with open(filename, "w") as target:
            target.write(repaired)
        print(f"repaired duplicate xml:id values in {filename}")


for filename in glob.glob("data/editions/*.xml"):
    repair_file(filename)
