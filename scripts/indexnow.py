#!/usr/bin/env python3
"""変更された p/ 配下のページを IndexNow（Bing・ChatGPT検索など）に通知する。

使い方: python3 scripts/indexnow.py p/foo/index.html p/bar.html ...
（GitHub Actions のデプロイ後に、push で変わったファイルを渡して実行する）
noindex のページと HTML 以外は送らない。
"""
import json
import sys
import urllib.request
from pathlib import Path

HOST = "seadice.win"
KEY = "5e7c2a9d41b84f6fa3c0d8e2b917f4a6"  # p/{KEY}.txt に同じ値を置いている


def to_url(path):
    p = Path(path)
    if p.suffix != ".html" or not p.exists() or p.parts[0] != "p":
        return None
    if p.name == "404.html":
        return None
    head = p.read_text(encoding="utf-8", errors="ignore")[:5000].lower()
    if 'name="robots"' in head and "noindex" in head.split('name="robots"', 1)[1][:80]:
        return None
    rel = "/".join(p.parts[1:])
    if rel == "index.html":
        rel = ""
    elif rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return f"https://{HOST}/{rel}"


def main():
    urls = sorted({u for u in map(to_url, sys.argv[1:]) if u})
    if not urls:
        print("IndexNow: 送るページなし")
        return
    body = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls[:10000],
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=body,
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow: {len(urls)}件 送信 → {r.status}")
    except Exception as e:  # 通知の失敗でデプロイを失敗扱いにしない
        print(f"IndexNow: 送信失敗 {e}")


if __name__ == "__main__":
    main()
