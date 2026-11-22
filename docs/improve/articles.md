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
1. 日誌ルーティン（trig_014vrcLwLafQyxivJUR58zvy）の「既にあるときは網羅していれば何もしない」に、`.sd-stats` の合計と `.sd-bars` の和が両リポジトリの件数（JST）と合うかの確認を足す。11-17〜11-21 の日誌はメディア0件のまま（夜に別のセッションが SEADICE 側だけで書くと、翌朝のルーティンが「ある」として飛ばす）。手元からの書き換えは自動モードで止められたので、ルーティンを直す許可をもらってから
1. 点検の「h2直下が結論でもリストでもない記事」を、h2→h3直続き（11本: shuukaku-sign-yasai・tanemaki-jiki-ichiran・kateisaien-munouyaku-konzoku・kateisaien-6gatsu-nani ほか）の結論文追加から1本ずつ直す。中身の書き換えなので手元で

### ルールの変更履歴
- 2026-11-12: seadice-media docs/quality/article.md に「書く前に、狙う検索語の上位を1回見る」を追加（上位にあって自分にないもの・上位にない一次情報を1つ決める）。順位を取りに行く手順がどこにもなかったため
- 2026-11-11: 点検から「外部リンク切れ（HEAD）」を削った（実行環境から外部サイトに届かず確かめられない。外部リンクは6本のみ）
- 2026-11-11: docs/writing.md のチェックリスト tool-cta に「リンク先は今 p/ にあるページだけ（未公開アプリは張らない）」を追記（canvaskit-13-apps-400mb が未公開の toite の紹介ページ /apps/toite/ に張っていてリンク切れだったため）

- 2026-11-18: docs/writing.md に「h2 直下に h3 を直接置かない」を追記（直続きが11本あり、基準が未記載だったため）

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
1. **デジタル探偵（tantei）の自動投稿で記事が増えない原因を調べる（後回し、2026-11-17 ユーザー判断）**: enabled:true・キュー残6なのに10月から16本にとどまる。10月の原因はルーティン環境のネットワーク制限だった。ルーティンの実行記録を見て、同じ原因か確かめる

## やったこと
- 2026-11-22: 日誌 11月21日を直した。SEADICE 5件だけで書かれていたのを、両リポジトリ29件（本体10・メディア19）に。EVIDENCE は 1573→1593 でなく 1560→1593（7バッチ+33）。メディアの新記事9・事実確認5・見送り2を「やったこと」に足し、トップの #blog に11月21日のカードを足した
- 2026-11-18: 点検（blog 142。publisher/tool-cta/BreadcrumbList 漏れ0、過去年題名0、noindex meta の sitemap 載り0、内部リンク切れ0、check_blog.py 出力なし）。h2直後（410箇所）のうち11箇所が h3 直続き。次にやること3件は日付待ち・Search Console 待ちで進められず。ルールの答え: h2→h3直続きの扱いが未記載だったので writing.md に追記。削ぎ: 実行できない「ルールの次にやること」1（必要が出たら決める）を点検由来の項目に置き換え

古い記録は [log/articles.md](log/articles.md)。
- 2026-11-22: 写真の404を直した（seadice-media 5b5bfaf13e）。全メディアで記事の /img/ 参照と git 上のファイルを照合し、欠けは research 4本・kogei 1本の -sm.webp（PILの無いクラウド実行で jpg のまま保存され、記録だけ webp になっていた）。localize_images.py に欠けたファイルを手元の jpg か remote から作り直す処理を足し、CI（deploy.yml）に Pillow を入れて公開のたびに直るようにした。research の jpg 96本も webp に変換。photo.py は ai-badge の無いテンプレート（neuro）で p.meta の直後に差し込み、差し込めないときは何も変えずに止まるようにした。ルールの答え: 同じ漏れはCIで自動的に直るので手順の追加は不要
- 2026-11-17・22: 心理学系（umbra・hanzai・neuro）に「よく聞く説を確かめたら違った」型で2回×3本ずつ、計18本を公開（ユーザーが楽しんで読む目的）。umbra の見送り済みトピック4件は topicDropped に記録して外し、確かめた候補10件を補充
- 2026-11-16〜17: 記事の少ないメディア3つに3本ずつ追加（tantei 13→16・shinka 31→35〔別の実行の1本を含む〕・kogei 54→57）。どれも公開前に出典を開き直して照合。益子焼の記事の写真が信楽焼と紛らわしい狸だったため、益子焼の鉄釉の皿に差し替えた
- 2026-11-11: 点検（blog 135。publisher/tool-cta/BreadcrumbList 漏れ0、過去年題名0、sitemap OK 556件）。内部リンク切れ1件: canvaskit-13-apps-400mb の tool-cta が未公開アプリの /apps/toite/ に張っていたため、同記事で触れる公開中の /rakuraku/ に差し替え。ルールの答え: 同じ問題（未公開先へのCTA）を防ぐためチェックリストに追記。次にやることの1・2番は Search Console／AIへの質問待ちのため据え置き
- 2026-11-04: 点検（blog 125。publisher/tool-cta/BreadcrumbList 漏れ0、過去年題名0、sitemapのずれ0、内部リンク切れ0、check_blog.py 出力なし）。削ぎ: 古い著作権表示「© 2025 SEADICE」が残る11ファイル（blog 10・apps/chozubora）を 2026 に直した（ほかの580ファイルは2026で、年が混在していたため）。次にやることの1・2番は Search Console／AIへの質問の数字待ちのため据え置き
- 2026-11-03: ai.seadice.win に分野「Web・検索の変化」を追加（AIでWeb自体に起きる変化を、読む人・サイトを持つ人の悩みとして書く）。3本公開（search-results-ai-written-articles・web-article-human-or-ai-how-to-trust・ai-overview-site-traffic-drop）、既存の ai-generated-web-content-share・ai-search-summary-accuracy を移した。目的は悩みの検索語での1位とAI検索の出典
