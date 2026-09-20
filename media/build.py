#!/usr/bin/env python3
"""media/{slug}-posts.json から一覧ページ(p/{slug}/index.html)と sitemap を再生成する。
使い方: python3 media/build.py research
記事を追加するときは posts.json の先頭に1件足してから実行する。JS不使用。"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATS = {  # 名前: (id, 色, アイコンpath)
    "睡眠": ("sleep", "#6366f1", "M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"),
    "集中力": ("focus", "#06b6d4", "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 5a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 3a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"),
    "先延ばし": ("delay", "#f59e0b", "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 5v5.4l3.7 2.2-.8 1.3L11 13V7z"),
    "気分・ストレス": ("mood", "#ec4899", "M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z"),
    "習慣": ("habit", "#10b981", "M17 2l4 4-4 4V7H8a3 3 0 0 0-3 3v1H3v-1a5 5 0 0 1 5-5h9V2zm-10 20l-4-4 4-4v3h9a3 3 0 0 0 3-3v-1h2v1a5 5 0 0 1-5 5H7v3z"),
    "記憶・学習": ("memory", "#8b5cf6", "M4 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4V4zm16 0h-4a3 3 0 0 0-2 .8V20a2 2 0 0 1 2-2h4V4z"),
}
FALLBACK = ("other", "#64748b", "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z")


def img_url(i, w, h):
    if "src" in i:  # Wikimedia Commons(表示用サムネイルURL)
        return i["src640"] if w <= 640 else i["src"]
    return f"{i['raw']}&w={w}&h={h}&fit=crop&q=70&fm=webp"


def card(p, images, base):
    cid, col, path = CATS.get(p["category"], FALLBACK)
    img = ""
    if p["slug"] in images:
        i = images[p["slug"]]
        img = f'<img src="{img_url(i, 640, 320)}" width="640" height="320" alt="{html.escape(i["alt"], quote=True)}" loading="lazy">'
    th = f'<div class="th" style="--c:{col}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path}"/></svg>{img}</div>'
    return (f'<a class="card" href="{base}{p["slug"]}/">{th}<div class="cb"><span class="tag" style="--c:{col}">{html.escape(p["category"])}</span>'
            f'<p class="t">{html.escape(p["title"])}</p><p class="d">{html.escape(p["summary"])}</p><time datetime="{p["date"]}">{p["date"]}</time></div></a>')


CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}:root{--bg:#05050C;--card:#0C0C1A;--accent:#00FFD1;--accent2:#38BDF8;--border:#1a1a2e;--text:#e2e8f0;--muted:#8592a6}html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.7;-webkit-text-size-adjust:100%}nav.top{position:fixed;top:0;left:0;right:0;z-index:100;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);background:rgba(5,5,12,.8);border-bottom:1px solid var(--border);padding:0 20px;height:56px;display:flex;align-items:center;justify-content:space-between}.nav-logo{font-size:15px;font-weight:800;letter-spacing:.15em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none}nav.top a.r{font-size:13px;color:var(--muted);text-decoration:none}main{max-width:960px;margin:0 auto;padding:88px 20px 64px}.hero{padding:24px 0 28px}h1{font-size:clamp(28px,7vw,46px);font-weight:800;letter-spacing:.06em;line-height:1.15;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}.tagline{font-size:15px;color:var(--muted);margin-top:8px;letter-spacing:.04em}.lead{font-size:15px;color:#cbd5e1;margin-top:14px;max-width:620px}.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 40px}.chip{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--text);text-decoration:none;border:1px solid var(--border);background:var(--card);border-radius:999px;padding:7px 14px}.chip svg{width:15px;height:15px;fill:var(--c)}.chip:hover{border-color:var(--c)}h2.sec{font-size:14px;letter-spacing:.14em;color:var(--muted);margin:0 0 14px}h2.cat{display:flex;align-items:center;gap:8px;font-size:18px;margin:44px 0 14px;padding-left:12px;border-left:4px solid var(--c)}h2.cat svg{width:20px;height:20px;fill:var(--c)}.grid{display:grid;gap:16px;grid-template-columns:1fr}@media(min-width:620px){.grid{grid-template-columns:1fr 1fr}}@media(min-width:900px){.grid{grid-template-columns:1fr 1fr 1fr}}.card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--text);transition:border-color .15s,transform .15s}.card:hover{border-color:var(--accent);transform:translateY(-2px)}.th{position:relative;overflow:hidden;aspect-ratio:16/8;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,color-mix(in srgb,var(--c) 38%,#05050C),color-mix(in srgb,var(--c) 10%,#05050C))}.th img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.th svg{width:44px;height:44px;fill:var(--c);opacity:.95}.cb{padding:14px 16px 16px}.tag{display:inline-block;font-size:11px;letter-spacing:.06em;color:var(--c);border:1px solid var(--c);border-radius:4px;padding:1px 8px}.card .t{font-size:16px;font-weight:700;line-height:1.5;margin:8px 0 6px}.card .d{font-size:13px;color:var(--muted);line-height:1.65}.card time{display:block;font-size:11px;color:var(--muted);margin-top:10px}.empty{grid-column:1/-1;background:var(--card);border:1px dashed var(--border);border-radius:12px;padding:20px;font-size:14px;color:var(--muted)}.about{margin-top:56px;padding:22px;background:linear-gradient(135deg,rgba(0,255,209,.08),rgba(56,189,248,.06));border:1px solid rgba(0,255,209,.28);border-radius:16px;font-size:14px;color:#cbd5e1}.about strong{color:var(--accent)}footer{border-top:1px solid var(--border);padding:24px;text-align:center;font-size:12px;color:var(--muted)}footer a{color:var(--muted)}"""


def build(slug):
    cfg = json.loads((ROOT / f"media/{slug}.json").read_text())
    posts = json.loads((ROOT / f"media/{slug}-posts.json").read_text())
    ip = ROOT / f"media/{slug}-images.json"
    images = json.loads(ip.read_text()) if ip.exists() else {}
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)
    base = f"/{slug}/"
    name, url = cfg["name"], cfg["url"]
    chips = "".join(f'<a class="chip" href="#c-{CATS[c][0]}" style="--c:{CATS[c][1]}"><svg viewBox="0 0 24 24"><path d="{CATS[c][2]}"/></svg>{c}</a>' for c in cfg["categories"] if c in CATS)
    latest = "".join(card(p, images, base) for p in posts[:12])
    secs = ""
    for c in cfg["categories"]:
        cid, col, path = CATS.get(c, FALLBACK)
        items = [p for p in posts if p["category"] == c]
        body = "".join(card(p, images, base) for p in items) or '<p class="empty">記事を準備中です。</p>'
        secs += f'<section id="c-{cid}"><h2 class="cat" style="--c:{col}"><svg viewBox="0 0 24 24"><path d="{path}"/></svg>{c}</h2><div class="grid">{body}</div></section>'
    ttl = f"{name} | 悩みを科学で調べる、AIリサーチメディア"
    desc = "睡眠・集中・先延ばし・気分・習慣・記憶。日常の悩みを公開された研究論文から調べ、今日から試せる形に整理するAIリサーチメディア。出典つきで毎日更新。"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": name, "url": url, "publisher": {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "HOME", "item": "https://seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": "RESEARCH", "item": url}]}]}, ensure_ascii=False)
    out = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{ttl}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{ttl}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head>
<body>
<nav class="top">
  <a href="/" class="nav-logo">SEADICE</a>
  <a href="{base}" class="r">RESEARCH</a>
</nav>
<main>
  <div class="hero">
    <h1>{name}</h1>
    <p class="tagline">Curious about your life, scientifically.</p>
    <p class="lead">睡眠、集中、先延ばし、気分、習慣、記憶。日常の悩みを公開された研究から調べ、今日から試せる形にします。</p>
  </div>
  <div class="chips" aria-label="カテゴリ">{chips}</div>

  <h2 class="sec">LATEST</h2>
  <div class="grid">{latest}</div>

  {secs}

  <div class="about"><strong>このメディアについて</strong><br>記事はAIが公開された研究論文や公的機関の資料を調べ、出典の内容を確認して作成しています。SEADICEが独自に実験したものではありません。各記事の末尾に出典を掲載しています。写真は <a href="https://commons.wikimedia.org/" style="color:#7dd3fc" target="_blank" rel="noopener">Wikimedia Commons</a> の自由ライセンス素材で、各記事に撮影者とライセンスを表示しています。</div>
</main>
<footer><p><a href="/">HOME</a> &nbsp;|&nbsp; <a href="/apps/">アプリ一覧</a> &nbsp;|&nbsp; &copy; SEADICE</p></footer>
</body>
</html>
'''
    (ROOT / cfg["path"] / "index.html").write_text(out)
    # sitemap: 未登録のURLだけ末尾に追加
    sm = ROOT / "p/sitemap.xml"
    if sm.exists():
        s = sm.read_text()
        urls = [url] + [f"{url}{p['slug']}/" for p in posts]
        add = "".join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{(posts[0]["date"] if posts else "")}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n' for u in urls if f"<loc>{u}</loc>" not in s)
        if add:
            sm.write_text(s.replace("</urlset>", add + "</urlset>"))
    print(f"built {cfg['path']}index.html ({len(posts)} posts)")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "research")
