#!/bin/bash
for teifile in data/editions/*xml; do
	pyscripts/add_attr_notation.py $teifile
done
