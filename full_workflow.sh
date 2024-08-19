#!/bin/sh
. ./secret.env
rm -rf editions
./download.py
rm -f mets/216937/{2914584,2926205,3374447,3374448,3374547,3376967,3377127,3377287,3385787,3406471,3674355}* || true
./transform.py
./amend_duplicate.py || true
./amend_pics_paths.sh || true
./renamefiles.py
./generate_headers.py
./generate_body.py
cp -f data/constants/* data/editions
