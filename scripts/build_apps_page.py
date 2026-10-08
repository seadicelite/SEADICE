#!/usr/bin/env python3
"""
p/released-apps.json（App Store公開済みアプリの正）から、アプリ一覧ページ p/apps/index.html を生成する。

- 一覧に載るのは released-apps.json のアプリだけ（未公開・審査落ちのアプリは載せない）
- アイコンが p/icons/apps/{id}.webp に無ければ、iTunes Lookup API から取得して 112px の WebP にする
- 説明文は各アプリの紹介ページ（p/tools/{id}/ か p/apps/{id}/）の meta description から取る
- テーマ分けは下の CATEGORIES。新しいアプリが未分類なら「その他」に入るので、ここに追記する

使い方:
    python3 scripts/build_apps_page.py
審査通過時は check_released_apps.py のあとにこれを実行する。
"""
import html
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "p"
REGISTRY = P / "released-apps.json"
ICON_DIR = P / "icons" / "apps"
OUT = P / "apps" / "index.html"

CATEGORIES = [
    ("mind", "心とメンタル", ["black-psychology", "hikaku-tomeru", "hitori-time", "mood-forecast",
                         "notify-mindfulness", "honshitsu-type", "curiosity-type", "nlp-mindshift",
                         "teishutsu-switch"]),
    ("habit", "習慣と行動", ["dopa-quest", "dopamine-detox", "habit-quit", "hiru10"]),
    ("learn", "学びと記憶", ["active-recall", "memory-palace", "book-quiz", "dokugaku-schedule",
                        "evidence", "tetsujin-friends", "boueki", "boueki-eigo"]),
    ("life", "暮らし", ["danshari-app3", "jikka-jimai", "coffee-taste"]),
    ("japan", "日本文化（英語）", ["yokai-mirror"]),
]


# 紹介ページが無い・説明が取れないアプリの説明文
DESC_OVERRIDE = {
    "tetsujin-friends": "歴史上の哲学者を「友達」に追加して、チャット感覚で対話するアプリ。ソクラテスやニーチェなど15人と話せます。",
}


def page_for(app_id):
    for sub in ("tools", "apps"):
        f = P / sub / app_id / "index.html"
        if f.exists():
            return f"/{sub}/{app_id}/", f.read_text(encoding="utf-8")
    return None, ""


def short_desc(text, limit=80):
    text = html.unescape(text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = cut.rfind("。")
    if end > 20:
        return cut[: end + 1]
    end = cut.rfind("、")
    return (cut[:end] if end > 20 else cut) + "…"


def ensure_icon(app):
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    out = ICON_DIR / f"{app['id']}.webp"
    if out.exists():
        return True
    try:
        url = f"https://itunes.apple.com/lookup?id={app['appStoreId']}&country=jp"
        with urllib.request.urlopen(url, timeout=10) as res:
            results = json.load(res).get("results", [])
        art = results[0].get("artworkUrl512") if results else None
        if not art:
            raise ValueError("artwork not found")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "icon.png"
            urllib.request.urlretrieve(art, src)
            subprocess.run(["sips", "-s", "format", "png", "-z", "112", "112", str(src), "--out", str(src)],
                           check=True, capture_output=True)
            subprocess.run(["cwebp", "-q", "85", str(src), "-o", str(out)], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"  ! icon failed for {app['id']}: {e}", file=sys.stderr)
        return False


def card(app):
    name = re.split(r"[　ー]", app["name"].strip())[0].strip() if app["id"] == "tetsujin-friends" else app["name"].strip().split("　")[0].strip()
    href, page = page_for(app["id"])
    m = re.search(r'<meta name="description" content="([^"]*)"', page)
    desc = DESC_OVERRIDE.get(app["id"]) or (short_desc(m.group(1)) if m else "")
    store = f"https://apps.apple.com/jp/app/id{app['appStoreId']}?ct=seadice"
    has_icon = ensure_icon(app)
    icon = (f'<img src="/icons/apps/{app["id"]}.webp" alt="" width="56" height="56" loading="lazy">'
            if has_icon else f'<span class="app-icon-fallback">{html.escape(name[:1])}</span>')
    title = (f'<a class="app-name" href="{href}">{html.escape(name)}</a>' if href
             else f'<span class="app-name">{html.escape(name)}</span>')
    more = f'<a class="app-link" href="{href}">くわしく</a>' if href else ""
    return f'''      <li class="app">
        <span class="app-icon">{icon}</span>
        <div class="app-body">
          {title}
          <p class="app-desc">{html.escape(desc)}</p>
          <div class="app-actions"><a class="app-store" href="{store}" target="_blank" rel="noopener">App Storeで見る</a>{more}</div>
        </div>
      </li>'''


def main():
    apps = json.loads(REGISTRY.read_text(encoding="utf-8"))["apps"]
    by_id = {a["id"]: a for a in apps}
    placed = set()
    sections, items_ld = [], []
    groups = [(k, label, [i for i in ids if i in by_id]) for k, label, ids in CATEGORIES]
    rest = [a["id"] for a in apps if not any(a["id"] in ids for _, _, ids in groups)]
    if rest:
        groups.append(("other", "その他", rest))
    for key, label, ids in groups:
        if not ids:
            continue
        cards = "\n".join(card(by_id[i]) for i in ids)
        placed.update(ids)
        sections.append(f'''  <section class="group" aria-labelledby="g-{key}">
    <h2 id="g-{key}">{label}<span>{len(ids)}本</span></h2>
    <ul class="app-list">
{cards}
    </ul>
  </section>''')
    for n, a in enumerate(apps, 1):
        items_ld.append({"@type": "ListItem", "position": n, "item": {
            "@type": "SoftwareApplication", "name": a["name"].strip().split("　")[0].strip(),
            "operatingSystem": "iOS", "applicationCategory": "LifestyleApplication",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
            "url": f"https://apps.apple.com/jp/app/id{a['appStoreId']}"}})
    today = date.today().isoformat()
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "アプリ一覧 | SEADICE", "url": "https://seadice.win/apps/",
         "dateModified": today, "publisher": {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win/"}},
        {"@type": "ItemList", "name": "SEADICEのiPhoneアプリ", "numberOfItems": len(apps), "itemListElement": items_ld},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "HOME", "item": "https://seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": "アプリ一覧", "item": "https://seadice.win/apps/"}]}]}
    count = len(apps)
    desc = f"SEADICE（シーダイス）がApp Storeで公開しているiPhoneアプリ{count}本の一覧。心とメンタル・習慣・学び・暮らしのアプリを、すべて無料・広告なしで提供しています。"
    out = TEMPLATE.format(count=count, desc=desc, ld=json.dumps(ld, ensure_ascii=False),
                          sections="\n\n".join(sections), year=date.today().year)
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({count} apps)")


TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>iPhoneアプリ一覧 | SEADICE</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://seadice.win/apps/">
<meta property="og:title" content="iPhoneアプリ一覧 | SEADICE">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://seadice.win/apps/">
<meta property="og:image" content="https://seadice.win/icons/seadice_ogp.png">
<meta property="og:type" content="website">
<link rel="icon" href="/favicon.png">
<script type="application/ld+json">{ld}</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#05050C;--card:#0C0C1A;--border:#1a1a2e;--text:#e2e8f0;--muted:#7c8aa0;--accent:#00FFD1;--accent2:#38BDF8}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.6}}
a{{color:inherit}}
a:focus-visible{{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}}
header{{border-bottom:1px solid var(--border)}}
.bar{{max-width:880px;margin:0 auto;padding:16px 24px;display:flex;align-items:center;justify-content:space-between}}
.logo{{font-size:16px;font-weight:800;letter-spacing:.15em;color:var(--accent);text-decoration:none}}
.crumb{{font-size:13px;color:var(--muted)}}
.crumb a{{text-decoration:none;padding:8px 0}}
main{{max-width:880px;margin:0 auto;padding:48px 24px 80px}}
.label{{font-size:12px;letter-spacing:.25em;color:var(--accent);text-transform:uppercase;margin-bottom:12px}}
h1{{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-.02em;margin-bottom:16px}}
.lead{{font-size:15px;color:var(--muted);max-width:640px}}
.lead strong{{color:var(--text)}}
.facts{{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 8px;list-style:none}}
.facts li{{font-size:13px;border:1px solid var(--border);border-radius:999px;padding:6px 14px;color:var(--text)}}
.group{{margin-top:56px}}
.group h2{{font-size:18px;font-weight:800;display:flex;align-items:baseline;gap:10px;padding-bottom:12px;border-bottom:1px solid var(--border);margin-bottom:8px}}
.group h2 span{{font-size:13px;font-weight:400;color:var(--muted)}}
.app-list{{list-style:none}}
.app{{display:flex;gap:16px;padding:18px 0;border-bottom:1px solid var(--border)}}
.app-icon{{flex:0 0 56px;width:56px;height:56px;border-radius:13px;overflow:hidden;background:var(--card);display:flex;align-items:center;justify-content:center}}
.app-icon img{{width:56px;height:56px;display:block}}
.app-icon-fallback{{font-weight:800;color:var(--accent)}}
.app-body{{flex:1;min-width:0}}
.app-name{{font-size:16px;font-weight:700;text-decoration:none}}
a.app-name:hover{{color:var(--accent)}}
.app-desc{{font-size:14px;color:var(--muted);margin-top:4px}}
.app-actions{{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:10px;font-size:13px}}
.app-store{{color:#05050C;background:var(--accent);font-weight:700;border-radius:999px;padding:6px 14px;text-decoration:none}}
.app-store:hover{{background:var(--accent2)}}
.app-link{{color:var(--accent2);padding:6px 0;text-decoration:none}}
.app-link:hover{{text-decoration:underline}}
.more{{margin-top:56px;font-size:14px;color:var(--muted)}}
.more a{{color:var(--accent2)}}
footer{{text-align:center;padding:40px 24px;color:var(--muted);font-size:13px;border-top:1px solid var(--border)}}
footer a{{text-decoration:none;margin:0 6px}}
</style>
</head>
<body>
<header><div class="bar"><a class="logo" href="/">SEADICE</a><nav class="crumb" aria-label="パンくずリスト"><a href="/">HOME</a> / アプリ一覧</nav></div></header>
<main>
  <p class="label">Apps</p>
  <h1>iPhoneアプリ一覧</h1>
  <p class="lead"><strong>SEADICE（シーダイス）は、App StoreでiPhoneアプリを{count}本公開しています。</strong>夜更かし・先延ばし・SNS疲れ・片付けなど、暮らしの「ちょっと困った」に効くアプリです。</p>
  <ul class="facts"><li>すべて無料</li><li>広告なし</li><li>iPhone・iPad対応</li></ul>

{sections}

  <p class="more">ブラウザで使えるツールは<a href="/tools/">無料Webツール一覧</a>にあります。</p>
</main>
<footer><a href="/">ホーム</a><a href="/tools/">Webツール</a><a href="/privacy/">プライバシーポリシー</a><p style="margin-top:10px">&copy; {year} SEADICE</p></footer>
</body>
</html>
'''

if __name__ == "__main__":
    main()
