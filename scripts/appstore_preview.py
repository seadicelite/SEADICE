#!/usr/bin/env python3
"""App Store での見え方（アプリページのヘッダと検索結果）を画像にする。申請前の見た目確認用。

  python3 scripts/appstore_preview.py /path/to/アプリのフォルダ [--shots screenshots/6.9]

入力: アプリのフォルダの APPSTORE_SUBMISSION.md（アプリ名・サブタイトル・カテゴリ・年齢制限）、
      assets/icon/icon.png、スクリーンショット（既定は screenshots/6.9/ か screenshots/ の 1〜3.png）
出力: アプリのフォルダの store_preview/header.png と search.png（iPhone の画面幅 430pt を3倍で描く）
フォントはアプリに同梱の NotoSansJP を使う（無ければ --font で指定）。
App Store の画面を正確に再現するものではなく、文字の長さ・アイコン・1〜3枚目の並びを確かめる目安。
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 3  # 1pt = 3px
W = 430 * S
BG = (255, 255, 255)
TEXT = (0, 0, 0)
GRAY = (138, 138, 142)
LINE = (216, 216, 220)
BLUE = (0, 122, 255)
PILL = (238, 238, 240)


def meta(md: str) -> dict:
    """表（| 項目 | 値 |）と箇条書き（- **項目**: 値）の両方の書き方から読む"""
    def find(*keys):
        for k in keys:
            m = re.search(rf"^\|\s*{k}[^|]*\|\s*(.+?)\s*\|", md, re.M) or re.search(
                rf"^-\s*\*\*{k}[^*]*\*\*\s*[:：]\s*(.+)$", md, re.M)
            if m:
                return m.group(1).strip()
        return ""
    cat = find("主カテゴリ", "カテゴリ")
    return {
        "name": find("アプリ名"),
        "subtitle": find("サブタイトル（日本語", "サブタイトル"),
        "category": re.split(r"\s*[/（(]", cat)[0],
        "age": re.split(r"[（(]", find("年齢制限"))[0].strip(),
    }


def font(path, size, bold=False):
    f = ImageFont.truetype(str(path), size * S)
    try:
        f.set_variation_by_axes([700 if bold else 400])
    except Exception:
        pass  # 可変フォントでなければそのまま
    return f


def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    out = Image.new("RGBA", img.size)
    out.paste(img.convert("RGBA"), mask=mask)
    return out


def icon(path: Path, pt: int) -> Image.Image:
    px = pt * S
    im = Image.open(path).convert("RGBA").resize((px, px), Image.LANCZOS)
    im = rounded(im, int(px * 0.2237))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, px - 1, px - 1), int(px * 0.2237), outline=LINE, width=1)
    return im


def fit(d: ImageDraw.ImageDraw, text: str, f, maxw: int) -> str:
    """幅に収まらなければ末尾を … にする（App Store も同じように切る）"""
    if d.textlength(text, font=f) <= maxw:
        return text
    while text and d.textlength(text + "…", font=f) > maxw:
        text = text[:-1]
    return text + "…"


def get_button(d, x_right, y_mid, f):
    w, h = 74 * S, 30 * S
    box = (x_right - w, y_mid - h // 2, x_right, y_mid + h // 2)
    d.rounded_rectangle(box, h // 2, fill=PILL)
    d.text(((box[0] + box[2]) // 2, y_mid), "入手", font=f, fill=BLUE, anchor="mm")


def header(m, icon_path, fonts, out: Path):
    img = Image.new("RGB", (W, 260 * S), BG)
    d = ImageDraw.Draw(img)
    x0, y0 = 20 * S, 24 * S
    img.paste(ic := icon(icon_path, 118), (x0, y0), ic)
    tx = x0 + 118 * S + 16 * S
    tw = W - tx - 20 * S
    d.text((tx, y0 + 4 * S), fit(d, m["name"], fonts["title"], tw), font=fonts["title"], fill=TEXT)
    d.text((tx, y0 + 36 * S), fit(d, m["subtitle"], fonts["sub"], tw), font=fonts["sub"], fill=GRAY)
    get_button(d, tx + 74 * S, y0 + 118 * S - 15 * S, fonts["btn"])
    # 下の情報の列（年齢・カテゴリ・価格）
    y = y0 + 118 * S + 30 * S
    d.line((x0, y, W - x0, y), fill=LINE, width=S)
    cols = [("年齢", m["age"] or "-"), ("カテゴリ", m["category"] or "-"), ("価格", "無料")]
    cw = (W - 2 * x0) // len(cols)
    for i, (k, v) in enumerate(cols):
        cx = x0 + cw * i + cw // 2
        d.text((cx, y + 18 * S), k, font=fonts["small"], fill=GRAY, anchor="mt")
        d.text((cx, y + 38 * S), fit(d, v, fonts["info"], cw - 8 * S), font=fonts["info"], fill=GRAY, anchor="mt")
        if i:
            d.line((x0 + cw * i, y + 18 * S, x0 + cw * i, y + 62 * S), fill=LINE, width=S)
    img.save(out)


def search(m, icon_path, shots, fonts, out: Path):
    pad = 20 * S
    gap = 8 * S
    sw = (W - 2 * pad - 2 * gap) // 3
    first = Image.open(shots[0])
    sh = int(sw * first.height / first.width)
    img = Image.new("RGB", (W, 24 * S + 64 * S + 14 * S + sh + 24 * S), BG)
    d = ImageDraw.Draw(img)
    y0 = 24 * S
    img.paste(ic := icon(icon_path, 64), (pad, y0), ic)
    tx = pad + 64 * S + 12 * S
    tw = W - tx - pad - 74 * S - 12 * S
    d.text((tx, y0 + 8 * S), fit(d, m["name"], fonts["name"], tw), font=fonts["name"], fill=TEXT)
    d.text((tx, y0 + 32 * S), fit(d, m["subtitle"], fonts["sub"], tw), font=fonts["sub"], fill=GRAY)
    get_button(d, W - pad, y0 + 32 * S, fonts["btn"])
    y = y0 + 64 * S + 14 * S
    for i, p in enumerate(shots[:3]):
        im = Image.open(p).convert("RGB").resize((sw, sh), Image.LANCZOS)
        im = rounded(im, 12 * S)
        img.paste(im, (pad + i * (sw + gap), y), im)
        d.rounded_rectangle((pad + i * (sw + gap), y, pad + i * (sw + gap) + sw - 1, y + sh - 1), 12 * S, outline=LINE, width=1)
    img.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("app", type=Path)
    ap.add_argument("--shots", type=Path, help="スクリーンショットのフォルダ（アプリのフォルダからの相対でも可）")
    ap.add_argument("--font", type=Path)
    a = ap.parse_args()
    app = a.app.resolve()
    md = (app / "APPSTORE_SUBMISSION.md").read_text()
    m = meta(md)
    # 更新用の提出ファイル（変わった項目だけ）は、見出しのアプリ名と「ja:」のサブタイトルから読み、
    # 足りない項目は APPSTORE_DRAFT.md（初回の下書き）から補う
    if not m["name"]:
        h = re.search(r"^#\s+(.+?)\s+\d+\.\d+", md, re.M)
        m["name"] = h.group(1).strip() if h else ""
    if not m["subtitle"]:
        sub = re.search(r"^##\s*サブタイトル[^\n]*\n(?:.*\n)*?\s*ja\s*[:：]\s*(.+)$", md, re.M)
        m["subtitle"] = sub.group(1).strip() if sub else ""
    # 「## サブタイトル（30字まで）」の次の行に値だけを書く形にも対応する（通知de人生改善 1.1.0 で読めなかった）
    for key, head in (("subtitle", "サブタイトル"), ("name", "アプリ名")):
        if not m[key]:
            v = re.search(rf"^##\s*{head}[^\n]*\n\s*([^\n#|\-][^\n]*)$", md, re.M)
            m[key] = v.group(1).strip() if v else m[key]
    draft = app / "APPSTORE_DRAFT.md"
    if draft.exists():
        for k, v in meta(draft.read_text()).items():
            m[k] = m[k] or v
    if not m["name"]:
        sys.exit("APPSTORE_SUBMISSION.md にアプリ名が見つかりません")
    icon_path = app / "assets/icon/icon.png"
    if not icon_path.exists():  # assets/icon がないアプリは iOS のアイコン（1024px）を使う
        icon_path = app / "ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png"
    shots_dir = a.shots if a.shots and a.shots.is_absolute() else app / (a.shots or "")
    if not a.shots:
        shots_dir = next((p for p in (app / "screenshots/6.9", app / "screenshots") if (p / "1.png").exists()), None)
    shots = [shots_dir / f"{i}.png" for i in (1, 2, 3)] if shots_dir else []
    if not shots or not all(p.exists() for p in shots):
        sys.exit(f"スクリーンショット 1〜3.png が見つかりません: {shots_dir}")
    font_path = a.font or next(iter(sorted((app / "assets/fonts").glob("NotoSansJP*"))), None)
    if not font_path:
        sys.exit("日本語フォントが見つかりません。--font で指定してください")
    fonts = {
        "title": font(font_path, 22, True), "name": font(font_path, 16, True),
        "sub": font(font_path, 14), "btn": font(font_path, 15, True),
        "small": font(font_path, 11), "info": font(font_path, 13, True),
    }
    out = app / "store_preview"
    out.mkdir(exist_ok=True)
    header(m, icon_path, fonts, out / "header.png")
    search(m, icon_path, shots, fonts, out / "search.png")
    print(f"{m['name']} / {m['subtitle']}\n→ {out}/header.png, search.png")


if __name__ == "__main__":
    main()
