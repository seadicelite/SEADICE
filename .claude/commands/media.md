---
description: 設定ファイル(media/{slug}.json)に従い、AIメディアの記事を1本以上、調査・執筆・配線まで作る。--draft でPR経由（自動運用向け）
argument-hint: <slug 例: research> [--draft] [トピック]
---

# /media — AIメディア記事エンジン

`$ARGUMENTS` の先頭が `media/{slug}.json` の slug。残りにトピックがあればそれを使う。

**作業リポジトリは `/Users/hidenori/Developer/seadice-media`**（このSEADICEリポジトリから呼ばれた場合も、以下の `media/` `sites/` `.claude/commands/*.md` はすべて seadice-media 側のパス。作業前に `git pull --rebase origin main`）。この手順書は seadice-media 側の `.claude/commands/media.md` と同じ内容に保つ（末尾のホームページ掲載手順だけはSEADICE側の作業）。

## 手順

1. `media/{slug}.json` を読む。無ければ中止して報告。
2. 設定の `rulesFrom` を読み、その「読者」「鉄則（信頼性）」「手順1〜6」を、設定の `name` `path` `url` `categories` `template` に置き換えて **そのまま適用** する（ルールはここに複製しない。修正は rulesFrom 側で一元管理）。あわせて `.claude/commands/quality.md`（全メディア共通の読みやすさ・見た目の基準。ジャンルを問わず適用）も読む。
3. トピックが未指定なら `topicQueue` の先頭から、`path` 配下の既存記事と被らないものを選ぶ。使ったトピックは `topicQueue` から削除して json を保存する。キューが3件以下になったら、既存記事と設定の `concept` から新トピックを10件補充する。
4. 記事を `postsPerRun` 本作る（確認不要）。出典を確認できないトピックは捨てて次へ。
5. 配線と写真（スクリプトで行う。一覧やsitemapを手で編集しない）:
   - `media/{slug}-posts.json` の先頭に `{"slug","category"(設定のcategoriesから),"date","title","summary"(60字前後)}` を1件追加する。
   - **写真は必須（キー不要）。写真なしで公開しない。** 手順・リトライの基準は `quality.md`「画像は必須」を参照。`python3 media/photo.py {slug} {記事slug} "<英語の検索語 2〜4語>"`（検索語は「物・場所・道具」に寄せる。"person" 等の人物語は避ける）。
   - `python3 media/build.py {slug}` で一覧ページとsitemapを再生成する。
6. **公開前の自己検査（人の目が無い前提。1つでも落ちたらその記事は公開せず破棄して次のトピックへ）**:
   - 記事内の全出典URLを WebFetch し直し、記事の数値・主張が出典本文に書かれていることを1件ずつ照合した。
   - 「私たちの研究で」等の一次研究表現、断定・医療行為の助言、絵文字、開発側事情（課金・価格）が無い。
   - 出典が3件未満、または査読論文・メタ分析・レビュー・公的機関のいずれも含まない場合は不合格。
   - 本文800字未満、h2直下の結論欠落、プレースホルダ（`{{`）残りが無い。
   - `quality.md`の基準（余白・カードの構造・1文の長さ・FAQの初期表示）を満たしているか、テンプレートから外れていないか確認する。
   - 既存記事と題材・結論が実質同じでない。
   - 出典の一次ページが開けない（403等）場合は、Europe PMC API（`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{doi}&resultType=core&format=json`）や大学・機関の公式発表など、第二の情報源で確認できた数値だけを使う。確認できなかった数値・主張は記事から削る（検索結果のスニペットだけを根拠にしない）。
7. 公開:
   - 設定の `enabled` が false なら何もせず終了（停止スイッチ）。
   - `publish: "auto"`（既定）: `git pull --rebase origin main` → `sites/{slug}/` `media/` の変更だけを `git add` → commit → `git push origin main`。デプロイは GitHub Actions が自動実行する。`firebase deploy` は使わない。
   - `--draft` 指定時、または `publish: "draft"`: ブランチ `media/{slug}-{YYYYMMDD}` にpushしてPRを作る（公開しない）。
   - 1回の実行で公開する本数は `postsPerRun` を超えない。連続して検査に落ちた場合は3トピックで打ち切る。
8. 報告: 記事URL(またはPR URL)、採用出典、キュー残数。

## 新しいメディアを増やすとき

`media/{新slug}.json` を `research.json` と同じ形で作るだけ。`template` `rulesFrom` は共有してよい（見た目やルールを変えたいときだけ別ファイルにする）。新しいテンプレート(`{新slug}-template.html`)を作る場合は、`quality.md`の余白・カード構造・画像必須のルールを土台にする（ジャンルが変わっても読みやすさの基準は共通）。

公開したら、SEADICEリポジトリのホームページ（`/Users/hidenori/Developer/SEADICE/p/index.html`）の次の3か所にも追加する（メディア一覧はここが正。「もっと見る」リンクは置かずカードだけで並べる）:
- `#media` セクションの `.hub-grid` にカード1枚（`blog-tag` にメディア名、`blog-meta` に1行説明）。グリッドは自動折り返しなので件数が増えてもCSS変更は不要
- フッターのメディアリンク列（`LEDGER` の後ろ、`Webツール` の前）
- JSON-LD の Organization `sameAs` 配列にメディアのURL
- `p/llms.txt` の「## メディア」にも1行追加
