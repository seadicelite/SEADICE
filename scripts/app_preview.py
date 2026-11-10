#!/usr/bin/env python3
"""App Store のアプリプレビュー（動画）を、録画とアプリの screenshots/preview.json から書き出す（docs/mockup.md）。

  python3 scripts/app_preview.py {アプリのフォルダ} --record 1   # 起動中のシミュレーターを録画 → screenshots/rec/1.mov（Enter で止める。--seconds 20 なら20秒で）
  python3 scripts/app_preview.py {アプリのフォルダ}              # 書き出し → 点検 → 開く

Apple の決まり: 中身はアプリの画面を録画したものだけ（文字を重ねるのは可）、15〜30秒、30fps。
形: 録画を縦のまま画面いっぱいに出し、下に見出しの帯を重ねるだけ（2026-11-11）。余白・枠・本体の縁・印（バッジ）・拡大窓は付けない。
  以前の「左に見出し、右に録画を枠で」は Guideline 2.3.4 で却下された（FBI式ボディランゲージ辞典 1.1.0:
  framing around the video screen capture / device frames / self-promotional ad）。色は mockup.json から読む。

preview.json:
{
  "clips": [{"video": "1.mov", "start": 0.5, "end": 6, "lines": ["1行目", "2行目（アクセント色）", "補足"]}, ...],
  # focus（拡大窓）は動画では使わない（枠で囲んだ絵を重ねると 2.3.4 の framing に取られうる）
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
from mockup import COLORS, HEAD_TRACK, PRICE_WORDS, fit, font, load, ocr_price, rgb, tdraw, tlen, use_font  # noqa: E402

# (名前, 幅, 高さ, 録画のフォルダ)。縦の録画を余白なしで出すので縦のサイズ（2026-11-11、横は余白が要り 2.3.4 で却下）
SIZES = [
    ("iphone", 886, 1920, "rec"),
    ("ipad", 1200, 1600, "rec_ipad"),
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


def caption(path, W, H, colors, lines):
    """録画の上に重ねる見出しの帯（下の端）。帯の外は透明で、録画がそのまま見える"""
    c = colors
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(W * 0.07)
    room = W - pad * 2
    line1, line2, sub = lines
    hs = min(fit(line1, "W7", W * 0.085, room)[1], fit(line2, "W7", W * 0.085, room)[1])
    head = font("W7", hs)
    small, ss = fit(sub, "W6", hs * 0.5, room)
    # 帯は下の端に置く（上はアプリの見出しと核の操作があることが多く、下はタブバーで隠しても困らない）
    band = int(hs * 0.7) + int(hs * 1.3) * 2 + int(ss * 1.6) + int(hs * 0.5)
    d.rectangle((0, H - band, W, H), fill=c["bg"] + (240,))
    top = H - band + int(hs * 0.6)
    for i, (t, f, col, tr) in enumerate(((line1, head, c["text"], HEAD_TRACK), (line2, head, c["accent"], HEAD_TRACK))):
        tdraw(d, ((W - tlen(t, f, tr)) / 2, top + int(hs * 1.3) * i), t, f, col, tr)
    tdraw(d, ((W - tlen(sub, small)) / 2, top + int(hs * 2.7)), sub, small, c["sub"])
    im.save(path)


def build(out, recs, size, colors, badge, clips, tmp):
    name, W, H, _ = size
    segs = []
    for i, cl in enumerate(clips):
        png = tmp / f"{name}_{i}.png"
        caption(png, W, H, colors, cl["lines"])
        dur = cl["end"] - cl["start"]
        seg = tmp / f"{name}_{i}.mp4"
        # 録画を縦横比を保って画面いっぱいに広げ、はみ出した上下（または左右）を切る。余白は作らない
        run(["ffmpeg", "-y", "-v", "error",
             "-ss", str(cl["start"]), "-t", str(dur), "-i", str(recs / cl["video"]),
             "-loop", "1", "-i", str(png),
             "-filter_complex",
             f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v];"
             f"[v][1:v]overlay=0:0[m];"
             # 1本目は黒から始めない（最初のコマが Finder の見本や App Store の静止画になり、真っ暗に見えた 2026-11-11）
             f"[m]" + (f"fade=t=in:st=0:d={FADE}," if i else "") + f"fade=t=out:st={dur - FADE}:d={FADE},format=yuv420p",
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
