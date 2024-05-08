#!/bin/sh
cd data
rm -rf editions
tar xvf numbers.tar
cd ..
./ammend_pics_paths.sh
./renamefiles.py
./generate_body.py
