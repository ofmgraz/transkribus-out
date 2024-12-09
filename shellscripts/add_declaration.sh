#!/bin/bash
if [[ -z $1 ]] ; then
	XMLPATH="data/editions"
else
	XMLPATH="$1"
fi

sed -i $'2s/^/<?xml-model href="https:\\/\\/hdl.handle.net\\/21.11115\\/0000-0014-4403-A" type="application\\/xml" schematypens="http:\\/\\/relaxng.org\\/ns\\/structure\\/1.0"?>\\\n/' $XMLPATH/*.xml

for i in `cat data/constants/handles.csv`; do
	echo $i; ARCHE="https:\\/\\/id.acdh.oeaw.ac.at\\/ofmgraz\\/teidocs\\/`echo $i | cut -d , -f 1`"
	HDL=`echo "$i" |cut -d , -f 2|sed 's/\//\\\\\//g'`
sed -i "s/$ARCHE/$HDL/g" data/editions/*
done