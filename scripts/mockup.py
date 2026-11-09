#!/usr/bin/env python3
"""App Store のモックアップを、アプリの screenshots/mockup.json から全部の枠ぶん書き出す（docs/mockup.md）。

  python3 scripts/mockup.py {アプリのフォルダ} --init-shots   # 実画面を撮るテストのひな形を作る
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
  "slides": [{"shot": "1.png", "lines": ["1行目", "2行目（アクセント色）", "補足"],
              "crop_y": 0.1,                              # 実画面を上から何割切って見せるか（見出しが指す所を枠の上半分に）
              "focus": [0.02, 0.17, 0.96, 0.33]}, ...],   # 拡大窓: 大事な所（実画面に対する割合 [x, y, 幅, 高さ]）。iPad は focus_ipad・crop_y_ipad
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


# 詰め組み: Pillow が palt を使えないので、約物を半角幅にし、見出しは字間を少し詰める（間延びして見えないように）
_OPEN, _CLOSE, _MID = set("「『（【〈《“"), set("」』）】〉》、。，．”"), set("・：；")


def _advances(text, f, track):
    em = f.size
    out = []
    for ch in text:
        w = f.getlength(ch)
        if ch in _OPEN:
            out.append((-em * 0.5, w - em * 0.5))
        elif ch in _CLOSE:
            out.append((0, w - em * 0.5))
        elif ch in _MID:
            out.append((-em * 0.25, w - em * 0.5))
        else:
            out.append((0, w + (em * track if ord(ch) > 0x2E80 else 0)))
    return out


def tlen(text, f, track=0.0):
    return sum(a for _, a in _advances(text, f, track))


def tdraw(d, xy, text, f, fill, track=0.0):
    x, y = xy
    for ch, (dx, a) in zip(text, _advances(text, f, track)):
        d.text((x + dx, y), ch, font=f, fill=fill)
        x += a


HEAD_TRACK = -0.03  # 見出しの字間（em）


def fit(text, weight, size, room):
    """room に収まるまで文字を小さくする（長い見出しが枠からはみ出さないように）"""
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    f = font(weight, size)
    while tlen(text, f, HEAD_TRACK) > room and size > 20:
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


def _ncc(img, tpl):
    """正規化相互相関（img の各位置で tpl とどれだけ似ているか、-1〜1）"""
    import numpy as np
    from scipy.signal import fftconvolve
    th, tw = tpl.shape
    t = tpl - tpl.mean()
    tn = np.sqrt((t ** 2).sum())
    if tn == 0 or img.shape[0] < th or img.shape[1] < tw:
        return None
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    ones = np.ones_like(tpl)
    s1 = fftconvolve(img, ones, mode="valid")
    s2 = fftconvolve(img ** 2, ones, mode="valid")
    var = np.maximum(s2 - s1 ** 2 / tpl.size, 1e-6)
    return num / (np.sqrt(var) * tn)


def locate(phone_path, rect, pad_path):
    """iPhone の実画面で決めた拡大の場所（rect）を、iPad の実画面の中で探す。
    iPad は字が約2/3の大きさで折り返しも違うので、範囲の上端と下端の左側を別々に照合する。
    戻り値: (iPad での rect, 似ている度合い 0〜1)"""
    import numpy as np
    D = 4  # 速さのために 1/4 に縮めて照合する
    ph = Image.open(phone_path).convert("L")
    pd = Image.open(pad_path).convert("L")
    pad = np.asarray(pd.resize((pd.width // D, pd.height // D)), dtype=float)
    fx, fy, fw, fh = rect
    x0, y0, x1, y1 = int(fx * ph.width), int(fy * ph.height), int((fx + fw) * ph.width), int((fy + fh) * ph.height)
    sh = min(y1 - y0, int(ph.height * 0.04))  # 上端・下端の帯の高さ
    sw = int((x1 - x0) * 0.45)               # 左側だけ（iPad は列の幅が違う）
    found = []
    for top in (y0, y1 - sh):
        strip = ph.crop((x0, top, x0 + sw, top + sh))
        best = (-1, 0, 0, 0)
        for scale in (0.6, 0.64, 0.68, 0.72, 0.76, 0.8):
            t = strip.resize((max(int(strip.width * scale / D), 4), max(int(strip.height * scale / D), 4)))
            r = _ncc(pad, np.asarray(t, dtype=float))
            if r is None:
                continue
            k = np.unravel_index(np.argmax(r), r.shape)
            if r[k] > best[0]:
                best = (float(r[k]), k[1] * D, k[0] * D, scale)
        found.append(best)
    (s_top, px, py0, sc), (s_bot, _, py1, sc2) = found
    py1 += int(sh * sc2)
    if py1 <= py0:  # 下端が上端より上に見つかったら、上端から大きさで決める
        py1 = py0 + int((y1 - y0) * sc)
    if abs(fx - (1 - fx - fw)) < 0.06:  # iPhone で左右対称の範囲なら、iPad でも中央で左右対称にする
        qx0, qx1 = px, pd.width - px
    else:
        qx0, qx1 = px, px + int((x1 - x0) * sc)
    return [float(qx0 / pd.width), float(py0 / pd.height), float((qx1 - qx0) / pd.width), float((py1 - py0) / pd.height)], min(s_top, s_bot)


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

    def shot(self, raw, name, width, ipad, crop_y=0.0, min_h=0):
        if name == "widget":
            return self.widget_panel(raw, (width, int(width * PHONE_RATIO)))
        im = Image.open(raw / name).convert("RGB")
        if crop_y:  # 見出しが指す所が枠の上半分に入るよう、上を切って見せる（画面が下まで届く所まで）
            keep = min_h * im.width / width
            im = im.crop((0, int(min(im.height * crop_y, max(im.height - keep, 0))), im.width, im.height))
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
                top_color = max(im.crop((0, 0, sw, 6)).getcolors(sw * 6), key=lambda t: t[0])[1]  # 上端でいちばん多い色
                tall = Image.new("RGB", (sw, im.height + bar), top_color)
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
        # 検索結果の小ささでも読めるよう、見出しは大きく、補足は太く（docs/mockup.md「3. 形」、neuro 役 2026-11-09）
        size = 116 * K * (1.15 if bold else 1)
        hs = min(fit(line1, "W7", size, room)[1], fit(line2, "W7", size, room)[1])
        head = font("W7", hs)
        small, _ = fit(sub, "W6", 54 * K, room)

        def put(text, f, y, color, track=HEAD_TRACK):
            x = left if bold else (W - tlen(text, f, track)) / 2
            tdraw(d, (x, y), text, f, color, track)

        top = 120 * K
        if bold:  # 左上に番号、その下に見出しを左寄せで大きく
            nf = font("W7", 56 * K)
            put(f"{i:02d}", nf, top, c["accent"], 0)
            d.rectangle((left + nf.getlength(f"{i:02d}") + 24 * K, top + 32 * K, left + nf.getlength(f"{i:02d}") + 104 * K, top + 36 * K), fill=c["accent"])
            if badge:
                bf = font("W6", 36 * K)
                tdraw(d, (W - left - tlen(badge, bf), top + 14 * K), badge, bf, c["sub"])
            top += 130 * K
        elif badge:  # 印は細い線の枠。塗りつぶすと見出しより目立つ
            bf = font("W6", 38 * K)
            bw = tlen(badge, bf) + 56 * K
            bx = (W - bw) / 2
            d.rounded_rectangle((bx, top, bx + bw, top + 68 * K), 34 * K, outline=c["sub"], width=max(int(3 * K), 2))
            tdraw(d, (bx + 28 * K, top + 12 * K), badge, bf, c["sub"])
            top += 130 * K
        else:
            top += 130 * K
        step = hs * 1.3
        put(line1, head, top, c["text"])
        put(line2, head, top + step, c["accent"])
        put(sub, small, top + step * 2, c["sub"], 0)
        top = int(top + step * 2 + 54 * K + 70 * K)

        sw = int(SW * (1.08 if bold else 1))
        x = W - sw + int(sw * 0.1) - left if bold else (W - sw) // 2  # bold は右へはみ出させる
        if style == "split":  # 画面の上から3割の所で地を切り替える（画面が境目にまたがる）
            d.rectangle((0, top + int(sw * 0.6), W, H), fill=mix(c["bg"], (255, 255, 255), 0.82))
        if self.cfg.get("device"):
            top += int(sw * 0.035)
        focus = slide.get("focus_ipad" if ipad else "focus")
        if ipad and not focus and slide.get("focus") and slide["shot"] != "widget":
            # iPad は iPhone で決めた場所を探して当てる（focus_ipad を書かなくても済むように）
            phone_raw = self.raw_dir("ja", False) / slide["shot"]
            if phone_raw.exists() and phone_raw != raw / slide["shot"]:
                focus, score = locate(phone_raw, slide["focus"], raw / slide["shot"])
                if score < 0.6:
                    print(f"注意: iPad の{i}枚目は拡大の場所が見つかりません（似ている度合い {score:.2f}）。focus_ipad を書いてください")
                    focus = None
        crop_y = slide.get("crop_y_ipad" if ipad else "crop_y", 0.0)
        if ipad and "crop_y_ipad" not in slide and slide.get("crop_y") and focus:
            crop_y = max(focus[1] - 0.05, 0.0)  # iPad も、拡大する所が枠の上の方に来るように
        if crop_y and slide["shot"] != "widget":  # 画面が下まで届くよう、切る量に上限を付ける
            h0 = Image.open(raw / slide["shot"]).height
            w0 = Image.open(raw / slide["shot"]).width
            crop_y = min(crop_y, max(1 - (H - top) * w0 / sw / h0, 0))
        self.phone(canvas, self.shot(raw, slide["shot"], sw, ipad, crop_y), x, top, ipad)
        if focus and slide["shot"] != "widget":
            bar = int(sw * 0.13) if self.cfg.get("device") and not ipad and not self.cfg.get("status_bar") else 0
            z = self.zoom(canvas, raw / slide["shot"], focus, crop_y, x, top + bar, sw, W, H, K)
            if z < 1.2 and not ipad and W == PORTRAIT[0][1]:
                print(f"注意: {i}枚目の拡大窓が {z:.2f} 倍です（1.2倍以上が目安。focus の幅を狭めて大事な所だけにする）")
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out)

    def zoom(self, canvas, path, rect, crop_y, px, py, sw, W, H, K, cx=None, zw=None):
        """拡大窓: 実画面の大事な所（rect は実画面に対する割合 [x, y, 幅, 高さ]）を、元の場所の上に大きくして重ねる
        （同じ中身が2回見えないように、元の所を覆う）。枠はアクセント色、影・暗幕は付けない"""
        a = self.c["accent"]
        im = Image.open(path).convert("RGB")
        fx, fy, fw, fh = rect
        box = (int(fx * im.width), int(fy * im.height), int((fx + fw) * im.width), int((fy + fh) * im.height))
        s = sw / im.width
        oy = py + (box[1] - crop_y * im.height) * s  # 元の所の上端（キャンバスの上で）
        part = im.crop(box)
        zw = int(zw or W * 0.94)
        zh = int(part.height * zw / part.width)
        if zh > H * 0.4:  # 縦に長すぎるときは高さで合わせる
            zh = int(H * 0.4)
            zw = int(part.width * zh / part.height)
        part = part.resize((zw, zh), Image.LANCZOS)
        zx = int((cx if cx is not None else W / 2) - zw / 2)
        center = oy + (box[3] - box[1]) * s / 2
        zy = int(min(max(center - zh / 2, py), H - zh - 40 * K))
        bw = max(int(6 * K), 3)
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle((zx - bw, zy - bw, zx + zw + bw, zy + zh + bw), int(8 * K) + bw, fill=a)
        r = rounded(part, int(8 * K))
        canvas.paste(r, (zx, zy), r)
        return zw / ((box[2] - box[0]) * s)  # 倍率

    def wide(self, out, raw, wide, size, badge=""):
        """ヘッダー・検索結果（横）。左に印と見出し、右に実画面を大きく（下へはみ出させる）。
        入りきらないときは台数を減らす。1台目には、縦のスクショと同じ拡大窓を付ける"""
        c = self.c
        w, h = size
        by_shot = {s["shot"]: s for s in self.cfg.get("slides", [])}
        shots = wide["shots"]
        for n in range(len(shots), 0, -1):  # 画面の高さが絵の9割以上になる台数
            sw = int(w * 0.55 / (n + 0.12 * (n - 1)))
            if sw * PHONE_RATIO >= h * 0.9 or n == 1:
                break
        sw = min(sw, int(h * 1.05 / PHONE_RATIO))
        shots, gap = shots[:n], int(sw * 0.12)
        x = w - int(w * 0.05) - sw * n - gap * (n - 1)
        line1, line2, sub = wide["lines"]
        left = int(w * 0.06)
        has_zoom = bool(by_shot.get(shots[0], {}).get("focus")) and shots[0] != "widget"
        room = x - left - int(w * 0.04) - (int(sw * 0.15) if has_zoom else 0)  # 拡大窓は画面より左右に15%ずつはみ出す
        hs = min(fit(line1, "W7", h * 0.13, room)[1], fit(line2, "W7", h * 0.13, room)[1])
        head = font("W7", hs)
        small, _ = fit(sub, "W6", hs * 0.42, room)
        canvas = Image.new("RGB", size, c["bg"])
        d = ImageDraw.Draw(canvas)
        bh = int(hs * 0.62) if badge else 0
        top = (h - (bh + int(hs * 0.5) * bool(badge) + int(hs * 1.3) * 2 + int(hs * 0.6))) // 2
        if badge:
            bf = font("W6", bh * 0.55)
            bw = tlen(badge, bf) + bh * 0.8
            d.rounded_rectangle((left, top, left + bw, top + bh), bh / 2, outline=c["sub"], width=max(int(hs * 0.03), 2))
            tdraw(d, (left + bh * 0.4, top + bh * 0.18), badge, bf, c["sub"])
            top += bh + int(hs * 0.5)
        tdraw(d, (left, top), line1, head, c["text"], HEAD_TRACK)
        tdraw(d, (left, top + int(hs * 1.3)), line2, head, c["accent"], HEAD_TRACK)
        tdraw(d, (left, top + int(hs * 2.75)), sub, small, c["sub"])
        y = int(h * 0.1)
        K = sw / 950
        later = []  # 拡大窓は全部の画面を描いた後に重ねる（隣の画面の下に隠れないように）
        for k, f in enumerate(shots):
            sl = by_shot.get(f, {})
            crop_y = sl.get("crop_y", 0.0)
            if crop_y and f != "widget":  # 画面が下まで届く所までしか切らない
                im0 = Image.open(raw / f)
                crop_y = min(crop_y, max(1 - (h - y) * im0.width / sw / im0.height, 0))
            im = self.shot(raw, f, sw, False, crop_y)
            im = im.crop((0, 0, sw, min(h - y + 40, im.height)))
            self.phone(canvas, im, x, y, False) if self.cfg.get("device") else self._flat(canvas, im, x, y)
            if k == 0 and sl.get("focus") and f != "widget":
                bar = int(sw * 0.13) if self.cfg.get("device") and not self.cfg.get("status_bar") else 0
                later.append((raw / f, sl["focus"], crop_y, x, y + bar))
            x += sw + gap
        for path, focus, crop_y, zx, zy in later:
            self.zoom(canvas, path, focus, crop_y, zx, zy, sw, w, h, K, cx=zx + sw / 2, zw=sw * 1.3)
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out)

    def _flat(self, canvas, im, x, y):
        sw = im.width
        r = int(sw * 0.07)
        ImageDraw.Draw(canvas).rounded_rectangle((x - 4, y - 4, x + sw + 4, y + im.height + 4), r + 4, fill=self.c["frame"])
        ri = rounded(im, r)
        canvas.paste(ri, (x, y), ri)


def sets(cfg):
    """(言語, 印, 見出し, 横の絵) の組。英語は "en" があるときだけ"""
    yield "ja", cfg.get("badge", ""), cfg["slides"], cfg["wide"]
    if "en" in cfg:
        en = cfg["en"]
        yield "en", en.get("badge", ""), en["slides"], en.get("wide", cfg["wide"])


def contrast(a, b):
    """WCAG のコントラスト比"""
    def lum(c):
        v = [x / 255 for x in c]
        v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def similar(raw, slides):
    """実画面がほぼ同じ枚の組（並べると違いがわからない）"""
    def small(s):
        im = Image.open(raw / s["shot"]).convert("L")
        im = im.crop((0, int(im.height * s.get("crop_y", 0)), im.width, im.height))
        return list(im.resize((24, 48)).getdata())
    ims = [(i, small(s)) for i, s in enumerate(slides, 1) if s["shot"] != "widget" and (raw / s["shot"]).exists()]
    return [(i, j) for k, (i, a) in enumerate(ims) for j, b in ims[k + 1:]
            if sum(abs(x - y) for x, y in zip(a, b)) / len(a) < 12]


def ocr_price(paths):
    """実画面の文字を Mac の Vision（scripts/ocr.swift）で読み、価格の言葉が映っている画像を返す。
    2026-10-16 の却下は、実画面に映った AI の返事の「無料」だった"""
    paths = sorted({str(p) for p in paths})
    if not paths:
        return []
    r = subprocess.run(["swift", str(Path(__file__).with_name("ocr.swift")), *paths], capture_output=True, text=True)
    if r.returncode:
        print(f"注意: 実画面の文字を読めませんでした（目で確かめてください）: {r.stderr[-300:]}")
        return []
    hits = []
    for line in r.stdout.splitlines():
        path, _, text = line.partition("\t")
        m = PRICE_WORDS.search(text)
        if m:
            hits.append(f"実画面に価格の言葉「{m.group(0)}」: {path}（…{text[max(m.start() - 15, 0):m.end() + 15]}…）")
    return hits


def lint(cfg, shots_dir, ocr=True):
    """書き出す前に止める問題: 価格の言葉・見出しの形・実画面のファイルがない・文字が読めない色"""
    errors = []
    used = set()
    c = {k: rgb(v) for k, v in {**COLORS, **cfg.get("colors", {})}.items()}
    for key, need in (("text", 4.5), ("sub", 4.5), ("accent", 3.0)):  # 2行目は大きい文字なので 3:1（WCAG）
        r = contrast(c[key], c["bg"])
        if r < need:
            errors.append(f"colors.{key} と地のコントラストが {r:.1f}:1（{need}:1 以上にする）")
    for lang, badge, slides, wide in sets(cfg):
        texts = [("印", badge)] + [(f"{i}枚目", t) for i, s in enumerate(slides, 1) for t in s["lines"]]
        texts += [("横の絵", t) for t in wide["lines"]]
        for where, t in texts:
            if PRICE_WORDS.search(t):
                errors.append(f"[{lang}] {where}に価格の言葉: {t}（Guideline 2.3.7）")
        for i, s in enumerate(slides, 1):
            if len(s["lines"]) != 3:
                errors.append(f"[{lang}] {i}枚目: lines は [1行目, 2行目, 補足] の3つ")
            elif lang == "ja" and max(len(s["lines"][0]), len(s["lines"][1])) > 10:
                print(f"注意: [{lang}] {i}枚目の見出しが10字を超えています（1行9字前後まで。長いと文字を小さくして収めるので、検索結果で読みにくくなる）")
        if len(slides) != 6:
            print(f"注意: [{lang}] スクショが{len(slides)}枚です（決まりは6枚）")
        m = Mockup(shots_dir, cfg)
        for i, j in similar(m.raw_dir(lang, False), slides):
            print(f"注意: [{lang}] {i}枚目と{j}枚目の実画面がほぼ同じです（crop_y で見せる所を変えるか、別の画面にする）")
        for ipad in (False, True):
            raw = m.raw_dir(lang, ipad)
            for name in {s["shot"] for s in slides} | (set() if ipad else set(wide["shots"])):
                names = cfg.get("widget", []) if name == "widget" else [name]
                errors += [f"[{lang}] 実画面がありません: {raw / n}" for n in names if not (raw / n).exists()]
                used.update(raw / n for n in names if (raw / n).exists())
    if ocr:
        errors += ocr_price(used)
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


def app_colors(raw):
    """実画面から、アプリの主な色と、色相の違うもう1色（アクセント）を拾う。白・黒・灰色は除く"""
    import colorsys
    count = {}
    for p in sorted(raw.glob("*.png"))[:6]:
        im = Image.open(p).convert("RGB").resize((120, 260)).quantize(48, method=Image.Quantize.MAXCOVERAGE).convert("RGB")
        for n, col in im.getcolors(4096):
            if max(col) - min(col) > 60 and max(col) > 40:
                count[col] = count.get(col, 0) + n
    if not count:
        return (31, 58, 95), (245, 158, 11)
    main = max(count, key=count.get)
    hue = lambda c: colorsys.rgb_to_hsv(*[x / 255 for x in c])[0] * 360
    sat = lambda c: colorsys.rgb_to_hsv(*[x / 255 for x in c])[1]
    # アクセントは少なくても鮮やかな色（印やボタンの色）なので、鮮やかさで重みを付ける
    far = {c: n * sat(c) ** 3 for c, n in count.items() if min(abs(hue(c) - hue(main)), 360 - abs(hue(c) - hue(main))) > 40}
    second = max(far, key=far.get) if far else mix(main, (255, 255, 255), 0.5)
    return main, second


def readable(col, bg, need):
    """col を、bg とのコントラストが need 以上になるまで白か黒に寄せる"""
    to = (255, 255, 255) if contrast((255, 255, 255), bg) > contrast((0, 0, 0), bg) else (0, 0, 0)
    t = 0.0
    while contrast(mix(col, to, t), bg) < need and t < 1:
        t += 0.05
    return mix(col, to, t)


def palettes(main, second):
    """アプリの2色から配色を3案。2行目はアクセント色で、どれも文字が読める組み合わせ（4.5:1、2行目は大きい文字なので3:1以上）"""
    hx = lambda c: "#%02X%02X%02X" % c
    out = {}
    for name, bg in (("アプリの色の地", main), ("淡い地", mix(main, (255, 255, 255), 0.9)), ("黒に近い地", mix(main, (0, 0, 0), 0.85))):
        light = contrast((0, 0, 0), bg) > contrast((255, 255, 255), bg)
        text = readable(mix(main, (0, 0, 0), 0.6) if light else (255, 255, 255), bg, 7)
        sub = readable(mix(text, bg, 0.3), bg, 4.5)
        accent = readable(second, bg, 3.5)
        out[name] = {"bg": hx(bg), "text": hx(text), "accent": hx(accent), "sub": hx(sub), "frame": hx(mix(main, (0, 0, 0), 0.75))}
    return out


def init(shots_dir):
    path = shots_dir / "mockup.json"
    if path.exists():
        sys.exit(f"もうあります: {path}")
    raw = shots_dir / "raw" / "ja" if (shots_dir / "raw" / "ja").is_dir() else shots_dir / "raw"
    names = sorted(p.name for p in raw.glob("*.png")) or [f"{i}.png" for i in range(1, 7)]
    pals = palettes(*app_colors(raw))
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


SHOTS_TEMPLATE = """// App Store 用の実画面を、本物のフォントで描いて書き出す（合成は SEADICE/scripts/mockup.py、docs/mockup.md）。
//   flutter test test_screenshots/shots_test.dart --update-goldens
// 出力: screenshots/raw/*.png（iPhone 6.9インチ）と screenshots/raw_ipad/*.png（iPad 13インチ）
// ひな形は `python3 SEADICE/scripts/mockup.py {{アプリのフォルダ}} --init-shots` で作った。TODO を埋める
//
// つまずきやすい所（docs/mockup.md「5. 実画面の撮り方」）:
// - テストには日本語フォントがないので、下の _families すべてに NotoSansJP を読ませる（Cupertino のタブも含む。読まないと□になる）
// - appBarTheme.titleTextStyle に fontFamily がないアプリはタイトルが□になる。テスト側でテーマを写し、タイトルにだけフォントを足す
// - 問題や単語がシャッフルされるアプリは、flutter/assets をモックして写す中身を差し込む（50KBを超えるJSONは tester.runAsync で待つ）
// - サンプルの中身は、それらしいもの。空の画面・エラー・個人名・価格の言葉（無料など）を写さない
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{package}/main.dart';
import 'package:shared_preferences/shared_preferences.dart';
{extra_imports}
const _sizes = {{
  'raw': (Size(440, 956), 3.0),
  'raw_ipad': (Size(1032, 1376), 2.0),
}};
const _fontDir = '{font_dir}';
const _families = ['NotoSansJP', 'Roboto', '.SF UI Text', '.SF UI Display', 'CupertinoSystemText', 'CupertinoSystemDisplay'];

Future<void> _loadFont(String family, String path) async {{
  final bytes = File(path).readAsBytesSync();
  await (FontLoader(family)..addFont(Future.value(ByteData.view(bytes.buffer)))).load();
}}

/// TODO: 使っている人の様子がわかる保存データ（SharedPreferences のキーと値）。
/// 初回の案内・ウェルカムは「見た」ことにしておく（しないと1枚目に案内が写る）
Map<String, Object> _prefs() => {{}};

void main() {{
  testWidgets('screenshots', (tester) async {{
    final flutterRoot = Platform.environment['FLUTTER_ROOT'] ?? '${{Platform.environment['HOME']}}/development/flutter';
    await tester.runAsync(() async {{
      for (final f in _families) {{
{font_loads}
      }}
      await _loadFont('MaterialIcons', '$flutterRoot/bin/cache/artifacts/material_fonts/MaterialIcons-Regular.otf');
    }});
    tester.platformDispatcher.localeTestValue = const Locale('ja', 'JP');
    tester.platformDispatcher.localesTestValue = const [Locale('ja', 'JP')];
{extra_setup}    addTearDown(tester.view.reset);
    addTearDown(tester.platformDispatcher.clearAllTestValues);

    for (final MapEntry(key: dir, value: (size, dpr)) in _sizes.entries) {{
      Future<void> shot(String name) async {{
        await tester.pumpAndSettle();
        await expectLater(find.byType(MaterialApp), matchesGoldenFile('../screenshots/$dir/$name.png'));
      }}

      SharedPreferences.setMockInitialValues(_prefs());
      tester.view.physicalSize = size * dpr;
      tester.view.devicePixelRatio = dpr;
      await tester.pumpWidget(const SizedBox());
      await tester.pumpWidget({app}(key: UniqueKey()));
      await tester.pump(const Duration(seconds: 9)); // 通信の確認などはタイムアウトまで進めて終わらせる
      await tester.pumpAndSettle();

      // 6枚の役割（docs/mockup.md「4. 見出しの書き方」）の順に撮る。名前は mockup.json の shot と合わせる
      await shot('1'); // TODO: 核の価値（何がわかる・何ができる）が見える画面
      // await tester.tap(find.text('…')); await shot('2'); // 手軽さ
      // await shot('3'); // わかった後にできること
      // await shot('4'); // 広がり
      // await shot('5'); // 別の人・場面
      // await shot('6'); // 安心・その後
    }}
  }});
}}
"""


def init_shots(app):
    """撮影用テスト（test_screenshots/shots_test.dart）のひな形を、アプリから読み取った値で書き出す"""
    out = app / "test_screenshots" / "shots_test.dart"
    if out.exists():
        sys.exit(f"もうあります: {out}")
    pub = (app / "pubspec.yaml").read_text() if (app / "pubspec.yaml").exists() else ""
    m = re.search(r"^name:\s*(\S+)", pub, re.M)
    if not m:
        sys.exit(f"pubspec.yaml の name が読めません: {app}")
    main_dart = (app / "lib" / "main.dart").read_text() if (app / "lib" / "main.dart").exists() else ""
    w = re.search(r"runApp\(\s*(?:const\s+)?(\w+)\(", main_dart)
    fonts = sorted(app.glob("assets/fonts/NotoSansJP*.[ot]tf"))
    if fonts:
        font_dir, names = "assets/fonts", [f.name for f in fonts]  # テストはアプリのフォルダで動く
    else:  # アプリに入っていなければ、貿易実務英単語の NotoSansJP を読む（テストでだけ使う）
        font_dir = str(Path("/Users/hidenori/Developer/学習系/trade-english-word/assets/fonts"))
        names = ["NotoSansJP-Regular.ttf", "NotoSansJP-Bold.ttf"]
    imports, setup = "", ""
    if "package_info_plus" in pub:  # バージョン表示はテストでは動かないので、仮の値を入れる
        ver = re.search(r"^version:\s*([\d.]+)\+?(\d*)", pub, re.M)
        imports += "import 'package:package_info_plus/package_info_plus.dart';\n"
        setup += (f"    PackageInfo.setMockInitialValues(appName: '', packageName: '', version: '{ver.group(1) if ver else '1.0.0'}', "
                  f"buildNumber: '{(ver.group(2) if ver else '') or '1'}', buildSignature: '');\n")
    loads = "\n".join(f"        await _loadFont(f, '$_fontDir/{n}');" for n in names)
    out.parent.mkdir(exist_ok=True)
    out.write_text(SHOTS_TEMPLATE.format(package=m.group(1), font_dir=font_dir, font_loads=loads, app=w.group(1) if w else "MyApp",
                                         extra_imports=imports, extra_setup=setup))
    print(f"ひな形を作りました: {out}（TODO の保存データと画面の操作を書く）")
    if not w:
        print("注意: lib/main.dart から起動する Widget が読めなかったので MyApp にしました")


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
    ap.add_argument("--init-shots", action="store_true", help="撮影用テスト test_screenshots/shots_test.dart のひな形を作る")
    ap.add_argument("--no-ocr", action="store_true", help="実画面の文字の確認（数秒かかる）を飛ばす")
    ap.add_argument("--styles", action="store_true", help="1〜3枚目を全部のスタイルで描いて見比べる（styles.png）")
    a = ap.parse_args()
    app = a.app.resolve()
    shots_dir = app / "screenshots"
    if a.init:
        return init(shots_dir)
    if a.init_shots:
        return init_shots(app)
    cfg = load(shots_dir / "mockup.json", ("slides", "wide"))
    use_font(app, cfg.get("font", "gothic"))
    if a.styles:
        out = styles_sheet(shots_dir, cfg)
        print(f"見比べ用を作りました: {out}")
        if not a.no_open:
            subprocess.run(["open", "-a", "Preview", str(out)], check=False)
        return
    errors = lint(cfg, shots_dir, not a.no_ocr)
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
            m.wide(base / kind / f"{w}x{h}.png", m.raw_dir(lang, False), wide, (w, h), badge)

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
