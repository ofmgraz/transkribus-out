#!/usr/bin/env python3
import hashlib
from datetime import datetime
import os
import sys

now = datetime.now().strftime("%Y-%m-%dT%H:%M")
output_file = "checksum.csv"
file_list = []
subdirs = []
with open(output_file, "w") as out_file:
    out_file.write(f'FILENAME,{now}')


def get_hash(input_file):
    with open(input_file, "rb") as in_file:
        file_contents = in_file.read()
        md5_hash = hashlib.md5(file_contents).hexdigest()
    return md5_hash


def parse_dir(path):
    base_name = os.path.basename(path)
    if os.path.isfile(path):
        md5 = get_hash(path)
        with open(output_file, "a") as out_file:
            out_file.write(f'{base_name},{md5}\n')
        print(f"[OK]\t{base_name}:\t{md5}")
    elif os.path.isdir(path):
        print(f"Entering in {path}")
        for subfile in os.listdir(path):
            parse_dir(os.path.join(path, subfile))
    else:
        print(f"[KO]\t{path}: Filetype unknown.")


for folder in sys.argv[1:]:
    parse_dir(folder)
