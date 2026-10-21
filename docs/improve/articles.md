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
1. 点検に出ない質問（外部リンク切れ・題名以外の重複）を確かめる方法を、必要が出たときに決める

### ルールの変更履歴
- 2026-10-21: scripts/check_blog.py を新設し docs/writing.md の配線欄に載せた（点検のたびに手書きの検査を書き直していたため。重複は題名の2文字の重なり0.5以上で数える。meta robots の noindex だけを見る、firebase.json の301は切れと数えない、で偽陽性をなくした）。配線欄の古い `firebase deploy` も Actions の記述に直した
- 2026-10-14: docs/writing.md の商品比較記事の節を「商品比較記事はつくらない」に置き換え、「既存の記事を作り直す型」も削除（p/reviews/ を消したため。家電の悩みは一次資料の数字と道具のツールページで答える）
- 2026-10-14: docs/writing.md の「Amazonアソシエイト」を「商品へのリンク」（アフィリエイトなし・通販ボタンなし・一次資料にだけリンク）に置き換え、CLAUDE.md の共通の約束を「広告・アフィリエイトは載せない」に（ユーザーがアフィリエイトをやらないと決めたため）
- 2026-10-14: docs/writing.md に「既存の記事を作り直す型」を追加（道具が欲しい検索語・記事内の道具・一次資料の数字。23件がAIの答えで済む比較だったため、作り直しの手順を毎回同じにする）
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
- p/blog/ で、publisher の `@id` がない記事、tool-cta がない記事、h2 直下が結論でもリストでもない記事の数
- タイトル・本文に過去の年（今年より前）を含み、dateModified が古い記事
- 外部リンク切れ（論文・公的資料。HEAD で 404 のもの）

## すぐ直してよいこと
- publisher の `@id`・BreadcrumbList・dateModified 形式などの構造化データの付け忘れ
- 内部リンク切れの修正、tool-cta の追加（合うツール・アプリが明らかなとき）

## 判断が必要なこと（次にやることに書く）
- 記事の中身の書き換え、記事の統合・削除・noindex

## 次にやること
1. **日誌（daily-YYYY-MM-DD）の扱いを決める**: 6件が sitemap・blog 一覧にある。検索から外す（noindex＋sitemap 除外）か残すかを、Search Console の表示回数を見て判断する（2026-11上旬のCSVと一緒に）

## やったこと
- 2026-10-21: 点検（blog 107。publisher/tool-cta/BreadcrumbList 漏れ0、過去年題名0、sitemapのずれ0、題名の重複候補0、内部リンク切れ0。/tools/link-matta/ は firebase.json の301で bohan へ行くので切れではない）。検査を scripts/check_blog.py にした。次にやることの一番上（日誌の扱い）は Search Console の数字待ちのため据え置き
- 2026-10-18: /about/ を短く書き直し（ユーザー「SEADICEについてのところを改善したい」「すっきり短く」）。冒頭をブランド（AI時代の問題・知る→解決する）に合わせ、表の重複（姿勢と運営の約束）をまとめ、訂正の節を編集方針に統合、メディア12件の説明を1行にそろえて AI時代のテーマから並べる。アプリ数47→48（本数は表の1か所だけに書く）。FAQ は重複の1問を外して5問、JSON-LD・meta・llms.txt 冒頭も同じ言葉に。トップの「4つの特徴」は誠実を先頭にし、古い「1テーマ1アプリ」を「AI時代の問題に」に替える
- 2026-10-14: 商品比較（p/reviews/ 23件と一覧）を削除（ユーザー「比較記事サイトごと消してもいい」）。作り直した電気毛布の1本は、商品比較を外して道具ページ /tools/denki-moufu-denkidai/（電気代の計算）に移し、旧URLは301。ほかの22件と /reviews/ は404。sitemap から24件を外す
- 2026-10-14: アフィリエイトをやめる（ユーザー「アフィリエイトやるつもりない」「価値あるものを作りたい」）。レビュー23件の「Amazonで見る」92個と .buy-link のCSS、/support/ の「Amazon経由のお買い物」とアソシエイトの開示文を削除。/support/ の「アプリの多くはAI（Claude API）を使う」という古い説明も実態に合わせる
- 2026-10-14: レビュー記事の作り直しの1本目。denki-moufu-hikaku を「電気毛布の電気代は1か月いくら？」に変え、電気代の計算（強・適温・弱のプリセットは山善 YMK-F43P 取扱説明書の値）、設定ごとの電気代と表面温度の表、NITE の低温やけどの注意（PSマガジン VOL.493 原文）、出典4件、FAQPage を追加。古い価格に時点を付け、開示文を「AIが仕様を比べた・SEADICEは使っていない」に。中身のない「電気代インパクト」の節は削除
- 2026-10-14: 点検（blog+reviews 121。publisher/tool-cta/BreadcrumbList 漏れ0、noindexなのにsitemap掲載0、sitemap漏れ0、内部リンク切れ1）。jitaku-dumbbell-hikaku の削除済み /apps/fitness-app1/ へのリンク2か所を、実在する /tools/karada-meyasu/（タンパク質の目安）に張り替え、存在しないアプリの機能説明も削除。レビュー23件を一覧化して次にやることに書いた
- 2026-10-14: kosodate の全ページのタイトルを「〜 | AI時代の子育て（SEADICE）」に。名前がよくある言葉のメディアは、設定に titleName を書くと build.py が <title>・og:title の末尾を差し替える（他のメディアでも使える）
- 2026-10-13: 「AI時代の子育て」でGoogle AIモードに聞いてもSEADICEが出ない（同名のYouTubeチャンネルが出る）とユーザーから。広い問いに1ページで答える柱ページ kosodate /ai-era-parenting/ を新設（AIの要約に出る7つの説を記事の出典で判定・わかっている度・FAQPage・道具4つへ。ナビとトップに追加）。足りなかった記事 /child-ai-critical-thinking-fact-check/（AIを疑う力は育てられるか。研究8本）も追加。型: AIの要約で出なかった問い → 要約の説を1つずつ確かめる柱ページ＋足りない記事
- 2026-10-13: AI時代の困りごと（ai.seadice.win）をA案「取扱説明書」のデザインに（白×黒罫線×青、分類に01〜10の番号）。症状と対処の表を新設（/symptoms/ に全件、トップに「よくある症状と対処」6件。番号は分類-分類内の古い順で固定。設定 symptomTable で他メディアにも使える）。3本追加（AI面接の準備・AIが自分について誤情報・AIチャット依存）で69本。注意: mastheadHtml を差し替えるときは末尾に `<!--mastend-->` を入れる（無いと extraNav の入口が消える）
- 2026-10-12: 点検（blog+reviews 116。publisher/tool-cta/BreadcrumbList 漏れ0、過去年タイトル0、sitemap漏れ1）。privacy-pages-noindex-audit を sitemap に追加。削除済み /apps/kateisaien-app*・pet-health-app1,2・koreisha-mimamori-kiki-hikaku へのリンク（記事33本、サイト全体で33ファイル）を /tools/ のハブへ張り替え。残: /apps/fitness-app1/（jitaku-dumbbell-hikaku）は行き先のハブなし
- 2026-10-12: 点検（blog 93・reviews 23。publisher の @id なし 2件、sitemap 漏れ 1件、tool-cta/BreadcrumbList 漏れ 0）。monetization-admob-iap・mobile-ad-networks-2026 に publisher @id を追加、shallow-clone-yesterday-check を sitemap に追加。日誌は 6件（daily-*）、すべて sitemap 掲載・noindex なし
- 2026-10-12: docs/writing.md を目標基準で書き直し（書く前に「AIが補えない部分」と検索語を決める。AIで比べただけのレビューは新規に作らない）
