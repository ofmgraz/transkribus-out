#!/bin/sh
. ./secret.env
rm -rf editions
./download.py
rm -f mets/216937/{2926205,1523134,2914584,2926205,3374447,3374448,3374547,3376967,377127,3377287,3385787,3406471,3377127}* || true
./transform.py
./amend_pics_paths.sh || true
./renamefiles.py
./generate_body.py
