#!/usr/bin/env python3
"""EVIDENCEのサイト（seadice.win/evidence/）を、アプリと同じトピックのデータから作る。

  python3 scripts/build_evidence_hub.py

入力: p/apps/evidence/data/topics.json / practice.json / corrections.json / focus.json（1問1ページにする説）
出力: p/evidence/ のトップ・分野別まとめ・1問1ページ・編集方針・訂正履歴、p/sitemap.xml の該当行
更新日は中身が変わったページだけ今日になる（page_dates.json に中身のハッシュを記録）
トピックを増やしたら、データを更新してからこれを実行するだけでページも増える。
"""
import datetime
import hashlib
import html
import json
import re
import apply_page_type
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "p"
DATA = P / "apps" / "evidence" / "data"
OUT = P / "evidence"
BASE = "https://seadice.win"
APP_URL = "https://apps.apple.com/app/id6814862760?ct=evidence-web"
TODAY = datetime.date.today().isoformat()
ORG = {"@type": "Organization", "@id": f"{BASE}/#organization", "name": "SEADICE", "url": BASE + "/"}
DATES_PATH = DATA / "page_dates.json"
DATES = json.loads(DATES_PATH.read_text()) if DATES_PATH.exists() else {}

# 分野名 → URL。新しい分野が出たらここに足す（足さないと仮のURLになり、警告が出る）
SLUGS = {
    "睡眠": "sleep", "睡眠環境": "sleep-environment", "睡眠と食欲": "sleep-appetite",
    "光と体内時計": "light-circadian", "カフェイン": "caffeine", "食事と脳": "food-brain",
    "運動と記憶": "exercise-memory", "運動と気分": "exercise-mood", "運動と老化": "exercise-aging",
    "姿勢と自信": "posture-confidence", "姿勢と痛み": "posture-pain", "笑いと健康": "laughter",
    "自然と健康": "nature", "からだの常識": "body-myths", "呼吸とストレス": "breathing-stress",
    "マインドフルネス": "mindfulness", "こころの不調": "mental-health", "幸福の科学": "happiness",
    "孤独とつながり": "loneliness", "対人関係の心理学": "relationships", "恋愛としぐさ": "romance",
    "集中力": "focus", "音楽と集中力": "music-focus", "香りと記憶": "scent-memory",
    "色彩心理": "color-psychology", "ひらめき": "insight", "学習法": "learning",
    "記憶のしくみ": "memory", "習慣形成": "habits", "先延ばし対策": "procrastination",
    "意思決定バイアス": "decision-bias", "お金の心理学": "money", "スマホとSNS": "smartphone-sns",
    "デジタルデトックス": "digital-detox", "AIとのつきあい方": "ai", "子育ての科学": "parenting",
    "親の老いと介護": "aging-parents", "仕事と働き方": "work", "ペットの科学": "pets", "恋愛と人間関係": "love", "心理学の再現性": "replication", "日本でよく聞く説": "japan", "脳の神話": "brain-myths", "防犯の心理": "crime-prevention", "犯罪の心理": "criminal-psychology",
}

e = lambda s: html.escape(str(s), quote=True)


def slug_of(cat):
    if cat in SLUGS:
        return SLUGS[cat]
    s = "c-" + hashlib.md5(cat.encode()).hexdigest()[:6]
    print(f"警告: 分野「{cat}」のURLが未設定のため /evidence/{s}/ にしました。SLUGS に追加してください")
    return s


CSS = (
    "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}"
    ":root{--bg:#05050C;--card:#0C0C1A;--accent:#00FFD1;--accent2:#38BDF8;--border:#1a1a2e;--text:#e2e8f0;--muted:#7c8aa0}"
    "body{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.7}"
    "header{position:sticky;top:0;z-index:10;background:rgba(5,5,12,.92);border-bottom:1px solid var(--border)}"
    "nav{height:56px;padding:0 16px;max-width:760px;margin:0 auto;display:flex;align-items:center;justify-content:space-between}"
    ".logo{font-size:15px;font-weight:800;letter-spacing:.15em;color:var(--accent);text-decoration:none}"
    "nav a.sub{color:var(--muted);font-size:13px;text-decoration:none;padding:8px 0}"
    "main{max-width:760px;margin:0 auto;padding:24px 16px 64px}"
    ".crumb{font-size:12px;color:var(--muted);margin-bottom:20px}.crumb a{color:var(--muted)}"
    ".label{font-size:12px;letter-spacing:.2em;color:var(--accent);margin-bottom:10px}"
    "h1{font-size:clamp(26px,6vw,40px);font-weight:800;line-height:1.25;margin-bottom:16px}"
    ".lead{font-size:15px;color:#cbd5e1;margin-bottom:28px}"
    "h2{font-size:20px;font-weight:800;line-height:1.4;margin-bottom:10px}"
    "h3{font-size:15px;font-weight:700;margin:14px 0 4px}"
    "a{color:#7dd3fc}"
    ".topic{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:22px 20px;margin-bottom:16px}"
    ".topic{scroll-margin-top:72px}.topic:target{border-color:var(--accent)}"
    ".rel{font-size:13px;color:var(--muted);margin-top:12px;padding:10px 12px;border:1px solid var(--border);border-radius:8px}.rel span{display:block;font-size:12px;font-weight:700;color:var(--accent2)}.rel a{display:block;font-weight:700;margin:2px 0}.rel.contrast span{color:#fbbf24}"
    ".type{margin-bottom:8px}.type a{display:inline-block;font-size:12px;font-weight:700;color:var(--text);border:1px solid var(--border);border-radius:6px;padding:3px 10px;text-decoration:none}"
    ".topic p{font-size:14px}.topic .ans{font-size:15px;color:#e2e8f0}"
    ".stage{display:inline-block;font-size:12px;font-weight:700;color:var(--accent);margin-top:14px}"
    ".unknown{border-left:3px solid #fbbf24;padding-left:12px;margin-top:14px}.unknown .stage{color:#fbbf24;margin-top:0}"
    ".src{font-size:13px;color:var(--muted);margin-top:16px;word-break:break-word}"
    ".links{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}"
    ".links a{font-size:13px;border:1px solid var(--border);border-radius:6px;padding:8px 14px;text-decoration:none}"
    ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin:8px 0 32px}"
    ".grid a{display:block;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px;text-decoration:none;color:var(--text);font-size:14px;font-weight:700}"
    ".grid span{display:block;font-size:12px;color:var(--muted);font-weight:400;margin-top:2px}"
    ".box{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:20px;margin:24px 0}"
    ".poll button{min-height:48px;padding:0 18px;margin:8px 8px 0 0;border:1px solid var(--border);border-radius:8px;background:var(--bg);color:var(--text);font:inherit;font-weight:700;cursor:pointer}"
    ".poll button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}.poll button:disabled{cursor:default;opacity:.6}"
    ".poll button[aria-pressed=true]{border-color:var(--accent);opacity:1}.poll .note{font-size:13px;color:var(--muted)}"
    ".box p,.box li{font-size:14px;color:#cbd5e1}.box ul{padding-left:20px}"
    ".cta{display:inline-block;margin-top:12px;padding:12px 22px;border-radius:8px;font-weight:700;text-decoration:none;color:#05050C;background:var(--accent)}"
    "table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0 20px}th,td{border:1px solid var(--border);padding:8px;text-align:left;vertical-align:top}th{color:var(--accent)}"
    "section{margin-top:36px}footer{max-width:760px;margin:0 auto;padding:24px 16px 48px;font-size:12px;color:var(--muted)}footer a{color:var(--muted)}"
)


# 一次データ「よく聞く説、どのくらい信じられている？」（Firestore belief_counts。yes か no を1増やすだけ、個人の情報は送らない）
POLL_JS = ("<script>(()=>{const s=document.querySelector('.poll');if(!s)return;"
    "const id=s.dataset.id,P='projects/seadiceweb/databases/(default)/documents',A='https://firestore.googleapis.com/v1/'+P,"
    "r=s.querySelector('.res'),bs=s.querySelectorAll('button'),K='bc-'+id,lock=v=>bs.forEach(b=>{b.disabled=v;}),"
    "show=c=>{if(!c)return;const t=c[0]+c[1];r.textContent=t<10?'これまでに'+t+'人が答えました。10人を超えたら割合を出します。'"
    ":'これまでに答えた'+t+'人のうち、'+Math.round(c[0]*100/t)+'%が本当だと思っていました。'},"
    "load=()=>fetch(A+'/belief_counts/'+id).then(x=>x.ok?x.json():{}).then(d=>{const f=d.fields||{};"
    "return[+((f.yes||{}).integerValue||0),+((f.no||{}).integerValue||0)]}).catch(()=>null);"
    "let v=null;try{v=localStorage.getItem(K)}catch(e){}"
    "if(v){lock(true);bs.forEach(b=>b.setAttribute('aria-pressed',b.dataset.v===v));load().then(show)}"
    "s.addEventListener('click',ev=>{const b=ev.target.closest('button');if(!b||b.disabled)return;lock(true);"
    "b.setAttribute('aria-pressed','true');r.textContent='送っています…';"
    "fetch(A+':commit',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({writes:[{transform:"
    "{document:P+'/belief_counts/'+id,fieldTransforms:[{fieldPath:b.dataset.v,increment:{integerValue:'1'}}]}}]})})"
    ".then(x=>{if(!x.ok)throw 0;try{localStorage.setItem(K,b.dataset.v)}catch(e){}return load()}).then(show)"
    ".catch(()=>{r.textContent='送れませんでした。時間をおいて、もう一度押してください。';b.removeAttribute('aria-pressed');lock(false)})})})()</script>")


def poll_html(tid):
    return (f'<section class="box poll" data-id="{e(tid)}"><h2>この話、本当だと思っていましたか？</h2>'
            '<button type="button" data-v="yes" aria-pressed="false">本当だと思っていた</button>'
            '<button type="button" data-v="no" aria-pressed="false">思っていなかった</button>'
            '<p class="res" aria-live="polite"></p>'
            '<p class="note">SEADICEが2026年10月から、よく聞く説がどのくらい信じられているかを数えています。匿名で、押したボタンの合計だけを記録します（登録なし・1つのブラウザで1回）。</p></section>' + POLL_JS)


def page(path, title, desc, body, crumbs, ld_extra=()):
    url = f"{BASE}/{path}"
    h = hashlib.sha1("\n".join([title, desc, body, json.dumps(ld_extra, ensure_ascii=False)]).encode()).hexdigest()[:16]
    if DATES.get(path, {}).get("hash") != h:
        DATES[path] = {"hash": h, "date": TODAY}
    date = DATES[path]["date"]
    bc = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{BASE}{u}"}
        for i, (n, u) in enumerate(crumbs)]}
    web = {"@type": "WebPage", "name": title, "description": desc, "url": url, "inLanguage": "ja",
           "dateModified": date, "publisher": ORG}
    ld = json.dumps({"@context": "https://schema.org", "@graph": [web, bc, *ld_extra]}, ensure_ascii=False, separators=(",", ":"))
    crumb_html = " / ".join(
        f'<a href="{u}">{e(n)}</a>' if i < len(crumbs) - 1 else e(n) for i, (n, u) in enumerate(crumbs))
    doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#05050C">
<link rel="icon" type="image/png" href="/favicon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="SEADICE">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/icons/evidence_icon.webp">
<meta property="og:locale" content="ja_JP">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head>
<body>
<header><nav><a class="logo" href="/evidence/">EVIDENCE</a><a class="sub" href="/evidence/policy/">編集方針</a></nav></header>
<main>
<p class="crumb">{crumb_html}</p>
{body}
</main>
<footer><p>EVIDENCEは <a href="/">SEADICE</a> が運営しています。広告は掲載していません。ここで紹介する内容は研究の紹介であり、医療の診断や治療の代わりにはなりません。<br><a href="/evidence/policy/">編集方針</a> ・ <a href="/evidence/corrections/">訂正履歴</a> ・ <a href="/apps/evidence/">アプリ</a> ・ <a href="mailto:hi@seadice.win">お問い合わせ</a></p></footer>
</body>
</html>
"""
    out = P / path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    apply_page_type.apply(out, "show")
    return url, date


def answer_of(t):
    """トピックの結論のカード。1枚目が「よく聞く説」「素朴な疑問」のときは、説ではなく「ほんとのところ」「わかったこと」を返す"""
    cards = t["cards"]
    if cards[0]["stage"] == "結論":
        return cards[0]
    for c in cards[1:]:
        if c["stage"] in ("ほんとのところ", "わかったこと", "結論"):
            return c
    return next((c for c in reversed(cards) if "わから" not in c["stage"]), cards[-1])


INDEX = {}


def topic_html(t, practice, focus_url=None, heading="h2"):
    cards = t["cards"]
    first, rest = cards[0], cards[1:]
    parts = [f'<article class="topic" id="{e(t["id"])}">',
             *([f'<p class="type"><a href="/evidence/policy/#types">{e(t["studyType"])}</a></p>'] if t.get("studyType") else []),
             (f'<{heading}><a href="{focus_url}">{e(first["title"])}</a></{heading}>' if focus_url else f'<{heading}>{e(first["title"])}</{heading}>'),
             *([] if first["stage"] == "結論" else [f'<p class="stage">{e(first["stage"])}</p>']),
             f'<p class="ans">{e(first["body"])}</p>']
    for c in rest:
        unknown = "わから" in c["stage"]
        parts.append(f'<div class="unknown">' if unknown else "<div>")
        parts.append(f'<p class="stage">{e(c["stage"])}</p><h3>{e(c["title"])}</h3><p>{e(c["body"])}</p></div>')
    parts.append(f'<p class="src">出典: <a href="{e(t["sourceUrl"])}" target="_blank" rel="nofollow noopener">{e(t["sourceLabel"])}</a></p>')
    links = []
    url = t.get("articleUrl") or t.get("researchUrl")
    if url:
        links.append(f'<a href="{e(url)}">{e(t.get("articleSite") or "SEADICEのメディア")}の記事で詳しく読む</a>')
    if practice:
        links.append(f'<a href="{e(practice["url"])}" rel="noopener">{e(practice["name"])}で試す</a>')
    if links:
        parts.append(f'<div class="links">{"".join(links)}</div>')
    for l in t.get("links", [])[:3]:
        other = INDEX.get(l["id"])
        if other:
            cls = "rel contrast" if l["type"] == "反対の結果" else "rel"
            parts.append(f'<p class="{cls}"><span>{e(l["type"])}</span><a href="/evidence/{slug_of(other["category"])}/#{e(l["id"])}">{e(other["cards"][0]["title"])}</a>{e(l.get("why", ""))}</p>')
    parts.append("</article>")
    return "".join(parts)


def main():
    topics = json.loads((DATA / "topics.json").read_text())
    pr = json.loads((DATA / "practice.json").read_text())
    corr_path = DATA / "corrections.json"
    corrections = json.loads(corr_path.read_text()) if corr_path.exists() else []
    focus = {k: v for k, v in json.loads((DATA / "focus.json").read_text()).items() if not k.startswith("_")}
    known = {t["id"] for t in topics}
    for k in focus:
        if k not in known:
            print(f"警告: focus.json の {k} は topics.json にありません")

    def focus_path(t):
        return f"evidence/{slug_of(t['category'])}/{t['id']}/" if t["id"] in focus else None

    def topic_link(t):
        fp = focus_path(t)
        return f"/{fp}" if fp else f"/evidence/{slug_of(t['category'])}/#{t['id']}"

    def practice_of(t):
        key = pr.get("topics", {}).get(t["id"]) or pr.get("categories", {}).get(t["category"])
        return pr["items"].get(key) if key else None

    INDEX.update({t["id"]: t for t in topics})
    by_cat = {}
    for t in topics:
        by_cat.setdefault(t["category"], []).append(t)

    # 各トピックにサイトのページURLを書き込む（アプリの共有で、iPhoneがない人も続きを読めるように）
    changed = False
    for t in topics:
        fp = focus_path(t)
        url = f"{BASE}/{fp}" if fp else f"{BASE}/evidence/{slug_of(t['category'])}/#{t['id']}"
        if t.get("webUrl") != url:
            t["webUrl"] = url
            changed = True
    if changed:
        (DATA / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=2) + "\n")
    cats = sorted(by_cat, key=lambda c: -len(by_cat[c]))
    urls = []

    home = ("EVIDENCE", "/evidence/")
    top_crumbs = [("SEADICE", "/"), home]

    # 分野別まとめ
    for cat in cats:
        ts, slug = by_cat[cat], slug_of(cat)
        n = len(ts)
        title = f"{cat}の研究まとめ｜出典つきで読む{n}本 | EVIDENCE"
        desc = f"{cat}について、研究でわかったこととまだわかっていないことを、出典（論文）つきで{n}本まとめました。例:「{ts[0]['cards'][0]['title']}」"[:120]
        faq = {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": t["cards"][0]["title"],
             "acceptedAnswer": {"@type": "Answer", "text": f'{answer_of(t)["title"]}。{answer_of(t)["body"]}' if t["cards"][0]["stage"] != "結論" else answer_of(t)["body"]}} for t in ts]}
        others = "".join(f'<a href="/evidence/{slug_of(c)}/">{e(c)}<span>{len(by_cat[c])}本</span></a>' for c in cats if c != cat)
        body = (f'<p class="label">EVIDENCE / {e(cat)}</p><h1>{e(cat)}の研究まとめ</h1>'
                f'<p class="lead">{e(cat)}について、研究でわかったことを{n}本、元の論文の出典つきでまとめています。'
                f'わかったことだけでなく、研究の限界や「まだわからないこと」も書いています。</p>'
                + "".join(topic_html(t, practice_of(t), "/" + focus_path(t) if focus_path(t) else None) for t in ts)
                + f'<div class="box"><p>スワイプで1本ずつ読めるアプリもあります。気になった話は、出典つきで友だちに送れます。</p><a class="cta" href="{APP_URL}" rel="noopener">EVIDENCEアプリ（無料）</a></div>'
                f'<section><h2>ほかの分野</h2><div class="grid">{others}</div></section>')
        urls.append(page(f"evidence/{slug}/", title, desc, body, [*top_crumbs, (cat, f"/evidence/{slug}/")], [faq]))

    # 1問1ページ（検索されている説）
    focus_links = []
    for t in topics:
        fp = focus_path(t)
        if not fp:
            continue
        f, cat, slug = focus[t["id"]], t["category"], slug_of(t["category"])
        first, ans = t["cards"][0], answer_of(t)
        concl = ans["body"] if ans is first else f'{ans["title"]}。{ans["body"]}'
        desc = concl[:120]
        same = [o for o in by_cat[cat] if o["id"] != t["id"]][:6]
        rel = "".join(f'<a href="{topic_link(o)}">{e(o["cards"][0]["title"])}</a>' for o in same)
        body = (f'<p class="label">EVIDENCE / {e(cat)}</p><h1>{e(f["title"])}</h1>'
                f'<p class="lead"><strong>結論:</strong> {e(concl)}</p>'
                f'<p class="lead">「{e(f["kw"])}」について、元の論文でわかったことと、まだわかっていないことをまとめました。研究の種類と出典の論文は下にあります。</p>'
                + poll_html(t["id"])
                + topic_html(t, practice_of(t), heading="h2")
                + f'<section><h2>{e(cat)}のほかの研究</h2><div class="grid">{rel}</div>'
                f'<p><a href="/evidence/{slug}/">{e(cat)}の研究まとめ（{len(by_cat[cat])}本）を読む</a></p></section>'
                f'<div class="box"><p>スワイプで1本ずつ読めるアプリもあります。気になった話は、出典つきで友だちに送れます。</p><a class="cta" href="{APP_URL}" rel="noopener">EVIDENCEアプリ（無料）</a></div>')
        art = {"@type": "Article", "headline": f["title"], "about": f["kw"], "inLanguage": "ja", "publisher": ORG,
               "citation": {"@type": "ScholarlyArticle", "name": t["sourceLabel"], "url": t["sourceUrl"]}}
        faq = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": first["title"],
               "acceptedAnswer": {"@type": "Answer", "text": concl}}]}
        urls.append(page(fp, f'{f["title"]} | EVIDENCE', desc, body,
                         [*top_crumbs, (cat, f"/evidence/{slug}/"), (f["kw"], "/" + fp)], [art, faq]))
        focus_links.append(f'<a href="/{fp}">{e(f["kw"])}<span>{e(f["title"].split("？")[0])}？</span></a>')

    # トップ
    grid = "".join(f'<a href="/evidence/{slug_of(c)}/">{e(c)}<span>{len(by_cat[c])}本</span></a>' for c in cats)
    item_list = {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": f"{c}の研究まとめ", "url": f"{BASE}/evidence/{slug_of(c)}/"}
        for i, c in enumerate(cats)]}
    body = (f'<p class="label">EVIDENCE</p><h1>信頼できる情報を、<br>研究の出典つきで。</h1>'
            f'<p class="lead">EVIDENCEは、睡眠・習慣・心理学などについて研究でわかったことを、元の論文の出典つきでまとめているSEADICEのサイトです。'
            f'AIで誰でもそれらしい文章を作れる今、「その話、元をたどれる？」を大事にしています。'
            f'{len(cats)}分野・{len(topics)}本の研究を、わかったことと、まだわかっていないことの両方から読めます。</p>'
            f'<div class="box"><p>EVIDENCEが大事にしていること</p><ul>'
            f'<li>すべての話に、元の論文の出典（DOI）をつける</li>'
            f'<li>研究の限界や「まだわからないこと」も書く</li>'
            f'<li>広告を載せず、特定の商品をすすめない</li>'
            f'<li>間違いを直したら、<a href="/evidence/corrections/">訂正履歴</a>に残す</li></ul>'
            f'<p>調べ方と確かめ方は<a href="/evidence/policy/">編集方針</a>にまとめています。</p></div>'
            f'<section><h2>よく聞く説を確かめる</h2><div class="grid">{"".join(focus_links)}</div></section>'
            f'<section><h2>分野から探す</h2><div class="grid">{grid}</div></section>'
            f'<div class="box"><p>スワイプで1本ずつ読めるアプリもあります。読んだあと、内容を試せるアプリやツールにもつながります。</p><a class="cta" href="{APP_URL}" rel="noopener">EVIDENCEアプリ（無料）</a></div>')
    urls.insert(0, page("evidence/", "EVIDENCE｜信頼できる情報を、研究の出典つきで | SEADICE",
                        f"EVIDENCEは、睡眠・習慣・心理学など{len(cats)}分野の研究を、元の論文の出典つきでまとめたSEADICEのサイト。わかったことと、まだわかっていないことの両方を書いています。",
                        body, top_crumbs, [item_list]))

    # 編集方針
    body = """<p class="label">EVIDENCE / 編集方針</p><h1>編集方針</h1>
<p class="lead">EVIDENCEは、研究でわかったことを、元の研究まで確かめられる形で紹介します。どう調べて、どう確かめているかをここにまとめます。</p>
<section><h2>出典の選び方</h2><p>査読のある論文、複数の研究をまとめた分析（メタ分析・系統的レビュー）、公的な統計を出典にします。論文はDOI（論文ごとの番号）を付け、論文の登録機関Crossrefで実在とタイトルを確かめています。</p></section>
<section><h2>数字の確かめ方</h2><p>人数、期間、効果の大きさなどの数字は、論文の本文または要旨と照らし合わせ、一致するものだけを書きます。確かめられなかった数字は書きません。対象者（例: 高齢の女性、大学生）や条件も、論文のとおりに書きます。</p></section>
<section id="types"><h2>研究の種類の見方</h2><p>研究にはいくつかの種類があり、言えることの強さが違います。EVIDENCEでは各トピックに、出典の研究の種類を表示しています。</p>
<table><tr><th>種類</th><th>どんな研究か</th><th>言えること</th></tr>
<tr><td>メタ分析</td><td>同じテーマの研究をまとめて分析</td><td>結果が一貫しているかがわかる</td></tr>
<tr><td>ランダム化比較試験</td><td>くじ引きでグループを分けて比べる</td><td>原因と結果の関係を調べやすい</td></tr>
<tr><td>レビュー</td><td>専門家がこれまでの研究を読み比べて整理</td><td>全体の傾向がわかるが、数字でまとめた分析ではない</td></tr>
<tr><td>観察研究</td><td>生活の様子と結果の関係を追いかける</td><td>関係（相関）はわかるが、原因とまでは言えない</td></tr>
<tr><td>実験</td><td>実験室などで条件を変えて試す</td><td>面白い手がかり。追試で確かめられるまでは慎重に</td></tr></table></section>
<section><h2>「まだわからないこと」を書く理由</h2><p>研究は「ここまではわかった」という途中経過です。相関なのか因果なのか、対象者が限られていないか、実験室の話なのかを書くことで、読む人が自分で判断できるようにしています。追試で再現されなかった研究は使わないか、その旨を書きます。</p></section>
<section><h2>AIの使い方</h2><p>トピックの下書きは、AI（Claude）が論文をもとに作っています。そのうえで、出典の実在と、数字・対象者・条件が論文と一致しているかを確かめてから載せています。AIを使っていることは隠さず、間違いに気づいたときは下の方法で直します。</p></section>
<section><h2>扱わないこと</h2><ul class="box"><li>病気の診断や治療についての助言（必要なときは医療機関に相談してください）</li><li>特定の商品やサービスのおすすめ</li><li>広告・お金をもらって書く記事</li></ul></section>
<section><h2>間違いを見つけたら</h2><p>アプリの設定画面の「不具合を報告する」、または <a href="mailto:hi@seadice.win">hi@seadice.win</a> に知らせてください。確認して直した内容は<a href="/evidence/corrections/">訂正履歴</a>に日付つきで載せます。</p></section>
<section><h2>運営</h2><p>EVIDENCEは、広告なし・登録不要のアプリとサイトを作っているSEADICEが運営しています。</p></section>"""
    urls.append(page("evidence/policy/", "編集方針｜EVIDENCE | SEADICE",
                     "EVIDENCEが研究を紹介するときの出典の選び方、数字の確かめ方、研究の種類の見方、AIの使い方、間違いを直す方法をまとめています。",
                     body, [*top_crumbs, ("編集方針", "/evidence/policy/")]))

    # 訂正履歴
    if corrections:
        rows = "".join(
            f'<tr><td>{e(c["date"])}</td><td>{e(c.get("topic", ""))}</td><td>{e(c["before"])}</td><td>{e(c["after"])}</td></tr>'
            for c in sorted(corrections, key=lambda c: c["date"], reverse=True))
        listing = f'<table><tr><th>日付</th><th>トピック</th><th>直す前</th><th>直した後</th></tr>{rows}</table>'
    else:
        listing = '<div class="box"><p>現在、公開している訂正はありません。訂正したときは、この一覧に日付と内容を載せます。</p></div>'
    body = (f'<p class="label">EVIDENCE / 訂正履歴</p><h1>訂正履歴</h1>'
            f'<p class="lead">EVIDENCEで紹介した内容に間違いがあり、直したときの記録です。どこをどう直したかを、日付つきで残しています。</p>{listing}'
            f'<p>間違いに気づいたときは <a href="mailto:hi@seadice.win">hi@seadice.win</a> に知らせてください。確かめ方は<a href="/evidence/policy/">編集方針</a>にまとめています。</p>')
    urls.append(page("evidence/corrections/", "訂正履歴｜EVIDENCE | SEADICE",
                     "EVIDENCEで紹介した研究の内容に間違いがあり、直したときの記録を日付つきで公開しています。",
                     body, [*top_crumbs, ("訂正履歴", "/evidence/corrections/")]))

    # サイトマップ: /evidence/ 配下の行を作り直す
    sm_path = P / "sitemap.xml"
    sm = sm_path.read_text()
    sm = re.sub(r"\s*<url><loc>https://seadice\.win/evidence/[^<]*</loc><lastmod>[^<]*</lastmod></url>", "", sm)
    add = "".join(f"\n  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    sm = sm.replace("\n</urlset>", add + "\n</urlset>")
    sm_path.write_text(sm)
    DATES_PATH.write_text(json.dumps(DATES, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    print(f"{len(cats)}分野・{len(topics)}本 → {len(urls)}ページを書き出しました")


if __name__ == "__main__":
    main()
