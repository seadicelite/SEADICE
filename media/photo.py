#!/usr/bin/env python3
"""記事に Unsplash の写真を1枚入れる。1記事につき検索1回・download通知1回のみ。
使い方: UNSPLASH_ACCESS_KEY=... python3 media/photo.py research <記事slug> "<英語の検索語>"
キー未設定・検索失敗・ヒット無しのときは何もせず正常終了(記事は写真なしでも成立する)。"""
import html, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UTM = "?utm_source=seadice_research&utm_medium=referral"
CSS = ".hero{margin:0 0 24px}.hero img{display:block;width:100%;height:auto;border-radius:14px;background:#0C0C1A}.hero figcaption{font-size:11px;color:var(--muted);margin-top:6px}.hero figcaption a{color:#7dd3fc}"


def api(u, key):
    r = urllib.request.Request(u, headers={"Authorization": "Client-ID " + key, "Accept-Version": "v1"})
    return json.load(urllib.request.urlopen(r, timeout=20))


def main(media, slug, query):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return print("skip: UNSPLASH_ACCESS_KEY 未設定")
    cfg = json.loads((ROOT / f"media/{media}.json").read_text())
    art = ROOT / cfg["path"] / slug / "index.html"
    ip = ROOT / f"media/{media}-images.json"
    images = json.loads(ip.read_text()) if ip.exists() else {}
    if slug in images or 'class="hero"' in art.read_text():
        return print("skip: 既に写真あり")
    used = {i["id"] for i in images.values()}
    try:
        res = api("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(
            {"query": query, "per_page": 10, "orientation": "landscape", "content_filter": "high"}), key)["results"]
        pick = next((r for r in res if r["id"] not in used), None)
        if not pick:
            return print("skip: 候補なし")
        api(pick["links"]["download_location"], key)  # 規約: 使用時にdownload通知
    except Exception as e:  # noqa: BLE001
        return print("skip: Unsplash API 失敗", e)
    i = {"id": pick["id"], "raw": pick["urls"]["raw"], "alt": pick.get("alt_description") or query,
         "name": pick["user"]["name"], "userUrl": pick["user"]["links"]["html"], "page": pick["links"]["html"],
         "w": pick["width"], "h": pick["height"]}
    images[slug] = i
    ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
    fig = (f'<figure class="hero"><img src="{i["raw"]}&w=1000&h=520&fit=crop&q=70&fm=webp" width="1000" height="520" alt="{html.escape(i["alt"], quote=True)}">'
           f'<figcaption>Photo by <a href="{i["userUrl"]}{UTM}" target="_blank" rel="noopener">{html.escape(i["name"])}</a> on '
           f'<a href="https://unsplash.com/{UTM}" target="_blank" rel="noopener">Unsplash</a></figcaption></figure>\n\n  ')
    s = art.read_text()
    s = s.replace('  <div class="ai-badge">', "  " + fig + '<div class="ai-badge">', 1).replace("footer{border-top", CSS + "footer{border-top", 1)
    art.write_text(s)
    print("photo:", pick["id"], i["name"])


if __name__ == "__main__":
    main(*sys.argv[1:4])
