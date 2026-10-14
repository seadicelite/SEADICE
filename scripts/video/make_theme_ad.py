"""テーマ別の短い広告（縦 1080x1920・約12秒）を作る。
使い方: python3 make_theme_ad.py <テーマのキー> [BGMのmp3]
テーマは同じフォルダの themes.json に足す（theme: 問いかけ2行 / items: 道具・アプリ3つ / media / url）。
出力: ~/Developer/Images/seadice-character/youtube/ad-{キー}.mp4。流れ: 問いかけ → SEADICEは研究をもとにアプリやツールを作っています → 道具3つ → シーダイスとURL"""
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = Path("/Users/hidenori/Developer/Images/seadice-character")  # 元絵と書き出し先（画像はリポジトリに入れない）
KEY = sys.argv[1]
BGM = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/Users/hidenori/Developer/youtube-auto/shorts/Linen_and_Slow_Light.mp3")
CFG = json.loads((HERE / "themes.json").read_text())[KEY]
OUT = ASSETS / "youtube" / f"ad-{KEY}.mp4"

W, H, FPS = 1080, 1920, 30
NAVY, BLUE, INK, LINE, WHITE, SKY = (32, 54, 138), (26, 68, 194), (17, 20, 24), (201, 205, 211), (255, 255, 255), (234, 241, 251)
BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
MID = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
F_Q = ImageFont.truetype(BOLD, 104)
F_H = ImageFont.truetype(BOLD, 82)
F_ITEM = ImageFont.truetype(BOLD, 58)
F_TAG = ImageFont.truetype(MID, 34)
F_LOGO = ImageFont.truetype(BOLD, 150)
F_MEDIA = ImageFont.truetype(MID, 52)
F_URL = ImageFont.truetype(MID, 48)

ch = Image.open(ASSETS / "seadice-original.png").convert("RGBA")
ch = ch.crop(ch.getbbox())


def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)


SMALL, BIG = fit(ch, 230, 230), fit(ch, 560, 560)
ICONS = {it["icon"]: fit(Image.open(it["icon"]).convert("RGBA"), 96, 96) for it in CFG["items"] if it.get("icon")}

# (秒, 種類)
CARDS = [(2.8, "ask"), (3.4, "about"), (3.2, "items"), (3.1, "end")]


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def layer(draw_fn, alpha=1.0, dy=0.0):
    ly = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ly, ImageDraw.Draw(ly))
    if alpha < 1:
        ly.putalpha(ly.split()[3].point(lambda v: round(v * alpha)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(ly, (0, round(dy)))
    return out


def shrink(d, s, font, maxw):
    """maxw に収まるまで文字を小さくする（長い道具名・問いかけ用）。"""
    while d.textlength(s, font=font) > maxw and font.size > 30:
        font = ImageFont.truetype(font.path, font.size - 2)
    return font


def lines(d, rows, font, top, gap):
    for i, (s, blue) in enumerate(rows):
        font = shrink(d, s, font, W - 140)
        y = top + i * gap
        d.text((W / 2, y), s, font=font, fill=BLUE if blue else INK, anchor="mm")
        if blue:  # 青い行には下線（色だけに頼らない）
            w = d.textlength(s, font=font)
            d.rectangle((W / 2 - w / 2, y + font.size * 0.62, W / 2 + w / 2, y + font.size * 0.62 + 8), fill=BLUE)


def frame(t):
    im = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((64, 300, W - 64, 304), fill=INK)
    d.rectangle((64, 1500, W - 64, 1502), fill=LINE)
    bob = math.sin(t * math.pi) * 10
    start = 0.0
    for dur, kind in CARDS:
        if start <= t < start + dur:
            lt = t - start
            fin = ease(lt / 0.45)
            a, dy = min(fin, ease((dur - lt) / 0.3)), (1 - fin) * 40
            if kind != "end":
                im.alpha_composite(SMALL, ((W - SMALL.width) // 2, round(420 + bob)))
            if kind == "ask":
                im.alpha_composite(layer(lambda ly, dd: lines(dd, [(s, i == 0) for i, s in enumerate(CFG["theme"])], F_Q, 900, 150), a, dy))
            elif kind == "about":
                rows = [("SEADICEでは", False), ("研究をもとにした", True), ("アプリやツールを", False), ("作っています", False)]
                im.alpha_composite(layer(lambda ly, dd: lines(dd, rows, F_H, 820, 118), a, dy))
            elif kind == "items":
                def items(ly, dd):
                    bw, bh, x = 860, 150, (W - 860) / 2
                    for i, it in enumerate(CFG["items"]):
                        k = ease((lt - i * 0.3) / 0.35)
                        if k <= 0:
                            continue
                        y = 760 + i * 190 + (1 - k) * 30
                        dd.rectangle((x, y, x + bw, y + bh), fill=WHITE, outline=INK, width=4)
                        tx = x + 40
                        if it.get("icon"):
                            ic = ICONS[it["icon"]]
                            ly.alpha_composite(ic, (round(x + 30), round(y + (bh - ic.height) / 2)))
                            tx = x + 30 + ic.width + 28
                        tag = it.get("tag", "ツール")
                        tw = dd.textlength(tag, font=F_TAG)
                        dd.text((tx, y + bh / 2), it["name"], font=shrink(dd, it["name"], F_ITEM, x + bw - tw - 90 - tx), fill=INK, anchor="lm")
                        dd.rectangle((x + bw - tw - 64, y + bh / 2 - 30, x + bw - 24, y + bh / 2 + 30), fill=BLUE)
                        dd.text((x + bw - 44 - tw / 2, y + bh / 2), tag, font=F_TAG, fill=WHITE, anchor="mm")
                im.alpha_composite(layer(items, min(1.0, ease((dur - lt) / 0.3))))
            elif kind == "end":
                k = ease(lt / 0.6)
                c = BIG
                if k < 1:
                    s = 0.85 + 0.15 * k
                    c = BIG.resize((round(BIG.width * s), round(BIG.height * s)), Image.LANCZOS)
                    c.putalpha(c.split()[3].point(lambda v: round(v * k)))
                im.alpha_composite(c, ((W - c.width) // 2, round(690 - c.height / 2 + bob)))
                k2 = ease((lt - 0.4) / 0.5)
                def logo(ly, dd):
                    dd.text((W / 2, 1110), "SEADICE", font=F_LOGO, fill=NAVY, anchor="mm")
                    dd.text((W / 2, 1230), CFG["media"], font=F_MEDIA, fill=INK, anchor="mm")
                    dd.text((W / 2, 1310), CFG["url"], font=F_URL, fill=BLUE, anchor="mm")
                im.alpha_composite(layer(logo, k2, (1 - k2) * 30))
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
