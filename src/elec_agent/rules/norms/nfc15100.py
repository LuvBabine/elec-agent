# ⚡ elec-agent — NF C 15-100 Rules (French Standard)
# Loaded from nfc15100.json for easy maintenance

import json
from pathlib import Path

_JSON_PATH = Path(__file__).parent.parent / "nfc15100.json"

with open(_JSON_PATH, encoding="utf-8") as _f:
    NF_C_15_100_RULES = json.load(_f)
