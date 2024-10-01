#!/bin/bash
. ./secret.env
rm -rf data/mets/* data/editions/* data/constants/tei_headers/*
./pyscripts/download.py
rm -f data/mets/*/{2914584,2926205,3374447,3374448,3374547,3376967,3377127,3377287,3385787,3406471,3674355}* ||true
./pyscripts/transform.py |nl
./pyscripts/amend_duplicate.py || true
./shellscripts/amend_pics_paths.sh || true
./pyscripts/renamefiles.py
./pyscripts/generate_headers.py
./pyscripts/generate_body_p.py
cp -f data/constants/S1*.xml data/editions
./pyscripts/add_handles.py data/editions/* |nl
./shellscripts/add_declaration.sh
