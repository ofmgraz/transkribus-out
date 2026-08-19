#!/bin/bash
mkdir -p tmp
for teifile in data/editions/*xml; do
	pyscripts/add_attr_notation.py $teifile
done
rm -rf tmp
