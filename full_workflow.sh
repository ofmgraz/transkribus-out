#!/bin/sh
. ./secret.env
rm -rf editions
./download.py
./transform.py
rm -f data/editions/*[A-Z_]*
cd data
tar cvf numbers.tar editions
# tar xvf numbers.tar
cd ..
./amend_pics_paths.sh || true
./renamefiles.py
rm -f data/editions/*duplicated*
./generate_body.py
