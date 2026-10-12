#!/usr/bin/env python3
"""docs/improve/manual.md（人の手が必要なタスク）の未対応を数えて表示する。

会話の開始時に hook から実行され、出力が Claude に渡る。Claude はそれをユーザーに知らせる。
  python3 scripts/manual_tasks.py          # 未対応の件数と上位5件
"""
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "docs" / "improve" / "manual.md"


def main():
    if not PATH.exists():
        return
    lines = PATH.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("## 未対応") + 1
    except ValueError:
        return
    todo = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.startswith("- [ ]"):
            todo.append(line[5:].strip())
    if not todo:
        print("手動タスク（docs/improve/manual.md）: 未対応なし")
        return
    print(f"手動タスク（docs/improve/manual.md）: 未対応 {len(todo)}件。会話の最初の返答で、件数と上のほうの項目を短くユーザーに知らせること。")
    for t in todo[:5]:
        print(f"- {t.split(' — ')[0]}")


if __name__ == "__main__":
    main()
