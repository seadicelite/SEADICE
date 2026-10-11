#!/usr/bin/env python3
"""SEADICE Safari拡張（コンテンツブロッカー）用のルールJSONを作る。

  python3 filters/build_filters.py --out filters/public [--state 前回のscam-firstseen.json.gz]

出力（filters/public/）:
  scam.json      詐欺サイトを止める（Phishing.Database, MIT）
  ads.json       広告を減らす（AdGuard Japanese + Base, GPL-3.0）
  trackers.json  あとをつけられないようにする（EasyPrivacy, CC BY-SA 3.0）
  meta.json      件数・更新日時・出典
  state/scam-firstseen.json.gz  詐欺ドメインを最初に見た日（新しい順に選ぶため。次回の --state に渡す）

Safariは1拡張15万ルールまでだが、iOS 18で5万前後でも読み込みに失敗する報告があるため各5万までに抑える。
"""
import argparse
import datetime
import gzip
import json
import os
import re
import sys
import urllib.request

MAX_RULES = 50000
SCAM_JP_SHARE = 20000  # 詐欺リストのうち日本関連を優先して残す枠

SOURCES = {
    "scam": [("Phishing.Database", "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-domains-ACTIVE.txt",
              "MIT", "https://github.com/mitchellkrogza/Phishing.Database")],
    "ads": [("AdGuard Japanese filter", "https://filters.adtidy.org/extension/safari/filters/7.txt",
             "GPL-3.0", "https://github.com/AdguardTeam/AdguardFilters"),
            ("AdGuard Base filter", "https://filters.adtidy.org/extension/safari/filters/2.txt",
             "GPL-3.0", "https://github.com/AdguardTeam/AdguardFilters")],
    "trackers": [("EasyPrivacy", "https://easylist.to/easylist/easyprivacy.txt",
                  "CC BY-SA 3.0 (The EasyList authors)", "https://easylist.to/")],
}

# 誰でもサブドメインを作れるサービス。親ドメインごと止めると普通のサイトまで止まるので、親だけの行は捨てる
SHARED_HOSTS = {
    "duckdns.org", "appspot.com", "pages.dev", "webflow.io", "vercel.app", "weeblysite.com", "000webhostapp.com",
    "github.io", "weebly.com", "r2.dev", "web.app", "firebaseapp.com", "glitch.me", "netlify.app", "wixsite.com",
    "blogspot.com", "herokuapp.com", "azurewebsites.net", "workers.dev", "godaddysites.com", "square.site",
    "sites.google.com", "google.com", "docs.google.com", "forms.gle", "ipfs.io", "replit.app", "repl.co",
    "framer.app", "framer.website", "notion.site", "carrd.co", "wordpress.com", "mystrikingly.com",
}

JP_WORDS = re.compile(
    r"\.jp$|rakuten|amazon|aeon|smbc|mufg|mizuho|resona|jcb|saison|epos|orico|docomo|softbank|yamato|kuroneko|"
    r"sagawa|japanpost|yubin|jppost|etax|e-tax|nta-|mercari|paypay|aupay|yahoo|jibun|sbi|rakuma|ntt|kddi|"
    r"view-card|viewcard|eki-net|ekinet|tepco|mynumber|myna|apple|icloud|line-|lineme|uniqlo|nhk")

DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+$")
NET_RULE = re.compile(r"^\|\|([a-z0-9.-]+)\^(?:\$(.+))?$")
# Safariのcss-display-noneで安全に通る、素直なセレクタだけを使う（1つでも不正だとリスト全体が読み込めない）
SAFE_SELECTOR = re.compile(r"^[A-Za-z0-9_\-#.\[\]=\"'^$*~ >+]+$")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "seadice-filters/1.0"})
    with urllib.request.urlopen(req, timeout=120) as res:
        return res.read().decode("utf-8", "replace")


def domain_filter(domain):
    return "^[^:]+://+([^:/]+\\.)?" + re.escape(domain).replace("\\-", "-") + "[:/]"


def block_rule(domain, third_party=False):
    trigger = {"url-filter": domain_filter(domain)}
    if third_party:
        trigger["load-type"] = ["third-party"]
    return {"trigger": trigger, "action": {"type": "block"}}


def allow_rule(domain):
    return {"trigger": {"url-filter": domain_filter(domain)}, "action": {"type": "ignore-previous-rules"}}


def collapse(domains):
    """親ドメインがあれば子ドメインを捨てる（url-filterはサブドメインにも効くため）。"""
    keep = set(domains)
    out = []
    for d in domains:
        parts = d.split(".")
        if any(".".join(parts[i:]) in keep for i in range(1, len(parts) - 1)):
            continue
        out.append(d)
    return out


# ---------- 詐欺サイト ----------

def build_scam(text, firstseen, today):
    domains = set()
    for line in text.splitlines():
        d = line.strip().lower().rstrip(".")
        if not d or d.startswith("#") or not DOMAIN_RE.match(d) or d in SHARED_HOSTS:
            continue
        domains.add(d)
    for d in domains:
        firstseen.setdefault(d, today)
    for d in list(firstseen):  # リストから消えたものは記録からも消す
        if d not in domains:
            del firstseen[d]
    newest = sorted(collapse(sorted(domains)), key=lambda d: (firstseen[d], d), reverse=True)
    jp = [d for d in newest if JP_WORDS.search(d)][:SCAM_JP_SHARE]
    jp_set = set(jp)
    rest = [d for d in newest if d not in jp_set][:MAX_RULES - len(jp)]
    return [block_rule(d) for d in jp + rest], len(domains)


# ---------- 広告・追跡（ABP/AdGuard形式のうち、確実に変換できる行だけ） ----------

def parse_abp(texts, cap):
    blocks, allows, generic_css, site_css = [], [], [], {}
    seen = set()
    for text in texts:
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("!") or line.startswith("["):
                continue
            if "#@#" in line or "#?#" in line or "#$#" in line or "#%#" in line or "$$" in line:
                continue
            if "##" in line:
                domains, sel = line.split("##", 1)
                if not SAFE_SELECTOR.match(sel):
                    continue
                if not domains:
                    generic_css.append(sel)
                    continue
                ds = domains.split(",")
                if any(d.startswith("~") for d in ds) or not all(DOMAIN_RE.match(d) for d in ds):
                    continue
                site_css.setdefault(tuple(sorted(ds)), []).append(sel)
                continue
            exception = line.startswith("@@")
            m = NET_RULE.match(line[2:] if exception else line)
            if not m:
                continue
            domain, opts = m.group(1), m.group(2)
            if not DOMAIN_RE.match(domain):
                continue
            opts = set(opts.split(",")) if opts else set()
            if exception:
                if opts - {"document", "important"}:
                    continue
                allows.append(domain)
                continue
            if opts - {"third-party", "important"}:
                continue
            key = (domain, "third-party" in opts)
            if key not in seen:
                seen.add(key)
                blocks.append(key)

    rules = []
    css_rules = []
    for i in range(0, len(generic_css), 200):  # まとめて1ルールにする（ルール数の節約）
        css_rules.append({"trigger": {"url-filter": ".*"},
                          "action": {"type": "css-display-none", "selector": ", ".join(dict.fromkeys(generic_css[i:i + 200]))}})
    for ds, sels in site_css.items():
        css_rules.append({"trigger": {"url-filter": ".*", "if-domain": ["*" + d for d in ds]},
                          "action": {"type": "css-display-none", "selector": ", ".join(dict.fromkeys(sels))}})
    allow_rules = [allow_rule(d) for d in dict.fromkeys(allows)]
    room = cap - len(css_rules) - len(allow_rules)
    if room < 0:  # CSSが多すぎる場合はサイト別CSSから削る
        css_rules = css_rules[:cap - len(allow_rules)]
        room = 0
    rules = [block_rule(d, tp) for d, tp in blocks[:room]] + css_rules + allow_rules
    return rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--state", help="前回の scam-firstseen.json.gz（パスまたはURL）")
    args = ap.parse_args()
    os.makedirs(os.path.join(args.out, "state"), exist_ok=True)
    today = datetime.date.today().isoformat()

    firstseen = {}
    if args.state:
        try:
            raw = urllib.request.urlopen(args.state, timeout=60).read() if args.state.startswith("http") \
                else open(args.state, "rb").read()
            firstseen = json.loads(gzip.decompress(raw))
        except Exception as e:  # 初回や取得失敗時は全件「今日」扱い
            print("state not loaded:", e, file=sys.stderr)

    counts = {}
    scam_rules, scam_total = build_scam(fetch(SOURCES["scam"][0][1]), firstseen, today)
    outputs = {
        "scam": scam_rules,
        "ads": parse_abp([fetch(s[1]) for s in SOURCES["ads"]], MAX_RULES),
        "trackers": parse_abp([fetch(s[1]) for s in SOURCES["trackers"]], MAX_RULES),
    }
    for name, rules in outputs.items():
        if not rules:
            sys.exit("empty rule list: " + name)
        with open(os.path.join(args.out, name + ".json"), "w") as f:
            json.dump(rules, f, ensure_ascii=False, separators=(",", ":"))
        counts[name] = len(rules)
    with open(os.path.join(args.out, "state", "scam-firstseen.json.gz"), "wb") as f:
        f.write(gzip.compress(json.dumps(firstseen, separators=(",", ":")).encode()))

    meta = {
        "version": datetime.datetime.utcnow().strftime("%Y%m%d%H%M"),
        "updated": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "counts": counts,
        "scamSourceTotal": scam_total,
        "sources": {k: [{"name": n, "license": l, "url": u} for n, _, l, u in v] for k, v in SOURCES.items()},
    }
    with open(os.path.join(args.out, "meta.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
