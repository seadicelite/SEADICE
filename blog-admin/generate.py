#!/usr/bin/env python3
"""
SEADICE Blog Auto Generator
cronで毎日実行: 0 23 * * * /usr/bin/python3 /Users/hidenori/Developer/SEADICE/blog-admin/generate.py
"""
import os, re, json, subprocess, unicodedata

try:
    import tweepy as _tweepy
except ImportError:
    _tweepy = None
from datetime import date
from pathlib import Path

# .envからAPIキー読み込み
def _load_env(path):
    p = Path(path)
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

_load_env(Path(__file__).parent / '.env')
_load_env(Path('/Users/hidenori/Developer/x-auto/.env'))

try:
    import anthropic
except ImportError:
    print('anthropic パッケージが必要です: pip3 install anthropic')
    exit(1)

SEADICE_DIR = Path('/Users/hidenori/Developer/SEADICE')
BLOG_DIR = SEADICE_DIR / 'p' / 'blog'
ADMIN_DIR = Path(__file__).parent
SCHEDULE_FILE = ADMIN_DIR / 'schedule.json'
ARTICLES_FILE = ADMIN_DIR / 'articles.json'

CATEGORY_IMAGES = {
    '開発': '/icons/blog_dev.webp',
    'Flutter': '/icons/blog_flutter.webp',
    'AI': '/icons/blog_ai.webp',
    'SEO': '/icons/blog_seo.webp',
    'ビジネス': '/icons/blog_business.webp',
    'ツール': '/icons/blog_tool.webp',
}

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\w\s-]', '', text, flags=re.ASCII).strip().lower()
    text = re.sub(r'[\s_-]+', '-', text)
    return text or f'post-{date.today().strftime("%Y%m%d")}'

def next_article() -> dict | None:
    if not SCHEDULE_FILE.exists():
        return None
    schedule = json.loads(SCHEDULE_FILE.read_text())
    for item in schedule:
        if not item.get('done'):
            return item
    return None

def mark_done(no: int):
    schedule = json.loads(SCHEDULE_FILE.read_text())
    for item in schedule:
        if item['no'] == no:
            item['done'] = True
    SCHEDULE_FILE.write_text(json.dumps(schedule, ensure_ascii=False, indent=2))

def generate_article(title: str, category: str) -> tuple[str, str]:
    client = anthropic.Anthropic()

    body_msg = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=4000,
        messages=[{
            'role': 'user',
            'content': f'''あなたはSEADICE STUDIOの開発ブログ記事を書くライターです。
以下の情報をもとに、読者に役立つ日本語のブログ記事をMarkdown形式で書いてください。

タイトル: {title}
カテゴリ: {category}

条件:
- 1500〜2500文字程度
- ## で大見出し、### で小見出し
- 具体的でわかりやすい内容
- SEADICEの開発者視点で書く（個人開発・AI活用・Flutter・自動化が得意分野）
- 読者は個人事業主・中小企業の経営者・担当者で、コストをかけずに業務効率化・自動化・AI活用をしたい人
- 専門用語はなるべく避け、わかりやすく実践的な内容にする
- 「自分もやってみよう」と思えるような具体的な手順や事例を入れる
- 最後に「まとめ」セクションを入れる
- 本文のみ出力（タイトル行は含めない）'''
        }]
    )
    body = body_msg.content[0].text.strip()

    desc_msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=150,
        messages=[{
            'role': 'user',
            'content': f'以下のブログ記事のmeta descriptionを100〜120文字で1文で書いてください。説明文のみ出力。\nタイトル: {title}\nカテゴリ: {category}'
        }]
    )
    meta_desc = desc_msg.content[0].text.strip()
    return body, meta_desc

def md_to_html(md: str) -> str:
    import html as htmllib
    text = htmllib.escape(md)
    text = re.sub(r'```[\w]*\n?(.*?)```', lambda m: f'<pre><code>{m.group(1)}</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group(0)}</ul>', text, flags=re.DOTALL)
    text = re.sub(r'^---$', '<hr>', text, flags=re.MULTILINE)
    paras = re.split(r'\n{2,}', text)
    result = []
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if re.match(r'^<(h[23]|ul|pre|hr)', p):
            result.append(p)
        else:
            result.append(f'<p>{p}</p>')
    return '\n'.join(result)

def build_html(title: str, slug: str, category: str, body_md: str, meta_desc: str, pub_date: str) -> str:
    body_html = md_to_html(body_md)
    cat_img = CATEGORY_IMAGES.get(category, '/icons/blog_dev.webp')
    ogp_img = f'https://seadice.win{cat_img}'
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | SEADICE STUDIO</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="https://seadice.win/blog/{slug}/">
<meta property="og:title" content="{title} | SEADICE STUDIO">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="{ogp_img}">
<link rel="preload" href="{cat_img}" as="image">
<meta property="og:url" content="https://seadice.win/blog/{slug}/">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BlogPosting","headline":"{title}","datePublished":"{pub_date}","author":{{"@type":"Organization","name":"SEADICE STUDIO"}},"publisher":{{"@type":"Organization","name":"SEADICE STUDIO","url":"https://seadice.win"}}}}</script>
<style>*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}:root{{--bg:#05050C;--card:#0C0C1A;--accent:#00FFD1;--accent2:#38BDF8;--border:#1a1a2e;--text:#e2e8f0;--muted:#64748b}}body{{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.7}}nav{{position:fixed;top:0;left:0;right:0;z-index:100;backdrop-filter:blur(12px);background:rgba(5,5,12,.8);border-bottom:1px solid var(--border);padding:0 20px;height:56px;display:flex;align-items:center;justify-content:space-between}}.nav-logo{{font-size:15px;font-weight:800;letter-spacing:.15em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none}}article{{max-width:680px;margin:0 auto;padding:96px 24px 80px}}.breadcrumb{{font-size:12px;color:var(--muted);margin-bottom:24px}}.breadcrumb a{{color:var(--muted);text-decoration:none}}.breadcrumb a:hover{{color:var(--text)}}.tag{{display:inline-block;font-size:10px;letter-spacing:.1em;color:var(--accent);border:1px solid var(--accent);border-radius:4px;padding:2px 8px;margin-bottom:12px}}h1{{font-size:clamp(24px,5vw,36px);font-weight:800;line-height:1.2;margin-bottom:16px}}.meta{{font-size:12px;color:var(--muted);margin-bottom:40px;padding-bottom:24px;border-bottom:1px solid var(--border)}}.body h2{{font-size:22px;font-weight:800;margin:40px 0 12px;color:var(--accent)}}.body h3{{font-size:17px;font-weight:700;margin:28px 0 8px}}.body p{{margin:14px 0;font-size:15px;color:#cbd5e1;line-height:1.8}}.body ul{{padding-left:24px;margin:10px 0}}.body li{{margin:6px 0;font-size:15px;color:#cbd5e1}}.body strong{{color:var(--text);font-weight:700}}.body code{{background:var(--card);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:13px}}.body pre{{background:var(--card);padding:20px;border-radius:10px;overflow-x:auto;margin:16px 0}}.body pre code{{background:none;padding:0;font-size:13px}}.body hr{{border:none;border-top:1px solid var(--border);margin:32px 0}}.body img{{max-width:100%;border-radius:10px;margin:16px 0}}.back{{display:inline-flex;align-items:center;gap:6px;color:var(--muted);text-decoration:none;font-size:13px;margin-top:48px;padding:10px 0}}.back:hover{{color:var(--text)}}footer{{border-top:1px solid var(--border);padding:24px;text-align:center;font-size:12px;color:var(--muted)}}</style>
</head>
<body>
<nav>
  <a href="/" class="nav-logo">SEADICE</a>
  <a href="/blog/" style="font-size:13px;color:var(--muted);text-decoration:none">Blog</a>
</nav>
<article>
  <p class="breadcrumb"><a href="/">HOME</a> / <a href="/blog/">BLOG</a> / {title}</p>
  <img src="{cat_img}" alt="{category}" width="680" height="340" style="width:100%;height:240px;object-fit:cover;border-radius:16px;margin-bottom:24px">
  <span class="tag">{category}</span>
  <h1>{title}</h1>
  <p class="meta"><time datetime="{pub_date}">{pub_date}</time> · SEADICE STUDIO</p>
  <div class="body">{body_html}</div>
  <a href="/blog/" class="back">
    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
    ブログ一覧へ
  </a>
</article>
<footer>&copy; 2025 SEADICE STUDIO</footer>
</body>
</html>'''

def load_articles() -> list[dict]:
    if ARTICLES_FILE.exists():
        return json.loads(ARTICLES_FILE.read_text())
    return []

def save_articles(articles: list[dict]):
    ARTICLES_FILE.write_text(json.dumps(articles, ensure_ascii=False, indent=2))

def update_blog_index(articles: list[dict]):
    cards = ''
    for a in sorted(articles, key=lambda x: x['date'], reverse=True):
        cards += f'''    <a class="blog-card" href="/blog/{a['slug']}/">
      <span class="blog-tag">{a['category']}</span>
      <p class="blog-title">{a['title']}</p>
      <p class="blog-meta">{a['date']} · SEADICE STUDIO</p>
    </a>\n'''

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>開発ブログ | SEADICE STUDIO</title>
<meta name="description" content="SEADICE STUDIOの開発ブログ。AI活用・Flutter・個人開発・自動化に関する記事を発信しています。">
<link rel="canonical" href="https://seadice.win/blog/">
<style>*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}:root{{--bg:#05050C;--card:#0C0C1A;--accent:#00FFD1;--accent2:#38BDF8;--border:#1a1a2e;--text:#e2e8f0;--muted:#64748b}}body{{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.6}}nav{{position:fixed;top:0;left:0;right:0;z-index:100;backdrop-filter:blur(12px);background:rgba(5,5,12,.8);border-bottom:1px solid var(--border);padding:0 20px;height:56px;display:flex;align-items:center;justify-content:space-between}}.nav-logo{{font-size:15px;font-weight:800;letter-spacing:.15em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none}}.main{{max-width:720px;margin:0 auto;padding:96px 24px 80px}}.section-label{{font-size:11px;letter-spacing:.2em;color:var(--accent);margin-bottom:12px}}.section-title{{font-size:clamp(24px,5vw,36px);font-weight:800;margin-bottom:40px}}.blog-list{{display:flex;flex-direction:column;gap:12px}}.blog-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 24px;text-decoration:none;color:var(--text);transition:border-color .2s,transform .2s;display:block}}.blog-card:hover{{border-color:var(--accent);transform:translateY(-2px)}}.blog-tag{{display:inline-block;font-size:10px;letter-spacing:.1em;color:var(--accent);border:1px solid var(--accent);border-radius:4px;padding:2px 8px;margin-bottom:8px}}.blog-title{{font-size:16px;font-weight:700;margin-bottom:6px}}.blog-meta{{font-size:12px;color:var(--muted)}}footer{{border-top:1px solid var(--border);padding:24px;text-align:center;font-size:12px;color:var(--muted)}}</style>
</head>
<body>
<nav>
  <a href="/" class="nav-logo">SEADICE</a>
  <a href="/" style="font-size:13px;color:var(--muted);text-decoration:none">Home</a>
</nav>
<div class="main">
  <p class="section-label">BLOG</p>
  <h1 class="section-title">開発ブログ</h1>
  <div class="blog-list">
{cards}  </div>
</div>
<footer>&copy; 2025 SEADICE STUDIO</footer>
</body>
</html>'''
    (BLOG_DIR / 'index.html').write_text(html, encoding='utf-8')

def update_top_page(articles: list[dict]):
    index_path = SEADICE_DIR / 'p' / 'index.html'
    content = index_path.read_text(encoding='utf-8')
    recent = sorted(articles, key=lambda x: x['date'], reverse=True)[:3]
    cards = ''
    for a in recent:
        cards += f'''    <a class="blog-card" href="/blog/{a['slug']}/">
      <div class="blog-card-body">
        <span class="blog-tag">{a['category']}</span>
        <p class="blog-title">{a['title']}</p>
        <p class="blog-meta">{a['date']} · SEADICE</p>
      </div>
      <span class="blog-arrow">›</span>
    </a>\n'''
    new_list = f'<div class="blog-list">\n{cards}  </div>'
    content = re.sub(
        r'<div class="blog-list">.*?</div>',
        new_list, content, flags=re.DOTALL
    )
    index_path.write_text(content, encoding='utf-8')

def _post_to_x(title, slug):
    if not _tweepy:
        print('tweepy未インストールのためX投稿をスキップ')
        return
    api_key        = os.environ.get('API_KEY')
    api_secret     = os.environ.get('API_SECRET')
    access_token   = os.environ.get('ACCESS_TOKEN')
    access_secret  = os.environ.get('ACCESS_TOKEN_SECRET')
    if not all([api_key, api_secret, access_token, access_secret]):
        print('X APIキー未設定のためX投稿をスキップ')
        return
    try:
        client = _tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        text = f'あ、新しい記事が出たみたい〜！\n\n「{title}」\n\nhttps://seadice.win/blog/{slug}/\n\nよかったら読んでみてね。ころころ。\n\n#個人事業 #自動化 #AI'
        client.create_tweet(text=text)
        print('X投稿完了')
    except Exception as e:
        print(f'X投稿エラー: {e}')


def main():
    item = next_article()
    if not item:
        print('スケジュールに残っている記事がありません')
        return

    title = item['title']
    category = item['category']
    slug = slugify(title)
    pub_date = str(date.today())

    print(f'生成中: {title}')
    body_md, meta_desc = generate_article(title, category)

    html = build_html(title, slug, category, body_md, meta_desc, pub_date)
    article_dir = BLOG_DIR / slug
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / 'index.html').write_text(html, encoding='utf-8')
    (article_dir / 'content.md').write_text(body_md, encoding='utf-8')

    articles = load_articles()
    articles = [a for a in articles if a['slug'] != slug]
    articles.append({'title': title, 'slug': slug, 'category': category, 'date': pub_date, 'meta_desc': meta_desc})
    save_articles(articles)

    update_blog_index(articles)
    update_top_page(articles)
    mark_done(item['no'])

    print('コミット中...')
    subprocess.run(['git', 'add', '-A'], cwd=str(SEADICE_DIR))
    subprocess.run(
        ['git', 'commit', '-m', f'Auto: add blog {slug}'],
        cwd=str(SEADICE_DIR), capture_output=True, text=True
    )

    print('デプロイ中...')
    result = subprocess.run(
        ['firebase', 'deploy', '--only', 'hosting'],
        cwd=str(SEADICE_DIR), capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f'公開完了: https://seadice.win/blog/{slug}/')
        _post_to_x(title, slug)
    else:
        print('デプロイエラー:', result.stderr)

if __name__ == '__main__':
    main()
