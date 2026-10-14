"""アプリ紹介の短い動画（縦 1080x1920・約15秒）を作る。
使い方: python3 scripts/video/make_app_ad.py <アプリのキー> [BGMのmp3]
アプリは同じフォルダの apps.json に足す（hook: 問いかけ2行 / screens: 画面と説明3つ / icon / name / lead / promise / store）。
画像のパスは SEADICE リポジトリからの相対。出力: ~/Developer/Images/seadice-character/youtube/app-{キー}.mp4
流れ: アプリの中の問いかけ → 画面3つ（説明つき）→ アイコンと名前、SEADICE"""
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ASSETS = Path("/Users/hidenori/Developer/Images/seadice-character")
KEY = sys.argv[1]
BGM = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/Users/hidenori/Developer/youtube-auto/shorts/Linen_and_Slow_Light.mp3")
CFG = json.loads((HERE / "apps.json").read_text())[KEY]
OUT = ASSETS / "youtube" / f"app-{KEY}.mp4"

W, H, FPS = 1080, 1920, 30
NAVY, BLUE, INK, LINE, WHITE = (32, 54, 138), (26, 68, 194), (17, 20, 24), (201, 205, 211), (255, 255, 255)
BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
MID = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
F_Q = ImageFont.truetype(BOLD, 100)
F_CAP = ImageFont.truetype(BOLD, 76)
F_NAME = ImageFont.truetype(BOLD, 120)
F_SUB = ImageFont.truetype(MID, 54)
F_SMALL = ImageFont.truetype(MID, 44)
F_BRAND = ImageFont.truetype(BOLD, 64)


def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def phone(path, h):
    """画面を黒い縁の端末の形にする。"""
    scr = fit(Image.open(REPO / path).convert("RGB"), 10_000, h - 24)
    body = Image.new("RGBA", (scr.width + 24, scr.height + 24), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle((0, 0, body.width - 1, body.height - 1), 56, fill=INK)
    body.alpha_composite(rounded(scr, 46), (12, 12))
    return body


ch = Image.open(ASSETS / "seadice-original.png").convert("RGBA")
ch = ch.crop(ch.getbbox())
SMALL = fit(ch, 220, 220)
MINI = fit(ch, 120, 120)
PHONES = [phone(s["img"], 860) for s in CFG["screens"]]
ICON = rounded(fit(Image.open(REPO / CFG["icon"]).convert("RGBA"), 300, 300), 66)

CARDS = [(2.6, "hook", None)] + [(3.0, "screen", i) for i in range(len(PHONES))] + [(4.0, "end", None)]


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def shrink(d, s, font, maxw):
    while d.textlength(s, font=font) > maxw and font.size > 30:
        font = ImageFont.truetype(font.path, font.size - 2)
    return font


def lines(d, rows, font, top, gap):
    for i, (s, blue) in enumerate(rows):
        f = shrink(d, s, font, W - 140)
        y = top + i * gap
        d.text((W / 2, y), s, font=f, fill=BLUE if blue else INK, anchor="mm")
        if blue:  # 青い行には下線（色だけに頼らない）
            w = d.textlength(s, font=f)
            d.rectangle((W / 2 - w / 2, y + f.size * 0.62, W / 2 + w / 2, y + f.size * 0.62 + 8), fill=BLUE)


def layer(fn, alpha=1.0, dy=0.0):
    ly = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ly, ImageDraw.Draw(ly))
    if alpha < 1:
        ly.putalpha(ly.split()[3].point(lambda v: round(v * alpha)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(ly, (0, round(dy)))
    return out


def frame(t):
    im = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((64, 300, W - 64, 304), fill=INK)
    bob = math.sin(t * math.pi) * 10
    start = 0.0
    for dur, kind, idx in CARDS:
        if start <= t < start + dur:
            lt = t - start
            fin = ease(lt / 0.45)
            a, dy = min(fin, ease((dur - lt) / 0.3)), (1 - fin) * 40
            if kind == "hook":
                im.alpha_composite(SMALL, ((W - SMALL.width) // 2, round(420 + bob)))
                im.alpha_composite(layer(lambda ly, dd: lines(dd, [(s, i == 0) for i, s in enumerate(CFG["hook"])], F_Q, 900, 150), a, dy))
            elif kind == "screen":
                cap = CFG["screens"][idx]["caption"]
                im.alpha_composite(layer(lambda ly, dd: lines(dd, cap, F_CAP, 400, 100), a, dy))
                p = PHONES[idx]
                k = 1.0 + 0.04 * (lt / dur)  # ゆっくり寄る
                pz = p.resize((round(p.width * k), round(p.height * k)), Image.LANCZOS)
                top = 400 + len(cap) * 100 + 10
                def ph(ly, dd):
                    ly.alpha_composite(pz, ((W - pz.width) // 2, top))
                im.alpha_composite(layer(ph, a, (1 - fin) * 60))
            elif kind == "end":
                k = ease(lt / 0.5)
                ic = ICON if k >= 1 else ICON.resize((round(ICON.width * (0.85 + 0.15 * k)),) * 2, Image.LANCZOS)
                def end(ly, dd):
                    ly.alpha_composite(ic, ((W - ic.width) // 2, round(560 - ic.height / 2)))
                    dd.text((W / 2, 820), CFG["name"], font=F_NAME, fill=INK, anchor="mm")
                    dd.text((W / 2, 930), CFG["lead"], font=F_SUB, fill=BLUE, anchor="mm")
                    dd.text((W / 2, 1010), CFG["promise"], font=F_SMALL, fill=INK, anchor="mm")
                    dd.rectangle((140, 1080, W - 140, 1082), fill=LINE)
                    dd.text((W / 2, 1150), CFG["store"], font=F_SUB, fill=INK, anchor="mm")
                im.alpha_composite(layer(end, k))
                k2 = ease((lt - 0.8) / 0.5)
                def brand(ly, dd):
                    ly.alpha_composite(MINI, (round(W / 2 - 200 - MINI.width / 2), round(1290 - MINI.height / 2 + bob)))
                    dd.text((W / 2 + 60, 1290), "SEADICE", font=F_BRAND, fill=NAVY, anchor="mm")
                im.alpha_composite(layer(brand, k2, (1 - k2) * 20))
            break
        start += dur
    return im.convert("RGB")


total = sum(c[0] for c in CARDS)
with tempfile.TemporaryDirectory() as tmp:
    for i in range(round(total * FPS)):
        frame(i / FPS).save(f"{tmp}/{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
                    "-i", str(BGM), "-t", f"{total}", "-af", f"afade=t=in:d=0.5,afade=t=out:st={total - 1.5}:d=1.5",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(OUT)], check=True)
print(OUT, f"{total}s")
