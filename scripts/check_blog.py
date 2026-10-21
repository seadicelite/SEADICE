#!/usr/bin/env python3
"""p/blog/ の点検: publisher @id・tool-cta・BreadcrumbList の漏れ、題名の過去年、
内部リンク切れ（firebase.json の301は除く）、sitemap のずれ（meta robots noindex の掲載・未掲載）。"""
import glob, json, os, re

fs = sorted(glob.glob('p/blog/*/index.html'))
sitemap = open('p/sitemap.xml', encoding='utf-8').read()
redirects = [r['source'].replace('{,/}', '').rstrip('/') for r in json.load(open('firebase.json')).get('hosting', {}).get('redirects', [])]
print('記事', len(fs))
for f in fs:
    s = open(f, encoding='utf-8').read()
    for key, name in (('#organization', 'publisher @id'), ('tool-cta', 'tool-cta'), ('BreadcrumbList', 'BreadcrumbList')):
        if key not in s:
            print('漏れ', name, f)
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    if t and re.search(r'20(1\d|2[0-5])年', t.group(1)):
        print('過去年の題名', f)
    for h in set(re.findall(r'href="(/[^"#?]*)', s)):
        p = 'p' + h
        if not (os.path.exists(p) and not os.path.isdir(p)) and not os.path.exists(p.rstrip('/') + '/index.html') \
                and not any(h.rstrip('/') == r or h.startswith(r + '/') for r in redirects):
            print('リンク切れ', f, h)
    url = 'https://seadice.win/' + f[2:-len('index.html')]
    noindex = re.search(r'<meta name="robots"[^>]*noindex', s) is not None
    if noindex and url in sitemap:
        print('noindexなのにsitemap', url)
    if not noindex and url not in sitemap:
        print('sitemap漏れ', url)

# 同じテーマの重複候補: 題名の2文字の並び（日誌は除く）の重なりが0.5以上の組
def grams(t):
    t = re.sub(r'[\s\W_|]+', '', t)
    return {t[i:i + 2] for i in range(len(t) - 1)}
titles = {}
for f in fs:
    if '/daily-' in f:
        continue
    t = re.search(r'<title>(.*?)</title>', open(f, encoding='utf-8').read(), re.S)
    if t:
        titles[f] = grams(t.group(1).split('|')[0])
ks = list(titles)
for i, a in enumerate(ks):
    for b in ks[i + 1:]:
        j = len(titles[a] & titles[b]) / max(1, len(titles[a] | titles[b]))
        if j >= 0.5:
            print('重複候補 %.2f' % j, a, b)
