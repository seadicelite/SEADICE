#!/usr/bin/env python3
"""財布の紐診断（/diagnosis/saifu-no-himo/）を、アプリ「財布の紐」の tricks.json から書き出す。

問い・研究・対抗のしかたはアプリと同じデータを使い、手で写さない。
tricks.json を直したら、このスクリプトを実行してから
`python3 scripts/apply_page_type.py use p/diagnosis/saifu-no-himo/index.html` を実行する。

使い方: python3 scripts/build_saifu_diagnosis.py [tricks.json のパス]
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    '~/Developer/ファイナンス系/spendology/assets/tricks.json')
OUT = os.path.join(ROOT, 'p/diagnosis/saifu-no-himo/index.html')
URL = 'https://seadice.win/diagnosis/saifu-no-himo/'
LEDGER = 'https://ledger.seadice.win/'
PUBLISHED = '2026-10-15'
MODIFIED = '2026-10-15'

data = json.load(open(SRC, encoding='utf-8'))
tricks = data['tricks']
notice = data['noticing']
esc = html.escape

# 合計点(12〜36点)の4段階。区切りはSEADICEが決めたもの(アプリと同じ)
TOTAL_BANDS = [
    {'min': 29, 'level': 'high', 'label': 'ほどけかけ', 'color': '#c2410c',
     'desc': '多くの仕掛けに、紐がほどけやすくなっています。でも、仕掛けに気づくだけで引っぱる力は弱まります。まずは下の点数が高い3つから覚えましょう。'},
    {'min': 23, 'level': 'mid', 'label': 'ゆるみ気味', 'color': '#a16207',
     'desc': 'いくつかの仕掛けに、紐がゆるみやすくなっています。意志が弱いのではなく、どれも研究で調べられている、だれにでも起きる心の働きです。弱い仕掛けを見たら、その場で決めずに時間を置きましょう。'},
    {'min': 17, 'level': 'mid', 'label': '蝶結び', 'color': '#1d4ed8',
     'desc': 'ふだんは結べていますが、引っぱられるとほどける仕掛けがあります。下の点数が高い仕掛けだけ覚えておけば、紐はもっと固くなります。'},
    {'min': 12, 'level': 'low', 'label': '固結び', 'color': '#15803d',
     'desc': '売る側の仕掛けに、ほとんど動かされていません。紐はしっかり固く結ばれています。迷った物だけ、時間を置いてから決めましょう。'},
]


def research_html(t):
    ja = t['ja']
    return (f'{esc(ja["finding"])}（<a href="{esc(t["doi"])}" target="_blank" rel="noopener">'
            f'{esc(ja["cite"])}</a>）')


def key_entry(t):
    ja = t['ja']
    return {
        'name': ja['name'], 'color': '#5b5bd6', 'min': 1, 'max': 3,
        'bands': [
            {'min': 3, 'level': 'high', 'label': '弱い',
             'desc': f'{research_html(t)}<br><b>対抗のしかた</b>: {esc(ja["counter"])}',
             'tori': f'{ja["name"]}: {ja["counter"]}'},
            {'min': 2, 'level': 'mid', 'label': 'ときどき',
             'desc': f'<b>対抗のしかた</b>: {esc(ja["counter"])}',
             'tori': f'{ja["name"]}: {ja["counter"]}'},
            {'min': 1, 'level': 'low', 'label': '強い',
             'desc': 'この仕掛けには流されにくいようです。'},
        ],
    }


scale = {
    'shareTitle': 'わたしの財布の紐',
    'sortByScore': True,
    'lead': 'ネットやお店で買い物をするとき、どれくらいありますか？',
    'labels': ['ない', 'ときどき', 'よくある'],
    'items': [{'text': t['ja']['q'], 'key': t['id']} for t in tricks],
    'total': {'name': '紐のゆるみ', 'min': len(tricks), 'max': len(tricks) * 3,
              'bands': TOTAL_BANDS},
    'keys': {t['id']: key_entry(t) for t in tricks},
}

FAQ = [
    ('財布の紐診断では何がわかりますか？',
     'ネット通販やお店で使われる「売る側の仕掛け」12種類のうち、あなたがどれに弱いかと、全体の財布の紐の固さ（固結び・蝶結び・ゆるみ気味・ほどけかけ）がわかります。12問に3択で答える1分ほどの診断で、弱い仕掛けごとに研究でわかっていることと対抗のしかたを出します。'),
    ('この診断は当たりますか？',
     '仕掛けそのもの（割引前の値段・時間の圧力・残りわずか・送料無料・分割払い・ポイントなど）は、行動経済学・心理学の研究で効果が調べられています。ただし質問と点数の区切りはSEADICEが作った簡易版で、研究で精度を確かめた尺度ではありません。そのため信ぴょう性はBとしています。'),
    ('衝動買いをしやすいのは意志が弱いからですか？',
     'そうとは限りません。この診断で扱う仕掛けは、だれにでも起きる心の働きを利用したものです。研究では、「残りわずか」の表示が売る側の仕掛けに見えると、買いたい気持ちはむしろ下がりました（Yeら, 2024）。どの仕掛けに弱いかを知っておくことが、流されないための第一歩です。'),
    ('買い物依存かどうかもわかりますか？',
     'わかりません。この診断は病気や依存の診断ではありません。買い物がやめられず生活に困っているときは、身近な消費生活センターや医療機関などの相談窓口を頼ってください。'),
    ('答えや結果はどこかに送られますか？',
     '送られません。結果はこのブラウザの中（診断プロフィール帳）にだけ保存され、もう一度診断すると前回との差が出ます。登録も不要です。'),
]

items_html = '\n'.join(
    f'''    <details class="trick">
      <summary><b>{esc(t["ja"]["name"])}</b><span>{esc(t["ja"]["how"])}</span></summary>
      <p><b>研究でわかったこと</b>: {research_html(t)}</p>
      <p><b>対抗のしかた</b>: {esc(t["ja"]["counter"])}</p>
      <p><a href="{LEDGER}{esc(t["article"])}/" target="_blank" rel="noopener">解説記事を読む（お金と心理）</a></p>
    </details>''' for t in tricks)

seen = set()
refs = []
for doi, cite in [(t['doi'], t['ja']['cite']) for t in tricks] + [(notice['doi'], notice['ja']['cite'])]:
    if doi in seen:
        continue
    seen.add(doi)
    refs.append(f'      <li>{esc(cite)}. <a href="{esc(doi)}" target="_blank" rel="noopener">論文</a></li>')

ld = {
    '@context': 'https://schema.org',
    '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'SEADICE', 'item': 'https://seadice.win/'},
            {'@type': 'ListItem', 'position': 2, 'name': '診断', 'item': 'https://seadice.win/diagnosis/'},
            {'@type': 'ListItem', 'position': 3, 'name': '財布の紐診断', 'item': URL}]},
        {'@type': 'WebApplication', 'name': '財布の紐診断（12問）', 'url': URL,
         'description': '12問に3択で答え、ネット通販やお店の「売る側の仕掛け」12種類のうちどれに弱いかと、財布の紐の固さを出す無料診断。仕掛けごとに研究と対抗のしかたつき。登録不要で、結果は端末内だけに保存される。',
         'applicationCategory': 'FinanceApplication', 'operatingSystem': 'Web', 'inLanguage': 'ja',
         'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'JPY'},
         'datePublished': PUBLISHED, 'dateModified': MODIFIED,
         'publisher': {'@id': 'https://seadice.win/#organization'}},
        {'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]},
    ],
}

faq_html = '\n'.join(
    f'    <h3 class="faq-q">{esc(q)}</h3>\n    <p class="faq-a">{esc(a)}</p>' for q, a in FAQ)
bands_html = '、'.join(f'{b["min"]}点以上「{b["label"]}」' for b in TOTAL_BANDS)

page = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>財布の紐診断｜衝動買いしやすい「売る側の仕掛け」がわかる（無料・12問） | SEADICE 診断</title>
  <meta name="description" content="あなたの財布の紐は固い？ゆるい？12問に3択で答えるだけで、「残りわずか」「◯%オフ」「送料無料」「分割払い」「ポイント◯倍」など売る側の仕掛け12種類のうち、どれに弱いかがわかる無料の衝動買い診断。仕掛けごとに行動経済学の研究と対抗のしかたつき。登録不要・約1分・結果は端末内だけに保存。">
  <meta name="author" content="SEADICE">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#f7f7fb">
  <link rel="canonical" href="{URL}">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="stylesheet" href="/diagnosis/assets/style.css">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="SEADICE">
  <meta property="og:title" content="財布の紐診断｜衝動買いしやすい「売る側の仕掛け」がわかる（12問）">
  <meta property="og:description" content="12問で、売る側の仕掛け12種類のうちどれに弱いかと、財布の紐の固さがわかる無料診断。研究と対抗のしかたつき。">
  <meta property="og:url" content="{URL}">
  <meta property="og:locale" content="ja_JP">
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body>
<header>
  <nav aria-label="ページナビゲーション">
    <a href="/" class="nav-logo">SEADICE</a>
  </nav>
</header>
<main>
  <div id="quiz-intro">
  <p class="breadcrumb"><a href="/">HOME</a> / <a href="/diagnosis/">診断</a> / 財布の紐診断</p>
  <p class="section-label">Diagnosis</p>
  <h1>財布の紐診断<br>（12問・あなたが弱い売る側の仕掛け）</h1>
  <p class="cred-row"><a class="cred cred-b" href="/diagnosis/rank/">信ぴょう性 <b>B</b></a>仕掛けは研究にもとづく・質問は簡易版</p>
  <p class="hero-desc">あなたの財布の紐は、どの仕掛けでゆるみますか。「残りわずか」「◯%オフ」「あと◯円で送料無料」「月々◯円」。買い物ページには、買わせるための仕掛けがたくさんあります。12問に答えると、どれに弱いかと、財布の紐の固さがわかります。所要時間は約1分です。</p>

    <button type="button" id="quiz-start-btn" class="quiz-start-btn">診断をはじめる（1分・全12問）</button>
  </div>

  <div id="quiz-progress-wrap">
    <div class="quiz-progress"><div class="quiz-progress-bar" id="quiz-progress-bar"></div></div>
    <p class="quiz-step-label"><span>質問</span><span id="quiz-progress-label">1 / {len(tricks)}</span></p>
  </div>
  <div id="quiz-questions" class="sd-tool"></div>

  <div id="quiz-result">
    <div class="result-card" style="--type-color:#5b5bd6">
      <p class="result-type">あなたの財布の紐は</p>
      <div class="total-box"></div>
      <h2 class="result-name" style="margin-top:8px;font-size:20px">仕掛けごとの弱さ（弱い順）</h2>
      <p class="sc-note">各1〜3点。点数が高いほど、その仕掛けで財布の紐がゆるみやすいということです。</p>
      <div class="sc-list"></div>
      <div class="tori">
        <p class="tori-title">あなたの対抗策（弱い仕掛けから）</p>
        <ul class="tori-list"></ul>
      </div>
      <div class="share-row">
        <a class="share-btn share-twitter" target="_blank" rel="noopener">Xでシェア</a>
        <a class="share-btn share-line" target="_blank" rel="noopener">LINEでシェア</a>
        <button type="button" class="retry-btn">もう一度診断する</button>
      </div>
      <a class="profile-note" href="/diagnosis/profile/"></a>
    </div>
  </div>

  <section class="about">
    <h2>結果の読み方</h2>
    <ul>
      <li>いちばん上が、財布の紐の固さです。12問の合計（12〜36点）で、固結び・蝶結び・ゆるみ気味・ほどけかけの4段階に分けます。</li>
      <li>その下に、仕掛けごとの弱さを弱い順に並べます。「弱い」「ときどき」の仕掛けには、研究でわかっていることと対抗のしかたを出します。</li>
      <li>1か月ほどたったら、もう一度診断してください。前回との差が出るので、紐が固くなったかを確かめられます（記録はこのブラウザの中だけ）。</li>
    </ul>

    <h2>売る側の仕掛け12種類と研究</h2>
    <p>開くと、研究でわかったこと・論文・対抗のしかた・解説記事が読めます。研究の数字は、SEADICEのメディア「お金と心理」で出典を確かめた記事から使っています。</p>
    <p><button type="button" class="open-all">すべて開く</button></p>
{items_html}

    <h2>点数の出し方</h2>
    <ul>
      <li>12問に3択（ない1点・ときどき2点・よくある3点）で答えます。1つの仕掛けにつき1問です。</li>
      <li>合計の区切りは {bands_html} です。この区切りと12の質問はSEADICEが作ったもので、研究で確かめた尺度ではありません。</li>
    </ul>

    <h2>研究ではどこまでわかっているか</h2>
    <ul>
      <li><b>わかっていること</b>: ここで扱う12の仕掛けは、どれも実験や購買データの分析で、買う量や買いたい気持ちを増やす方向に働くことが報告されています（上の各項目）。また、「残りわずか」の表示が売る側の仕掛けに見えると、買いたい気持ちはむしろ下がりました（5点満点で3.34→2.26。<a href="{esc(notice["doi"])}" target="_blank" rel="noopener">{esc(notice["ja"]["cite"])}</a>）。仕掛けに気づくこと自体に意味がある、というのがこの診断の考え方です。</li>
      <li><b>弱いところ</b>: {esc(notice["ja"]["limit"])} 仕掛けごとの効果の大きさは、商品や場面によって変わります。</li>
      <li><b>まだわからないこと</b>: 自分でどの仕掛けに弱いと答えた人が、実際の買い物でもその仕掛けに動かされやすいかは、確かめられていません。</li>
    </ul>

    <h2>買い物の途中で見抜くなら</h2>
    <p>SEADICEのiPhoneアプリ「<a href="/tools/spendology/">財布の紐</a>」（App Store近日公開）は、Safariの共有メニューや機能拡張から、開いている買い物ページの仕掛けを端末の中だけで見つけ、欲しい物は待つリストで時間を置いて決められます。同じ12の仕掛けと研究を使っています。</p>

    <h2>よくある質問</h2>
{faq_html}

    <h2>出典</h2>
    <ul class="ref-list">
{chr(10).join(refs)}
    </ul>
    <p style="font-size:12.5px;color:#5d5d70">質問・点数の区切り・結果の説明文は、上の研究をもとにSEADICEが書いたものです（公開: {PUBLISHED}）。</p>
  </section>

  <div class="related-box">
    <p class="related-title">関連</p>
    <div class="diag-list">
      <a class="diag-card" href="/diagnosis/loss-aversion/"><span class="diag-body"><span class="diag-title">損失回避度チェック（信ぴょう性B）</span></span></a>
      <a class="diag-card" href="/diagnosis/crt/"><span class="diag-body"><span class="diag-title">認知反射テスト（バットとボール問題）</span></span></a>
      <a class="diag-card" href="{LEDGER}impulse-buying-pre-purchase-checklist/"><span class="diag-body"><span class="diag-title">衝動買いしそうなときの、買う前チェック表（お金と心理）</span></span></a>
      <a class="diag-card" href="/diagnosis/profile/"><span class="diag-body"><span class="diag-title">診断プロフィール帳</span></span></a>
    </div>
  </div>

  <script type="application/json" id="scale-data">
{json.dumps(scale, ensure_ascii=False, indent=2)}
  </script>
  <script src="/diagnosis/assets/likert.js"></script>
  <script>document.querySelector('.open-all').addEventListener('click',function(){{var d=document.querySelectorAll('details.trick'),o=[].some.call(d,function(x){{return !x.open}});d.forEach(function(x){{x.open=o}});this.textContent=o?'すべて閉じる':'すべて開く'}});</script>
</main>
<footer>
  <p><a href="/">SEADICE</a> &nbsp;|&nbsp; &copy; 2026 SEADICE · <a href="/about/">運営者情報</a> · <a href="/promise/">7ヶ条</a></p>
</footer>
</body>
</html>
'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
# 中身が変わったときだけ書き換える（apply_page_type が差し込んだ CSS は残す）
if os.path.exists(OUT):
    old = open(OUT, encoding='utf-8').read()
    i = old.find('<style id="sd-design">')
    if i >= 0 and '</head>' in old:
        css = old[i:old.find('</head>')]
        page = page.replace('</head>', css + '</head>', 1).replace('<body>', '<body class="t-use">', 1)
    if old == page:
        print('変更なし')
        sys.exit(0)
open(OUT, 'w', encoding='utf-8').write(page)
print('書き出し:', OUT)
