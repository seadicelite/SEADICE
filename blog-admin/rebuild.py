#!/usr/bin/env python3
"""
編集済みcontent.mdからHTMLを再ビルドする
使い方: python3 blog-admin/rebuild.py <slug>
"""
import sys, json
from pathlib import Path
from generate import build_html, load_articles, md_to_html

def main():
    if len(sys.argv) < 2:
        print('使い方: python3 blog-admin/rebuild.py <slug>')
        return

    slug = sys.argv[1]
    SEADICE_DIR = Path('/Users/hidenori/Developer/SEADICE')
    article_dir = SEADICE_DIR / 'p' / 'blog' / slug
    md_file = article_dir / 'content.md'

    if not md_file.exists():
        print(f'content.mdが見つかりません: {md_file}')
        return

    articles = load_articles()
    meta = next((a for a in articles if a['slug'] == slug), None)
    if not meta:
        print(f'記事メタデータが見つかりません: {slug}')
        return

    body_md = md_file.read_text(encoding='utf-8')
    html = build_html(meta['title'], slug, meta['category'], body_md, meta['meta_desc'], meta['date'])
    (article_dir / 'index.html').write_text(html, encoding='utf-8')
    print(f'再ビルド完了: p/blog/{slug}/index.html')

if __name__ == '__main__':
    main()
