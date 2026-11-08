# 記事（水曜）

## 目的
AIが補えない部分を持つ記事だけが、問いに結論から答えている状態にする。記事は道具（ツール・アプリ）への入口でもある。

## この分野のルール
docs/writing.md

## ルールを良くする（毎回1つ問う）
ページを直すだけでなく、その下にあるルールもユーザーのために良くしていく。
- このルールは、ユーザーの悩みの解決に効いているか（効いていない・古い・足りないルールはないか）
- 今回の点検で見つかった問題は、ルールがなかった・あいまいだったせいではないか（同じ問題が二度出たら、ルールで防ぐ）
- 守る手間がかかるだけで、ユーザーのためになっていないルールはないか

### ルールの次にやること
1. 題名以外の重複を確かめる方法を、必要が出たときに決める（外部リンクは p/blog/ に6本だけで、点検の対象にする意味が薄い。ルーティンの実行環境は外部サイトに届かず HEAD で確かめられない）

### ルールの変更履歴


10月までは [log/articles.md](log/articles.md)。
## 良い状態（docs/writing.md）
- h1直後と各h2直下に結論、数値に出典リンク、末尾に tool-cta
- JSON-LD に BlogPosting（publisher は `"@id":"https://seadice.win/#organization"`）と BreadcrumbList
- タイトルに年を入れた記事は、その年の内容に更新されている
- 同じテーマの記事が本体とメディアで重複していない

## 点検
- p/blog/ で、publisher の `@id` がない記事、tool-cta がない記事、h2 直下が結論でもリストでもない記事の数
- タイトル・本文に過去の年（今年より前）を含み、dateModified が古い記事
- 外部リンク切れ（論文・公的資料。HEAD で 404 のもの）

## すぐ直してよいこと
- publisher の `@id`・BreadcrumbList・dateModified 形式などの構造化データの付け忘れ
- 内部リンク切れの修正、tool-cta の追加（合うツール・アプリが明らかなとき）

## 判断が必要なこと（次にやることに書く）
- 記事の中身の書き換え、記事の統合・削除・noindex

## 次にやること
1. **ai.seadice.win の分野「Web・検索の変化」を続けるか決める（2026-12-31）**: 11-03に3本公開＋既存2本を移した。Search Console でこの5本のクリックが出ているか、月1回のAIへの質問（「検索がAI記事だらけなのはなぜ」「AI要約でブログのアクセスが減った」）で ai.seadice.win が出るかを見る。どちらもなければ増やさない。出ていれば残りのマス（立て直す・起きた/知るの2本目）を埋める
1. **日誌（daily-YYYY-MM-DD）の扱いを決める**: 6件が sitemap・blog 一覧にある。検索から外す（noindex＋sitemap 除外）か残すかを、Search Console の表示回数を見て判断する（2026-11上旬のCSVと一緒に）

## やったこと

10月までは [log/articles.md](log/articles.md)。
- 2026-11-04: 点検（blog 125。publisher/tool-cta/BreadcrumbList 漏れ0、過去年題名0、sitemapのずれ0、内部リンク切れ0、check_blog.py 出力なし）。削ぎ: 古い著作権表示「© 2025 SEADICE」が残る11ファイル（blog 10・apps/chozubora）を 2026 に直した（ほかの580ファイルは2026で、年が混在していたため）。次にやることの1・2番は Search Console／AIへの質問の数字待ちのため据え置き
- 2026-11-03: ai.seadice.win に分野「Web・検索の変化」を追加（AIでWeb自体に起きる変化を、読む人・サイトを持つ人の悩みとして書く）。3本公開（search-results-ai-written-articles・web-article-human-or-ai-how-to-trust・ai-overview-site-traffic-drop）、既存の ai-generated-web-content-share・ai-search-summary-accuracy を移した。目的は悩みの検索語での1位とAI検索の出典
