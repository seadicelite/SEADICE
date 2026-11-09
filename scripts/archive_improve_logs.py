#!/usr/bin/env python3
"""docs/improve/*.md の「やったこと」「ルールの変更履歴」から、今月より前の記録を docs/improve/log/ へ移す。

毎回読むファイルを小さく保つため（2026-11-09〜）。何度実行しても同じ結果になる。
月曜のルーティン（rules 担当）が、月の最初の回に実行する。

    python3 scripts/archive_improve_logs.py            # 今月1日より前を移す
    python3 scripts/archive_improve_logs.py 2026-12-01 # 指定日より前を移す
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "improve"
SECTIONS = {"やったこと", "全体のやったこと", "ルールの変更履歴"}
POINTER = "古い記録は [log/{name}](log/{name})。"


def split(lines):
    """本文と、移す記録（節ごと）に分ける。記録は「- YYYY-MM-DD」で始まる箇条書き（続きの行も含む）。"""
    keep, moved, cur, i = [], {}, None, 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^#{2,3} (.+?)\s*$", line)
        if m:
            cur = m.group(1) if m.group(1) in SECTIONS else None
            keep.append(line)
            i += 1
            continue
        if cur and line.startswith("- "):
            item = [line]
            i += 1
            while i < len(lines) and lines[i] and not lines[i].startswith(("- ", "#")):
                item.append(lines[i])
                i += 1
            d = re.match(r"- \**(\d{4}-\d{2}-\d{2})", line)
            (moved.setdefault(cur, []) if d and d.group(1) < CUT else keep).extend(item)
            continue
        keep.append(line)
        i += 1
    return keep, moved


def add_pointer(lines, name, sections):
    """移した節の見出しの直後に、log へのリンクがなければ足す。"""
    out = []
    for i, line in enumerate(lines):
        out.append(line)
        m = re.match(r"^#{2,3} (.+?)\s*$", line)
        if not (m and m.group(1) in sections):
            continue
        body = []
        for l in lines[i + 1:]:
            if l.startswith("#"):
                break
            body.append(l)
        if not any("](log/" in l for l in body):
            out += ["", POINTER.format(name=name)]
    return out


CUT = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().replace(day=1).isoformat()

for path in sorted(ROOT.glob("*.md")):
    if path.name == "manual.md":
        continue
    keep, moved = split(path.read_text().split("\n"))
    if not moved:
        continue
    log = ROOT / "log" / path.name
    log.parent.mkdir(exist_ok=True)
    old = log.read_text() if log.exists() else (
        f"# {path.stem} の古い記録\n\n[../{path.name}](../{path.name}) から移した記録。普段は読まない。\n")
    block = "".join(f"\n## {sec}（{CUT} より前）\n\n" + "\n".join(items) + "\n" for sec, items in moved.items())
    log.write_text(old.rstrip("\n") + "\n" + block)
    path.write_text("\n".join(add_pointer(keep, path.name, moved)))
    print(path.relative_to(ROOT.parent.parent), {k: len(v) for k, v in moved.items()})
