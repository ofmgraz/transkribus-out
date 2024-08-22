#!/usr/bin/env python
import os
from pathlib import Path
from transkribus_utils.transkribus_utils import ACDHTranskribusUtils
import glob

user = os.environ.get("TR_USER")
pw = os.environ.get("TR_PW")
XSLT = "https://csae8092.github.io/page2tei/page2tei-0.xsl"
METS_DIR = Path("./data/mets")

os.makedirs(METS_DIR, exist_ok=True)
transkribus_client = ACDHTranskribusUtils(
    user=user, password=pw, transkribus_base_url="https://transkribus.eu/TrpServer/rest"
)

with open("col_ids.txt", "r") as f:
    lines = f.readlines()
print(lines)

for y in lines:
    col_id = y.strip()
    print(f"processing collection: {col_id}")
    mpr_docs = transkribus_client.collection_to_mets(col_id, file_path=METS_DIR)
    print(f"{METS_DIR}/{col_id}*.xml")
