#!/usr/bin/env python
import csv
from sys import argv
# For a visual info output

red = '\033[92mOK\033[00m'
green = '\033[91mKO\033[00m'
yellow = '\033[93m--\033[00m'



if len(argv) < 2:
    print('Use:\n\t./checkhash.py checksums-1.csv checksums-2.csv\n')
    exit()


def get_dict(filename):
    dicti = {}
    with open(filename) as f:
        for row in csv.reader(f, delimiter=','):
            if row:
                dicti[row[0]] = row[1]
    return [filename, dicti]


def compare_sums(d1, d2, common):
    for element in common:
        OK = red
        if d1[1][element] == d2[1][element]:
            OK = green
        print(f'[{OK}]\t{element}')


def compare_dicts(dict1, dict2):
    # dict1 and dict2 are a list of "filename" and "string"
    intersect = []
    for item in dict1[1].keys():
        if item in dict2[1].keys():
            intersect.append(item)
        else:
            print(f'[{yellow}]\t{item} from {dict1[0]} not found in {dict2[0]}')
    for item in [x for x in dict2[1].keys() if x not in intersect]:
        if item not in dict1[1].keys():
            print(f'[{yellow}]\t{item} from {dict2[0]} not found in {dict1[0]}')
    return intersect


dict1 = get_dict(argv[1])
dict2 = get_dict(argv[2])
common_files = compare_dicts(dict1, dict2)
compare_sums(dict1, dict2, common_files)
