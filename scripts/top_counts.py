"""トップページ（p/index.html）の数字の行を、生成スクリプトから最新に保つ。

<b data-count="evidence">1115</b> のような要素の中身だけを書き換える。数字が変わらなければファイルに触らない。
"""
import re
from pathlib import Path

TOP = Path(__file__).resolve().parent.parent / "p" / "index.html"


def set_count(key, n):
    s = TOP.read_text()
    new = re.sub(rf'(<b data-count="{key}">)\d+(</b>)', rf"\g<1>{n}\g<2>", s)
    if new != s:
        TOP.write_text(new)
