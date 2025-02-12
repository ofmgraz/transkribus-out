#!/bin/bash
. ./secret.env
rm -rf data/mets/* data/editions/* data/constants/tei_headers/*
./pyscripts/download.py
find data/mets/ -type f \( -name "2914584*" -o -name "2926205*" -o -name "3374447*" -o -name "3374448*" -o -name "3374547*" -o -name "3376967*" -o -name "3377127*" -o -name "3377287*" -o -name "3385787*" -o -name "3406471*" -o -name "3674355*" -o -name "6327169*" -o -name "6370807*" \) -exec rm -f {} +
./pyscripts/transform.py |nl
./pyscripts/amend_duplicate.py || true
./shellscripts/amend_pics_paths.sh || true
./pyscripts/renamefiles.py
./pyscripts/generate_headers.py
./pyscripts/generate_body_p.py
cp -f data/constants/S1*.xml data/editions
./pyscripts/add_handles.py data/editions/* |nl
./shellscripts/add_declaration.sh
