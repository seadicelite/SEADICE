#!/usr/bin/env python3
"""ページに3タイプ（read=読ませる / show=魅せる / use=使う）のデザインを当てる。

design/base.css + design/{type}.css を minify して <head> 末尾に
<style id="sd-design"> として差し込み（既にあれば差し替え）、<body> に class="t-{type}" を付ける。
CSSを直したら同じコマンドを再実行すれば全ページに反映される。

  python3 scripts/apply_page_type.py read p/blog/xxx/index.html ...
  python3 scripts/apply_page_type.py --refresh   # design/ を直した後、適用済みの全ページを各タイプで再適用
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = ("read", "show", "use")


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def design_css(kind):
    return minify((ROOT / "design/base.css").read_text() + (ROOT / f"design/{kind}.css").read_text())


def apply(path, kind, css=None):
    css = css or design_css(kind)
    html = path.read_text(encoding="utf-8")
    tag = f'<style id="sd-design">{css}</style>'
    if 'id="sd-design"' in html:
        html = re.sub(r'<style id="sd-design">.*?</style>', lambda _: tag, html, flags=re.S)
    else:
        html = html.replace("</head>", tag + "</head>", 1)
    m = re.search(r"<body([^>]*)>", html)
    attrs = m.group(1)
    cm = re.search(r'class="([^"]*)"', attrs)
    if cm:
        classes = [c for c in cm.group(1).split() if c not in ("t-read", "t-show", "t-use")]
        new_attrs = attrs.replace(cm.group(0), f'class="{" ".join(classes + ["t-" + kind])}"')
    else:
        new_attrs = f' class="t-{kind}"' + attrs
    html = html[:m.start()] + f"<body{new_attrs}>" + html[m.end():]
    path.write_text(html, encoding="utf-8")


def refresh():
    css = {k: design_css(k) for k in TYPES}
    count = dict.fromkeys(TYPES, 0)
    for f in (ROOT / "p").rglob("index.html"):
        m = re.search(r'<body[^>]*class="[^"]*\bt-(read|show|use)\b', f.read_text(encoding="utf-8"))
        if m:
            apply(f, m.group(1), css[m.group(1)])
            count[m.group(1)] += 1
    print(count)


def main():
    if sys.argv[1:] == ["--refresh"]:
        return refresh()
    if len(sys.argv) < 3 or sys.argv[1] not in TYPES:
        sys.exit(__doc__)
    kind = sys.argv[1]
    css = design_css(kind)
    for f in sys.argv[2:]:
        apply(Path(f), kind, css)
    print(f"{kind}: {len(sys.argv) - 2} pages, {len(css)} bytes")


if __name__ == "__main__":
    main()
