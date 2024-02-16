#!/usr/bin/env python
import csv
from sys import argv
# For a visual info output
dicti = {}


if len(argv) < 2:
    print('Use:\n\t./checkhash.py checksums-1.csv checksums-2.csv\n')
    exit()


def get_dict(filename):
    with open(filename) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            if row:
                dicti[row[0]] = row[1]
    return filename, dicti


def compare_sums(d1, d2, common):
    for element in common:
        OK = 'KO'
        if d1[1][element] == d2[1][element]:
            print(d1[1][element], d2[1][element])
            OK = 'OK'
        print(f'[{OK}]\t{element}')


def compare_dicts(dict1, dict2):
    # dict1 and dict2 are a list of "filename" and "string"
    intersect = []
    for item in dict1[1].keys():
        if item in dict2[1].keys():
            intersect.append(item)
        else:
            print(f'{item} not found in {dict2[0]}\n')
    for item in [x for x in dict2[1].keys() if x not in intersect]:
        if item not in dict1[1].keys():
            print(f'{item} not found in {dict1[0]}\n')
    return intersect


dict1 = get_dict(argv[1])
dict2 = get_dict(argv[2])
common_files = compare_dicts(dict1, dict2)
compare_sums(dict1, dict2, common_files)
