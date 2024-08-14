#!/bin/sh
sed -i $'1s/^/<?xml version="1.0" encoding="utf-8"?>\\\n<?xml-model href="https:\\/\\/id.acdh.oeaw.ac.at\\/ofmgraz\\/schema.rng" type="application\\/xml" schematypens="http:\\/\\/relaxng.org\\/ns\\/structure\\/1.0"?>\\\n>/' data/editions/*
