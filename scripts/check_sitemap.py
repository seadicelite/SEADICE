#!/usr/bin/env python3
"""p/sitemap.xml を検査する（デプロイ前に Actions が実行）。

1つの <url> に <loc> が2つ入るなど規格外の書き方があると、Search Console は
サイトマップ全体を「読み込めませんでした」にする（2026-10-13 に実例）。
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "p"
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
ALLOWED = {"loc", "lastmod", "changefreq", "priority"}
HOST = "https://seadice.win/"
NOINDEX = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', re.I)

errors = []
try:
    urls = ET.parse(ROOT / "sitemap.xml").getroot()
except ET.ParseError as e:
    sys.exit(f"sitemap.xml: XML として読めない: {e}")

seen = set()
for i, url in enumerate(urls, 1):
    tags = [c.tag.replace(NS, "") for c in url]
    locs = url.findall(NS + "loc")
    where = locs[0].text if locs else f"{i}件目"
    if len(locs) != 1:
        errors.append(f"{where}: <loc> が {len(locs)} 個")
        continue
    for t in set(tags) & ALLOWED:
        if tags.count(t) > 1:
            errors.append(f"{where}: <{t}> が重複")
    loc = locs[0].text.strip()
    if not loc.startswith(HOST):
        errors.append(f"{loc}: {HOST} 以外のURL")
        continue
    if loc in seen:
        errors.append(f"{loc}: URL が重複")
    seen.add(loc)
    path = loc[len(HOST):]
    target = ROOT / path / "index.html" if path == "" or path.endswith("/") else ROOT / path
    if not target.exists():
        errors.append(f"{loc}: p/ にファイルがない")
    elif target.suffix == ".html" and NOINDEX.search(target.read_text(errors="ignore")):
        errors.append(f"{loc}: noindex のページ")

# 公開済みアプリのページ（審査通過時に noindex が外れる）が載っているか
apps = json.loads((ROOT / "released-apps.json").read_text())
for app in apps if isinstance(apps, list) else apps.get("apps", []):
    app_id = app.get("id") or app.get("appId")
    page = ROOT / "tools" / str(app_id) / "index.html"
    loc = f"{HOST}tools/{app_id}/"
    if page.exists() and loc not in seen and not NOINDEX.search(page.read_text(errors="ignore")):
        errors.append(f"{loc}: 公開済みアプリのページが載っていない")

if errors:
    print("\n".join(errors))
    sys.exit(f"sitemap.xml: {len(errors)} 件の問題")
print(f"sitemap.xml: OK（{len(seen)} 件）")
