# ニッチアプリ自動生成

SEADICEサイト用のニッチアプリを1セット生成してサイトに追加する。

## Step 1: ニッチリサーチ

まず `ls p/tools/` を実行して既存のニッチを確認し、**重複しないもの**を選ぶ。

スラッグ（英数字・ハイフンのみ）を決める。例: `hiking`, `study-timer`, `baby-log`

**10個のアプリを定義する**：
- app1〜app5: メジャー系（そのニッチで需要が広いアプリ）
- app6〜app9: マイナー系（ニッチの中でもさらに特化したアプリ）
- app10: **Claude APIを使ったAIアプリ**（鉢・スペース・環境を入力するとAIが植物・野菜を提案するなど、ユーザーの具体的な悩みをAIが解決するもの）

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
3. アプリ10枚カード: 各カードが `/apps/{slug}-app1/` 等にリンク
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

## Step 3: アプリ詳細ページ生成（10個）

`p/apps/{slug}-app1/index.html` 〜 `p/apps/{slug}-app10/index.html` を作成する。

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

## Step 4: プライバシーポリシーページ生成（10個）

`p/privacy/{slug}-app1/index.html` 〜 `p/privacy/{slug}-app10/index.html` を作成する。

各ページに含める：アプリ名、開発者（SEADICE）、連絡先 seadice.home@gmail.com、収集データ、AdMob/Firebase サードパーティ、データ削除方法。日本語。同じSEADICEデザイン。favicon `/favicon.png`。

app10（AIアプリ）はClaude APIへのテキスト送信についても明記する。

## Step 5: インデックスページ更新

**`p/tools/index.html`** の `.tools-grid` 内の先頭に追加：
```html
<a class="tool-card" href="/tools/{slug}/">
  <span class="tool-tag">{カテゴリ}</span>
  <p class="tool-title">{タイトル}</p>
  <p class="tool-desc">{30〜50文字の説明}</p>
</a>
```

**`p/index.html`** の `<section id="tools"` 内 `.explore-grid` divに追加：
```html
<a class="explore-card" href="/tools/{slug}/">{ジャンル名}</a>
```

## Step 6: Flutterアプリスケルトン生成（10個）

`/Users/hidenori/Developer/apps-pipeline/apps/{slug}_app1/` 〜 `{slug}_app10/` に以下を作成する。

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
  google_mobile_ads: ^9.0.0
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

app10（AIアプリ）のみ追加依存：
```yaml
  http: ^1.2.0
  url_launcher: ^6.3.0
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
- **`runApp()` を先に呼び、その後 `try { await MobileAds.instance.initialize(); } catch (_) {}`**（クラッシュ防止）
- `AdWidget` は `SizedBox(height: 50)` でラップ

app10（AIアプリ）のmain.dartの追加仕様：
- ユーザーが鉢サイズ・置き場所・日当たり・季節などを入力するフォーム画面
- Claude API（`https://api.anthropic.com/v1/messages`）にPOSTしてAIの提案を表示
- APIキーはユーザーが設定画面で入力して`shared_preferences`に保存
- レスポンスをカード形式で表示

**flutter create でプロジェクト初期化とBundle ID設定**:

各アプリディレクトリで以下を実行：

```bash
cd /Users/hidenori/Developer/apps-pipeline/apps/{slug}_appN
flutter create --org win.seadice --project-name {slug}_appN --platforms ios,android,web . --quiet
```

`ios/Runner/Info.plist` の `</dict>` の直前に以下を追加（AdMobクラッシュ防止）：
```xml
<key>GADApplicationIdentifier</key>
<string>ca-app-pub-3940256099942544~1458002511</string>
<key>GADIsAdManagerApp</key>
<false/>
```

`ios/Podfile` の `post_install` ブロックに以下を追加（iOS deployment target 警告防止）：
```ruby
post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '14.0'
    end
  end
end
```

NotoSansJPフォントをコピー：
```bash
mkdir -p assets/fonts
cp /Users/hidenori/Developer/NotoSansJP-VariableFont_wght.ttf assets/fonts/
```

`ios/Runner/Assets.xcassets/LaunchImage.imageset/` のLaunchImageをアプリアイコンから生成：
```bash
ICON="ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png"
DEST="ios/Runner/Assets.xcassets/LaunchImage.imageset"
sips -s format png -z 200 200 "$ICON" --out "$DEST/LaunchImage.png"
sips -s format png -z 400 400 "$ICON" --out "$DEST/LaunchImage@2x.png"
sips -s format png -z 600 600 "$ICON" --out "$DEST/LaunchImage@3x.png"
```

**README.md**: アプリ概要・ターゲット・機能・マネタイズ（AdMob）を記載。

## Step 7: firebase.json にrewrite追加

`firebase.json` の `**` catch-allの直前に以下を追加する：

```json
{"source": "/tools/{slug}/**", "destination": "/tools/{slug}/index.html"},
{"source": "/apps/{slug}-app1/**", "destination": "/apps/{slug}-app1/index.html"},
{"source": "/apps/{slug}-app2/**", "destination": "/apps/{slug}-app2/index.html"},
{"source": "/apps/{slug}-app3/**", "destination": "/apps/{slug}-app3/index.html"},
{"source": "/apps/{slug}-app4/**", "destination": "/apps/{slug}-app4/index.html"},
{"source": "/apps/{slug}-app5/**", "destination": "/apps/{slug}-app5/index.html"},
{"source": "/apps/{slug}-app6/**", "destination": "/apps/{slug}-app6/index.html"},
{"source": "/apps/{slug}-app7/**", "destination": "/apps/{slug}-app7/index.html"},
{"source": "/apps/{slug}-app8/**", "destination": "/apps/{slug}-app8/index.html"},
{"source": "/apps/{slug}-app9/**", "destination": "/apps/{slug}-app9/index.html"},
{"source": "/apps/{slug}-app10/**", "destination": "/apps/{slug}-app10/index.html"},
{"source": "/privacy/{slug}-app1/**", "destination": "/privacy/{slug}-app1/index.html"},
{"source": "/privacy/{slug}-app2/**", "destination": "/privacy/{slug}-app2/index.html"},
{"source": "/privacy/{slug}-app3/**", "destination": "/privacy/{slug}-app3/index.html"},
{"source": "/privacy/{slug}-app4/**", "destination": "/privacy/{slug}-app4/index.html"},
{"source": "/privacy/{slug}-app5/**", "destination": "/privacy/{slug}-app5/index.html"},
{"source": "/privacy/{slug}-app6/**", "destination": "/privacy/{slug}-app6/index.html"},
{"source": "/privacy/{slug}-app7/**", "destination": "/privacy/{slug}-app7/index.html"},
{"source": "/privacy/{slug}-app8/**", "destination": "/privacy/{slug}-app8/index.html"},
{"source": "/privacy/{slug}-app9/**", "destination": "/privacy/{slug}-app9/index.html"},
{"source": "/privacy/{slug}-app10/**", "destination": "/privacy/{slug}-app10/index.html"}
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
git add apps/{slug}_app1/ apps/{slug}_app2/ apps/{slug}_app3/ apps/{slug}_app4/ apps/{slug}_app5/ apps/{slug}_app6/ apps/{slug}_app7/ apps/{slug}_app8/ apps/{slug}_app9/ apps/{slug}_app10/
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
- `MobileAds.instance.initialize()` は必ず `runApp()` の後にtry-catchで呼ぶ
- `CFBundleDisplayName` は必ず日本語アプリ名を設定する
