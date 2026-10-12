# CLAUDE.md

SEADICE（シーダイス）のリポジトリ。中身は **seadice.win の静的サイト（`p/`）** と、その運用スクリプト。iOSアプリ（Flutter）は各アプリのフォルダで作り、規則だけをここに置いている。

## どの規則がどこにあるか

| 作業 | 読むもの |
|---|---|
| サイト（`p/`）のページを作る・直す | このファイル ＋ [design/README.md](design/README.md)（3タイプのデザイン・これからの設計） |
| ブログ・レビュー記事を書く | [docs/writing.md](docs/writing.md) |
| Flutterアプリを作る・改修する・申請する | [docs/flutter-app.md](docs/flutter-app.md)（設定画面・広告なし・利用回数・オンボーディング・フォント・Deployment Target など） |
| アプリをサイトに載せる・審査通過時の更新 | このファイルの「アプリをサイトに載せるとき」 |

全作業に共通する約束: **絵文字禁止**（末尾）、**広告は載せない**、**登録・個人情報の収集はしない**、「科学的に証明された」と書かない（[7ヶ条](p/promise/index.html)）。

## コマンドと運用

```bash
firebase deploy --only hosting   # p/ をそのまま配信（ビルド不要、functions の警告を避けるため hosting のみ）
python3 scripts/apply_page_type.py {read|show|use} p/…/index.html   # 新しいページにデザインを当てる
python3 scripts/apply_page_type.py --refresh                         # design/ を直した後に全ページへ反映
python3 scripts/check_released_apps.py && python3 scripts/build_apps_page.py   # 審査通過時のアプリ一覧更新
```

- `firebase.json` の `public` は `"p"`。静的ディレクトリは `index.html` を置けば配信される（rewrite 不要。全体を `/index.html` に飛ばす rewrite はソフト404になるので入れない）
- **main は手元とクラウドの2か所から更新される**。作業前に `git pull`、手元でデプロイしたら必ず push する（push しないと Actions のデプロイで本番が巻き戻る）。作業ツリーに他の作業の未コミット変更があるときは、自分の変更だけコミットし、きれいな worktree からデプロイする
- 個別の Flutter Web アプリ（`toite`, `rakuraku`, `boueki-hub/*` など）は各アプリ側で `flutter build web --release` して `p/該当ディレクトリ/` に置く

## サイトの構成（seadice.win）

- トップページ: `p/index.html`（**頼まれない限り触らない**。デザイン注入の対象外）
- アプリ紹介: `p/tools/{appId}/`（`p/apps/` はアプリ一覧 `p/apps/index.html` と一部の旧ページ）／ブラウザツール: `p/tools/{toolId}/` ほか
- ジャンル別ハブ: `p/tools/{ジャンル}/` ／ 診断: `p/diagnosis/` ／ EVIDENCE: `p/evidence-series/`
- ブログ: `p/blog/` ／ 商品比較: `p/reviews/` ／ プライバシー: `p/privacy/{appId}/` ／ 運営者情報: `p/about/` ／ 7ヶ条: `p/promise/` ／ 寄付: `p/support/`（アプリからはリンクしない）
- 公開済みアプリ一覧（関連アプリ選定の唯一の正）: `p/released-apps.json`
- AI向けの案内: `p/llms.txt` ／ 404: `p/404.html`

# サイト（p/）の作り方

## ページの3タイプとデザイン（質実剛健、2026-10-12〜）

`p/` 配下のページは「読ませる / 魅せる / 使う」のどれかに分け、デザインは [design/](design/) の `base.css` + `{read,show,use}.css` で一元管理する。テーマは**質実剛健**（グラデーション・ぼかし・光・影なし、角丸は8px以下、アクセント色は要所だけ）。

| タイプ | 対象 | 形 |
|---|---|---|
| read（読ませる） | ブログ記事・レビュー記事・プライバシー | 本文幅660px（約38字）の1段、本文16→17px・行間1.95、h2は左の縦線 |
| show（魅せる） | アプリ紹介・各種一覧・EVIDENCE | 幅1080px、大見出し、カード1→2→3列、PCは見出し左/中身右の2段 |
| use（使う） | ブラウザツール・診断 | 見出し小さめ、操作部は `.sd-tool` の1枚パネル、入力48px以上。PCは説明左/道具右に固定 |

- ブレークポイントは **600px / 960px** の2つだけ。左右余白は `--sd-g`（16/24/32px）
- **ページを新しく作ったら必ず** `python3 scripts/apply_page_type.py {read|show|use} p/…/index.html` を実行する（`<head>` 末尾にインラインCSSを差し込み、`<body class="t-…">` を付ける。外部CSSは使わない）。ツールは操作パネルの要素に `sd-tool` クラスを付けてから実行する
- デザインを直すときは `design/*.css` を編集し、`python3 scripts/apply_page_type.py --refresh` で適用済みの全ページに反映する（`p/index.html` のトップページと Flutter SPA は対象外）
- `build_apps_page.py` / `build_evidence_page.py` は書き出し時に自動で show を差し込む

## サイト設計の12項目（p/ 配下のページを作る・直すときに毎回確認する、2026-09-30〜）

1. **SEO**: 固有のtitle/description/canonical、h1は1つ、sitemap・内部リンクを更新
2. **AIO/AEO**: 質問に結論から答える文、主語に「SEADICE」等の固有名、JSON-LD（FAQPage等）、`p/llms.txt`を最新に保つ
3. **モバイル操作**: 本文14px以上・補助テキストも12px未満にしない、タップ領域は上下8px以上の余白、フォームは最小項目
4. **パフォーマンス**: WebPは表示サイズの2倍までに縮小、JS最小、width/height指定、ファーストビュー画像はpreload
5. **アクセシビリティ**: 文字色は背景とコントラスト4.5:1以上（`--muted`は`#7c8aa0`）、色だけで状態を伝えない、キーボード操作・focus表示、装飾画像は`alt=""`
6. **情報設計**: 重要ページへ少ない操作で到達、パンくず（下層ページ）、関連ページ同士をつなぐ
7. **セキュリティ・プライバシー**: HTTPS、フォームで個人情報を集めない（匿名フォームにはその旨を明記）
8. **CVR**: ボタンは「送る」でなく「要望を送る」のように具体的な文言、不安要素（返信の有無・無料かどうか）を先に書く
9. **計測**: 外部スクリプトを入れない方針のため、Search Console（検索流入）とフィードバック件数で見る
10. **エラー処理**: 送信中の表示、失敗時は入力を消さない、存在しないURLは`p/404.html`で本物の404を返す（`firebase.json`に`"**"→/index.html`のような全体rewriteを入れない。ソフト404になる）
11. **保守性**: 共通のCSS変数・クラスを使い回す、メディア追加等の手順はスキル側に書いておく
12. **信頼性**: 運営者・連絡先・プライバシーポリシーへの導線、更新日（JSON-LDの`dateModified`）を入れる。フッターに `/about/`（運営者情報・編集方針）へのリンクを置き、JSON-LDの`publisher`には `"@id":"https://seadice.win/#organization"` を付けて運営者を1つに紐付ける（AIが同じ運営者だと認識できるようにするため）

## Web制作方針（SEO・パフォーマンス）

SEOのためにモバイルファースト・読み込み速度を極限まで高めることを最優先とする。

### 画像の管理

**全ての画像素材は `/Users/hidenori/Developer/Images/` に置かれている。**
サイトで使用する画像はここから取得し、WebPに変換して `p/icons/` に配置すること。

```bash
cwebp -q 85 /Users/hidenori/Developer/Images/image.png -o /Users/hidenori/Developer/SEADICE/p/icons/image.webp
```

> この「外部リクエストゼロ」方針は `p/` 配下の静的サイトに適用されるものであり、**個別のFlutterアプリ内で使う画像には適用されない**。Flutterアプリ（記号辞典・図鑑など、写真素材が必要な機能）ではUnsplashから画像を検索・ダウンロードし、アプリの`assets/`にバンドルして良い。ダウンロードした画像は実行時に外部URLへアクセスするのではなく、`flutter pub get`前に一度取得してローカルアセットとして同梱すること（Unsplash Licenseは商用・非商用利用とも許可、著作権表示は必須ではないが`CREDITS.md`等に撮影者名とURLを残しておくと親切）。

### 画像フォーマット
| 用途 | 形式 |
|---|---|
| Web上で表示する画像（キャラクター・スクショなど） | WebP |
| OGP画像（SNSシェア用） | PNG |
| アプリアイコン・ファビコン | PNG |

WebP変換コマンド:
```bash
cwebp -q 85 input.png -o output.webp
```

### HTMLページの原則
- JS は原則ゼロ（どうしても必要な場合のみ最小限）
- 外部フォントは使わない（システムフォント `-apple-system` を使用）
- Google Fonts 不使用（外部フォントリクエストゼロ）
- CSS はインラインで minify して記述（外部CSS読み込みゼロ）。共通部分は design/ から注入する（上記「ページの3タイプ」）
- Critical CSS のみインライン記述、不要なスタイルは削除
- 画像には `width` `height` 属性を必ず指定（レイアウトシフト防止）
- モバイルファーストのレイアウト（`max-width` で PC に対応）

### 読み込み速度最速のルール（PageSpeed Insights 100点を目標）
- **画像**: WebP必須。表示サイズに合わせてリサイズ済みのものを使う
- **画像遅延読み込み**: ファーストビュー以外の全画像に `loading="lazy"` を付ける
- **ファーストビュー画像先読み**: `<link rel="preload" as="image">` でヒーロー画像を先読み
- **アイコン**: 可能な限りインラインSVGで記述（画像リクエスト削減）
- **外部リクエストゼロ**: フォント・スクリプト・スタイルシートの外部読み込み禁止
- **テキスト圧縮**: Firebase Hosting が自動でgzip/Brotli圧縮するため設定不要
- **レンダーブロッキング禁止**: `<script>` は `defer` または body末尾に置く

### SEO原則
- 各ページに固有の `<title>` と `<meta name="description">` を設定
- `<link rel="canonical">` を必ず設定
- OGPタグ（og:title / og:description / og:image / og:url）を設定
- JSON-LDでStructured Dataを設定（WebPage / Article / SoftwareApplication）
- BreadcrumbList の JSON-LD を必ず追加
- `<h1>` は1ページに1つ、見出し階層（h1→h2→h3）を守る
- 画像に `alt` 属性を必ず設定
- sitemap.xmlに新規ページを追加したら必ずGoogle Search Consoleで再送信

## SEO 設定（ドメイン: seadice.win）

| ファイル | 役割 |
|---|---|
| `p/index.html` | canonical / OGP / JSON-LD / noscript コンテンツ |
| `p/robots.txt` | クローラー許可 + サイトマップ指定 |
| `p/sitemap.xml` | 全ページ URL リスト |
| `p/manifest.json` | PWA 設定 |
| `p/llms.txt` | AI検索向けのサイト構成・索引 |
| `firebase.json` | キャッシュヘッダー + セキュリティヘッダー + 301リダイレクト |

**Firebase カスタムドメイン設定（コンソールで手動）:**
1. Firebase コンソール → Hosting → カスタムドメインを追加
2. `seadice.win` を登録
3. DNS プロバイダーに表示される A レコードを登録
4. SSL 証明書の自動発行を待つ（〜24時間）

## アプリをサイトに載せるとき（新規・審査通過時）

新しいアプリを `seadice.win` に公開する際は、以下を必ず対応すること。
（`firebase.json` の rewrite 追加は不要。静的ディレクトリは index.html があれば自動で配信される。レガシー Flutter SPA パス（`toite`, `rakuraku`, `boueki-hub/*` 等）を新設する場合のみ rewrite が必要）

### 1. ファビコン・PWA アイコン

Flutter Web 版を置く場合だけ。手順は [docs/flutter-app.md](docs/flutter-app.md) の「Flutter Web 版のファビコン・PWA アイコン」。

### 2. どこに追加するかの判断基準（重要）

`p/index.html` のトップページには「Apps」（主力アプリ）と「Explore」（ジャンル別）の2つの入口があり、新しいアプリはどちらか一方にしか追加しない。

- **既存ジャンル（kateisaien / fitness / pet-health / danshari / black-psychology）の量産アプリ**
  → トップページは触らない。該当する `p/tools/該当ジャンル/index.html` のグリッドにカードを追加するだけ。Explore 経由で自動的に辿れる。
- **既存ジャンルに当たらない単独の主力アプリ**
  → `p/index.html` の `#apps` セクション（`.apps-grid`）にカードを追加。
- **新しいジャンルそのもの**
  → 新しい `p/tools/新ジャンル/index.html` ハブページを作り、`p/index.html` の `#tools`（Explore）セクションに chip を1つ追加。

### 3. プライバシーポリシーの追加

- `p/privacy/新アプリ名/index.html` を作成（read タイプを適用）
- `p/privacy/index.html` の一覧にリンクを追加

### 4. デプロイ

- `firebase deploy --only hosting`

### 5. 審査通過後のアプリページ更新（ユーザーからの一言トリガー）

新規アプリ作成時点ではアプリページ（`p/tools/{appId}/`。`p/apps/` は大半が削除済み）は `App Store近日公開` のまま据え置いてよい（App Store IDが未定のため）。**ユーザーが「〇〇（アプリ名）審査通った」と伝えてきたタイミングで**、以下をまとめて対応する。

- App Store IDは**ユーザーに聞かない**。`python3 scripts/check_released_apps.py` を実行すると、Bundle ID（`win.seadice.{appId}` / camelCase版）から iTunes Lookup API で公開済みアプリを総当たりで見つけ、`p/released-apps.json` に追加する（今後作る他アプリの「関連アプリ」欄の選定元になるため必須）。Bundle IDが命名規則と違う場合は `curl "https://itunes.apple.com/lookup?bundleId={Bundle ID}"` で直接引く
- 続けて `python3 scripts/build_apps_page.py` を実行し、アプリ一覧 `p/apps/index.html` を作り直す（アイコンも自動取得。未公開の間に付けていた `noindex` もこのとき自動で外れる。サイトマップへの再追加は手動）。新しいアプリが「その他」に入ったら、スクリプト内の `CATEGORIES` に追記して再実行する。`/tools/` の一覧（ブラウザで動くツールだけを載せる）にはアプリを追加しない
- アプリページの「近日公開」を公開表記に変え、「App Storeで見る」ボタン（`https://apps.apple.com/app/id{ID}?ct=seadice`）を付ける
- **メディアとの相互送客**（下記「アプリとメディアの相互送客」）を設定する
- **「もとになった研究」欄**（下記7）をアプリページに入れる（相互送客の設定後に `/evidence {appId}`）
- `firebase deploy --only hosting` でデプロイ

### 6. アプリとメディアの相互送客（2026-10-06〜）

目的は「メディアを読んだ人がアプリを使い、アプリを使った人がメディアに戻る」往復を作ること。仕組みは `seadice-media/media/apps.py`。

**メディア → アプリ**（審査通過時に設定。アプリの再申請は不要）
- テーマが合うメディアの設定 `seadice-media/media/{slug}.json` の `apps` 配列に1件追加する（`id` / `name` / `appStoreId` / `icon` / `catch` / `hubLead` / `theme` / `articles`）。アイコンは128pxのWebPにして `sites/{slug}/img/apps/{appId}.webp` に置く
- `articles` には**テーマが合う記事のslugだけ**を明示的に並べる。カテゴリ丸ごとにはしない。アプリと矛盾する記事（例: 通知アプリを「通知を減らす」記事）には付けない
- `python3 media/build.py {slug}` で、対象記事の関連記事の直前にアプリカードが入り、アプリ用ページ `/apps/{appId}/` が生成される。新しい記事は、執筆時に `posts.json` の `"app"` フィールドと本文中の1行リンクで付く（`relatedApps` の指示）
- 1記事1アプリまで。App Storeリンクには `?ct={メディアslug}` を付け、App Store Connect のアナリティクスでどのメディアから来たかを見る
- `p/released-apps.json` の該当アプリに `"media": [{"site": ..., "hub": ...}]` を書き、`p/tools/{appId}/` からもアプリ用ページにリンクする

**アプリ → メディア**（次のアップデートで実装。新規アプリは最初から）
- アプリに入れるURLは**メディアのアプリ用ページ `https://{メディア}/apps/{appId}/` の1本だけ**。個別記事のURLは入れない（記事はアプリ用ページ側で増えていくため、アプリを再申請せずに中身が育つ）
- 置き場所は2か所: ①コア機能を終えた直後の画面に小さなテキストリンク（例:「なぜ深呼吸で落ち着くの？ 解説を読む」。毎回出さず3回目以降など控えめに）②設定画面の「関連アプリ」の上に「もっと知る（SEADICEのメディア）」

事前に「近日公開」のまま作っておき、公開確定後にこの一括更新だけ行うことで、リリース申請時点での二度手間を避ける。

### 7. 「もとになった研究」欄（EVIDENCEシリーズ、2026-10-09〜）

SEADICEの売りは「研究結果（科学メディア）」で、アプリ・ツールはそこから展開した実践手段。どのアプリにも根拠が書いてあることをブランドにする。

- **対象**: 公開済みアプリのページ（`p/tools/{appId}/`）。新規アプリは審査通過時に、既存アプリはページを触るついでに追加する
- **見本**: `p/tools/habit-quit/index.html` の `<section class="evidence">`（CSSの `.evidence` / `.ev-*` ごと流用）。CTAの直前に置く
- **マーク**: EVIDENCEロゴから切り出した `/icons/evidence-mark.webp`（96px、表示40px、`alt=""`）。文字入りの大きい版は `/icons/evidence_icon.webp`
- **1件の中身**: ①研究でわかったことを一文（数字入り）②著者(年), 誌名 / それを使っているアプリの機能 ③「解説記事を読む」（メディア記事）と「論文」（DOI）のリンク。2〜3件
- **根拠の出どころ**: `seadice-media/media/{slug}.json` の `apps[].articles` に並ぶ記事から選び、記事内の出典・数値をそのまま使う。記事にない研究や数値を足さない（捏造禁止）
- **表現**: 「科学的に証明された」「証明済み」とは書かない（効果が示されたのは方法でありアプリ自体ではない。景品表示法の優良誤認・App Store 1.4.1/2.3.1対策）。「研究にもとづく」「研究でわかった」を使う。チェック・盾・メダル等の認証風マークも使わない
- アプリ内にも同じ内容の画面を入れる（次のアップデートで。新規アプリは最初から）
- **シリーズ化（2026-10-10〜）**: 「もとになった研究」欄があるアプリは **EVIDENCEシリーズ（研究にもとづくアプリ）** として一覧ページ `p/evidence-series/` にまとめる。**追加は `/evidence {appId}` の一言で済ませる**（紐づくメディア記事の出典から欄を作り、一覧の再生成・デプロイまで行う。引数なしで追加できる候補を全部処理）。手で欄を直したときは `python3 scripts/build_evidence_page.py` → `python3 scripts/build_apps_page.py` の順に実行する（一覧ページの生成、各アプリ欄への一覧リンク追加、アプリ一覧の「研究にもとづく」バッジが自動で付く）。研究の文章は各アプリページの欄だけに書き、一覧側に別の文章を持たない
- シリーズ名・宣伝文でも「科学が証明する」「証明済み」は使わない。呼び名は「EVIDENCEシリーズ」「研究にもとづくアプリ」に統一する

## App Store 提出情報はチャットにも出す

`/release` 実行時や App Store Connect 登録の準備では、`APPSTORE_SUBMISSION.md` に書くだけで終わらせず、同じ内容をチャットにも直接出力する（ユーザーはファイルを開かずコピペするため）。詳細は [docs/flutter-app.md](docs/flutter-app.md) の末尾。

## 絵文字禁止

**コード・ページ内での絵文字使用は禁止。**
Flutter Web の読み込み時に絵文字フォントが未ロードで文字化けが発生するため。サイトでもアイコンはインラインSVGにする。

- `AppItem.icon` フィールド → 短い文字列（例: `'SRS'`, `'AI'`, `'貿'`）
- UI アイコン → `Icon(Icons.xxx)` （Material Icons を使用）
- ボタンラベル・テキスト → 絵文字を含まないプレーンテキスト
- データ定数（`_visionSlides` 等）→ 絵文字フィールド自体を設けない
