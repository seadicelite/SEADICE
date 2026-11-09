#!/usr/bin/env python3
"""App Store のアプリプレビュー（動画）を、録画とアプリの screenshots/preview.json から書き出す（docs/mockup.md）。

  python3 scripts/app_preview.py {アプリのフォルダ} --record 1   # 起動中のシミュレーターを録画 → screenshots/rec/1.mov（Enter で止める。--seconds 20 なら20秒で）
  python3 scripts/app_preview.py {アプリのフォルダ}              # 書き出し → 点検 → 開く

Apple の決まり: 中身はアプリの画面を録画したものだけ（文字を重ねるのは可）、15〜30秒、30fps。横の 1920×886・1600×1200。
形はヘッダーの絵と同じ（左に印と見出し、右に録画を角丸の枠でまるごと）。色と印は mockup.json から読む。

preview.json:
{
  "clips": [{"video": "1.mov", "start": 0.5, "end": 6, "lines": ["1行目", "2行目（アクセント色）", "補足"],
             "focus": [0.02, 0.17, 0.96, 0.25]}, ...],   # 拡大窓（録画に対する割合）。iPad は自動で探す（focus_ipad で指定も可）
  "en": {"clips": [...]}          # 英語版（録画は rec/en/）
}
録画: iPhone は screenshots/rec/（英語は rec/en/）、iPad は rec_ipad/（無ければ iPad の動画は作らない）
出力: screenshots/preview/{iphone,ipad}.mp4（英語は screenshots/en/preview/）
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from mockup import COLORS, HEAD_TRACK, PRICE_WORDS, fit, font, load, locate, ocr_price, rgb, tdraw, tlen, use_font  # noqa: E402

# (名前, 幅, 高さ, 録画のフォルダ)。docs/mockup.md の表のアプリプレビュー（横、2026-11-09 ユーザー指定）
SIZES = [
    ("iphone", 1920, 886, "rec"),
    ("ipad", 1600, 1200, "rec_ipad"),
]
FPS = 30
FADE = 0.2


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg が失敗しました:\n{r.stderr[-1500:]}")
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]))


def layout(W, H, rec):
    """録画を右に、縦いっぱい（上下に余白）で置く。(x, y, 幅, 高さ)"""
    rw, rh = map(int, run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(rec)]).strip().split(","))
    sh = int(H * 0.88) // 2 * 2
    sw = int(sh * rw / rh) // 2 * 2
    if sw > W * 0.55:  # 横向きの録画（iPad など）は、見出しの場所を残して幅で合わせる
        sw = int(W * 0.55) // 2 * 2
        sh = int(sw * rh / rw) // 2 * 2
    return W - int(W * 0.06) - sw, (H - sh) // 2, sw, sh


def front(path, W, H, box, colors, badge, lines, overhang=0):
    """録画の上に重ねる絵。左に印と見出し、録画の所だけ角丸にくり抜く"""
    c = colors
    x, y, sw, sh = box
    im = Image.new("RGBA", (W, H), c["bg"] + (255,))
    d = ImageDraw.Draw(im)
    left = int(W * 0.06)
    room = x - left - int(W * 0.05) - overhang  # 拡大窓が録画より左にはみ出す分も空ける
    line1, line2, sub = lines
    hs = min(fit(line1, "W7", H * 0.11, room)[1], fit(line2, "W7", H * 0.11, room)[1])
    head = font("W7", hs)
    small, _ = fit(sub, "W6", hs * 0.45, room)
    bh = int(hs * 0.7) if badge else 0
    top = (H - (bh + int(hs * 0.5) + int(hs * 1.3) * 2 + int(hs * 0.6))) // 2
    if badge:
        # スクショと同じ: 印は細い線の枠、文字は詰め組み（scripts/mockup.py）
        bf = font("W6", hs * 0.36)
        bw = tlen(badge, bf) + hs * 0.56
        d.rounded_rectangle((left, top, left + bw, top + bh), bh / 2, outline=c["sub"], width=max(int(hs * 0.03), 2))
        tdraw(d, (left + hs * 0.28, top + bh * 0.18), badge, bf, c["sub"])
        top += bh + int(hs * 0.5)
    tdraw(d, (left, top), line1, head, c["text"], HEAD_TRACK)
    tdraw(d, (left, top + int(hs * 1.3)), line2, head, c["accent"], HEAD_TRACK)
    tdraw(d, (left, top + int(hs * 2.75)), sub, small, c["sub"])
    r = int(sw * 0.08)
    d.rounded_rectangle((x - 4, y - 4, x + sw + 4, y + sh + 4), r + 4, fill=c["frame"])
    d.rounded_rectangle((x, y, x + sw, y + sh), r, fill=(0, 0, 0, 0))
    im.save(path)


def frame_png(video, t, out):
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(video), "-frames:v", "1", str(out)])
    return out


def focus_for(cl, name, recs, tmp, i):
    """拡大窓の場所（録画に対する割合）。iPad は iPhone の録画で決めた場所を、iPad の録画の最初のコマから探す"""
    if name == "iphone" or cl.get("focus_ipad"):
        return cl.get("focus") if name == "iphone" else cl["focus_ipad"]
    if not cl.get("focus"):
        return None
    phone = recs.parent.parent / "rec" / recs.name if recs.name == "en" else recs.parent / "rec"
    if not (phone / cl["video"]).exists():
        return None
    t = cl["start"] + 0.5
    rect, score = locate(frame_png(phone / cl["video"], t, tmp / f"p{i}.png"), cl["focus"], frame_png(recs / cl["video"], t, tmp / f"q{i}.png"))
    if score < 0.6:
        print(f"注意: iPad の{i + 1}本目は拡大の場所が見つかりません（{score:.2f}）。focus_ipad を書いてください")
        return None
    return rect


def build(out, recs, size, colors, badge, clips, tmp):
    name, W, H, _ = size
    segs = []
    for i, cl in enumerate(clips):
        png = tmp / f"{name}_{i}.png"
        bx, by, SW, SH = box = layout(W, H, recs / cl["video"])
        focus = focus_for(cl, name, recs, tmp, i)
        zw = int(SW * 1.3) // 2 * 2
        front(png, W, H, box, colors, badge, cl["lines"], (zw - SW) // 2 if focus else 0)
        dur = cl["end"] - cl["start"]
        seg = tmp / f"{name}_{i}.mp4"
        bg = "#%02x%02x%02x" % colors["bg"]
        zoom = ""
        if focus:  # 録画の大事な所を切り抜いて拡大し、元の場所の上に重ねる（録画と一緒に動く。枠はアクセント色）
            fx, fy, fw, fh = focus
            zh = int(zw * fh * SH / (fw * SW)) // 2 * 2
            zx = int(min(max(bx + SW / 2 - zw / 2, 0), W - zw))
            zy = int(min(max(by + (fy + fh / 2) * SH - zh / 2, by), H - zh - 8))
            b = max(W // 320, 3)
            acc = "#%02x%02x%02x" % colors["accent"]
            zoom = (f";[z]crop=iw*{fw}:ih*{fh}:iw*{fx}:ih*{fy},scale={zw}:{zh},setsar=1[zz];"
                    f"[f]drawbox=x={zx - b}:y={zy - b}:w={zw + 2 * b}:h={zh + 2 * b}:color={acc}:t=fill[fb];[fb][zz]overlay={zx}:{zy}")
        run(["ffmpeg", "-y", "-v", "error",
             "-f", "lavfi", "-i", f"color=c={bg}:s={W}x{H}:r={FPS}",
             "-ss", str(cl["start"]), "-t", str(dur), "-i", str(recs / cl["video"]),
             "-loop", "1", "-i", str(png),
             "-filter_complex",
             f"[1:v]fps={FPS}" + (",split[r][z];[r]" if focus else ",") + f"scale={SW}:{SH},setsar=1[v];[0:v][v]overlay={bx}:{by}[b];"
             f"[b][2:v]overlay=0:0[f]" + (zoom if focus else ";[f]null") + "[m];"
             f"[m]fade=t=in:st=0:d={FADE},fade=t=out:st={dur - FADE}:d={FADE},format=yuv420p",
             "-t", str(dur), "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18", str(seg)])
        segs.append(seg)
    lst = tmp / f"{name}.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    out.parent.mkdir(parents=True, exist_ok=True)
    # 音声トラックがないと受け付けられないことがあるので、無音のステレオを入れる
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", str(FPS), "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-maxrate", "10M", "-bufsize", "20M", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(out)])


def check(out, W, H):
    info = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                "-of", "csv=p=0", str(out)]).strip().split(",")
    d = duration(out)
    errors = []
    if (int(info[0]), int(info[1])) != (W, H):
        errors.append(f"サイズが {info[0]}×{info[1]}（{W}×{H} のはず）")
    if info[2] != f"{FPS}/1":
        errors.append(f"フレームレートが {info[2]}")
    if not 15 <= d <= 30:
        errors.append(f"長さが {d:.1f} 秒（15〜30秒）")
    if out.stat().st_size > 500 * 1024 * 1024:
        errors.append("500MB を超えています")
    return d, errors


def record(shots_dir, name, seconds=None):
    out = shots_dir / "rec" / f"{name}.mov"
    out.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.Popen(["xcrun", "simctl", "io", "booted", "recordVideo", "--codec=h264", "--force", str(out)])
    if seconds:  # Claude が録るとき（Enter を押せない）は秒数で止める
        try:
            p.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            pass
    else:
        input("録画中です。シミュレーターでアプリを操作して、終わったら Enter を押してください: ")
    p.send_signal(2)
    p.wait()
    print(f"録画しました: {out}（{duration(out):.1f}秒）。preview.json に start・end を書いてください")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app", type=Path, help="アプリのフォルダ")
    ap.add_argument("--record", metavar="名前", help="起動中のシミュレーターを録画する")
    ap.add_argument("--seconds", type=float, help="--record を指定の秒数で止める")
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    shots_dir = a.app.resolve() / "screenshots"
    if a.record:
        return record(shots_dir, a.record, a.seconds)

    cfg = load(shots_dir / "preview.json", ("clips",))
    mock = shots_dir / "mockup.json"
    mcfg = json.loads(mock.read_text()) if mock.exists() else {}
    use_font(a.app.resolve(), mcfg.get("font", "gothic"))
    colors = {k: rgb(v) for k, v in {**COLORS, **mcfg.get("colors", {})}.items()}
    sets = [("ja", mcfg.get("badge", ""), cfg["clips"])]
    if "en" in cfg:
        sets.append(("en", mcfg.get("en", {}).get("badge", ""), cfg["en"]["clips"]))

    errors = []
    for lang, badge, clips in sets:
        for i, cl in enumerate(clips, 1):
            if len(cl.get("lines", [])) != 3:
                errors.append(f"[{lang}] {i}本目: lines は [1行目, 2行目, 補足] の3つ")
                continue
            if not 0 <= cl.get("start", -1) < cl.get("end", 0) or cl["end"] - cl["start"] < 1:
                errors.append(f"[{lang}] {i}本目: start・end は 0 ≦ start、end − start ≧ 1秒")
                continue
            rec = shots_dir / "rec" / ("en" if lang == "en" else "") / cl.get("video", "")
            if rec.is_file() and cl["end"] > duration(rec) + 0.05:
                errors.append(f"[{lang}] {i}本目: end {cl['end']} 秒が録画の長さ {duration(rec):.1f} 秒を超えています")
            for t in [badge, *cl["lines"]]:
                if PRICE_WORDS.search(t):
                    errors.append(f"[{lang}] {i}本目に価格の言葉: {t}（Guideline 2.3.7）")
        total = sum(cl.get("end", 0) - cl.get("start", 0) for cl in clips)
        if not 15 <= total <= 29.9:  # 30秒ちょうどは書き出しで少し延びることがあるので 29.9 まで
            errors.append(f"[{lang}] 合計 {total:.1f} 秒です（15〜29.9秒）")
        elif total > 15.5:  # 短いほうがよい（2026-11-10 ユーザー）。Apple の下限の15秒を基本にする
            print(f"注意: [{lang}] 合計 {total:.1f} 秒です。3場面×5秒＝15秒を基本にしています")
    if errors:
        sys.exit("書き出しを止めました:\n  " + "\n  ".join(errors))

    outs = []
    with tempfile.TemporaryDirectory() as t:
        for lang, badge, clips in sets:
            base = shots_dir if lang == "ja" else shots_dir / "en"
            for size in SIZES:
                recs = shots_dir / size[3] / ("en" if lang == "en" else "")
                missing = [cl["video"] for cl in clips if not (recs / cl["video"]).exists()]
                if missing:
                    if size[0] == "iphone":
                        sys.exit(f"[{lang}] 録画がありません: {recs} の {', '.join(missing)}")
                    print(f"[{lang}] {recs} に録画がないので、iPad のプレビューは作りません")
                    continue
                out = base / "preview" / f"{size[0]}.mp4"
                build(out, recs, size, colors, badge, clips, Path(t))
                d, errs = check(out, size[1], size[2])
                frames = Path(t) / f"frames_{lang}_{size[0]}"
                frames.mkdir()
                run(["ffmpeg", "-v", "error", "-i", str(out), "-vf", "fps=1", str(frames / "%03d.png")])
                errs += ocr_price(frames.glob("*.png"))  # 録画の中に価格の言葉が映っていないか（1秒ごと）
                if errs:
                    sys.exit(f"{out}: " + "・".join(errs))
                print(f"書き出しました: {out}（{size[1]}×{size[2]}・{d:.1f}秒・{FPS}fps、確認済み）")
                outs.append(out)
    if not a.no_open:
        subprocess.run(["open", *map(str, outs)], check=False)


if __name__ == "__main__":
    main()
