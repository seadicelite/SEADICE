#!/usr/bin/env python3
"""App Store のモックアップを、アプリの screenshots/mockup.json から全部の枠ぶん書き出す（docs/mockup.md）。

  python3 scripts/mockup.py {アプリのフォルダ} --init   # raw/ の画像から mockup.json のひな形と、アプリの色からの配色3案を出す
  python3 scripts/mockup.py {アプリのフォルダ}          # 書き出し → 点検 → 見え方の確認 → プレビューで開く
  python3 scripts/mockup.py {アプリのフォルダ} --styles   # 1〜3枚目を全スタイルで描いて見比べる（styles.png）
  python3 scripts/mockup.py {アプリのフォルダ} --no-open

アプリごとに make.py を写さず、色・印・見出し・使う画面だけを mockup.json に書く。形は
evidence/screenshots/make.py と同じ（上に印と見出し2行＋補足、下に実画面を角丸の枠で）。
書き出しの前に、価格の言葉と見出しのはみ出しを確かめ、あれば止める。

mockup.json:
{
  "colors": {"bg": "#1F3A5F", "text": "#FFFFFF", "accent": "#F59E0B", "sub": "#C9D3E0", "frame": "#0E1B2C"},
  "badge": "広告なし・登録なし",
  "slides": [{"shot": "1.png", "lines": ["1行目", "2行目（アクセント色）", "補足"]}, ...],
  "wide": {"shots": ["1.png", "3.png", "5.png"], "lines": ["1行目", "2行目", "補足"]},
  "style": "classic",                      # classic・split（上下で地が変わる）・bold（左寄せと番号）・panorama（6枚で図形がつながる）
  "font": "gothic",                        # gothic・maru・mincho・アプリの書体（例: "assets/fonts/NotoSansJP-VariableFont_wght.ttf"）
  "device": false,                         # iPhone・iPad の本体の縁を描く（"status_bar": true なら実画面にステータスバーがある）
  "crop_center": [],                       # iPad で中身が中央に小さく出る画面（中央を切り出す）
  "widget": ["widget_medium.png", "widget_large.png"],   # slides の shot に "widget" と書くと、これを並べた絵を使う
  "en": {"badge": ..., "slides": [...], "wide": {...}}   # 英語版（画面が日本語だけのアプリは書かない）
}
実画面: 日本語は screenshots/raw/（または raw/ja/）、iPad は raw_ipad/（または raw_ipad/ja/）。英語は raw/en/・raw_ipad/en/。
出力: 日本語は screenshots/{6.3,duo,ipad,header,search}/、英語は screenshots/en/{…}/、全部を並べた確認用は screenshots/check.png
"""
import argparse
import glob
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# 縦のスクショ: (フォルダ, 幅, 高さ, 文字の倍率, 実画面の幅, iPad か)。枠ごとに1サイズだけ（docs/mockup.md の表）
PORTRAIT = [
    ("6.3", 1206, 2622, 0.92, 950, False),
    ("duo", 1398, 2034, 0.85, 900, False),
    ("ipad", 2064, 2752, 1.45, 1500, True),
]
WIDE = [("header", 3840, 1646), ("search", 3840, 2560)]
PHONE_RATIO = 2868 / 1320  # 横の絵に並べる実画面の縦横比

# 価格の言葉と、確かめられない最上級（Guideline 2.3.7。docs/mockup.md の「価格の言葉」）
# 「Ad-free」「sugar-free」の free は価格ではないので、ハイフンのあとの free は止めない
PRICE_WORDS = re.compile(
    r"無料|無償|タダ|ゼロ円|[0０]\s*円|課金なし|割引|セール|特価|お得|お試し|月額|年額|サブスク|買い切り|[0-9０-９]+\s*[%％]\s*(?:オフ|off)"
    r"|(?<![-\w])free\b|\bsale\b|discount|\$\s*0\b|\b0\s*yen\b"
    r"|No\.\s*1|#1|ナンバーワン|\bbest\b", re.I)

COLORS = {"bg": "#FFFFFF", "text": "#111111", "accent": "#1F3A5F", "sub": "#555555", "frame": "#111111"}


def font_path(weight):
    # ファイル名の濁点が分解された形でも見つかるよう、正規化して探す
    for p in glob.glob("/System/Library/Fonts/*.ttc"):
        if unicodedata.normalize("NFC", Path(p).name) == f"ヒラギノ角ゴシック {weight}.ttc":
            return p
    raise FileNotFoundError(f"ヒラギノ角ゴシック {weight}")


FACE = {"name": "gothic", "app": None}  # mockup.json の "font"（gothic・maru・mincho・アプリの書体ファイル）


def font(weight, size):
    """weight は "W7"（見出し）か "W3"（補足）。書体は FACE で切り替える"""
    size = max(int(size), 8)
    bold = weight in ("W6", "W7", "W8")
    name = FACE["name"]
    if name == "maru":
        return ImageFont.truetype(font_path_any("ヒラギノ丸ゴ ProN W4.ttc"), size)
    if name == "mincho":
        return ImageFont.truetype(font_path_any("ヒラギノ明朝 ProN.ttc"), size, index=1 if bold else 0)
    if FACE["app"]:
        f = ImageFont.truetype(str(FACE["app"]), size)
        try:
            f.set_variation_by_axes([700 if bold else 400])
        except Exception:
            pass  # 可変フォントでなければそのまま
        return f
    return ImageFont.truetype(font_path(weight), size)


def font_path_any(name):
    for p in glob.glob("/System/Library/Fonts/*.ttc"):
        if unicodedata.normalize("NFC", Path(p).name) == name:
            return p
    raise FileNotFoundError(name)


def mix(a, b, t):
    """a と b を t（0〜1、b の割合）で混ぜた色"""
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def fit(text, weight, size, room):
    """room に収まるまで文字を小さくする（長い見出しが枠からはみ出さないように）"""
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    f = font(weight, size)
    while d.textlength(text, font=f) > room and size > 20:
        size *= 0.96
        f = font(weight, size)
    return f, size


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *im.size), radius, fill=255)
    out = Image.new("RGBA", im.size)
    out.paste(im, (0, 0), mask)
    return out


class Mockup:
    def __init__(self, shots_dir, cfg):
        self.dir = shots_dir
        self.cfg = cfg
        self.c = {k: rgb(v) for k, v in {**COLORS, **cfg.get("colors", {})}.items()}
        self.strips = {}

    def raw_dir(self, lang, ipad):
        base = self.dir / ("raw_ipad" if ipad else "raw")
        if (base / lang).is_dir():
            return base / lang
        if lang == "ja" and base.is_dir():
            return base
        if ipad:  # iPad の画面がなければ iPhone の画面で代用する（警告だけ出す）
            print(f"注意: {base} がないので iPad の枠も iPhone の画面で作ります")
            return self.raw_dir(lang, False)
        sys.exit(f"実画面のフォルダがありません: {base}")

    def shot(self, raw, name, width, ipad):
        if name == "widget":
            return self.widget_panel(raw, (width, int(width * PHONE_RATIO)))
        im = Image.open(raw / name).convert("RGB")
        if ipad and name in self.cfg.get("crop_center", []):
            cw = 1400
            ch = int(cw * 4 / 3)
            cx, cy = im.width // 2, im.height // 2
            im = im.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2))
        return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)

    def widget_panel(self, raw, size):
        """ウィジェットを置いたホーム画面の見本（実画面の代わり）"""
        panel = Image.new("RGB", size, (16, 20, 32))
        gap, y = int(size[0] * 0.07), int(size[0] * 0.15)
        for name in self.cfg.get("widget", []):
            w = Image.open(raw / name).convert("RGBA")
            scale = (size[0] - gap * 2) / w.width
            w = w.resize((int(w.width * scale), int(w.height * scale)), Image.LANCZOS)
            panel.paste(w, (gap, y), w)
            y += w.height + gap
        return panel

    def phone(self, canvas, im, x, y, ipad):
        """実画面を角丸の枠で貼る。device なら本体の縁（とダイナミックアイランド）も描く"""
        c, sw = self.c, im.width
        d = ImageDraw.Draw(canvas)
        if self.cfg.get("device"):
            if not ipad and not self.cfg.get("status_bar"):
                # 実画面にステータスバーがない（テストで描いた）ときは、画面の一番上の色で帯を足してアイランドを置く
                bar = int(sw * 0.13)
                tall = Image.new("RGB", (sw, im.height + bar), im.getpixel((sw // 2, 2)))
                tall.paste(im, (0, bar))
                im = tall.crop((0, 0, sw, im.height))
            b = int(sw * (0.022 if ipad else 0.035))  # 縁の太さ
            ro, ri = int(sw * (0.06 if ipad else 0.15)), int(sw * (0.045 if ipad else 0.12))
            d.rounded_rectangle((x - b, y - b, x + sw + b, y + im.height + b), ro, fill=c["frame"])
            r = rounded(im, ri)
            canvas.paste(r, (x, y), r)
            if not ipad:
                iw, ih = int(sw * 0.29), int(sw * 0.085)
                d.rounded_rectangle((x + (sw - iw) // 2, y + int(sw * 0.03), x + (sw + iw) // 2, y + int(sw * 0.03) + ih), ih // 2, fill=(0, 0, 0))
            return
        d.rounded_rectangle((x - 4, y - 4, x + sw + 4, y + im.height + 4), 68, fill=c["frame"])
        r = rounded(im, 64)
        canvas.paste(r, (x, y), r)

    def background(self, W, H, i, n):
        """地。panorama は6枚を横につなげた1枚の絵から切り出す（並べると図形がつながる）"""
        c, style = self.c, self.cfg.get("style", "classic")
        if style != "panorama":
            return Image.new("RGB", (W, H), c["bg"])
        key = (W, H, n)
        if key not in self.strips:
            strip = Image.new("RGB", (W * n, H), c["bg"])
            d = ImageDraw.Draw(strip)
            # アクセント色を混ぜると濁るので、地の色を白か黒に寄せた2段で描く
            to = (0, 0, 0) if sum(c["bg"]) > 600 else (255, 255, 255)
            tint, tint2 = mix(c["bg"], to, 0.12), mix(c["bg"], to, 0.06)
            for k in range(n + 1):  # 枚の境目ごとに大きな円を置き、両隣の枚にまたがらせる
                cx, cy, r = k * W, int(H * (0.62 if k % 2 else 0.4)), int(W * (0.62 if k % 2 else 0.45))
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tint if k % 2 else tint2)
            d.polygon([(0, int(H * 0.92)), (W * n, int(H * 0.7)), (W * n, H), (0, H)], fill=tint2)
            self.strips[key] = strip
        return self.strips[key].crop(((i - 1) * W, 0, i * W, H))

    def portrait(self, out, raw, badge, slide, W, H, K, SW, ipad, i=1, n=6):
        c, style = self.c, self.cfg.get("style", "classic")
        canvas = self.background(W, H, i, n)
        d = ImageDraw.Draw(canvas)
        line1, line2, sub = slide["lines"]
        bold = style == "bold"
        left = int(W * 0.08)
        room = W * (0.84 if bold else 0.9)
        size = 104 * K * (1.22 if bold else 1)
        hs = min(fit(line1, "W7", size, room)[1], fit(line2, "W7", size, room)[1])
        head = font("W7", hs)
        small, _ = fit(sub, "W3", 46 * K, room)

        def put(text, f, y, color):
            x = left if bold else (W - d.textlength(text, font=f)) / 2
            d.text((x, y), text, font=f, fill=color)

        top = 120 * K
        if bold:  # 左上に番号、その下に見出しを左寄せで大きく
            put(f"{i:02d}", font("W7", 64 * K), top, c["accent"])
            if badge:
                bf = font("W3", 40 * K)
                d.text((W - left - d.textlength(badge, font=bf), top + 14 * K), badge, font=bf, fill=c["sub"])
            top += 130 * K
        elif badge:
            bf = font("W7", 40 * K)
            bw = d.textlength(badge, font=bf) + 64 * K
            bx = (W - bw) / 2
            d.rounded_rectangle((bx, top, bx + bw, top + 72 * K), 36 * K, fill=c["text"])
            d.text((bx + 32 * K, top + 13 * K), badge, font=bf, fill=c["bg"])
            top += 130 * K
        else:
            top += 130 * K
        step = hs * 150 / 104
        put(line1, head, top, c["text"])
        put(line2, head, top + step, c["accent"])
        put(sub, small, top + step * 2, c["sub"])
        top = int(top + step * 2 + 100 * K)

        sw = int(SW * (1.08 if bold else 1))
        x = W - sw + int(sw * 0.1) - left if bold else (W - sw) // 2  # bold は右へはみ出させる
        if style == "split":  # 画面の上から3割の所で地を切り替える（画面が境目にまたがる）
            d.rectangle((0, top + int(sw * 0.6), W, H), fill=mix(c["bg"], (255, 255, 255), 0.82))
        if self.cfg.get("device"):
            top += int(sw * 0.035)
        self.phone(canvas, self.shot(raw, slide["shot"], sw, ipad), x, top, ipad)
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out)

    def wide(self, out, raw, wide, size):
        """ヘッダー・検索結果（横）。左に見出し、右に実画面を並べる（幅の55%まで）"""
        c = self.c
        w, h = size
        shots = wide["shots"]
        n = len(shots)
        sh = int(h * 0.84)
        sw = int(sh / PHONE_RATIO)
        gap = int(sw * 0.12)
        if sw * n + gap * (n - 1) > w * 0.55:
            sw = int(w * 0.55 / (n + 0.12 * (n - 1)))
            sh, gap = int(sw * PHONE_RATIO), int(sw * 0.12)
        x = w - int(w * 0.04) - sw * n - gap * (n - 1)
        line1, line2, sub = wide["lines"]
        left = int(w * 0.05)
        room = x - left - int(w * 0.04)
        hs = min(fit(line1, "W7", 400, room)[1], fit(line2, "W7", 400, room)[1])
        head = font("W7", hs)
        small, _ = fit(sub, "W3", hs * 0.42, room)
        canvas = Image.new("RGB", size, c["bg"])
        d = ImageDraw.Draw(canvas)
        top = (h - (int(hs * 1.25) * 2 + int(hs * 0.72))) // 2
        d.text((left, top), line1, font=head, fill=c["text"])
        d.text((left, top + int(hs * 1.25)), line2, font=head, fill=c["accent"])
        d.text((left, top + int(hs * 2.8)), sub, font=small, fill=c["sub"])
        y = (h - sh) // 2
        for f in shots:
            im = self.shot(raw, f, sw, False)
            im = im.crop((0, 0, sw, min(sh, im.height)))
            if self.cfg.get("device"):
                self.phone(canvas, im, x, y, False)
            else:
                r = int(sw * 0.07)
                d.rounded_rectangle((x - 4, y - 4, x + sw + 4, y + im.height + 4), r + 4, fill=c["frame"])
                ri = rounded(im, r)
                canvas.paste(ri, (x, y), ri)
            x += sw + gap
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out)


def sets(cfg):
    """(言語, 印, 見出し, 横の絵) の組。英語は "en" があるときだけ"""
    yield "ja", cfg.get("badge", ""), cfg["slides"], cfg["wide"]
    if "en" in cfg:
        en = cfg["en"]
        yield "en", en.get("badge", ""), en["slides"], en.get("wide", cfg["wide"])


def lint(cfg, shots_dir):
    """書き出す前に止める問題: 価格の言葉・見出しの形・実画面のファイルがない"""
    errors = []
    for lang, badge, slides, wide in sets(cfg):
        texts = [("印", badge)] + [(f"{i}枚目", t) for i, s in enumerate(slides, 1) for t in s["lines"]]
        texts += [("横の絵", t) for t in wide["lines"]]
        for where, t in texts:
            if PRICE_WORDS.search(t):
                errors.append(f"[{lang}] {where}に価格の言葉: {t}（Guideline 2.3.7）")
        for i, s in enumerate(slides, 1):
            if len(s["lines"]) != 3:
                errors.append(f"[{lang}] {i}枚目: lines は [1行目, 2行目, 補足] の3つ")
            elif lang == "ja" and max(len(s["lines"][0]), len(s["lines"][1])) > 12:
                print(f"注意: [{lang}] {i}枚目の見出しが12字を超えています（1行10字前後まで、文字は小さくして収めます）")
        if len(slides) != 6:
            print(f"注意: [{lang}] スクショが{len(slides)}枚です（決まりは6枚）")
        m = Mockup(shots_dir, cfg)
        for ipad in (False, True):
            raw = m.raw_dir(lang, ipad)
            for name in {s["shot"] for s in slides} | (set() if ipad else set(wide["shots"])):
                names = cfg.get("widget", []) if name == "widget" else [name]
                errors += [f"[{lang}] 実画面がありません: {raw / n}" for n in names if not (raw / n).exists()]
    return errors


def contact_sheet(shots_dir, langs):
    """全部の書き出しを1枚に並べる（1枚ずつ開かなくても、見出しの流れと色のむらを見られる）"""
    rows = []
    for lang in langs:
        base = shots_dir if lang == "ja" else shots_dir / "en"
        for folder, *_ in PORTRAIT:
            rows.append(sorted((base / folder).glob("*.png"), key=lambda p: p.stem.zfill(3)))
        rows.append([base / f"{k}/{w}x{h}.png" for k, w, h in WIDE])
    th = 520
    ims = [[Image.open(p) for p in r] for r in rows]
    thumbs = [[im.resize((int(im.width * th / im.height), th), Image.LANCZOS) for im in r] for r in ims]
    gap = 24
    W = max(sum(t.width for t in r) + gap * (len(r) + 1) for r in thumbs)
    sheet = Image.new("RGB", (W, (th + gap) * len(thumbs) + gap), (235, 235, 235))
    y = gap
    for r in thumbs:
        x = gap
        for t in r:
            sheet.paste(t, (x, y))
            x += t.width + gap
        y += th + gap
    sheet.save(shots_dir / "check.png")


def app_color(raw):
    """実画面でいちばん多く使われている、はっきりした色（アプリの色）"""
    count = {}
    for p in sorted(raw.glob("*.png"))[:6]:
        im = Image.open(p).convert("RGB").resize((120, 260)).quantize(16).convert("RGB")
        for n, col in im.getcolors(4096):
            hi, lo = max(col), min(col)
            if hi - lo > 60 and 40 < hi:  # 白・黒・灰色は除く
                count[col] = count.get(col, 0) + n
    return max(count, key=count.get) if count else (31, 58, 95)


def palettes(a):
    """アプリの色 a から配色を3案（どれも文字が読める組み合わせ）"""
    hx = lambda c: "#%02X%02X%02X" % c
    dark = mix(a, (0, 0, 0), 0.55)
    light = mix(a, (255, 255, 255), 0.85)
    return {
        "アプリの色の地・白い文字": {"bg": hx(a), "text": "#FFFFFF", "accent": hx(mix(a, (255, 255, 255), 0.75)), "sub": hx(mix(a, (255, 255, 255), 0.6)), "frame": hx(dark)},
        "淡い地・濃い文字": {"bg": hx(light), "text": hx(mix(a, (0, 0, 0), 0.75)), "accent": hx(dark), "sub": hx(mix(a, (0, 0, 0), 0.6)), "frame": hx(mix(a, (0, 0, 0), 0.8))},
        "黒に近い地・アプリの色": {"bg": hx(mix(a, (0, 0, 0), 0.85)), "text": "#FFFFFF", "accent": hx(mix(a, (255, 255, 255), 0.25)), "sub": "#B8BCC6", "frame": "#000000"},
    }


def init(shots_dir):
    path = shots_dir / "mockup.json"
    if path.exists():
        sys.exit(f"もうあります: {path}")
    raw = shots_dir / "raw" / "ja" if (shots_dir / "raw" / "ja").is_dir() else shots_dir / "raw"
    names = sorted(p.name for p in raw.glob("*.png")) or [f"{i}.png" for i in range(1, 7)]
    pals = palettes(app_color(raw))
    cfg = {
        "style": "classic",
        "font": "gothic",
        "device": False,
        "colors": next(iter(pals.values())),
        "badge": "広告なし・登録なし",
        "slides": [{"shot": n, "lines": ["1行目（悩み・場面）", "2行目（何ができるか）", "補足"]} for n in names[:6]],
        "wide": {"shots": names[:3], "lines": ["1行目", "2行目", "補足"]},
        "crop_center": [],
    }
    shots_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
    print(f"ひな形を作りました: {path}（見出しはユーザーが選んだものを入れる）")
    print("実画面から拾った配色の案（colors に入れ替えて使う）:")
    for k, v in pals.items():
        print(f"  {k}: {json.dumps(v)}")


def styles_sheet(shots_dir, cfg):
    """1〜3枚目を、スタイル・枠の組み合わせ全部で描いて並べる（どれにするかユーザーに選んでもらう用）"""
    folder, W, H, K, SW, ipad = PORTRAIT[0]
    m0 = Mockup(shots_dir, cfg)
    raw = m0.raw_dir("ja", False)
    rows, labels = [], []
    for style in ("classic", "split", "bold", "panorama"):
        for device in (False, True):
            m = Mockup(shots_dir, {**cfg, "style": style, "device": device})
            row = []
            for i, s in enumerate(cfg["slides"][:3], 1):
                tmp = shots_dir / ".styles.png"
                m.portrait(tmp, raw, cfg.get("badge", ""), s, W, H, K, SW, ipad, i, len(cfg["slides"]))
                row.append(Image.open(tmp).resize((W * 600 // H, 600), Image.LANCZOS))
                tmp.unlink()
            rows.append(row)
            labels.append(f"{style}{' + device' if device else ''}")
    tw, gap, lab = rows[0][0].width, 20, 60
    cols = 2
    cw = tw * 3 + gap * 4
    sheet = Image.new("RGB", (cw * cols, (600 + lab + gap) * ((len(rows) + 1) // cols)), (235, 235, 235))
    d = ImageDraw.Draw(sheet)
    for k, (row, label) in enumerate(zip(rows, labels)):
        ox, oy = (k % cols) * cw, (k // cols) * (600 + lab + gap)
        d.text((ox + gap, oy + 14), label, font=ImageFont.truetype(font_path("W7"), 36), fill=(30, 30, 30))
        for j, t in enumerate(row):
            sheet.paste(t, (ox + gap + j * (tw + gap), oy + lab))
    out = shots_dir / "styles.png"
    sheet.save(out)
    return out


def load(path, keys):
    """手で書く JSON なので、読めない・足りないときは日本語で止める"""
    if not path.exists():
        sys.exit(f"{path} がありません（--init でひな形を作れます）")
    try:
        cfg = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"{path} の {e.lineno} 行目が JSON として読めません: {e.msg}")
    missing = [k for k in keys if not cfg.get(k)]
    if missing:
        sys.exit(f"{path} に {'・'.join(missing)} がありません")
    return cfg


def use_font(app, name):
    """mockup.json の "font"。gothic・maru・mincho のほかは、アプリのフォルダからの書体ファイルのパス"""
    if name in ("gothic", "maru", "mincho"):
        FACE["name"] = name
    else:
        FACE["name"], FACE["app"] = "app", app / name
        if not FACE["app"].exists():
            sys.exit(f"書体がありません: {FACE['app']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app", type=Path, help="アプリのフォルダ")
    ap.add_argument("--init", action="store_true", help="mockup.json のひな形を作る")
    ap.add_argument("--no-open", action="store_true", help="書き出した画像を開かない")
    ap.add_argument("--styles", action="store_true", help="1〜3枚目を全部のスタイルで描いて見比べる（styles.png）")
    a = ap.parse_args()
    app = a.app.resolve()
    shots_dir = app / "screenshots"
    if a.init:
        return init(shots_dir)
    cfg = load(shots_dir / "mockup.json", ("slides", "wide"))
    use_font(app, cfg.get("font", "gothic"))
    if a.styles:
        out = styles_sheet(shots_dir, cfg)
        print(f"見比べ用を作りました: {out}")
        if not a.no_open:
            subprocess.run(["open", "-a", "Preview", str(out)], check=False)
        return
    errors = lint(cfg, shots_dir)
    if errors:
        sys.exit("書き出しを止めました:\n  " + "\n  ".join(errors))

    m = Mockup(shots_dir, cfg)
    langs = []
    for lang, badge, slides, wide in sets(cfg):
        langs.append(lang)
        base = shots_dir if lang == "ja" else shots_dir / "en"
        for folder, W, H, K, SW, ipad in PORTRAIT:
            raw = m.raw_dir(lang, ipad)
            for i, s in enumerate(slides, 1):
                m.portrait(base / folder / f"{i}.png", raw, badge, s, W, H, K, SW, ipad, i, len(slides))
        for kind, w, h in WIDE:
            m.wide(base / kind / f"{w}x{h}.png", m.raw_dir(lang, False), wide, (w, h))

    # サイズが表のとおりか（docs/mockup.md の申請前チェック）
    for lang in langs:
        base = shots_dir if lang == "ja" else shots_dir / "en"
        expect = [(base / f, (W, H)) for f, W, H, *_ in PORTRAIT] + [(base / k, (w, h)) for k, w, h in WIDE]
        for folder, size in expect:
            for p in folder.glob("*.png"):
                if Image.open(p).size != size:
                    sys.exit(f"サイズが違います: {p} {Image.open(p).size} ≠ {size}")
    contact_sheet(shots_dir, langs)

    print(f"書き出しました: {shots_dir}（{'・'.join(langs)} × 縦{len(PORTRAIT)}枠 × {len(cfg['slides'])}枚 ＋ ヘッダー・検索結果、サイズ確認済み）")
    print("\n| 枚 | 見出し | 補足 |\n|---|---|---|")
    for i, s in enumerate(cfg["slides"], 1):
        print(f"| {i} | {s['lines'][0]} / {s['lines'][1]} | {s['lines'][2]} |")

    preview = Path(__file__).with_name("appstore_preview.py")
    if (app / "APPSTORE_SUBMISSION.md").exists():
        subprocess.run([sys.executable, str(preview), str(app), "--shots", "screenshots/6.3"], check=False)
    if not a.no_open:
        outs = [shots_dir / "check.png"]
        for lang in langs:
            base = shots_dir if lang == "ja" else shots_dir / "en"
            for f in [p[0] for p in PORTRAIT] + [k for k, *_ in WIDE]:
                outs += sorted((base / f).glob("*.png"))
        outs += sorted((app / "store_preview").glob("*.png"))
        subprocess.run(["open", str(shots_dir)], check=False)
        subprocess.run(["open", "-a", "Preview", *map(str, outs)], check=False)


if __name__ == "__main__":
    main()
