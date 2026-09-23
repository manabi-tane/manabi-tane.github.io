#!/bin/bash
# ダブルクリックでサイトを開きます。
cd "$(dirname "$0")" || exit 1
python3 build.py >/dev/null 2>&1
open index.html
