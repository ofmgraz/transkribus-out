#!/bin/sh
sed -i 's/A\-Gf_S1_65/A-Gf_S1_69/g' data/editions/S1_69.xml data/editions/1529931.xml  || true
sed -i 's/A\-Gf_A64_41/A-Gf_64_41/g' data/editions/*.xml || true 
sed -i -r 's/(A\-Gf_S1_(2[356]|73?)-[[:digit:]]*)[rv]/\1/g' data/editions/*.xml || true 
sed -i -r 's/A-Gf_S1_65-001/A-Gf_S1_65-002/g' data/editions/*.xml || true 
sed -i -r 's/S1_73\/files/S1_76\/files/g' data/editions/*.xml || true
sed -i -r 's/\/64_41\/files/\/A64_41\/files/g' data/editions/*.xml ||true
