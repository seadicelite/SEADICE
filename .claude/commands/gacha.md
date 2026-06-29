# ニッチアプリ自動生成

SEADICEサイト用のニッチアプリを1セット生成してサイトに追加する。

## Step 1: ニッチリサーチ

WebSearchを使って以下を満たすニッチを1つ選ぶ。
- 日本のApp Storeで競合が少ない
- 需要が高い・伸びている
- 個人開発者が作れる規模

まず `ls p/tools/` を実行して既存のニッチを確認し、**重複しないもの**を選ぶ。

スラッグ（英数字・ハイフンのみ）を決める。例: `hiking`, `study-timer`, `baby-log`

3つのアプリを定義する：
- app1: コアユーティリティ
- app2: トラッカー・習慣系
- app3: クイズ・ガイド系

各アプリについて以下を定義する：
- アプリ名（30文字以内、日本語）
- サブタイトル（30文字以内、日本語）
- カテゴリ（App Storeカテゴリ、日本語）
- ターゲットユーザー
- 主要機能5つ
- プロモーション用テキスト（170文字以内）
- 概要（500〜1000文字）
- キーワード（100文字以内、カンマ区切り）

## Step 2: ランディングページ生成

`p/tools/{slug}/index.html` を作成する。

CLAUDE.mdを必ず読んでからHTMLを書く。

ページ構成：
1. Hero: ニッチタイトル + ターゲットユーザー説明
2. 課題セクション: このニッチが抱える問題
3. アプリ3枚カード: 各カードが `/apps/{slug}-app1/` 等にリンク
4. CTAセクション: SEADICEトップへのリンク

ルール：
- JS禁止、システムフォント（-apple-system）のみ、CSSはインラインでminify
- favicon: `/favicon.png`
- canonical: `https://seadice.win/tools/{slug}/`
- OGP・JSON-LD（WebPage + BreadcrumbList）
- モバイルファースト、h1は1つ、絵文字禁止
- デザイン: bg #05050C, accent #00FFD1, blue #38BDF8
- 戻るリンク: `href="https://seadice.win/"` （絶対パス）

アプリカード形式：
```html
<a class="app-card" href="/apps/{slug}-app1/">
  <p class="app-name">{アプリ名}</p>
  <p class="app-desc">{説明}</p>
  <span class="app-badge">App Store近日公開</span>
</a>
```

## Step 3: アプリ詳細ページ生成（3つ）

`p/apps/{slug}-app1/index.html`, `p/apps/{slug}-app2/index.html`, `p/apps/{slug}-app3/index.html` を作成する。

各ページに以下のセクションを含める：

**Section 1: Hero**
アプリ名（h1）、サブタイトル、「App Store近日公開」バッジ、プライバシーポリシーリンク

**Section 2: App Storeメタデータ（そのままコピペできる形式）**
- 名前（30字以内）
- サブタイトル（30字以内）
- カテゴリ
- プライバシーポリシーURL: `https://seadice.win/privacy/{slug}-appN/`
- プロモーション用テキスト（170字以内）
- 概要（500〜1000字）
- キーワード（100字以内）

**Section 3: 機能一覧**（5つのカードグリッド）

**Section 4: 広告について**（AdMob バナー・インタースティシャル・リワード）

**Section 5: 今後実装予定の機能**（3〜5個）

**Section 6: なぜこのアプリが必要か**（マーケティングコピー）

ルール：
- JS禁止、システムフォント、CSSインラインminify
- favicon: `/favicon.png`
- canonical: `https://seadice.win/apps/{slug}-appN/`
- OGP・JSON-LD（SoftwareApplication + BreadcrumbList）
- デザイン: bg #05050C, accent #00FFD1, card #0C0C1A、絵文字禁止

## Step 4: プライバシーポリシーページ生成（3つ）

`p/privacy/{slug}-app1/index.html`, `p/privacy/{slug}-app2/index.html`, `p/privacy/{slug}-app3/index.html` を作成する。

各ページに含める：アプリ名、開発者（SEADICE）、連絡先 seadice.home@gmail.com、収集データ、AdMob/Firebase サードパーティ、データ削除方法。日本語。同じSEADICEデザイン。favicon `/favicon.png`。

## Step 5: インデックスページ更新

**`p/tools/index.html`** の `.tools-grid` 内の先頭に追加：
```html
<a class="tool-card" href="/tools/{slug}/">
  <span class="tool-tag">{カテゴリ}</span>
  <p class="tool-title">{タイトル}</p>
  <p class="tool-desc">{30〜50文字の説明}</p>
</a>
```

**`p/index.html`** の `<section id="tools"` 内 `.blog-list` divの先頭に追加：
```html
<a class="blog-card" href="/tools/{slug}/">
  <div class="blog-card-body">
    <span class="blog-tag">{カテゴリ}</span>
    <p class="blog-title">{タイトル}</p>
    <p class="blog-meta">{一行説明}</p>
  </div>
  <span class="blog-arrow" aria-hidden="true">›</span>
</a>
```

## Step 6: Flutterアプリスケルトン生成（3つ）

`/Users/hidenori/Developer/apps-pipeline/apps/{slug}_app1/` 等に以下を作成する。

**pubspec.yaml**:
```yaml
name: {slug}_appN
description: {アプリ説明}
version: 1.0.0+1
environment:
  sdk: ">=3.3.0 <4.0.0"
dependencies:
  flutter:
    sdk: flutter
  google_mobile_ads: ^5.1.0
  shared_preferences: ^2.3.2
  intl: ^0.19.0
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
flutter:
  uses-material-design: true
  assets:
    - assets/fonts/
  fonts:
    - family: NotoSansJP
      fonts:
        - asset: assets/fonts/NotoSansJP-VariableFont_wght.ttf
```

**lib/main.dart**: 動くFlutterアプリを実装する。
- MaterialApp + ダークテーマ、日本語UI、絵文字禁止
- BottomNavigation（3タブ、アプリ内容に合わせた機能）
- NotoSansJPフォントフォールバック
- AdMob（テストID使用）:
  - App ID: `ca-app-pub-3940256099942544~1458002511`
  - バナー: `ca-app-pub-3940256099942544/2934735716`
  - インタースティシャル: `ca-app-pub-3940256099942544/4411468910`
  - リワード: `ca-app-pub-3940256099942544/1712485313`
- バナー広告をメイン画面下部に常時表示
- インタースティシャルをタスク完了等の適切なタイミングで表示
- リワードを「広告を見る」ボタンでプレミアム機能解放
- `MobileAds.instance.initialize()` を `runApp()` 前に呼ぶ
- `AdWidget` は `SizedBox(height: 50)` でラップ

**flutter create でプロジェクト初期化とBundle ID設定**:

各アプリディレクトリで以下を実行してiOS/Android/Webプロジェクトを作成し、Bundle IDを設定する。

```bash
cd /Users/hidenori/Developer/apps-pipeline/apps/{slug}_appN
flutter create --org win.seadice --project-name {slug}_appN --platforms ios,android,web . --quiet
```

Bundle IDは `win.seadice.{slugCamelCase}App1` の形式になる（例: `win.seadice.tsuriApp1`）。

`ios/Runner/Info.plist` の `</dict>` の直前に以下を追加する（AdMobクラッシュ防止）：
```xml
<key>GADApplicationIdentifier</key>
<string>ca-app-pub-3940256099942544~1458002511</string>
```

NotoSansJPフォントをコピー：
```bash
mkdir -p assets/fonts
cp /Users/hidenori/Developer/NotoSansJP-VariableFont_wght.ttf assets/fonts/
```

**README.md**: アプリ概要・ターゲット・機能・マネタイズ（AdMob）を記載。以下のセクションを必ず含める：

```
## ビルド前の注意

ios/Runner/Info.plist の `</dict>` の直前に以下を追加すること。追加しないと起動直後にクラッシュする。

<key>GADApplicationIdentifier</key>
<string>ca-app-pub-3940256099942544~1458002511</string>
```

## Step 7: firebase.json にrewrite追加

`firebase.json` の `**` catch-allの直前に以下を追加する：

```json
{"source": "/tools/{slug}/**", "destination": "/tools/{slug}/index.html"},
{"source": "/apps/{slug}-app1/**", "destination": "/apps/{slug}-app1/index.html"},
{"source": "/apps/{slug}-app2/**", "destination": "/apps/{slug}-app2/index.html"},
{"source": "/apps/{slug}-app3/**", "destination": "/apps/{slug}-app3/index.html"},
{"source": "/privacy/{slug}-app1/**", "destination": "/privacy/{slug}-app1/index.html"},
{"source": "/privacy/{slug}-app2/**", "destination": "/privacy/{slug}-app2/index.html"},
{"source": "/privacy/{slug}-app3/**", "destination": "/privacy/{slug}-app3/index.html"}
```

## Step 8: git commit & deploy

```bash
cd /Users/hidenori/Developer/SEADICE
git add -A
git commit -m "Add {slug}: landing + app pages + privacy policies"
firebase deploy --only hosting
```

```bash
cd /Users/hidenori/Developer/apps-pipeline
git add apps/{slug}_app1/ apps/{slug}_app2/ apps/{slug}_app3/
git commit -m "Add {slug} app skeletons"
git push
```

## ルール

- CLAUDE.mdを必ず読んでからHTMLを書く
- `ls p/tools/` で既存ニッチを確認してから開始
- 既存ファイルを丸ごと上書きしない（追記のみ）
- HTMLは本番品質、プレースホルダー禁止
- ユーザー向けテキストはすべて日本語
- 絵文字禁止
- faviconは常に `/favicon.png`（絶対パス）
- 戻るリンクは `https://seadice.win/`（絶対URL）
