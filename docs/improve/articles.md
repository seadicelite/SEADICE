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
1. 題名以外の重複を確かめる方法を、必要が出たときに決める

### ルールの変更履歴
- 2026-11-12: seadice-media docs/quality/article.md に「書く前に、狙う検索語の上位を1回見る」を追加（上位にあって自分にないもの・上位にない一次情報を1つ決める）。順位を取りに行く手順がどこにもなかったため
- 2026-11-11: 点検から「外部リンク切れ（HEAD）」を削った（実行環境から外部サイトに届かず確かめられない。外部リンクは6本のみ）
- 2026-11-11: docs/writing.md のチェックリスト tool-cta に「リンク先は今 p/ にあるページだけ（未公開アプリは張らない）」を追記（canvaskit-13-apps-400mb が未公開の toite の紹介ページ /apps/toite/ に張っていてリンク切れだったため）


古い記録は [log/articles.md](log/articles.md)。
- 2026-11-12: 伸ばす4メディアにSEO記事8本（上位が弱い具体的な問いを検索で選び、確かめた表を1つずつ）。kosodate: sns-age-limit-by-service・game-cero-age-rating-follow、oya: parent-hospital-admission-guarantor・parent-care-disability-deduction、ai: gemini-share-link-delete-search・chatgpt-fake-app-how-to-tell、dokugaku: english-2200-hours-fsi-myth・working-adults-study-time-average-statistics。source-check で誤り1（豪州SNS法が施行済み）・ずれ5・未確認6を直してから公開（seadice-media e6934bd2b5）。何を書くかの土台として docs/world/（悩み・欲しいもの・これからの動き・最新の動き）を新設
- 2026-11-12: kosodate が「AI時代の子育て」で上位に出ない件。原因は公開6週・広い言葉で大手と競合・自動執筆が上位を見ずに書いていたこと。日本語の上位が宣伝・会社員向け記事だけの3問を選び、既存記事に確かめた表を足した（ai-age-for-kids: サービス別の利用年齢5社、child-told-ai-name-school-privacy: 入力後の削除・学習オフ・保存期間3社、ai-chatbot-worry-consultation-safety: Common Sense Media の年齢別の勧め＋日本の相談窓口3つ）。source-check で誤り0・ずれ1（Gemini の地域差）を直して公開（seadice-media 48630cfd1b）
## 良い状態（docs/writing.md）
- h1直後と各h2直下に結論、数値に出典リンク、末尾に tool-cta
- JSON-LD に BlogPosting（publisher は `"@id":"https://seadice.win/#organization"`）と BreadcrumbList
- タイトルに年を入れた記事は、その年の内容に更新されている
- 同じテーマの記事が本体とメディアで重複していない

## 点検
- p/blog/ で、publisher の `@id` がない記事、tool-cta がない記事、h2 直下が結論でもリストでもない記事の数
- タイトル・本文に過去の年（今年より前）を含み、dateModified が古い記事

## すぐ直してよいこと
- publisher の `@id`・BreadcrumbList・dateModified 形式などの構造化データの付け忘れ
- 内部リンク切れの修正、tool-cta の追加（合うツール・アプリが明らかなとき）

## 判断が必要なこと（次にやることに書く）
- 記事の中身の書き換え、記事の統合・削除・noindex

## 次にやること
1. **kosodate の強化3本が効いたか見る（2026-12-15ごろ）**: Search Console で「子ども ChatGPT 何歳から」「子ども AI 個人情報 入力」「子ども AI 悩み相談」の順位・クリックと、ChatGPT・Perplexity に同じ問いを聞いて kosodate が引用されるかを見る。効いていれば同じ型（確かめた表）を AI×子どもの他の問いへ広げる
1. **ai.seadice.win の分野「Web・検索の変化」を続けるか決める（2026-12-31）**: 11-03に3本公開＋既存2本を移した。Search Console でこの5本のクリックが出ているか、月1回のAIへの質問（「検索がAI記事だらけなのはなぜ」「AI要約でブログのアクセスが減った」）で ai.seadice.win が出るかを見る。どちらもなければ増やさない。出ていれば残りのマス（立て直す・起きた/知るの2本目）を埋める
1. **日誌（daily-YYYY-MM-DD）の扱いを決める**: 6件が sitemap・blog 一覧にある。検索から外す（noindex＋sitemap 除外）か残すかを、Search Console の表示回数を見て判断する（2026-11上旬のCSVと一緒に）

## やったこと

古い記録は [log/articles.md](log/articles.md)。
- 2026-11-11: 点検（blog 135。publisher/tool-cta/BreadcrumbList 漏れ0、過去年題名0、sitemap OK 556件）。内部リンク切れ1件: canvaskit-13-apps-400mb の tool-cta が未公開アプリの /apps/toite/ に張っていたため、同記事で触れる公開中の /rakuraku/ に差し替え。ルールの答え: 同じ問題（未公開先へのCTA）を防ぐためチェックリストに追記。次にやることの1・2番は Search Console／AIへの質問待ちのため据え置き
- 2026-11-04: 点検（blog 125。publisher/tool-cta/BreadcrumbList 漏れ0、過去年題名0、sitemapのずれ0、内部リンク切れ0、check_blog.py 出力なし）。削ぎ: 古い著作権表示「© 2025 SEADICE」が残る11ファイル（blog 10・apps/chozubora）を 2026 に直した（ほかの580ファイルは2026で、年が混在していたため）。次にやることの1・2番は Search Console／AIへの質問の数字待ちのため据え置き
- 2026-11-03: ai.seadice.win に分野「Web・検索の変化」を追加（AIでWeb自体に起きる変化を、読む人・サイトを持つ人の悩みとして書く）。3本公開（search-results-ai-written-articles・web-article-human-or-ai-how-to-trust・ai-overview-site-traffic-drop）、既存の ai-generated-web-content-share・ai-search-summary-accuracy を移した。目的は悩みの検索語での1位とAI検索の出典
