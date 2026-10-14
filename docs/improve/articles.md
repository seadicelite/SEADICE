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
1. 点検の「同じテーマの重複」を数字で確かめる方法（記事タイトルの語の重なり）を決める

### ルールの変更履歴
- 2026-10-14: docs/writing.md から「h2直下の結論」の良い例のコード例を削除（直前の規則文で足りる）
- 2026-10-14: docs/writing.md「書く前に決めること」の2に、重複の確かめ方を grep の手順として具体化（「確かめる」だけでは手順がなく、再現できないため）
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
2. **既存のレビュー記事23件の扱い**: 2026-10-14 点検で全23件が「AIが通販サイトを比べた4選比較」で、実測・一次データはなし（Amazon へのリンクは計92件。アソシエイトIDつきは mimamori-camera-hikaku の4件だけで、19件はIDなしの商品リンク、3件は商品リンクなし。出典リンク・道具も0件で、価格は2026-07〜09時点のまま。手元の点検で数え直して訂正）。残す／統合する／noindex にするかの判断を、Search Console のCSV（2026-11上旬）で表示回数を見てから manual.md に出す。それまで新規は作らない

## やったこと
- 2026-10-14: 点検（blog+reviews 121。publisher/tool-cta/BreadcrumbList 漏れ0、noindexなのにsitemap掲載0、sitemap漏れ0、内部リンク切れ1）。jitaku-dumbbell-hikaku の削除済み /apps/fitness-app1/ へのリンク2か所を、実在する /tools/karada-meyasu/（タンパク質の目安）に張り替え、存在しないアプリの機能説明も削除。レビュー23件を一覧化して次にやることに書いた
- 2026-10-14: kosodate の全ページのタイトルを「〜 | AI時代の子育て（SEADICE）」に。名前がよくある言葉のメディアは、設定に titleName を書くと build.py が <title>・og:title の末尾を差し替える（他のメディアでも使える）
- 2026-10-13: 「AI時代の子育て」でGoogle AIモードに聞いてもSEADICEが出ない（同名のYouTubeチャンネルが出る）とユーザーから。広い問いに1ページで答える柱ページ kosodate /ai-era-parenting/ を新設（AIの要約に出る7つの説を記事の出典で判定・わかっている度・FAQPage・道具4つへ。ナビとトップに追加）。足りなかった記事 /child-ai-critical-thinking-fact-check/（AIを疑う力は育てられるか。研究8本）も追加。型: AIの要約で出なかった問い → 要約の説を1つずつ確かめる柱ページ＋足りない記事
- 2026-10-13: AI時代の困りごと（ai.seadice.win）をA案「取扱説明書」のデザインに（白×黒罫線×青、分類に01〜10の番号）。症状と対処の表を新設（/symptoms/ に全件、トップに「よくある症状と対処」6件。番号は分類-分類内の古い順で固定。設定 symptomTable で他メディアにも使える）。3本追加（AI面接の準備・AIが自分について誤情報・AIチャット依存）で69本。注意: mastheadHtml を差し替えるときは末尾に `<!--mastend-->` を入れる（無いと extraNav の入口が消える）
- 2026-10-12: 点検（blog+reviews 116。publisher/tool-cta/BreadcrumbList 漏れ0、過去年タイトル0、sitemap漏れ1）。privacy-pages-noindex-audit を sitemap に追加。削除済み /apps/kateisaien-app*・pet-health-app1,2・koreisha-mimamori-kiki-hikaku へのリンク（記事33本、サイト全体で33ファイル）を /tools/ のハブへ張り替え。残: /apps/fitness-app1/（jitaku-dumbbell-hikaku）は行き先のハブなし
- 2026-10-12: 点検（blog 93・reviews 23。publisher の @id なし 2件、sitemap 漏れ 1件、tool-cta/BreadcrumbList 漏れ 0）。monetization-admob-iap・mobile-ad-networks-2026 に publisher @id を追加、shallow-clone-yesterday-check を sitemap に追加。日誌は 6件（daily-*）、すべて sitemap 掲載・noindex なし
- 2026-10-12: docs/writing.md を目標基準で書き直し（書く前に「AIが補えない部分」と検索語を決める。AIで比べただけのレビューは新規に作らない）
