#!/usr/bin/env python3
"""SEADICE Safari拡張（コンテンツブロッカー）用のルールJSONを作る。

  python3 filters/build_filters.py --out filters/public [--state 前回のscam-firstseen.json.gz]

出力（filters/public/）:
  scam.json      詐欺サイトを止める（Phishing.Database, MIT）
  ads.json       広告を減らす（AdGuard Japanese: GPL-3.0 + EasyList: CC BY-SA 3.0）
  trackers.json  あとをつけられないようにする（EasyPrivacy, CC BY-SA 3.0）
  scam-domains.txt  scam.json と同じ詐欺ドメインを1行1件で（QRガードが端末内で照らし合わせる用。軽い）
  meta.json      件数・更新日時・出典
  state/scam-firstseen.json.gz  詐欺ドメインを最初に見た日（新しい順に選ぶため。次回の --state に渡す）

Safariは1拡張15万ルールまでだが、iOS 18で5万前後でも読み込みに失敗する報告があるため各5万までに抑える。
"""
import argparse
import datetime
import gzip
import hashlib
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
            ("EasyList", "https://easylist.to/easylist/easylist.txt",
             "CC BY-SA 3.0 (The EasyList authors)", "https://easylist.to/")],
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


def block_rule(domain, extra=None):
    trigger = {"url-filter": domain_filter(domain)}
    trigger.update(extra or {})
    return {"trigger": trigger, "action": {"type": "block"}}


# ABPの資源タイプ → WebKitのresource-type（iOS 15でも通るものだけ）
RTYPES = {"script": "script", "image": "image", "stylesheet": "style-sheet", "css": "style-sheet", "font": "font",
          "xmlhttprequest": "raw", "xhr": "raw", "websocket": "raw", "ping": "raw", "media": "media",
          "subdocument": "document", "frame": "document", "document": "document", "doc": "document",
          "popup": "popup", "other": "raw", "object": "raw"}
ALL_TYPES = ["document", "image", "style-sheet", "script", "font", "raw", "media", "popup"]


def convert_opts(opts):
    """$以降の条件をWebKitのtriggerの追加項目に変える。変換できない条件があれば None（その行は使わない）。"""
    extra, types, neg = {}, set(), set()
    for o in opts:
        if o in ("important", "match-case", "all", ""):
            continue
        if o in ("third-party", "3p"):
            extra["load-type"] = ["third-party"]
        elif o in ("~third-party", "1p", "first-party", "~3p"):
            extra["load-type"] = ["first-party"]
        elif o.startswith("domain="):
            ds = o[7:].split("|")
            inc = [d for d in ds if not d.startswith("~")]
            exc = [d[1:] for d in ds if d.startswith("~")]
            if (inc and exc) or not all(DOMAIN_RE.match(d) for d in inc + exc):
                return None
            extra["if-domain" if inc else "unless-domain"] = ["*" + d for d in (inc or exc)]
        elif o.lstrip("~") in RTYPES:
            (neg if o.startswith("~") else types).add(RTYPES[o.lstrip("~")])
        else:
            return None  # redirect, csp, removeparam, badfilter など
    if neg and not types:
        types = set(ALL_TYPES) - neg
    if types:
        extra["resource-type"] = sorted(types)
    return extra


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
    rest = [d for d in newest if d not in jp_set][:MAX_RULES - len(jp) - 1]
    # 「効いているか試す」用のページ。拡張がオンなら開けない（アプリと審査での確認に使う）
    test = {"trigger": {"url-filter": "^https?://seadice-filters\\.web\\.app/blocked-test/"}, "action": {"type": "block"}}
    return [test] + [block_rule(d) for d in jp + rest], len(domains)


# ---------- 広告・追跡（ABP/AdGuard形式のうち、確実に変換できる行だけ） ----------

# EasyListの章ごとの優先度（小さいほど先に残す）。前半のマイナーな広告配信ドメイン群より、主要な広告・個別サイト向けを優先する
SECTION_PRIORITY = [("third-party adverts", 0), ("specific advert", 1), ("general advert", 1),
                    ("adservers_popup", 4), ("adult", 5), ("adservers", 3)]


def section_priority(header, current):
    h = header.lower()
    for key, pr in SECTION_PRIORITY:
        if key in h:
            return pr
    return current


def parse_abp(texts, cap):
    blocks, allows, generic_css, site_css = [], [], [], {}
    seen = set()
    for text in texts:
        prio = 0
        for raw in text.splitlines():
            line = raw.strip()
            if line.startswith("!"):
                prio = section_priority(line, prio)
                continue
            if not line or line.startswith("["):
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
            opts = opts.split(",") if opts else []
            if exception:
                if set(opts) - {"document", "important"}:
                    continue
                allows.append(domain)
                continue
            extra = convert_opts(opts)
            if extra is None:
                continue
            key = (domain, json.dumps(extra, sort_keys=True))
            if key not in seen:
                seen.add(key)
                blocks.append((domain, extra, prio))

    rules = []
    css_rules = []
    for i in range(0, len(generic_css), 200):  # まとめて1ルールにする（ルール数の節約）
        css_rules.append({"trigger": {"url-filter": ".*"},
                          "action": {"type": "css-display-none", "selector": ", ".join(dict.fromkeys(generic_css[i:i + 200]))}})
    for ds, sels in site_css.items():
        css_rules.append({"trigger": {"url-filter": ".*", "if-domain": ["*" + d for d in ds]},
                          "action": {"type": "css-display-none", "selector": ", ".join(dict.fromkeys(sels))}})
    allow_rules = [allow_rule(d) for d in dict.fromkeys(allows)]
    # 上限を超えるときは、どのサイトでも効く通信ブロックを最優先で残す。
    # 見た目を隠すCSSは全体の2割まで（日本語リストを先に読むので、国内サイト向けが残る）
    css_rules = css_rules[:cap // 5]
    blocks.sort(key=lambda b: b[2])
    room = cap - len(css_rules) - len(allow_rules)
    rules = [block_rule(d, extra) for d, extra, _ in blocks[:room]] + css_rules + allow_rules
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
    hashes = {}
    for name, rules in outputs.items():
        if not rules:
            sys.exit("empty rule list: " + name)
        body = json.dumps(rules, ensure_ascii=False, separators=(",", ":")).encode()
        with open(os.path.join(args.out, name + ".json"), "wb") as f:
            f.write(body)
        counts[name] = len(rules)
        hashes[name] = hashlib.sha256(body).hexdigest()[:16]  # アプリは変わったファイルだけ取り直す
    # QRガード用: 同じ詐欺ドメインを1行1件で（Safari用のJSONより軽い）
    scam_domains = [m.group(1).replace("\\.", ".") for r in outputs["scam"][1:]
                    if (m := re.search(r"\)\?(.+)\[:/\]$", r["trigger"]["url-filter"]))]
    body = ("\n".join(scam_domains) + "\n").encode()
    with open(os.path.join(args.out, "scam-domains.txt"), "wb") as f:
        f.write(body)
    hashes["scamDomains"] = hashlib.sha256(body).hexdigest()[:16]
    with open(os.path.join(args.out, "state", "scam-firstseen.json.gz"), "wb") as f:
        f.write(gzip.compress(json.dumps(firstseen, separators=(",", ":")).encode()))

    meta = {
        "version": datetime.datetime.utcnow().strftime("%Y%m%d%H%M"),
        "updated": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "counts": counts,
        "hashes": hashes,
        "scamSourceTotal": scam_total,
        "sources": {k: [{"name": n, "license": l, "url": u} for n, _, l, u in v] for k, v in SOURCES.items()},
    }
    with open(os.path.join(args.out, "meta.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
