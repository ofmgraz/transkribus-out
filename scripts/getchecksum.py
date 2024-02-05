#!/usr/bin/env python
import hashlib
from datetime import datetime
import os
import sys

now = datetime.now().strftime("%Y-%m-%dT%H:%M")
output_file = "checksum.csv"


def get_hash(input_file):
    with open(input_file, "rb") as f:
        file_contents = f.read()
        md5_hash = hashlib.md5(file_contents).hexdigest()
    return md5_hash


def parse_dir(path, file_list=[]):
    print(f'Reading directory "{path}"')
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fullpath = os.path.join(dirpath, f)
            file_list.append(f'"{f}",{get_hash(fullpath)},{now}\n')
            print(f"[OK]\t{fullpath}")
        [parse_dir(os.path.join(dirpath, d), file_list) for d in dirnames]
    return file_list


file_list = parse_dir(sys.argv[1])
with open(output_file, "w") as f:
    f.writelines(file_list)
