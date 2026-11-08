# サイト（p/）の作り方（詳細）

CLAUDE.md から移した詳細（2026-11-08）。`p/` のページを作る・直すときに、[design/README.md](../design/README.md) と一緒に読む。

## ページの3タイプとデザイン（質実剛健、2026-10-12〜）

`p/` 配下のページは「読ませる / 魅せる / 使う」のどれかに分け、デザインは [design/](../design/) の `base.css` + `{read,show,use}.css` で一元管理する。テーマは**質実剛健**（グラデーション・ぼかし・光・影なし、角丸は8px以下、アクセント色は要所だけ）。

| タイプ | 対象 | 形 |
|---|---|---|
| read（読ませる） | ブログ記事・レビュー記事・プライバシー | 本文幅660px（約38字）の1段、本文16→17px・行間1.95、h2は左の縦線 |
| show（魅せる） | アプリ紹介・各種一覧・EVIDENCE | 幅1080px、大見出し、カード1→2→3列、PCは見出し左/中身右の2段 |
| use（使う） | ブラウザツール・診断 | 見出し小さめ、操作部は `.sd-tool` の1枚パネル、入力48px以上。PCは説明左/道具右に固定 |

- **文字はできる限り減らす**（2026-11-05〜）: 説明は1文まで、伝えられる所はアイコン・図にする。出典・FAQ・JSON-LD は削らない（詳しくは design/README.md「文字を減らす」）
- ブレークポイントは **600px / 960px** の2つだけ。左右余白は `--sd-g`（16/24/32px）
- **ページを新しく作ったら必ず** `python3 scripts/apply_page_type.py {read|show|use} p/…/index.html` を実行する（`<head>` 末尾にインラインCSSを差し込み、`<body class="t-…">` を付ける。外部CSSは使わない）。ツールは操作パネルの要素に `sd-tool` クラスを付けてから実行する
- デザインを直すときは `design/*.css` を編集し、`python3 scripts/apply_page_type.py --refresh` で適用済みの全ページに反映する（`p/index.html` のトップページと Flutter SPA は対象外）
- `build_apps_page.py` / `build_evidence_page.py` は書き出し時に自動で show を差し込む

## サイト設計の12項目（毎回確認する、2026-09-30〜）

1. **SEO**: 固有のtitle/description/canonical、h1は1つ、sitemap・内部リンクを更新。noindexのページはsitemapに入れない。sitemapの`lastmod`とJSON-LDの`dateModified`は中身を変えたときだけ更新する
2. **AIO/AEO**: 質問に結論から答える文、主語に「SEADICE」等の固有名、JSON-LD（FAQPage等）、`p/llms.txt`を最新に保つ
3. **モバイル操作**: 本文14px以上・補助テキストも12px未満にしない、タップ領域は上下8px以上の余白、フォームは最小項目
4. **パフォーマンス**: WebPは表示サイズの2倍までに縮小、JS最小、width/height指定、ファーストビュー画像はpreload
   - **効果のない部分は削ぐ**（2026-10-12〜）: 効果のない部分（使われないページ・読まれない文・効かないルール・使っていないCSSやコード・大きすぎるファイル）は削ぐ。増やす前に「同じ用事をもっと小さく済ませられないか」を考える。生成ページは中身が変わったときだけ書き換える。利用者からデータを集める仕組み（カウンター・匿名集計を含む）は作らない（APIの上限のための呼び出し回数だけは例外）。ログや履歴をサーバーにためない（記録は端末内）。Hosting のリリース保持は5件、PRプレビューは p/ が変わるときだけ
   - **代謝の仕組み**（2026-11-03〜）: 作るときに「どうなったら消えるか」も一緒に決める（アカウントは一定期間使われなければ中身ごと自動で消す、投稿・記事・ページ・ルールも同じ）
5. **アクセシビリティ**: 文字色は背景とコントラスト4.5:1以上（`--sd-muted`の`#7c8aa0`は暗い背景`#05050C`の上で約5.8:1。明るい背景には使わない）、色だけで状態を伝えない、キーボード操作・focus表示、装飾画像は`alt=""`
6. **情報設計**: 重要ページへ少ない操作で到達、パンくず（下層ページ）、関連ページ同士をつなぐ
7. **プライバシー**: フォームで個人情報を集めない（匿名フォームにはその旨を明記）
8. **CVR**: ボタンは「送る」でなく「要望を送る」のように具体的な文言、不安要素（返信の有無・無料かどうか）を先に書く
9. **計測**: 外部スクリプトを入れない。見る数字は [strategy.md](strategy.md) の4つ（＋フィードバック件数）
10. **エラー処理**: 送信中の表示、失敗時は入力を消さない、存在しないURLは`p/404.html`で本物の404を返す（`firebase.json`に`"**"→/index.html`のような全体rewriteを入れない。ソフト404になる）
11. **保守性**: 共通のCSS変数・クラスを使い回す、メディア追加等の手順はスキル側に書いておく
12. **信頼性**: 運営者・連絡先・プライバシーポリシーへの導線、更新日（JSON-LDの`dateModified`）を入れる。フッターに `/about/` へのリンクを置き、JSON-LDの`publisher`には `"@id":"https://seadice.win/#organization"` を付けて運営者を1つに紐付ける

## Web制作方針（SEO・パフォーマンス）

モバイルファーストで、今の速さ（静的HTML・外部リクエストゼロ）を落とさない。PageSpeed Insights 100点が目標。

### 画像
全ての画像素材は `/Users/hidenori/Developer/Images/` にある。WebPに変換して `p/icons/` に置く:
```bash
cwebp -q 85 /Users/hidenori/Developer/Images/image.png -o /Users/hidenori/Developer/SEADICE/p/icons/image.webp
```

| 用途 | 形式 |
|---|---|
| Web上で表示する画像（キャラクター・スクショなど） | WebP（表示サイズに合わせてリサイズ） |
| OGP画像（SNSシェア用） | PNG |
| アプリアイコン・ファビコン | PNG |

- ファーストビュー以外の全画像に `loading="lazy"`、ヒーロー画像は `<link rel="preload" as="image">`
- `width` `height` 属性を必ず指定（レイアウトシフト防止）、`alt` を必ず設定
- アイコンは可能な限りインラインSVG

「外部リクエストゼロ」は `p/` の静的サイトの方針で、Flutterアプリ内の画像には適用しない。アプリで写真素材が要るときは Unsplash から一度ダウンロードして `assets/` に同梱してよい（実行時に外部URLを読まない。撮影者名とURLを `CREDITS.md` 等に残す）。

### HTML
- JS は原則ゼロ（必要な場合のみ最小限、`defer` か body 末尾。レンダーブロッキング禁止）
- 外部フォント・Google Fonts・外部CSS・外部スクリプトは使わない（システムフォント `-apple-system`）
- CSS はインラインで minify。共通部分は design/ から注入する
- モバイルファーストのレイアウト（`max-width` で PC に対応）

### SEO
- 各ページに固有の `<title>`・`<meta name="description">`・`<link rel="canonical">`
- OGP（og:title / og:description / og:image / og:url）
- JSON-LD（WebPage / Article / SoftwareApplication）と BreadcrumbList を必ず
- `<h1>` は1つ、見出し階層（h1→h2→h3）を守る

### SEO 設定ファイル

| ファイル | 役割 |
|---|---|
| `p/index.html` | canonical / OGP / JSON-LD / noscript コンテンツ |
| `p/robots.txt` | クローラー許可 + サイトマップ指定 |
| `p/sitemap.xml` | 全ページ URL リスト |
| `p/manifest.json` | PWA 設定 |
| `p/llms.txt` | AI検索向けのサイト構成・索引 |
| `firebase.json` | キャッシュヘッダー + セキュリティヘッダー + 301リダイレクト |
