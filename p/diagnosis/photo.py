#!/usr/bin/env python3
"""診断ページにWikimedia Commonsの写真を1枚入れる（APIキー不要）。
使い方: python3 photo.py <診断slug> "<英語の検索語>" [--replace]
パブリックドメイン/CC0/CC BY/CC BY-SA のJPEGのみを採用し、撮影者・ライセンス・元ページを必ず表示する。
候補なし・API失敗のときは何もせず正常終了（ページは写真なしでも成立する）。
seadice-media の media/photo.py と同じ方式を流用（今後の診断追加時もこのスクリプトを都度呼ぶだけでよい）。
"""
import html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UA = "SEADICE-diagnosis/1.0 (https://seadice.win; hi@seadice.win)"
OK_LIC = re.compile(r"^(CC0|CC BY(?!-N)(?!.*\bN[CD]\b)|CC BY-SA(?!.*\bN[CD]\b)|Public domain|PD)", re.I)
BAD_TITLE = re.compile(r"\b(map|logo|flag|diagram|chart|coat of arms|screenshot|scan|poster|stamp|illustration|statue|sculpture|"
                       r"nude|naked|nudity|topless|erotic|sex\w*|bikini|lingerie|underwear|fetish|porn\w*|"
                       r"patient|hospital|intensive care|surgery|wound|injur\w*|corpse|dead|death|funeral|autopsy|"
                       r"war|weapon|gun|blood|accident|crash|disaster|victim|suicide|drug\w*|child abuse)\b", re.I)
IMAGES_FILE = ROOT / "assets" / "photos.json"
FIG = re.compile(r'<figure class="hero">.*?</figure>\s*', re.S)


def strip(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t or "")).strip()


def clean_artist(a):
    if a.startswith("http"):
        name = re.sub(r"-\d+$", "", a.rstrip("/").split("/")[-1])
        return (name + (" (Pixabay)" if "pixabay" in a else ""))[:80]
    return a[:80] or "Unknown"


def search(query):
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
              "gsrnamespace": 6, "gsrlimit": 30, "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
              "iiurlwidth": 960, "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|ImageDescription"}
    r = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    pages = json.load(urllib.request.urlopen(r, timeout=20)).get("query", {}).get("pages", {})
    return sorted(pages.values(), key=lambda p: p.get("index", 999))


def main(slug, query, flag=""):
    art = ROOT / slug / "index.html"
    images = json.loads(IMAGES_FILE.read_text()) if IMAGES_FILE.exists() else {}
    text = art.read_text()
    if flag == "--replace":
        images.pop(slug, None)
        text = FIG.sub("", text)
    elif slug in images or 'class="hero"' in text:
        return print("skip: 既に写真あり")
    used = {i.get("file") for i in images.values()}
    try:
        pick = None
        for p in search(query):
            ii = (p.get("imageinfo") or [{}])[0]
            m = ii.get("extmetadata", {})
            lic = strip(m.get("LicenseShortName", {}).get("value"))
            if (ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 1200 or ii.get("width", 0) < ii.get("height", 0)
                    or not OK_LIC.match(lic) or BAD_TITLE.search(p["title"] + " " + strip(m.get("ImageDescription", {}).get("value"))) or p["title"] in used or not ii.get("thumburl")):
                continue
            pick = (p, ii, m, lic)
            break
    except Exception as e:  # noqa: BLE001
        return print("skip: Commons API 失敗", e)
    if not pick:
        return print("skip: 候補なし")
    p, ii, m, lic = pick
    base = ii["thumburl"].split("?")[0].replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/")
    t1024 = re.sub(r"/\d+px-", "/960px-", base)
    ratio = ii["thumbheight"] / ii["thumbwidth"]
    i = {"file": p["title"], "src": t1024, "w": 960, "h": round(960 * ratio),
         "alt": (strip(m.get("ImageDescription", {}).get("value")) or query)[:140],
         "artist": clean_artist(strip(m.get("Artist", {}).get("value"))), "license": lic,
         "licenseUrl": m.get("LicenseUrl", {}).get("value", ""), "page": ii["descriptionurl"]}
    images[slug] = i
    IMAGES_FILE.write_text(json.dumps(images, ensure_ascii=False, indent=1))
    lic_html = f'<a href="{html.escape(i["licenseUrl"], quote=True)}" target="_blank" rel="noopener">{html.escape(lic)}</a>' if i["licenseUrl"] else html.escape(lic)
    fig = (f'<figure class="hero"><img src="{i["src"]}" width="{i["w"]}" height="{i["h"]}" alt="{html.escape(i["alt"], quote=True)}" loading="eager">'
           f'<figcaption>Photo: {html.escape(i["artist"])} / {lic_html} / '
           f'<a href="{i["page"]}" target="_blank" rel="noopener">Wikimedia Commons</a></figcaption></figure>\n\n  ')
    text = text.replace('  <div class="ad-slot">', "  " + fig + '<div class="ad-slot">', 1)
    art.write_text(text)
    print("photo:", p["title"], "|", i["artist"], "|", lic)


if __name__ == "__main__":
    main(*sys.argv[1:4])
