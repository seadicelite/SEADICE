#!/usr/bin/env python3
"""
EVIDENCEシリーズ（研究にもとづくアプリ）の一覧ページ p/evidence-series/index.html を生成する。

- シリーズに入るのは、released-apps.json に載っていて、紹介ページ（p/tools/{id}/ か p/apps/{id}/）に
  「もとになった研究」欄 <section class="evidence"> があるアプリ。欄を足せば次の実行で自動的に載る
- 研究の中身は各アプリページの欄からそのまま取る（一覧側に別の文章を持たない＝二重管理しない）
- 各アプリページの欄の末尾に、一覧ページへのリンクが無ければ足す

使い方:
    python3 scripts/build_evidence_page.py
アプリページに「もとになった研究」欄を追加・修正したら実行し、build_apps_page.py も続けて実行する。
"""
import html
import json
import re
from datetime import date

from build_apps_page import P, REGISTRY, page_for
from evidence import MEDIA_CSS, media_list, media_section

OUT = P / "evidence-series" / "index.html"
URL = "https://seadice.win/evidence-series/"
SECTION = re.compile(r'<section class="evidence".*?</section>', re.S)
ITEM = re.compile(r'<li>(.*?)</li>', re.S)
SERIES_LINK = '<p class="ev-series"><a href="/evidence-series/">EVIDENCEシリーズ（研究にもとづくアプリ）をすべて見る</a></p>'
SERIES_CSS = '.ev-series{font-size:.85rem;margin-top:4px}.ev-series a{color:#7dd3fc;padding:4px 0}'


def ensure_series_link(href):
    """アプリページの「もとになった研究」欄の末尾に一覧ページへのリンクを足す"""
    f = P / href.strip("/") / "index.html"
    text = f.read_text(encoding="utf-8")
    if 'href="/evidence-series/"' in text:
        return
    text = re.sub(r'(<section class="evidence".*?</ul>)', lambda m: m.group(1) + "\n" + SERIES_LINK, text, count=1, flags=re.S)
    text = text.replace("</style>", SERIES_CSS + "</style>", 1)
    f.write_text(text, encoding="utf-8")
    print(f"  added series link: {f.relative_to(P.parent)}")


def ensure_media_block(href, app_id):
    """「もとになった研究」欄の直後に、関連するメディア記事の欄を入れる（毎回作り直す。メディア側の追加が自動で反映される）"""
    f = P / href.strip("/") / "index.html"
    text = f.read_text(encoding="utf-8")
    blk = media_section(app_id)
    if "<!--media-->" in text:
        new = re.sub(r"<!--media-->.*?<!--/media-->\n?", lambda m: blk + "\n" if blk else "", text, flags=re.S)
    elif blk:
        new = SECTION.sub(lambda m: m.group(0) + "\n" + blk, text, count=1)
    else:
        return
    if blk and ".ev-media{" not in new:
        new = new.replace("</style>", MEDIA_CSS + "</style>", 1)
    if new != text:
        f.write_text(new, encoding="utf-8")
        print(f"  media block: {f.relative_to(P.parent)}")


def sync_registry_media(apps):
    """released-apps.json の media をメディア設定（apps[] に載っているメディア）に合わせる"""
    changed = False
    for a in apps:
        ms = [{"site": c["slug"], "hub": f'{c["url"]}apps/{a["id"]}/'} for c, _ in media_list(a["id"])]
        if ms and a.get("media") != ms:
            a["media"], changed = ms, True
    return changed


FLAGSHIP = "evidence"  # シリーズの名前の元になったアプリ。研究そのものを読むアプリなので、研究欄ではなく先頭に看板として置く


def flagship_block(apps):
    a = next((x for x in apps if x["id"] == FLAGSHIP), None)
    href, page = page_for(FLAGSHIP)
    if not a or not href:
        return ""
    m = re.search(r'<meta name="description" content="([^"]*)"', page)
    store = f"https://apps.apple.com/jp/app/id{a['appStoreId']}?ct=seadice"
    return f'''  <section class="flag" aria-labelledby="flag-title">
    <div class="app-head"><span class="app-icon"><img src="/icons/apps/{FLAGSHIP}.webp" alt="" width="56" height="56"></span>
      <div><p class="label">シリーズの入口</p><h2 id="flag-title"><a href="{href}">EVIDENCE</a></h2></div></div>
    <p class="flag-desc">{html.escape(m.group(1) if m else "")}</p>
    <div class="app-actions"><a class="app-store" href="{store}" target="_blank" rel="noopener">App Storeで見る</a><a class="app-link" href="{href}">アプリの紹介を読む</a></div>
  </section>'''


def main():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    apps = reg["apps"]
    if sync_registry_media(apps):
        REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  updated media in {REGISTRY.relative_to(P.parent)}")
    blocks, items_ld, total = [], [], 0
    for a in apps:
        href, page = page_for(a["id"])
        sec = SECTION.search(page) if href else None
        if not sec:
            continue
        ensure_series_link(href)
        ensure_media_block(href, a["id"])
        items = [i.strip() for i in ITEM.findall(sec.group(0))]
        total += len(items)
        name = a["name"].strip().split("　")[0].strip()
        title = re.search(r"<title>([^<|｜]*)", page)
        name = title.group(1).strip() if title and len(title.group(1).strip()) <= 20 else name
        store = f"https://apps.apple.com/jp/app/id{a['appStoreId']}?ct=seadice"
        icon = (f'<img src="/icons/apps/{a["id"]}.webp" alt="" width="56" height="56" loading="lazy">'
                if (P / "icons" / "apps" / f"{a['id']}.webp").exists() else "")
        lis = "\n".join(f"      <li>{i}</li>" for i in items)
        blocks.append(f'''  <section class="app" aria-labelledby="a-{a["id"]}">
    <div class="app-head"><span class="app-icon">{icon}</span>
      <div><h2 id="a-{a["id"]}"><a href="{href}">{html.escape(name)}</a></h2>
      <p class="app-meta">研究{len(items)}件</p></div></div>
    <ul class="ev-list">
{lis}
    </ul>
    <div class="app-actions"><a class="app-store" href="{store}" target="_blank" rel="noopener">App Storeで見る</a><a class="app-link" href="{href}">アプリの紹介を読む</a></div>
  </section>''')
        items_ld.append({"@type": "ListItem", "position": len(items_ld) + 1, "item": {
            "@type": "SoftwareApplication", "name": name, "operatingSystem": "iOS",
            "applicationCategory": "LifestyleApplication", "url": f"https://seadice.win{href}",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}}})
    flag = flagship_block(apps)
    count = len(blocks) + (1 if flag else 0)
    if flag:
        items_ld.insert(0, {"@type": "ListItem", "position": 0, "item": {
            "@type": "SoftwareApplication", "name": "EVIDENCE", "operatingSystem": "iOS",
            "applicationCategory": "EducationApplication", "url": "https://seadice.win/apps/evidence/",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}}})
        for n, it in enumerate(items_ld, 1):
            it["position"] = n
    today = date.today().isoformat()
    desc = (f"EVIDENCEシリーズは、SEADICEのアプリのうち、機能のもとになった研究の論文と解説記事を公開しているアプリのまとめです。"
            f"現在{count}本・研究{total}件。すべて無料・広告なし。")
    faq = [
        ("EVIDENCEシリーズとは何ですか？",
         f"SEADICEのアプリのうち、機能ごとに「もとになった研究」の論文（DOI）と日本語の解説記事を公開しているアプリのシリーズです。現在{count}本あります。"),
        ("「科学的に証明されたアプリ」ですか？",
         "いいえ。研究で効果が示されたのはアプリに取り入れた方法（記録する、間隔をあけて復習する等）で、アプリそのものの効果を試験したわけではありません。そのため「証明」ではなく「研究にもとづく」と書いています。"),
        ("お金はかかりますか？", "すべて無料で、広告もありません。登録も不要です。"),
    ]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "EVIDENCEシリーズ｜研究にもとづくアプリ", "url": URL,
         "description": desc, "dateModified": today, "inLanguage": "ja",
         "publisher": {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win/"}},
        {"@type": "ItemList", "name": "EVIDENCEシリーズのアプリ", "numberOfItems": count, "itemListElement": items_ld},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "HOME", "item": "https://seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": "アプリ一覧", "item": "https://seadice.win/apps/"},
            {"@type": "ListItem", "position": 3, "name": "EVIDENCEシリーズ", "item": URL}]}]}
    faq_html = "\n".join(f"    <dt>{html.escape(q)}</dt><dd>{html.escape(t)}</dd>" for q, t in faq)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(TEMPLATE.format(desc=desc, ld=json.dumps(ld, ensure_ascii=False), count=count, total=total,
                                   apps="\n\n".join(([flag] if flag else []) + blocks), faq=faq_html, year=date.today().year), encoding="utf-8")
    print(f"wrote {OUT.relative_to(P.parent)} ({count} apps, {total} studies)")


TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EVIDENCEシリーズ｜研究にもとづくアプリ | SEADICE</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://seadice.win/evidence-series/">
<link rel="preload" href="/icons/evidence-mark.webp" as="image" type="image/webp">
<meta property="og:title" content="EVIDENCEシリーズ｜研究にもとづくアプリ">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://seadice.win/evidence-series/">
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
.bar{{max-width:880px;margin:0 auto;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;gap:12px}}
.logo{{font-size:16px;font-weight:800;letter-spacing:.15em;color:var(--accent);text-decoration:none}}
.crumb{{font-size:13px;color:var(--muted)}}
.crumb a{{text-decoration:none;padding:8px 0}}
main{{max-width:880px;margin:0 auto;padding:48px 24px 80px}}
.hero{{display:flex;align-items:center;gap:16px;margin-bottom:16px}}
.hero img{{border-radius:12px;flex-shrink:0}}
.label{{font-size:12px;letter-spacing:.25em;color:var(--accent);text-transform:uppercase}}
h1{{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-.02em}}
.lead{{font-size:15px;color:var(--muted);max-width:660px}}
.lead strong{{color:var(--text)}}
.facts{{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 8px;list-style:none}}
.facts li{{font-size:13px;border:1px solid var(--border);border-radius:999px;padding:6px 14px}}
.rules{{margin-top:40px;border:1px solid var(--border);border-radius:16px;padding:20px;background:var(--card)}}
.rules h2{{font-size:16px;font-weight:800;margin-bottom:10px}}
.rules ol{{padding-left:20px;font-size:14px;color:var(--muted)}}
.rules li{{margin:6px 0}}
.rules li strong{{color:var(--text)}}
.flag{{margin-top:40px;border:1px solid var(--accent);border-radius:16px;padding:20px;background:var(--card)}}
.flag h2{{font-size:18px;font-weight:800}}
.flag h2 a{{text-decoration:none}}
.flag-desc{{font-size:14px;color:var(--muted);margin-top:4px}}
.app{{margin-top:48px;padding-top:24px;border-top:1px solid var(--border)}}
.app-head{{display:flex;align-items:center;gap:14px;margin-bottom:8px}}
.app-icon{{flex:0 0 56px;width:56px;height:56px;border-radius:13px;overflow:hidden;background:var(--card)}}
.app-icon img{{width:56px;height:56px;display:block}}
.app h2{{font-size:18px;font-weight:800}}
.app h2 a{{text-decoration:none}}
.app h2 a:hover{{color:var(--accent)}}
.app-meta{{font-size:13px;color:var(--muted)}}
.ev-list{{list-style:none}}
.ev-list li{{border-top:1px solid var(--border);padding:14px 0}}
.ev-list li:first-child{{border-top:0}}
.ev-find{{font-size:15px;font-weight:600;line-height:1.6}}
.ev-src{{font-size:13px;color:var(--muted);margin-top:6px}}
.ev-links{{display:flex;flex-wrap:wrap;gap:4px 16px;margin-top:6px;font-size:14px}}
.ev-links a{{color:#7dd3fc;padding:4px 0}}
.app-actions{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 18px;margin-top:10px;font-size:13px}}
.app-store{{color:#05050C;background:var(--accent);font-weight:700;border-radius:999px;padding:6px 14px;text-decoration:none}}
.app-store:hover{{background:var(--accent2)}}
.app-link{{color:var(--accent2);padding:6px 0;text-decoration:none}}
.faq{{margin-top:56px}}
.faq h2{{font-size:18px;font-weight:800;margin-bottom:12px}}
.faq dt{{font-weight:700;margin-top:16px}}
.faq dd{{font-size:14px;color:var(--muted);margin-top:4px}}
.more{{margin-top:48px;font-size:14px;color:var(--muted)}}
.more a{{color:var(--accent2)}}
footer{{text-align:center;padding:40px 24px;color:var(--muted);font-size:13px;border-top:1px solid var(--border)}}
footer a{{text-decoration:none;margin:0 6px;padding:8px 0}}
</style>
</head>
<body>
<header><div class="bar"><a class="logo" href="/">SEADICE</a><nav class="crumb" aria-label="パンくずリスト"><a href="/">HOME</a> / <a href="/apps/">アプリ一覧</a> / EVIDENCE</nav></div></header>
<main>
  <div class="hero"><img src="/icons/evidence-mark.webp" width="48" height="48" alt=""><div><p class="label">Evidence Series</p><h1>研究にもとづくアプリ</h1></div></div>
  <p class="lead"><strong>EVIDENCEシリーズは、機能のもとになった研究の論文と解説記事をすべて公開しているSEADICEのアプリです。</strong>「なぜこの機能があるのか」を、元の論文とやさしい解説記事で確かめてから使えます。入口は、研究そのものを3枚のカードで読めるアプリ「EVIDENCE」です。</p>
  <ul class="facts"><li>{count}本のアプリ</li><li>研究{total}件</li><li>すべて無料・広告なし</li></ul>

  <section class="rules" aria-labelledby="rules-title">
    <h2 id="rules-title">シリーズの3つの約束</h2>
    <ol>
      <li><strong>機能ごとに元の論文を示す。</strong>どの研究のどの結果を、アプリのどの機能に使ったかを書きます。</li>
      <li><strong>研究の中身を日本語で読める。</strong>SEADICEのメディアの解説記事に、研究の方法と数字をまとめています。</li>
      <li><strong>「証明された」とは書かない。</strong>研究で効果が示されたのはアプリに取り入れた方法で、アプリそのものではないためです。</li>
    </ol>
  </section>

{apps}

  <section class="faq" aria-labelledby="faq-title">
    <h2 id="faq-title">よくある質問</h2>
    <dl>
{faq}
    </dl>
  </section>

  <p class="more">ほかのアプリは<a href="/apps/">アプリ一覧</a>にあります。</p>
</main>
<footer><a href="/">ホーム</a><a href="/apps/">アプリ一覧</a><a href="/privacy/">プライバシーポリシー</a><p style="margin-top:10px">&copy; {year} SEADICE</p></footer>
</body>
</html>
'''

if __name__ == "__main__":
    main()
