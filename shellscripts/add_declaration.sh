#!/bin/bash
if [[ -z $1 ]] ; then
	XMLPATH="data/editions"
else
	XMLPATH="$1"
fi

sed -i $'2s/^/<?xml-model href="https:\\/\\/id.acdh.oeaw.ac.at\\/ofmgraz\\/schema.rng" type="application\\/xml" schematypens="http:\\/\\/relaxng.org\\/ns\\/structure\\/1.0"?>\\\n/' $XMLPATH/*.xml

