#!/usr/bin/env python3
"""
p/apps/ 配下の全アプリについて、App Store公開済みかどうかを
公開API（iTunes Lookup、認証不要）で総当たりチェックし、
新しく見つかったものを p/released-apps.json に自動追加する。

bundle idは `win.seadice.{slug}` を基本形とし、Flutterの
プロジェクト名がDartパッケージ命名規則（アンダースコア）に
変換されている場合に備えて camelCase 版も試す。

使い方:
    python3 scripts/check_released_apps.py            # チェックして released-apps.json を更新
    python3 scripts/check_released_apps.py --dry-run   # 更新せず結果表示のみ
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT / "p" / "apps"
REGISTRY = ROOT / "p" / "released-apps.json"


def to_camel(slug: str) -> str:
    parts = re.split(r"[-_]", slug)
    if not parts:
        return slug
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def lookup_bundle(bundle_id: str):
    url = f"https://itunes.apple.com/lookup?bundleId={bundle_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            data = json.load(res)
    except Exception as e:
        print(f"  ! lookup failed for {bundle_id}: {e}", file=sys.stderr)
        return None
    if data.get("resultCount", 0) > 0:
        return data["results"][0]
    return None


def main():
    dry_run = "--dry-run" in sys.argv

    registry = {"_comment": "", "apps": []}
    if REGISTRY.exists():
        registry = json.loads(REGISTRY.read_text())
    known_ids = {a["id"] for a in registry["apps"]}

    slugs = sorted(
        p.name for p in APPS_DIR.iterdir()
        if p.is_dir() and (p / "index.html").exists()
    )

    found = []
    for slug in slugs:
        candidates = {f"win.seadice.{slug}", f"win.seadice.{to_camel(slug)}"}
        for bundle_id in candidates:
            result = lookup_bundle(bundle_id)
            if result:
                entry = {
                    "id": slug,
                    "name": result.get("trackName", slug),
                    "genre": "",
                    "appStoreId": str(result.get("trackId")),
                    "appStoreUrl": f"https://apps.apple.com/app/id{result.get('trackId')}",
                }
                found.append(entry)
                status = "NEW" if slug not in known_ids else "already known"
                print(f"[FOUND] {slug} -> {entry['appStoreUrl']} ({status})")
                break
        else:
            print(f"[ ]     {slug} (not found on App Store)")

    if dry_run:
        print("\n--dry-run: released-apps.json was not modified")
        return

    changed = False
    for entry in found:
        existing = next((a for a in registry["apps"] if a["id"] == entry["id"]), None)
        if existing is None:
            registry["apps"].append(entry)
            changed = True
        elif existing.get("appStoreId") != entry["appStoreId"]:
            existing.update(entry)
            changed = True

    if changed:
        registry["_comment"] = (
            "App StoreでApple審査を通過し公開済みのアプリだけをここに登録する。"
            "新規アプリの「関連アプリ」欄はこのファイルから選ぶ。"
            "scripts/check_released_apps.py で自動更新される。"
        )
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
        print(f"\n released-apps.json を更新しました（{len(registry['apps'])}件登録）")
    else:
        print("\n変更なし")


if __name__ == "__main__":
    main()
