"""シーダイスのYouTube用素材を作る。使い方: python3 make.py <元画像> <出力フォルダ>"""
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
FR = OUT / "_frames"
NAVY = (32, 54, 138)
SKY = (234, 241, 251)
WHITE = (255, 255, 255)
BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
MID = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

ch = Image.open(SRC).convert("RGBA")
ch = ch.crop(ch.getbbox())  # 余白を落とす
head = ch.crop((0, 0, ch.width, int(ch.height * 0.80)))  # 胸から上（腕まで入れて、切り口を胴にする）


def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)


def paste_center(base, im, cx, cy):
    base.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def font(path, size):
    return ImageFont.truetype(path, size)


def text_c(d, xy, s, f, fill):
    d.text(xy, s, font=f, fill=fill, anchor="mm")


# 1. 透過の全身（編集アプリに重ねる用）
fit(ch, 2000, 2000).save(OUT / "seadice-full.png")

# 2. チャンネルアイコン 800x800（丸く切り抜かれるので中央に頭）
ic = Image.new("RGBA", (800, 800), SKY + (255,))
hc = fit(head, 600, 640)
ic.alpha_composite(hc, ((800 - hc.width) // 2, 800 - hc.height))  # 胴の切り口を下端にそろえる
ic.convert("RGB").save(OUT / "channel-icon-800.png")

# 3. 透かし 150x150（YouTube Studio の「ブランディング」→「動画の透かし」）
wm = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
hw = fit(head, 150, 150)
wm.alpha_composite(hw, ((150 - hw.width) // 2, 150 - hw.height))
wm.save(OUT / "watermark-150.png")

# 4. チャンネルバナー 2560x1440（どの端末でも見える中央 1546x423 に収める）
bn = Image.new("RGBA", (2560, 1440), WHITE + (255,))
d = ImageDraw.Draw(bn)
paste_center(bn, fit(ch, 380, 380), 1280 - 430, 720)
text_c(d, (1280 + 170, 690), "SEADICE", font(BOLD, 150), NAVY)
text_c(d, (1280 + 170, 800), "seadice.win", font(MID, 56), NAVY)
bn.convert("RGB").save(OUT / "channel-banner-2560x1440.png")

# 5. 動画に重ねる透過フレーム（右下にシーダイス）
for w, h, name, s in ((1920, 1080, "overlay-1920x1080.png", 300), (1080, 1920, "overlay-1080x1920.png", 340)):
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    c = fit(ch, s, s)
    ov.alpha_composite(c, (w - c.width - 48, h - c.height - 48))
    ov.save(OUT / name)


# 6. 動き（ふわふわ浮く2秒ループ）を描いたフレーム列
def float_frame(i, n, size):
    t = i / n * 2 * math.pi
    c = fit(ch, size, size).rotate(math.sin(t) * 3, resample=Image.BICUBIC, expand=True)
    return c, math.sin(t) * size * 0.035


def run(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def frames(draw, n):
    FR.mkdir(exist_ok=True)
    for f in FR.glob("*.png"):
        f.unlink()
    for i in range(n):
        draw(i).save(FR / f"{i:04d}.png")


N, FPS = 60, 30
# 6a. 透過のループ（Final Cut・Premiere・DaVinci 用 ProRes 4444）と、グリーンバック版（CapCut・iMovie などのクロマキー用）
def loop_frame(bg):
    def f(i):
        im = Image.new("RGBA", (1080, 1080), bg)
        c, dy = float_frame(i, N, 860)
        paste_center(im, c, 540, 540 + dy)
        return im
    return f

frames(loop_frame((0, 0, 0, 0)), N)
run(["-framerate", str(FPS), "-i", str(FR / "%04d.png"), "-c:v", "prores_ks", "-profile:v", "4444",
     "-pix_fmt", "yuva444p10le", str(OUT / "seadice-float-alpha.mov")])
frames(loop_frame((0, 177, 64, 255)), N)
run(["-framerate", str(FPS), "-i", str(FR / "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
     str(OUT / "seadice-float-greenback.mp4")])


# 6b. 締めの画面（横 10秒：右側に終了画面の要素を置ける余白／縦 Shorts 3秒）
def outro(w, h, secs, cx, cy, size, tx, ty, ts):
    n = secs * FPS
    def f(i):
        im = Image.new("RGBA", (w, h), WHITE + (255,))
        d = ImageDraw.Draw(im)
        c, dy = float_frame(i % N, N, size)
        paste_center(im, c, cx, cy + dy)
        text_c(d, (tx, ty), "SEADICE", font(BOLD, ts), NAVY)
        text_c(d, (tx, ty + ts * 0.85), "seadice.win", font(MID, round(ts * 0.38)), NAVY)
        return im
    return f, n

f, n = outro(1920, 1080, 10, 480, 470, 560, 480, 880, 96)
frames(f, n)
run(["-framerate", str(FPS), "-i", str(FR / "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
     str(OUT / "outro-1920x1080-10s.mp4")])
f, n = outro(1080, 1920, 3, 540, 820, 760, 540, 1400, 120)
frames(f, n)
run(["-framerate", str(FPS), "-i", str(FR / "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
     str(OUT / "outro-shorts-1080x1920-3s.mp4")])

for f in FR.glob("*.png"):
    f.unlink()
FR.rmdir()
print("\n".join(sorted(p.name for p in OUT.iterdir())))
