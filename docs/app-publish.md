# アプリをサイトに載せるときの詳細（相互送客・もとになった研究）

審査通過時の作業で読む。前半は相互送客・もとになった研究（2026-10-19に CLAUDE.md から移した）、後半は新規公開・審査通過時の手順1〜5（2026-10-26に移した）。

## 1. アプリとメディアの相互送客（2026-10-06〜）

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

## 2. 「もとになった研究」欄（EVIDENCEシリーズ、2026-10-09〜）

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

---

# 新規公開・審査通過時の手順（CLAUDE.md から移した、2026-10-26）

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
- 続けて `python3 scripts/build_apps_page.py` を実行し、アプリ一覧 `p/apps/index.html` を作り直す（アイコンも自動取得。未公開の間に付けていた `noindex` もこのとき自動で外れる。`p/sitemap.xml` への `/tools/{appId}/` の追加は手動で、漏れると `scripts/check_sitemap.py` がデプロイを止める）。新しいアプリが「その他」に入ったら、スクリプト内の `CATEGORIES` に追記して再実行する。`/tools/` の一覧（ブラウザで動くツールだけを載せる）にはアプリを追加しない
- アプリページの「近日公開」を公開表記に変え、「App Storeで見る」ボタン（`https://apps.apple.com/app/id{ID}?ct=seadice`）を付ける
- **メディアとの相互送客**（下記「アプリとメディアの相互送客」）を設定する
- **「もとになった研究」欄**（下記7）をアプリページに入れる（相互送客の設定後に `/evidence {appId}`）
- `firebase deploy --only hosting` でデプロイ

### 6. アプリとメディアの相互送客 / 7. 「もとになった研究」欄

審査通過時に必ず行う。手順・書き方・禁止表現は [docs/app-publish.md](docs/app-publish.md)（EVIDENCEシリーズへの追加は `/evidence {appId}` の一言）。
