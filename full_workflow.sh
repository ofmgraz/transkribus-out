#!/bin/sh
. ./secret.env
rm -rf editions
./download.py
rm -f data/editions/*[A-Z_]*
cd data
tar cvf numbers.tar editions
# tar xvf numbers.tar
cd ..
./amend_pics_paths.sh
./renamefiles.py
./generate_body.py
