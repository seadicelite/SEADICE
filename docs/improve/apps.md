# アプリ（金曜）

## 目的
アプリ紹介ページから App Store へ人が行き（ct=seadice）、アプリ自体も目的に沿って良くなっていく状態にする。11月中に Google Play で1本を公開する（11月の目標、2026-11-02）ための材料を出す。アプリは事業の柱なので、売上と課金した人の数（CLAUDE.md の見る数字4）に効くかも見る。

## この分野のルール
docs/flutter-app.md（アプリ本体）、docs/app-publish.md（アプリ紹介ページ・審査通過時の手順）

## ルールを良くする（毎回1つ問う）
ページを直すだけでなく、その下にあるルールもユーザーのために良くしていく。
- このルールは、ユーザーの悩みの解決に効いているか（効いていない・古い・足りないルールはないか）
- 今回の点検で見つかった問題は、ルールがなかった・あいまいだったせいではないか（同じ問題が二度出たら、ルールで防ぐ）
- 守る手間がかかるだけで、ユーザーのためになっていないルールはないか

### ルールの次にやること
2. 「良いアプリの基準」4つで、公開済みアプリを1本ずつ見る手順を /improve-app に足す（手元の作業で。/improve-app はこのリポジトリになく、クラウドからは変えられない。2026-10-30 確認）

### ルールの変更履歴
- 2026-11-27: 点検の「tools にページなし」は p/apps/{id}/ にあるものを含み12件前後出る。「p/tools と p/apps のどちらにもないものだけ直す」と読むこと。このファイルの肥大（43KB）を防ぐため、「やったこと」は直近2週間分だけ残し、古いものは毎回 log/apps.md へ移す
- 2026-11-20: 点検の「公開済みなのに研究欄がない」は毎回38件前後が出て誤読のもとだった（欄は研究があるアプリだけの任意）。「欄がないアプリは数字の記録のみ・直すのは /evidence の候補だけ」に直した
- 2026-11-13: /improve-app（~/.claude/commands/improve-app.md）の「評価ボタンは requestReview() だけ」が flutter-app.md と逆のまま残っていた（nlp-mindshift の改修で発見）。write-review の URL を開く形に直した
- 2026-11-10: 起動画面をユーザーの希望で「地の色の無地＋下にサイコロのマーク＋SEADICE（全アプリ共通の青 #2F7BFF）」に変更。scripts/apply_app_splash.py を作り、新規と改修するアプリで必ず当てる（一斉の再申請はしない）。試しに yofukashi-quest（未公開）に当てた
- 2026-11-10: 起動画面が白いままのアプリが15本あった（flutter_native_splash 未設定）。14本の storyboard を地の色に直し、flutter-app.md「起動画面」に申請前の確認を足した。trade-english-word/appbuild は地の色が不明で未対応
- 2026-11-10: ユーザーの指示「ターゲットを決めて、脳科学マーケでデザイン・色・機能を決める」。全アプリ共通だったダーク固定・アクセント `#00FFD1` をやめ、flutter-app.md に「ターゲット票（TARGET.md）」、neuro.md に「ターゲットから決める」の表を足した。neuro・experience・design 役と /improve-app を票に合わせた
- 2026-11-10: 5.1.2(i)（App Privacy にトラッキングの古い申告が残る）が2回目（LUCK UNLUCK・本音診断）になったので、flutter-app.md の出力ルールに「提出前に App Privacy の取り残しを確かめる・トラッキングは常に空」を足した


古い記録は [log/apps.md](log/apps.md)。
- 2026-11-10: 本音診断 出会いの安全 1.1.0・目指せシャーロックホームズ 1.1.0 の 5.1.2(i) 対応をユーザーが完了（ASC のプライバシー申告を実際の収集に合わせて公開し、却下メッセージに返信）。審査の結果待ち
## 良い状態
- 公開済みアプリ（p/released-apps.json）のページは「App Storeで見る」ボタンつき（`?ct=seadice`）、未公開は noindex
- 公開済みアプリのページに「もとになった研究」欄（EVIDENCEシリーズ）がある
- プライバシーポリシーがあり、アプリ一覧 p/apps/ と食い違いがない

## 点検
- released-apps.json にあるのに、ページが「近日公開」「準備中」のまま・App Store リンクがない（空の cta-box に注意）・ct がないもの
- 「もとになった研究」欄がないアプリ（欄は紐づく研究があるものだけに付ける。ないのが普通なので、件数は数字として記録するだけで、直すのは `/evidence {appId}` で候補に挙がったものだけ）
- p/privacy/{appId}/ がないアプリ、および p/privacy/index.html・アプリページのフッターが指す /privacy/…/ の実在
- 公開済みなのに released-apps.json・アプリページがないアプリ（手元の各アプリの Bundle ID を iTunes Lookup で引く。check_released_apps.py はページのあるアプリしか探さない）。手元でしか見られないのでクラウドの点検では対象外、手元で /improve-app したときに確かめる
- アプリが共有するURL（多くは seadice.win/apps/{appId}/）が200か301で着くか
- 設定画面から届いた要望・不具合（Firestore `feedback`、source が `{appId}` / `{appId}-bug`）を週1回読む。書き込み専用でルーティンからは読めないので、Firebase コンソールで人が見る（manual.md）。不具合はそのアプリの次にやることの先頭へ（2026-10-27）

## すぐ直してよいこと
- ct の付け忘れ、App Store リンクの追加（released-apps.json に ID があるもの）、プライバシーへのリンク切れ

## 判断が必要なこと（次にやることに書く）
- アプリ本体の改善（アプリは別フォルダ ~/Developer/{ジャンル}系/ にあり、クラウドからは変更できない。改善案を書き、手元で /improve-app する）
- アプリページの削除・統合

## 次にやること

1. **LIFE is RPG ドット調版（1.2.0予定）をリリースするとき**（2026-11-12 critic 役）: ①p/privacy/lifeisrpg/ の「Google Fonts を読み込む」を消す（書体は同梱にした）②Web版 p/lifeisrpg/ を作り直すか決める（作り直すと DotGothic16＋NotoSansJP で重い。作らないならアプリと見た目がずれる）③シミュで動かしたので ipa 前に flutter clean
1. **スーパーの野菜の目利き（写真で「どちらが新鮮？」）は新規アプリにしない**（2026-11-12 market・business・appstore-review・brand）: 野菜まるごと検定と同じ型で 4.3 の見込み高、払う人も見当たらない（同分野は評価0〜2件）。順番は ①サイトに10品目の read ページ（自分で買って0・3・7日目に同条件で撮った写真＋出典＋5問）②Search Console と ct=seadice の数字が出たら、1.2.3 提出後の野菜まるごと検定に「スーパーで選ぶ」モードと季節パック（買い切り160円／全部480円、サブスクにしない）。名前は「新鮮」に絞り「美味しい・甘い」は言い切らない。見分け方は 鮮度（出典あり）／美味しさ（品目ごとに確認）／経験則（未確認と書く）の3段で、既存の「新鮮な野菜の選び方」カテゴリにも出典を付け source-check に通す。（README は直した）。同日、ユーザーの方針で買う人（内部の票では主婦）向けに育てると決め、設計は yasai_kentei/TARGET.md・DESIGN.md。順番: 1.2.3 提出 → 1.3.0（売り場カード・選ぶ/覚える/設定・ライト固定・ウィジェット。名前は変えない）→ 数字を見て名前・課金
1. **いきみチェックの Apple Watch 版は、最初の100人の声を見てから**（2026-11-11 platform 役）: レビュー・要望に「画面を点けたままがつらい」「ウォッチで」が出たら着手。設計は ~/Developer/女性の健康系/pelvic_guide/DESIGN.md「端末・面」
1. **設定の「App Storeで評価する」が `requestReview()` を呼んでいるアプリを直す**（2026-11-11 neuro 役）: Apple の規定でボタンからは呼ばない（押しても何も起きないことがある）。`grep -rn "requestReview" ~/Developer --include=*.dart` で設定のボタンを探し、write-review の URL（`https://apps.apple.com/app/id{ID}?action=write-review`）に変える。改修のついでに、広める・評価してもらう仕組みの4つもそろえる
1. **docs/neuro.md に「レビューの頼み方」の行を足す**（2026-11-11 neuro 役）: Burtch ほか 2018（見返りで件数は増えるが短くなる）・Rains 2013（反発のメタ分析）・Hu ほか 2009（J字型の分布）を source-check に通してから
1. **提出文の見出し「【安心して使える】」を事実の見出しに直す**（2026-11-11 brand 役）: kiroku-nou-training・attachment_style・body_language_scan・yosegaki_maker・saiencer の APPSTORE_SUBMISSION.md。CLAUDE.md の「安心・安全は掲げない、行動で示す」に反する。次のアップデートのついでに「登録なし・端末の中だけ」などへ
1. **女性の健康の分野を広げるのは、いきみチェックの最初の100人の反応を見てから**（2026-11-11 brand 役）: レビューと要望（週1で読む）を見て、悩み→メディア→アプリの順でメディア（記事・印刷シート）を先に考える
1. **恋のしぐさノート 1.2.0 が審査を通ったら**（2026-11-11）: p/tools/body-language-scan/ の名前・説明を恋愛中心に、released-apps.json の名前。その後に「同じ練習10問を友だちに送るリンク」（seadice.win の静的ページ、作る前に security・critic）とウィジェット（小1種「次に見ること」、名前を出さない）、1.3 で課金（パック・記録の無制限）

1. **テス活ログ 1.1.0 が審査を通ったら、サイトの紹介ページを直す**（2026-11-10）: p/tools/tesukatsu-log/ の description・本文の「AIが次の一歩を提案」「増やす」を、ふりかえり・次の一歩・端末の中だけ・研究でわかっていること、に。released-apps.json の名前「テス活」も App Store の名前と合わせるか確かめる
- LUCK UNLUCK のウィジェットは 2026-11-06 に widget 役が 1.0(2) に実装済み（ホーム中・小、ロック画面の円形、Control）。残り: 実機での配置確認、課金を入れるときに大（棚）。拡張機能の版は pbxproj に固定なので、版を上げるたびに LuckWidget の MARKETING_VERSION・CURRENT_PROJECT_VERSION も合わせる
- 公開中なのにサイトに載っていないアプリを見つける点検を作る: 各アプリのフォルダの Bundle ID（ios/Runner.xcodeproj の PRODUCT_BUNDLE_IDENTIFIER）を集めて iTunes Lookup に当て、released-apps.json にないものを出す。`check_released_apps.py` は nlp-lab を拾えなかった（11-05 のニートクエスト100・11-06 のNLPラボで同じ問題が2回）
1. **check_all_apps.py の結果を直す**（2026-11-11 初回）: サイトに載っていない公開中アプリ3本（IJIN の紹介ページ /tools/tetsujin-friends/、hiragana-japanese と ピラミッド型タスク管理 が released-apps.json にない）、released-apps.json にあるが App Store にない4本（danshari-app3・mood-forecast・procrastination-type・yumetoki）。登録を外す・ページを足すのは公開範囲なのでユーザーに確かめてから
1. **独学スケジュールメーカー 1.1.0 が審査を通ったら、サイトとメディアからAIの表記を外す**（2026-11-05）: p/tools/dokugaku-schedule/（description・og・JSON-LD・ラベル「AI Planning」・リード・特徴「AIが計画を組む」）を、目次の撮影は端末内で読み取り・章の数や貼り付けでも作れる・休む曜日と調整日・残りを組み直す、に。サポートURL（/apps/dokugaku-schedule/ はこのページへ飛ぶ）なので審査員も見る。p/apps/index.html（build_apps_page.py）と dokugaku.seadice.win/apps/dokugaku-schedule/ と記事6本の紹介文も。プライバシーポリシーは版ごとの書き方にしたので触らなくてよい
1. **心配の答え合わせ（worry-check）が審査を通ったら**（2026-10-20）: check_released_apps.py → build_apps_page.py（noindex が外れる）、p/sitemap.xml に /tools/worry-check/ と /privacy/worry-check/、p/llms.txt に1行、p/tools/worry-check/ の「近日公開」を「App Storeで見る」（?ct=seadice）に。悩みの科学（seadice-media の media/research.json の apps）に1件足し、research.seadice.win/apps/worry-check/ を作る（アプリの設定画面はこのページが200を返すときだけリンクを出す作り）。記事は stop-ruminating-after-bad-day-research に付ける。EVIDENCE に LaFreniere & Newman 2020・Schwob & Newman 2026 を /evidence-topics で足してから `/evidence worry-check`
- （保留中: 2026-10-20 に 4.3(a) で却下され放置。再開するときだけ）無事ボタン（buji-button）が審査を通ったら、メディア側の相互送客を設定する: `seadice-media/media/oya.json` の `apps` に1件（id buji-button / name 無事ボタン / appStoreId / icon /img/apps/buji-button.webp（128px）/ articles: parent-living-alone-found-late, parent-living-apart-call-visit-frequency, parent-living-alone-isolation-health / theme: 離れて暮らす親の見守り・孤立の記事だけ。認知症・運転・介護費用には付けない）→ `python3 media/build.py oya`。BOHAN にも同じく `media/bohan.json` の `apps` に1件（articles: disaster-evacuation-crime-myth-research / theme: 災害の後・避難の記事だけ）→ `python3 media/build.py bohan`。アプリは oya・bohan の /apps/buji-button/ がそれぞれ200を返したときだけリンクを出す作りなので、ページができれば再申請なしでリンクが出る（2026-10-17。審査前に作らなかったのは、oya に別作業の未コミット変更があったため）
1. **通知de人生改善の保留テーマ**（2026-10-14）: 笑う・40秒の休憩・朝の光・つながる・思い出す・ふれる。研究が1本だけか、届くと嬉しいが弱い。EVIDENCE にメタ分析か複数の比較試験を足せたら（/evidence-topics）、テーマに入れる。「思い出す」「お風呂」の時間を決めた通知はもう作れる
1. **通知de人生改善 1.1.0 が審査を通ったら、サイトを新しい名前と中身に合わせる**（2026-10-14）: p/tools/notify-mindfulness/ の見出し・説明・FAQ・JSON-LD を「7テーマ（呼吸・姿勢・目標・感謝と親切・好きな曲・未来の自分・1分の筋トレ）、どれも届いたらすぐできる、テーマごとに届く時刻、通知から始めるまでの時間の記録」に、p/privacy/notify-mindfulness/ に記録（気分・目標と1歩・ありがとう帳・未来ノート、端末内のみ）を、released-apps.json・アプリ一覧・llms.txt の名前を「通知de人生改善」に。EVIDENCE の practice.json で「姿勢と自信」をアプリにも向けるか（今は /tools/shisei-reset/）を決める。「もとになった研究」欄は `/evidence notify-mindfulness`（アプリの研究タブと同じ assets/research.json の研究から）。アイコンは1.1.0で「ベルから芽・上向きの矢印」（元絵 ~/Developer/Images/jinsei.png）に変えたので、サイトのアイコン（p/icons/apps/ の notify-mindfulness）も build_apps_page で取り直すか、元絵から作り直す。/tools/shisei-reset/ からこのアプリへ案内する
1. **HSPナビ 1.1.0 が審査を通ったら、サイトとメディアからAIの表記を外す**（2026-10-14）: p/tools/hsp-relationship-check/ の title・description・og・JSON-LD・ラベル「Relationship AI」・説明文・特徴02（AIがHSP視点で分析→気持ちの整理）・特徴05（AI相談は1日3回→通信なし）、p/apps/index.html の説明（build_apps_page.py で作り直し）、seadice-media の media/research.json の HSPナビの catch（「人間関係の悩みのAI相談」→「タップで気持ちの整理」）。プライバシーポリシーは版ごとの書き方にしてあるので触らなくてよい
1. **AIに文章を送る公開済みアプリ66本は、改修のついでに1本ずつAIを外す**（2026-10-14、ユーザー判断。一括ではやらない）: 方針は「まずAPIなしで利用者を増やす」。AIの機能は通信なしの道具に置き換える（見本: HSPナビ 1.1.0 の「気持ちの整理」）。外したら同じ作業でプライバシーポリシー（版ごとの書き方）・提出文書・審査通過後にサイトとメディアの紹介文も直す。残り: `grep -rl claude-proxy ~/Developer --include=main.dart | grep -v /build/`
1. **IJIN（旧 哲人フレンド）1.2.0 が審査を通ったら、名前をサイトとメディアでそろえる**（2026-10-17）: p/released-apps.json（check_released_apps.py が拾う）→ build_apps_page.py、p/privacy/tetsujin-friends/ と p/privacy/index.html、seadice-media の media/tetsugaku.json の apps[].name と .claude/commands/tetsugaku.md → build.py tetsugaku（seadice-media は他の作業の未コミット変更があるので自分のファイルだけコミット）。URL・Bundle ID は tetsujin-friends のまま。アイコンも新しくなる（~/Developer/Images/ijin.png）ので、メディアの sites/tetsugaku/img/apps/tetsujin-friends.webp（128px）とアプリ一覧のアイコンも差し替える
1. **夢とき（yumetoki）の日付キーを2桁にそろえる**（2026-10-14）: `${now.year}${now.month}${now.day}` のままで、1月11日と11月1日が同じキーになる。次の改修のついでに（古いキーの掃除も一緒に）。MBTIコンパスは 1.1.0 で回数制限ごと消えた
1. **推理ノート（holmes-deduction）1.1.0 が審査を通ったら、サイトのアプリページからAIの表記を外す**（2026-11-08）: 1.1.0 で Claude API を撤去し、通信なしの「今日の事件」30件（手がかり→4択→自信3段→決め手当て、1日1件解放、neuro 役の設計）と「推理ノート」（見たこと→説明2つ以上→確かめ方→あとで答え合わせ）に置き換えた。p/tools/holmes-deduction/ の description・og・JSON-LD・リード・特徴01/02・注記（「AI採点」）を新しい中身に、build_apps_page.py で一覧の説明も。プライバシーポリシーは版ごとの書き方にしたので触らなくてよい。事件は30件なので、遊ばれていれば足す（lib/cases.dart）。英語の掲載（名前・説明に「AI」が残る）と英語の画面は後回し（2026-11-08 ユーザー判断）。書き直し案は holmes-deduction/APPSTORE_SUBMISSION_EN.md
1. **MBTIコンパス 1.1.0 が審査を通ったら、サイトのアプリページからAIの表記を外す**（2026-11-06）: 1.1.0 で Claude API を撤去し、相性の解説を4軸から端末内で組み立てる形に（課金は入れない、ユーザー判断）。p/tools/mbti-compass/ の description・リード・特徴「AIによる解説」を「どの軸が近いか・場面ごとの解説・通信なしで何度でも・相性を送れる」に、JSON-LD と FAQ（なければ足す）も。EVIDENCE の MBTI 記事（/evidence/personality/personality-mbti-types/）へのリンクを置き、「測定」の言い方をやめる。build_apps_page.py で一覧の説明も。プライバシーポリシーは版ごとの書き方にしたので触らなくてよい。残り: アプリ名の「性格診断」を変えるか（ユーザー判断）
1. **HSPナビ 1.1.0 が審査を通ったら、EVIDENCEシリーズに入れるか決める**（2026-10-14）: 悩みの科学のHSPの記事ができたので `/evidence hsp-relationship-check` で「もとになった研究」欄を作れる。ただしセルフチェックは自作の質問なので、欄に書けるのは「3つの面の分け方は髙橋（2016）にならった」までで、尺度そのものを研究にもとづくとは書かない。HSP-J10 の許諾が取れて差し替えた後のほうが筋がよい
1. **HSPナビ: 作者の許諾が届いたら、セルフチェックを HSP-J10 に差し替える**（2026-10-14）: 10問・7件法・平均点、日本の成人1,626人の平均 4.24（SD 0.96）とくらべる位置と3つの面の点を出す。3群の区切り（HSP-J10）は論文で未確認なので使わない。依頼文は ~/Developer/心理学系/hsp-relationship-check/PERMISSION_REQUEST.md。許諾がとれたらサイトの /diagnosis/ にも同じチェックを置く（「HSP 診断」は悩みの検索語として大きい）
1. **愛着スタイル診断 1.1.0 が審査を通ったら、サイトのアプリページを中身に合わせる**（2026-10-13）: p/tools/attachment-style/ の「16問・5段階」「AIが結果を解説」「AI相談」「AI解説・AI相談を使うと…送られます」を、ECR-RS 日本語版9問・相手を選ぶ・日本の成人の平均とくらべる・端末内で完結（AIなし）に書き換え、JSON-LD の説明も直す。「もとになった研究」欄は `/evidence attachment-style`（古村2016・Fraley2011/2015・Bretaña2022。アプリの「学ぶ」タブと同じ）で EVIDENCE シリーズへ。p/llms.txt に1行あれば同じく直す
1. **コードが見つからないアプリのプライバシーポリシー171件を整理する**（2026-10-13、判断が必要）: AdMob や Claude API の記載があるのに、~/Developer にそのアプリのコード（_appId が一致するもの）がない。多くは未公開・削除済みのアプリと思われる。p/released-apps.json と App Store の公開状況を照らし、公開していないものは削除（410）か noindex か決める。公開中なのにコードがないものは、ストアの App Privacy と食い違っていないか確かめる
1. **プライバシーポリシーに任意のフィードバック送信（Firebase）が書かれていないアプリが多い**（2026-10-13）: ほぼ全アプリが設定画面から Firestore に文章を送るが、多くのポリシーは「端末内にのみ保存」としか書いていない。愛着スタイル診断・好奇心診断などで使った「2. 送信する情報」の段落を、コードに _feedbackUrl があるアプリへ足す
1. **Life's RPG 2.0（保留・優先度低。ユーザーの関心が薄い、2026-10-13）**: 11月の ct=seadice の数字で、作り直すか公開をやめるかを決めるまで手を付けない。検討した案: ユーザー本人も「使いにくい」。まずシンプルなタスクアプリとして使いやすいことが先。案＝自分で決める「大ボス」（大きな目標。HP＝何日ぶん勝てば倒せるか）＋毎日のピラミッド（大1・中3・小5の9枠まで、てっぺん＝今日のボス。倒すと大ボスに1ダメージ、全部済ませなくてもボスを倒せば勝ち）＋「毎日」くり返し（小の枠）。下メニューは「きょう」「きろく」。外すもの＝目標・クエスト・デイリー・NOT TO DO・体調管理・コイン・ショップ・能力・フロア・BGM（レベル・XPは引き継ぐ）。さわれる試作: https://claude.ai/artifact/Ft9ySMGuq7vtvctkHZELem 。1.1.2（寄付リンク削除）は先に申請してよい
1. **やめラボ 1.1.0 が審査を通ったら、サイトのページを作り替えに合わせる**: 1.1.0 で「10の対象から選ぶ」から「やめたいことを自分の言葉で書く」アプリに変わった。p/tools/yame-lab/ の見出し・説明・stat（「10の対象」→「何でも書ける」）・FAQ・JSON-LD、p/llms.txt の1行を「やめたいことを書く → やめる／まず減らすを選ぶ → 対処法を1つ試す → 記録 → 1週間ごとのふりかえりでやり方を変える」に書き換え、1.1.0 で増えた機能（「衝動が来た」タイマー、代わりにすること・「もし〜なら」・効いた置き換え、量のグラフと減らせた量、自分のパターン、昨日以前の記録、やめたい理由、CSVの書き出し、参考にした論文10本の画面）を足す。「もとになった研究」の1件目の機能名を「対処法『衝動サーフィン』」から「衝動が来たのタイマー」に、置き換えの研究（Moritz 2022 など、アプリの論文画面と同じ文）を1件足す（2026-10-13）
1. **ビッグファイブ診断 1.1.0 が審査を通ったら、サイトのアプリページを中身に合わせる**: p/tools/honshitsu-type/ の「20問」「情緒安定性」「誠実性」「AIが本質タイプを生成」を、TIPI-J 10問・年代別の平均とくらべる・AIは任意、に書き換え、「もとになった研究」欄（小塩2012・川本2015・Roberts2006/2017・Soto2019、アプリの「研究」タブと同じ5件）を足して EVIDENCE シリーズへ。/diagnosis/bigfive-tipi/ と相互リンク。App Store Connect のサポートURLが寄付ページ（/support/）なので /about/ に変える（2026-10-13）
1. **エニアグラム 1.1.0 が審査を通ったら、サイトのAI表記を外す**: p/tools/enneagram/（タイトル「〜AI」・説明・FAQ「Claude API に送信」・特徴の「AIが解説」）と p/privacy/enneagram/（Claude API への送信）を、通信なし・要望フォームだけ送信、に書き換える。p/released-apps.json の名前も。公開中の 1.0.2 はまだ API を使うので、それまでは触らない（2026-10-13）
1. **EVIDENCE のデータを neuro 役の案に合わせる（ユーザー判断待ち、2026-11-06）**: ①1枚目の段階名「結論」なのに疑問文の516枚のラベルを直す（段階名は問い・調べたこと・わかったこと・まだわからないことの4つへ寄せる）②1枚目が断定文の説（例「雨の日はみんな気分が沈む」）約27件を「？」付きの問いに（ウィジェット・通知で説だけがくり返し目に入ると本当らしく感じる錯覚を避ける）③クイズのない575件に q・correct・wrong を足す（思い出す練習に出せるのは今555件だけ）。どれも p/apps/evidence/data/topics.json の書き換えで、evidence.md の「既存トピックの結論の書き換え」に当たるので先に確認する
1. **EVIDENCE の稼ぎ方を、中身でなく機能で考える**（2026-11-06）: 1.5.0 のパック課金はやめて全トピック無料に戻した。課金を入れるなら、続けて使う人向けの機能（着せ替えの追加・ウィジェットの種類・復習クイズの記録など）にするかを、次の版の前に `business` で見る。撤去したコードの控えは evidence/drafts/billing-1.5.0/（購入・復元の部分は流用できる）。p/apps/evidence/data/access.json は公開中のアプリが読まないので、方針が決まったら消してよい
1. **ほかの公開済みアプリにも寄付ページ（seadice.win/support/）へのリンクが残っている**（2026-10-13 に判明、~/Developer 配下の72本の lib/main.dart。`grep -rl "seadice.win/support" --include='*.dart' ~/Developer | grep -v /build/`）。審査 3.1.1 の却下例があるので、各アプリを次に改修するときに必ず外す（docs/flutter-app.md の決まり）。Life's RPG は 1.1.2 で済み。改修のついでに share_plus 11 の新APIと Deployment Target 15.0（Podfile の post_install も）も確かめる
2. **カスタマイズを他のアプリにも**: ユーザーは「デザイン・カラー・機能のオン/オフを自分で変えられるアプリ」を強く好む（2026-10-13）。EVIDENCE の lib/customize.dart を型にして、次に改修する公開済みアプリから入れる
3. **Google Play 候補の判断材料**: 公開済みアプリごとに、App Store アナリティクスの ct=seadice の数字を記録する表を作る（数字はユーザーから受け取る）
4. **p/tools/tetsujin-chat/ を削除して 301 にする（判断が必要、manual.md に記載）**（2026-10-16 点検）: 同じアプリ（哲人フレンド、released-apps.json の tetsujin-friends）の旧ページで、noindex・「準備中」のまま・App Store リンクなし・sitemap と他ページからのリンクなし。公開側の /tools/tetsujin-friends/ と /apps/tetsujin-friends/ はすでに tetsugaku.seadice.win へ rewrite 済み
5. **公開済みアプリで「もとになった研究」欄がないもの（40件）を一覧にし、/evidence で足せるものから足す**

## やったこと
- 2026-11-27: 点検（金曜）。released-apps.json 51件のうち、tools にページなしは12件（11件は p/apps/{id}/ にあり、tetsujin-friends は既知）。ページのあるもの39件は App Store リンク・ct=seadice あり・「近日公開」なし・noindex なし・privacy 51件あり。p/tools・privacy・apps の href="/…" 切れ0（p/privacy/link-matta の /tools/link-matta/ は firebase.json の301で bohan.seadice.win へ行くので正常）、sitemap 574件に meta noindex・ファイルなし0。削いだもの: このファイルの「やったこと」のうち11-10・11-11の14行（約10KB、記録は log/apps.md へ）。
- 2026-11-22: ひる10（hiru10、ストア1.0・無料・評価0件）を 1.0.1+3 に改修（未提出）。共有リンクとサポートURLの seadice.win/apps/hiru10/ が公開から7週間404だった→firebase.json に /tools/hiru10/ への301を足して本番で確認、アプリの共有文は App Store のURLに変えた（サイトの道筋が変わっても切れない）。ほかに、評価ボタンを write-review のURLに、関連アプリを先頭3本から近い用途の3本に、ウェルカムダイアログを外して起動してすぐ昼寝タブに、アップデートのお知らせ、眠気がやわらいだ昼寝のあとに生涯1回の「身近な人にも教える」、起動画面の差し替え。プライバシーポリシーにバージョン確認と関連アプリの読み込みを追記。提出資料の「買い切り」は実際は無料だったので直した（nlp-mindshift に続いて2本目）
- 2026-11-13: 点検（金曜）。released-apps.json 50件のうち、ページなしは tetsujin-friends のみ（既知）。ページのある49件は App Store リンクあり・ct=seadice あり・「近日公開」なし・noindex なし。プライバシー p/privacy/{id}/ は50件すべてあり、p/privacy/index.html のリンク切れ0、アプリページの href="/…" の p/ にないもの0、sitemap 558件でファイルなし0・noindex 実体0。進めた作業なし: 次にやることの先頭3件は「審査通過・リリース時」「新規は作らない」「ユーザーの確認待ち」で、クラウドからは動かせない
- 2026-11-13: NLPで自分を書き換える３０日（nlp-mindshift、ストア1.0・評価0件）を「NLPで人生改善を試す30日」1.1.0+2 に作り替え（未提出）。ユーザー判断「4.3（NLPアプリ3本）は気にしない・NLPで人生改善アプリにする」。AI・寄付リンク・連続日数を外し、毎日の流れを「30秒やってみる→役立ち度1タップ→メモは任意」に。30日を研究の強さで並べ替え（近い研究あり／研究はまだ少ない／ふり返りの日）、研究と限界の画面（source-check で10件、ずれ3か所を直した）、手札・今日の1枚・書き出し・毎日のお知らせ・1.0の記録の移行。TARGET.md を新設しアクセントを金1色に（NLPラボの紫と分ける）。点検役は user×4・design・experience・neuro・brand・appstore-review×2・source-check・device-check。ストア説明が「買い切り」なのに実際は無料だった食い違いも直した
- 2026-11-20: 点検（金曜）。released-apps.json 51件のうち、tools にページなしは9件（p/apps/ 側にあるもの。既知）。ページのあるもの42件は App Store リンク・ct=seadice あり・「近日公開」なし・noindex なし・privacy あり。研究欄なし38件（任意のため正常）。p/tools・privacy・apps 内の内部リンク切れ0、sitemap 565件でファイルなし0・noindex 0（blog 5件は本文にその語があるだけの誤検出）。削った: 本ファイルの 2026-11-10 より前の「やったこと」16件を log/apps.md へ移し 67KB→41KB。「次にやること」の先頭はどれも審査通過待ち・手元作業（~/Developer）で進められず

古い記録は [log/apps.md](log/apps.md)。
