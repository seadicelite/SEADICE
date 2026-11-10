#!/usr/bin/env python3
"""Flutterアプリの起動画面を「地の色の無地＋下に SEADICE のマーク（青 #2F7BFF）」にする。

design/app-splash/branding.png（@4x）をアプリの assets/splash/ に置き、pubspec.yaml の
flutter_native_splash を書き換えて（真ん中の image は外す）`dart run flutter_native_splash:create` する。
地の色は pubspec の color、なければ lib/ の scaffoldBackgroundColor の色を使う。

  python3 scripts/apply_app_splash.py /path/to/app ...
  python3 scripts/apply_app_splash.py --color "#0A1628" /path/to/app   # 地の色を指定
"""
import re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANDING = ROOT / "design/app-splash/branding.png"
PADDING = 48
# 1x1 の透明 PNG
TRANSPARENT_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c636000020000050001e9fadcd80000000049454e44ae426082")


def ground_color(app):
    for f in sorted((app / "lib").rglob("*.dart")):
        s = f.read_text(errors="ignore")
        m = re.search(r"scaffoldBackgroundColor:\s*(?:const\s+)?(?:Color\(0x[Ff]{2}([0-9A-Fa-f]{6})\)|(\w+))", s)
        if not m:
            continue
        if m.group(1):
            return "#" + m.group(1).upper()
        v = re.search(re.escape(m.group(2)) + r"\s*=\s*(?:const\s+)?Color\(0x[Ff]{2}([0-9A-Fa-f]{6})\)", s)
        if v:
            return "#" + v.group(1).upper()
    return None


def apply(app, color=None):
    pub = app / "pubspec.yaml"
    s = pub.read_text()
    block = re.search(r"^flutter_native_splash:\n(?:[ \t]+.*\n|\n)*", s, re.M)
    if not color and block:
        m = re.search(r'^  color:\s*"?(#[0-9A-Fa-f]{6})', block.group(0), re.M)
        color = m and m.group(1).upper()
    color = color or ground_color(app)
    if not color:
        return f"地の色が見つからない（--color で指定）"
    new = (f'flutter_native_splash:\n  color: "{color}"\n  branding: assets/splash/branding.png\n'
           f'  branding_bottom_padding: {PADDING}\n  android_12:\n    color: "{color}"\n\n')
    s = s.replace(block.group(0), new) if block else s.rstrip("\n") + "\n\n" + new
    if not re.search(r"^  flutter_native_splash:", s, re.M):
        s = re.sub(r"^dev_dependencies:\n", "dev_dependencies:\n  flutter_native_splash: ^2.4.1\n", s, count=1, flags=re.M)
        subprocess.run(["flutter", "pub", "get", "--offline"], cwd=app, capture_output=True)
    pub.write_text(s)
    (app / "assets/splash").mkdir(parents=True, exist_ok=True)
    shutil.copy(BRANDING, app / "assets/splash/branding.png")
    r = subprocess.run(["dart", "run", "flutter_native_splash:create"], cwd=app, capture_output=True, text=True)
    if r.returncode:
        return "create 失敗: " + (r.stderr or r.stdout).strip().splitlines()[-1]
    # 真ん中の画像がないとき flutter_native_splash は不透明な黒の 1x1 を置くので、透明にする（明るい地で点に見える）
    for png in (app / "ios/Runner/Assets.xcassets/LaunchImage.imageset").glob("*.png"):
        png.write_bytes(TRANSPARENT_PNG)
    return f"ok {color}"


if __name__ == "__main__":
    args = sys.argv[1:]
    color = None
    if args[:1] == ["--color"]:
        color, args = args[1].upper(), args[2:]
    for a in args:
        print(apply(Path(a).resolve(), color), a)
