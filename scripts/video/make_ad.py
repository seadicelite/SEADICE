"""SEADICEの広告動画（縦 1080x1920・15秒）を作る。
使い方: python3 make_ad.py <キャラの元画像> <BGMのmp3> <出力mp4>
台本は CARDS を直す。Shorts の右側（ボタン）と下（題名）に隠れないよう、文字は中央の上寄りに置く。"""
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC, BGM, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
W, H, FPS = 1080, 1920, 30
NAVY = (32, 54, 138)
BLUE = (26, 68, 194)
INK = (17, 20, 24)
LINE = (201, 205, 211)
WHITE = (255, 255, 255)
BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
MID = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

# 台本（A案）。行は (文字, 青くするか)。秒は各カードの長さ
CARDS = [
    (3.0, "lines", [("その悩み、", False), ("調べるほど", False), ("答えがバラバラ？", False)]),
    (3.2, "lines", [("SEADICEは", False), ("研究と公的な資料で", False), ("確かめて答えます", True)]),
    (3.2, "tools", [("読んだら、その場で", False), ("使える道具も", True)]),
    (2.8, "promise", [("無料", False), ("広告なし", False), ("登録なし", False)]),
    (3.3, "end", []),
]

ch = Image.open(SRC).convert("RGBA")
ch = ch.crop(ch.getbbox())


def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)


SMALL = fit(ch, 230, 230)
BIG = fit(ch, 620, 620)
F_H = ImageFont.truetype(BOLD, 92)
F_TOOL = ImageFont.truetype(BOLD, 54)
F_PROM = ImageFont.truetype(BOLD, 110)
F_LOGO = ImageFont.truetype(BOLD, 150)
F_URL = ImageFont.truetype(MID, 58)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def text_layer(draw_fn, alpha, dy):
    """文字だけの層を描いて、透明度と縦のずれを付けて返す。"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    if alpha < 1:
        a = layer.split()[3].point(lambda v: round(v * alpha))
        layer.putalpha(a)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(layer, (0, round(dy)))
    return out


def lines_fn(lines, top=820, gap=128, reveal=None):
    def f(d):
        for i, (s, blue) in enumerate(lines):
            if reveal is not None and i >= reveal:
                break
            d.text((W / 2, top + i * gap), s, font=F_H, fill=BLUE if blue else INK, anchor="mm")
            if blue:  # 青い行には下線（色だけに頼らない）
                w = d.textlength(s, font=F_H)
                d.rectangle((W / 2 - w / 2, top + i * gap + 60, W / 2 + w / 2, top + i * gap + 68), fill=BLUE)
    return f


def frame(t):
    im = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(im)
    # 上下の細い罫線（取扱説明書ふうの枠）
    d.rectangle((64, 300, W - 64, 304), fill=INK)
    d.rectangle((64, 1500, W - 64, 1502), fill=LINE)
    start = 0.0
    for dur, kind, lines in CARDS:
        if start <= t < start + dur:
            lt = t - start
            fade_in, fade_out = ease(lt / 0.45), ease((dur - lt) / 0.3)
            a = min(fade_in, fade_out)
            dy = (1 - fade_in) * 40
            bob = math.sin(t * 2 * math.pi / 2) * 10
            if kind != "end":
                im.alpha_composite(SMALL, ((W - SMALL.width) // 2, round(420 + bob)))
            if kind == "lines":
                im.alpha_composite(text_layer(lines_fn(lines), a, dy))
            elif kind == "tools":
                im.alpha_composite(text_layer(lines_fn(lines, top=800), a, dy))
                def tools(dd):
                    names = ["チェック", "タイマー", "記録"]
                    bw, gapx, y = 270, 30, 1130
                    x0 = (W - (bw * 3 + gapx * 2)) / 2
                    for i, n in enumerate(names):
                        k = ease((lt - 0.5 - i * 0.25) / 0.35)
                        if k <= 0:
                            continue
                        x = x0 + i * (bw + gapx)
                        dd.rectangle((x, y, x + bw, y + 130), outline=INK, width=4)
                        dd.text((x + bw / 2, y + 65), n, font=F_TOOL, fill=BLUE, anchor="mm")
                im.alpha_composite(text_layer(tools, a, 0))
            elif kind == "promise":
                def prom(dd):
                    for i, (s, _) in enumerate(lines):
                        k = ease((lt - i * 0.35) / 0.35)
                        if k <= 0:
                            continue
                        y = 860 + i * 190
                        w = dd.textlength(s, font=F_PROM)
                        dd.text((W / 2, y), s, font=F_PROM, fill=INK, anchor="mm")
                        dd.rectangle((W / 2 - w / 2 - 30, y + 78, W / 2 - w / 2 - 30 + (w + 60) * k, y + 84), fill=BLUE)
                im.alpha_composite(text_layer(prom, a, dy))
            elif kind == "end":
                k = ease(lt / 0.6)
                c = BIG
                if k < 1:
                    s = 0.85 + 0.15 * k
                    c = BIG.resize((round(BIG.width * s), round(BIG.height * s)), Image.LANCZOS)
                    c.putalpha(c.split()[3].point(lambda v: round(v * k)))
                im.alpha_composite(c, ((W - c.width) // 2, round(700 - c.height / 2 + bob)))
                def logo(dd):
                    dd.text((W / 2, 1150), "SEADICE", font=F_LOGO, fill=NAVY, anchor="mm")
                    dd.text((W / 2, 1270), "seadice.win", font=F_URL, fill=NAVY, anchor="mm")
                im.alpha_composite(text_layer(logo, ease((lt - 0.4) / 0.5), (1 - ease((lt - 0.4) / 0.5)) * 30))
            break
        start += dur
    return im.convert("RGB")


total = sum(c[0] for c in CARDS)
n = round(total * FPS)
with tempfile.TemporaryDirectory() as tmp:
    for i in range(n):
        frame(i / FPS).save(f"{tmp}/{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
                    "-i", str(BGM), "-t", f"{total}",
                    "-af", f"afade=t=in:d=0.5,afade=t=out:st={total - 1.5}:d=1.5",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(OUT)], check=True)
print(OUT, f"{total}s")
