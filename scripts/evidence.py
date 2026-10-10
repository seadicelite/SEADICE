#!/usr/bin/env python3
"""
EVIDENCEシリーズ（研究にもとづくアプリ）にアプリを足すための道具。/evidence コマンドから使う。

    python3 scripts/evidence.py candidates          # シリーズに足せるアプリ（公開済み・メディア記事あり・欄なし）
    python3 scripts/evidence.py sources {appId}     # 根拠の材料: 紐づく記事ごとの出典(DOI)と数字入りの文
    python3 scripts/evidence.py add {appId} {json}  # JSONから「もとになった研究」欄を作ってアプリページに入れる

add に渡す JSON:
    {"items": [{"find": "研究でわかったこと（数字入り一文）", "src": "著者 (年), 誌名",
                "feature": "使っているアプリの機能", "article": "記事slug", "doi": "10.xxxx/..."}]}
記事・出典はメディア側（../seadice-media）にあるものだけを使う。add は記事slugとDOIが
sources の結果に含まれるかを確かめ、無ければ止まる（記事にない研究を足さないため）。
"""
import html
import json
import re
import sys
from pathlib import Path

from build_apps_page import P, REGISTRY, page_for

MEDIA = P.parent.parent / "seadice-media"
CSS = (".evidence{border:1px solid var(--border,#1E2A3A);border-radius:16px;padding:24px 20px;margin:32px 0;background:var(--card,#0D0D1A)}"
       ".ev-head{display:flex;align-items:center;gap:12px;margin-bottom:6px}.ev-head img{border-radius:8px;flex-shrink:0}"
       ".evidence .ev-head h2{font-size:1.1rem;font-weight:700;color:#fff;margin:0}"
       ".ev-lead{font-size:.85rem;color:var(--muted,#94A3B8);margin:0 0 16px}.ev-list{list-style:none;padding:0;margin:0}"
       ".ev-list li{border-top:1px solid var(--border,#1E2A3A);padding:16px 0;margin:0}"
       ".ev-find{font-size:.95rem;color:#fff;font-weight:600;line-height:1.6;margin:0}"
       ".ev-src{font-size:.78rem;color:var(--muted,#94A3B8);margin:6px 0 0;line-height:1.6}"
       ".ev-links{display:flex;flex-wrap:wrap;gap:4px 16px;margin:6px 0 0;font-size:.85rem}.ev-links a{color:#7dd3fc;padding:4px 0}"
       ".ev-series{font-size:.85rem;margin-top:4px}.ev-series a{color:#7dd3fc;padding:4px 0}")
NUM = re.compile(r"[0-9０-９]+(?:[.,][0-9]+)?\s*(?:%|％|人|件|倍|週|日|分|時間|年|ポイント)")


def media_for(app_id):
    """そのアプリを apps[] に持つメディア設定を返す"""
    for f in sorted((MEDIA / "media").glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict):
            for a in d.get("apps", []):
                if a.get("id") == app_id:
                    return d, a
    return None, None


def text_of(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def article_material(cfg, slug):
    f = MEDIA / cfg["path"] / slug / "index.html"
    if not f.exists():
        return None
    s = f.read_text(encoding="utf-8")
    title = text_of(re.search(r"<title>(.*?)</title>", s, re.S).group(1)).split("|")[0].strip()
    body = re.search(r"<article.*?</article>", s, re.S)
    body = body.group(0) if body else s
    src = re.search(r'<div class="sources">(.*?)</div>', body, re.S)
    refs = []
    if src:
        for li in re.findall(r"<li>(.*?)</li>", src.group(1), re.S):
            doi = re.search(r"doi\.org/([^\"<\s]+)", li)
            refs.append({"cite": text_of(re.sub(r"<a.*?</a>", "", li, flags=re.S)), "doi": doi.group(1) if doi else ""})
        body = body.replace(src.group(0), "")
    paras = [text_of(p) for p in re.findall(r"<(?:p|li|td)[^>]*>(.*?)</(?:p|li|td)>", body, re.S)]
    facts = [p for p in dict.fromkeys(paras) if NUM.search(p) and 15 < len(p) < 260
             and not re.search(r"読めます|広告なし|HOME /", p)]
    return {"slug": slug, "title": title, "url": cfg["url"] + slug + "/", "refs": refs, "facts": facts[:12]}


def cmd_candidates():
    apps = json.loads(REGISTRY.read_text(encoding="utf-8"))["apps"]
    for a in apps:
        href, page = page_for(a["id"])
        cfg, m = media_for(a["id"])
        has = 'class="evidence"' in page
        if has:
            print(f"  済  {a['id']}")
        elif cfg and href:
            print(f"  候補 {a['id']}  ({cfg['name']} 記事{len(m.get('articles', []))}本, ページ {href})")
        else:
            why = "メディア記事の紐づけなし" if not cfg else "紹介ページなし"
            print(f"  不可 {a['id']}  ({why})")


def cmd_sources(app_id):
    cfg, m = media_for(app_id)
    if not cfg:
        sys.exit(f"{app_id}: どのメディアの apps[] にも無い。先にメディア側でアプリと記事を紐づける")
    href, page = page_for(app_id)
    feats = [text_of(h) for h in re.findall(r"<h3[^>]*>(.*?)</h3>", page, re.S)]
    print(f"# {app_id} / メディア: {cfg['name']} ({cfg['url']}) / ページ: p{href}")
    print(f"アプリの見出し(機能の手がかり): {' / '.join(feats[:15])}\n")
    for slug in m.get("articles", []):
        a = article_material(cfg, slug)
        if not a:
            print(f"## {slug}: 記事ファイルなし\n")
            continue
        print(f"## {a['slug']} — {a['title']}")
        for r in a["refs"]:
            print(f"  出典: {r['cite']}  DOI:{r['doi'] or 'なし'}")
        for t in a["facts"]:
            print(f"  ・{t}")
        print()


def cmd_add(app_id, json_path):
    cfg, m = media_for(app_id)
    href, page = page_for(app_id)
    if not cfg or not href:
        sys.exit("メディアの紐づけか紹介ページが無い")
    if 'class="evidence"' in page:
        sys.exit("すでに欄がある。直すときはページを直接編集する")
    items = json.loads(Path(json_path).read_text(encoding="utf-8"))["items"]
    allowed = {}
    for slug in m.get("articles", []):
        a = article_material(cfg, slug)
        if a:
            allowed[slug] = {r["doi"].lower() for r in a["refs"] if r["doi"]}
    lis = []
    for it in items:
        if it["article"] not in allowed:
            sys.exit(f"記事 {it['article']} はこのアプリに紐づいていない")
        if it.get("doi") and it["doi"].lower() not in allowed[it["article"]]:
            sys.exit(f"DOI {it['doi']} は記事 {it['article']} の出典に無い")
        if re.search(r"証明", it["find"] + it["feature"]):
            sys.exit("「証明」は使わない")
        links = f'<a href="{cfg["url"]}{it["article"]}/" target="_blank" rel="noopener">解説記事を読む</a>'
        if it.get("doi"):
            links += f'<a href="https://doi.org/{it["doi"]}" target="_blank" rel="noopener">論文</a>'
        lis.append(f'<li><p class="ev-find">{html.escape(it["find"])}</p>\n'
                   f'<p class="ev-src">{html.escape(it["src"])} / {html.escape(it["feature"])}</p>\n'
                   f'<p class="ev-links">{links}</p></li>')
    sec = ('<section class="evidence" aria-labelledby="ev-title">\n'
           '<div class="ev-head"><img src="/icons/evidence-mark.webp" width="40" height="40" alt="" loading="lazy">'
           '<h2 id="ev-title">もとになった研究</h2></div>\n'
           f'<p class="ev-lead">このアプリの機能は、次の研究をもとに作っています。研究の詳しい解説は{cfg["name"]}の記事で読めます。</p>\n'
           '<ul class="ev-list">\n' + "\n".join(lis) + '\n</ul>\n</section>\n')
    f = P / href.strip("/") / "index.html"
    text = f.read_text(encoding="utf-8")
    # 置き場所: CTA の直前。無ければ </main> の直前
    cta = re.search(r'<(?:section|div|a|p)[^>]*class="[^"]*\bcta\b[^"]*"', text)
    pos = cta.start() if cta else text.rindex("</main>")
    text = text[:pos] + sec + text[pos:]
    if ".evidence{" not in text:
        text = text.replace("</style>", CSS + "</style>", 1)
    f.write_text(text, encoding="utf-8")
    print(f"added evidence section to {f.relative_to(P.parent)} ({len(lis)} items, {'before CTA' if cta else 'before </main>'})")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["candidates"]:
        cmd_candidates()
    elif args[:1] == ["sources"] and len(args) == 2:
        cmd_sources(args[1])
    elif args[:1] == ["add"] and len(args) == 3:
        cmd_add(args[1], args[2])
    else:
        sys.exit(__doc__)
