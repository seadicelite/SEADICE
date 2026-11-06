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

import apply_page_type
import json
import re
import subprocess
import top_counts
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
                         "teishutsu-switch", "body-language-scan"]),
    ("habit", "習慣と行動", ["dopa-quest", "dopamine-detox", "habit-quit", "hiru10"]),
    ("learn", "学びと記憶", ["active-recall", "memory-palace", "book-quiz", "dokugaku-schedule",
                        "evidence", "tetsujin-friends", "boueki", "boueki-eigo", "drone-cbt"]),
    ("life", "暮らし", ["danshari-app3", "jikka-jimai", "coffee-taste"]),
    ("japan", "日本文化（英語）", ["yokai-mirror"]),
]


# カードの一言（10〜25字。design/README.md「文字を減らす」）。新しいアプリはここに1行足す
DESC_OVERRIDE = {
    "black-psychology": "しぐさや行動から、相手の気持ちをAIで読む",
    "hikaku-tomeru": "SNS疲れを、その場でAIに話して整える",
    "hitori-time": "ひとり時間の過ごし方を提案し、記録する",
    "mood-forecast": "気分の記録から、崩れやすい曜日や流れを知る",
    "notify-mindfulness": "呼吸・姿勢など7つのテーマを通知で届ける",
    "honshitsu-type": "ビッグファイブで、自分の取扱説明書を作る",
    "curiosity-type": "20問で好奇心のタイプと、今日の小さな挑戦",
    "nlp-mindshift": "NLPの技法を1日1つ、30日間で試す",
    "teishutsu-switch": "完璧主義を、4週間のCBTプログラムでゆるめる",
    "body-language-scan": "表情・姿勢・しぐさから、相手の心理をAIで読む",
    "dopa-quest": "現実の行動で育つ、RPG型の習慣アプリ",
    "dopamine-detox": "5分の小さな一歩で、行動をつなげる",
    "habit-quit": "やめたい習慣を、代わりの行動と記録で減らす",
    "hiru10": "研究にもとづく10分の昼寝タイマー",
    "active-recall": "覚えたい範囲から、AIが思い出しクイズを作る",
    "memory-palace": "記憶の宮殿で、リストや原稿を覚える",
    "book-quiz": "読んだ本から、AIがクイズを作る",
    "dokugaku-schedule": "参考書の目次から、学習スケジュールを作る",
    "evidence": "よく聞く説を、論文の出典つきで読む",
    "tetsujin-friends": "偉人が話しかけてくる、話し相手のアプリ",
    "boueki": "貿易実務検定C級の模擬試験と演習",
    "boueki-eigo": "貿易実務の英単語を覚える",
    "drone-cbt": "ドローン二等の学科試験、解説つき200問",
    "danshari-app3": "手放すか迷う物を、AIが理由つきで判定",
    "jikka-jimai": "親の家の片付け・相続・空き家に備える",
    "coffee-taste": "好みから、合うコーヒー豆と淹れ方を診断",
    "yokai-mirror": "日本の妖怪伝承で遊ぶ診断（英語）",
    "nlp-lab": "NLPの技法を、試す前後で比べて確かめる",
    "renshu-sns": "子どもがSNSの危ない場面を練習する",
    "tesukatsu-log": "テストステロンを増やす習慣を記録する",
    "attachment-style": "16問で、4つの愛着スタイルを判定",
    "cognitive-bias-guide": "80種類の認知バイアスを、例と研究つきで",
    "dark-triad": "27問で、ダークトライアドの傾向を測る",
    "enneagram": "36問で、エニアグラムの9タイプを判定",
    "fbi-bodylanguage": "元FBI捜査官の観察法を、辞典で引く",
    "holmes-deduction": "日常の一場面で、観察と推理を練習する",
    "hsp-relationship-check": "HSPのセルフチェックと、人づきあいの工夫",
    "kateisaien-app10": "土のpHを測って記録し、土づくりに使う",
    "lifeisrpg": "習慣をこなすとキャラが育つ、RPG型管理",
    "line-honne-scan": "LINEの会話から、相手の温度感をAIで読む",
    "mbti-compass": "MBTIの16タイプと、友だちとの相関図",
    "nlp-goal-coach": "NLPの枠組みで、目標を明確にする",
    "pet-health-app3": "犬・猫の病気と予防を、毎日1問のクイズで",
    "procrastination-type": "先延ばしのタイプと、タイプ別の対策",
    "trauma-response-type": "4Fモデルで、ストレスへの反応を知る",
    "yaritai-100": "やりたいこと100個と、次の一歩",
    "yumetoki": "夢の内容から、夢占いと記号辞典",
    "kiroku-nou-training": "離れて暮らす親に入れる、脳トレ記録",
    "yame-lab": "やめたいことの仕組みを知り、記録で続ける",
    "kateisaien-app3": "家庭菜園の知識を、4択クイズで",
    "shakai-fukki-quest100": "外に出るまでを、100の小さなクエストに",
}


def is_tracked(path):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", str(path)], cwd=ROOT, capture_output=True)
    return r.returncode == 0


NOINDEX = re.compile(r'<meta name="robots" content="noindex">\n?')


def page_for(app_id):
    # 未コミットのページは本番に出ていないのでリンクしない
    for sub in ("tools", "apps"):
        f = P / sub / app_id / "index.html"
        if f.exists() and is_tracked(f):
            # 審査通過前に検索から外していたページは、公開と同時に戻す
            text = f.read_text(encoding="utf-8")
            if NOINDEX.search(text):
                f.write_text(NOINDEX.sub("", text), encoding="utf-8")
                print(f"  removed noindex: {f.relative_to(ROOT)}")
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
    name = re.split(r"　|\s*-\s*", app["name"].strip())[0].strip()
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
    if 'class="evidence"' in page or app["id"] == "evidence":
        more += '<a class="app-ev" href="/evidence-series/">研究にもとづく</a>'
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
         "dateModified": today, "publisher": {"@id": "https://seadice.win/#organization", "@type": "Organization", "name": "SEADICE", "url": "https://seadice.win/"}},
        {"@type": "ItemList", "name": "SEADICEのiPhoneアプリ", "numberOfItems": len(apps), "itemListElement": items_ld},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "HOME", "item": "https://seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": "アプリ一覧", "item": "https://seadice.win/apps/"}]}]}
    count = len(apps)
    top_counts.set_count("apps", count)
    desc = f"SEADICE（シーダイス）がApp Storeで公開しているiPhoneアプリ{count}本の一覧。心とメンタル・習慣・学び・暮らしのアプリを、広告なしで提供しています（基本の機能は無料）。"
    out = TEMPLATE.format(count=count, desc=desc, ld=json.dumps(ld, ensure_ascii=False),
                          sections="\n\n".join(sections), year=date.today().year)
    OUT.write_text(out, encoding="utf-8")
    apply_page_type.apply(OUT, "show")  # 魅せるページのデザイン（design/）を差し込む
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
header{{position:fixed;top:0;left:0;right:0;z-index:100;background:var(--bg);border-bottom:1px solid var(--border)}}
.bar{{height:56px;padding:0 20px;display:flex;align-items:center;justify-content:space-between}}
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
.series{{display:flex;align-items:center;gap:14px;margin-top:24px;padding:16px 18px;border:1px solid var(--accent);border-radius:14px;background:var(--card);text-decoration:none}}
.series:hover{{background:#10102a}}
.series img{{border-radius:8px;flex-shrink:0}}
.series strong{{display:block;font-size:15px;color:var(--accent)}}
.series span span{{display:block;font-size:13px;color:var(--muted);margin-top:2px}}
.app-ev{{color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:5px 12px;text-decoration:none;font-size:12px}}
.app-ev:hover{{background:rgba(0,255,209,.1)}}
.more{{margin-top:56px;font-size:14px;color:var(--muted)}}
.more a{{color:var(--accent2)}}
footer{{text-align:center;padding:40px 24px;color:var(--muted);font-size:13px;border-top:1px solid var(--border)}}
footer a{{text-decoration:none;margin:0 6px}}
</style>
</head>
<body>
<header><div class="bar"><a class="logo nav-logo" href="/">SEADICE</a><nav class="crumb" aria-label="パンくずリスト"><a href="/">HOME</a> / アプリ一覧</nav></div></header>
<main>
  <p class="label">Apps</p>
  <h1>iPhoneアプリ一覧</h1>
  <p class="lead"><strong>SEADICE（シーダイス）のiPhoneアプリ{count}本。</strong>暮らしの「ちょっと困った」に。</p>
  <ul class="facts"><li>基本の機能は無料</li><li>広告なし</li><li>iPhone・iPad対応</li></ul>
  <a class="series" href="/evidence-series/"><img src="/icons/evidence-mark.webp" width="40" height="40" alt=""><span><strong>EVIDENCEシリーズ｜研究にもとづくアプリ</strong><span>機能のもとになった論文と解説記事を公開しているアプリをまとめて見る</span></span></a>

{sections}

  <p class="more">ブラウザで使えるツールは<a href="/tools/">無料Webツール一覧</a>にあります。</p>
</main>
<footer><a href="/">ホーム</a><a href="/tools/">Webツール</a><a href="/promise/">7ヶ条</a><a href="/about/">運営者情報</a><a href="/privacy/">プライバシーポリシー</a><p style="margin-top:10px">&copy; {year} SEADICE</p></footer>
</body>
</html>
'''

if __name__ == "__main__":
    main()
