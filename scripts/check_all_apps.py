#!/usr/bin/env python3
"""App Store で公開中の SEADICE のアプリを全部引き、サイトに載っていないものを出す（手元専用・読むだけ）。

開発者ID で公開中のアプリを全部取り（iTunes Lookup、認証不要）、それぞれについて
  - p/released-apps.json にあるか（appStoreId で照合）
  - 紹介ページ p/tools/{id}/ か p/apps/{id}/ があるか
  - プライバシーポリシー p/privacy/{id}/ があるか
を見る。~/Developer 配下の Flutter アプリの Bundle ID も集め、どのフォルダのアプリかを添える。
/improve-app したアプリだけを見る check_released_apps.py では、触っていないアプリが漏れた
（やめラボ 10-13、ニートクエスト100 11-05 の2回、2026-11-11 に作った）。

  python3 scripts/check_all_apps.py
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "p/released-apps.json"
DEV = Path.home() / "Developer"


def get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def local_bundles():
    """Bundle ID → アプリのフォルダ（~/Developer 配下、4階層まで）"""
    out = {}
    for pub in DEV.glob("**/pubspec.yaml"):
        rel = pub.relative_to(DEV).parts
        if len(rel) > 5 or any(p.startswith(".") or p in ("build", "Pods", "ephemeral") for p in rel):
            continue
        pbx = pub.parent / "ios/Runner.xcodeproj/project.pbxproj"
        if not pbx.exists():
            continue
        ids = re.findall(r"PRODUCT_BUNDLE_IDENTIFIER = \"?([\w.\-]+)\"?;", pbx.read_text(errors="ignore"))
        ids = [i for i in ids if "RunnerTests" not in i]
        if ids:
            out.setdefault(min(ids, key=len), str(pub.parent.relative_to(DEV)))
    return out


def main():
    apps = json.loads(REGISTRY.read_text())["apps"]
    by_store = {a["appStoreId"]: a for a in apps}
    first = get(f"https://itunes.apple.com/lookup?id={apps[0]['appStoreId']}&country=jp")["results"][0]
    live = []
    for country in ("jp", "us"):
        res = get(f"https://itunes.apple.com/lookup?id={first['artistId']}&entity=software&limit=200&country={country}")
        live += [r for r in res["results"] if r.get("wrapperType") == "software"]
    live = list({str(r["trackId"]): r for r in live}.values())
    folders = local_bundles()

    problems = 0
    for r in sorted(live, key=lambda r: r["trackName"]):
        sid = str(r["trackId"])
        entry = by_store.get(sid)
        where = folders.get(r["bundleId"], "手元にフォルダなし")
        miss = []
        if not entry:
            miss.append("released-apps.json")
        else:
            i = entry["id"]
            if not ((ROOT / f"p/tools/{i}/index.html").exists() or (ROOT / f"p/apps/{i}/index.html").exists()):
                miss.append(f"紹介ページ /tools/{i}/")
            if not (ROOT / f"p/privacy/{i}/index.html").exists():
                miss.append(f"プライバシー /privacy/{i}/")
        if miss:
            problems += 1
            print(f"[ない] {r['trackName']}（id{sid}, {r['bundleId']}, {where}）: {'・'.join(miss)}")
    gone = [a for a in apps if a["appStoreId"] not in {str(r["trackId"]) for r in live}]
    for a in gone:
        print(f"[公開中でない] released-apps.json の {a['id']}（{a['name']}）が App Store で見つからない")
    print(f"\n公開中 {len(live)} 本・載っていない所があるもの {problems} 本・公開中でない登録 {len(gone)} 本")


if __name__ == "__main__":
    main()
