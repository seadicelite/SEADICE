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
1. メディア（seadice-media）と本体ブログで同じテーマを書かないための確かめ方を具体的な手順にする

### ルールの変更履歴
- 2026-10-12: docs/writing.md に「リンク先は実在するページだけ（/apps/ 個別ページは大半削除済み）」を追加（記事から削除済みアプリページへのリンク切れが33件あったため）
- 2026-10-12: docs/writing.md に日誌の位置づけを追加、「悪い例」を削除（良い例だけで足りるため）

## 良い状態（docs/writing.md）
- h1直後と各h2直下に結論、数値に出典リンク、末尾に tool-cta
- JSON-LD に BlogPosting（publisher は `"@id":"https://seadice.win/#organization"`）と BreadcrumbList
- タイトルに年を入れた記事は、その年の内容に更新されている
- 同じテーマの記事が本体とメディアで重複していない

## 点検
- p/blog/・p/reviews/ で、publisher の `@id` がない記事、tool-cta がない記事、h2 直下が結論でもリストでもない記事の数
- タイトル・本文に過去の年（今年より前）を含み、dateModified が古い記事
- 外部リンク切れ（論文・公的資料。HEAD で 404 のもの）

## すぐ直してよいこと
- publisher の `@id`・BreadcrumbList・dateModified 形式などの構造化データの付け忘れ
- 内部リンク切れの修正、tool-cta の追加（合うツール・アプリが明らかなとき）

## 判断が必要なこと（次にやることに書く）
- 記事の中身の書き換え、記事の統合・削除・noindex、レビュー記事のアフィリエイト

## 次にやること
1. **日誌（daily-YYYY-MM-DD）の扱いを決める**: 6件が sitemap・blog 一覧にある。検索から外す（noindex＋sitemap 除外）か残すかを、Search Console の表示回数を見て判断する（2026-11上旬のCSVと一緒に）
2. **既存のレビュー記事24件を docs/writing.md の新しい条件で点検**: 実際に使った結果・一次データがない記事を一覧にする（直さず報告）

## やったこと
- 2026-10-12: 点検（blog+reviews 116。publisher/tool-cta/BreadcrumbList 漏れ0、過去年タイトル0、sitemap漏れ1）。privacy-pages-noindex-audit を sitemap に追加。削除済み /apps/kateisaien-app*・pet-health-app1,2・koreisha-mimamori-kiki-hikaku へのリンク（記事33本、サイト全体で33ファイル）を /tools/ のハブへ張り替え。残: /apps/fitness-app1/（jitaku-dumbbell-hikaku）は行き先のハブなし
- 2026-10-12: 点検（blog 93・reviews 23。publisher の @id なし 2件、sitemap 漏れ 1件、tool-cta/BreadcrumbList 漏れ 0）。monetization-admob-iap・mobile-ad-networks-2026 に publisher @id を追加、shallow-clone-yesterday-check を sitemap に追加。日誌は 6件（daily-*）、すべて sitemap 掲載・noindex なし
- 2026-10-12: docs/writing.md を目標基準で書き直し（書く前に「AIが補えない部分」と検索語を決める。AIで比べただけのレビューは新規に作らない）
