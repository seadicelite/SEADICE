# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# 開発
flutter run -d chrome          # Web で起動（メインターゲット）
flutter run -d ios             # iOS シミュレーター
flutter run -d android         # Android エミュレーター

# 品質チェック
flutter analyze lib/main.dart  # Lint（lib/main.dart のみが対象）

# ビルド & デプロイ
flutter build web --release    # --web-renderer は Flutter 3.22 以降廃止。オプションなしでOK

# ⚠️ 絶対禁止: cp -r build/web/. p/ は実行しない
# p/ は静的HTMLファイルを含む。上書きするとSEO用HTMLが消える。
# デプロイは必ず flutter build web --release 後に以下を実行:
rsync -av --exclude='index.html' --exclude='manifest.json' --exclude='favicon.png' --exclude='robots.txt' --exclude='sitemap.xml' --exclude='apps/' --exclude='icons/' --exclude='fonts/' --exclude='privacy/' --exclude='blog/' build/web/ p/
firebase deploy --only hosting # hosting のみデプロイ（functions の警告を避けるため）
```

> **Firebase 注意**: `firebase.json` の `public` は `"p"` に設定されている。Flutter のビルド出力 (`build/web`) とは異なるため、デプロイ前に必ず `cp -r build/web/. p/` を実行すること。

## 新規 Flutter Web アプリを追加するときのチェックリスト

新しいアプリを Web に公開する際は、以下を必ず対応すること。

### 1. ファビコン・PWA アイコンをアプリアイコンから生成

デフォルトの Flutter ファビコン（青い Flutter ロゴ）のままにしない。
アプリアイコン（1024×1024 PNG）から以下のコマンドで生成する。

```bash
ICON_SRC="assets/icon/icon.png"  # または ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png

sips -s format png -z 32 32  "$ICON_SRC" --out web/favicon.png
sips -s format png -z 192 192 "$ICON_SRC" --out web/icons/Icon-192.png
sips -s format png -z 512 512 "$ICON_SRC" --out web/icons/Icon-512.png
sips -s format png -z 192 192 "$ICON_SRC" --out web/icons/Icon-maskable-192.png
sips -s format png -z 512 512 "$ICON_SRC" --out web/icons/Icon-maskable-512.png
```

> アイコンが `assets/icon/icon.png` にない場合は iOS の `Icon-App-1024x1024@1x.png` を使う。

### 2. SEADICE ポートフォリオへの追加

- `lib/main.dart` の `_defaultApps` にエントリを追加
- `_appPrivacyData` にプライバシーポリシーを追加
- `firebase.json` の `rewrites` にサブパスを追加
- `flutter build web --release --base-href /サブパス名/` でビルド
- `cp -r build/web/. /Users/hidenori/Developer/SEADICE/p/サブパス名/` でコピー
- `firebase deploy --only hosting` でデプロイ

## アーキテクチャ

### 概要

SEADICE スタジオの **Flutter Web ポートフォリオ**。単一ページのスクロールサイト（Linear/Vercel スタイル）で、モバイルにも対応している。

- **エントリーポイント**: `lib/main.dart` のみ。全コンポーネントが 1 ファイルに集約されている
- **ルーティング**: `go_router` + `MaterialApp.router`。ルートは `/`（HomePage）と `/apps/:id`（AppDetailPage）の 2 つ

### ページ構成（スクロールセクション）

`HomePage` が `SingleChildScrollView` でセクションを縦に並べる。各セクションは `RevealOnScroll` でラップされ、スクロール到達時に fade + slide-up アニメーションが発火する。

```
Navbar（fixed top）
└── HeroSection           ← fade+slide（600ms）+ タイトルタイピングアニメーション
└── RevealOnScroll
    └── AppsSection       ← フィルターチップ付きグリッド
└── RevealOnScroll
    └── AboutSection      ← 統計グリッド（apps リストから自動集計）
└── RevealOnScroll
    └── ContactSection
```

### データ管理

`AppItem` モデルのリストを `SharedPreferences` に JSON で保存。`AppStorage.load()` / `AppStorage.save()` で永続化。デフォルトデータは `_defaultApps` 定数（`lib/main.dart` 冒頭）。

管理モードは Navbar の「⚙ 管理」ボタンで ON/OFF。ON 時はカードに「✎ 編集」ボタンが出現し、`AppFormDialog` で CRUD 操作ができる。

### デザインシステム（定数）

```dart
const _bg      = Color(0xFF05050C);   // 背景
const _accent  = Color(0xFF00FFD1);   // プライマリアクセント（ティール）
const _accent2 = Color(0xFF38BDF8);   // グラデーション用（ブルー）
const _cardBg  = Color(0xFF0C0C1A);   // カード背景
```

フォント: **Syne**（見出し）/ **DM Sans**（本文）/ **Space Mono**（ラベル・モノスペース）

### Navbar のレスポンシブ

幅 700px 未満でハンバーガーメニューに切替。`BackdropFilter` による backdrop blur が適用されている（`dart:ui` が必要）。

## 日本語フォント（文字化け対策）

Flutter Web では Google Fonts の Latin フォントが日本語グリフを持たないため、漢字・かなが文字化けする。
すべての Flutter アプリで以下を必ず適用すること。

### 1. フォントファイルを `assets/fonts/` に配置
```
assets/fonts/NotoSansJP-VariableFont_wght.ttf  ← /Users/hidenori/Developer/ からコピー
```

### 2. `pubspec.yaml` に登録
```yaml
flutter:
  assets:
    - assets/fonts/
  fonts:
    - family: NotoSansJP
      fonts:
        - asset: assets/fonts/NotoSansJP-VariableFont_wght.ttf
```

### 3. フォントを `web/fonts/` にも配置（**Web 専用**）

Flutter Web のビルドでは user assets が `assets/assets/fonts/...` という二重パスになるため、
CSS から直接参照できない。`web/fonts/` に直置きすることで予測可能な URL になる。

```bash
cp /Users/hidenori/Developer/NotoSansJP-VariableFont_wght.ttf web/fonts/
```

### 4. `web/index.html` の `<head>` にフォント宣言を追加（**最重要**）

Flutter Web HTML レンダラーはブラウザの CSS フォントシステムを使うため、
Dart 側の FontLoader だけでは初回レンダリングに間に合わない。

```html
<!-- NotoSansJP: ブラウザに先読みさせて文字化けを防ぐ -->
<link rel="preload" href="fonts/NotoSansJP-VariableFont_wght.ttf" as="font" type="font/ttf" crossorigin>
<style>
  @font-face {
    font-family: 'NotoSansJP';
    src: url('fonts/NotoSansJP-VariableFont_wght.ttf') format('truetype');
    font-weight: 100 900;
    font-display: block;
  }
  body { font-family: 'DM Sans', 'NotoSansJP', sans-serif; }
</style>
```

### 4. `main()` で先読み（Flutter ネイティブ向け保険）
```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final fontLoader = FontLoader('NotoSansJP')
    ..addFont(rootBundle.load('assets/fonts/NotoSansJP-VariableFont_wght.ttf'));
  await fontLoader.load();
  runApp(const MyApp());
}
```

### 5. `ThemeData` にフォールバック設定
```dart
textTheme: GoogleFonts.dmSansTextTheme(ThemeData.dark().textTheme)
    .apply(fontFamilyFallback: ['NotoSansJP']),
```

> Latin フォント（Syne / DM Sans）が優先され、日本語グリフのみ NotoSansJP にフォールバックする。
> **Web では手順3が必須**。手順4・5だけでは文字化けが再現することがある。

### フォント先読みの原則（文字化けゼロにするための順序）

文字化けは「フォントが読み込まれる前に描画が始まる」ことで起きる。以下の2段構えで防ぐ。

**① ブラウザ側（CSS）: 描画をブロックしてフォントを待つ**

`web/index.html` の `@font-face` に `font-display: block` を必ず指定する。
これによりフォント読み込み完了まで描画を止め、文字化けした状態が一瞬でも見えるのを防ぐ。

```html
<link rel="preload" href="fonts/NotoSansJP-VariableFont_wght.ttf" as="font" type="font/ttf" crossorigin>
<style>
  @font-face {
    font-family: 'NotoSansJP';
    src: url('fonts/NotoSansJP-VariableFont_wght.ttf') format('truetype');
    font-weight: 100 900;
    font-display: block;  /* ← これが重要。swap にすると一瞬文字化けが見える */
  }
</style>
```

**② Dart 側: `runApp` の前にフォントロードを完了させる**

`await fontLoader.load()` を `runApp()` より前に置くことで、Flutter のウィジェットツリーが構築される時点でフォントが確実に使える状態になる。

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final fontLoader = FontLoader('NotoSansJP')
    ..addFont(rootBundle.load('assets/fonts/NotoSansJP-VariableFont_wght.ttf'));
  await fontLoader.load();  // ← runApp より前に完了させる
  runApp(const MyApp());
}
```

---

## デプロイ後の自動更新（キャッシュ設定）

デプロイしてもユーザーが古いバージョンを見続けないよう、`firebase.json` の `headers` を以下のルールで設定する。

| ファイル | Cache-Control | 理由 |
|---|---|---|
| `index.html` | `no-cache` | 毎回サーバーに確認させ、新バージョンを即反映 |
| `flutter_service_worker.js` | `no-cache` | SW 自体がキャッシュされると更新が一切届かない |
| `flutter_bootstrap.js` | `no-cache` | エントリーポイントなので常に最新を取得 |
| `flutter.js` | `no-cache` | ファイル名にハッシュがないため `immutable` 厳禁 |
| `main.dart.js` | `no-cache` | ファイル名にハッシュがないため `immutable` 厳禁 |
| `version.json` | `no-cache` | SW がバージョン比較に使うファイル |

> **重要**: Flutter Web のビルドでは `main.dart.js` / `flutter.js` のファイル名にハッシュが付かない。
> これらに `immutable`（`max-age=31536000`）を設定するとブラウザが1年間再取得しなくなり、
> デプロイしても古いバージョンが表示され続ける。`**/*.@(js|css|wasm)` のような広いグロブで
> `immutable` を設定してはいけない。

```json
{ "source": "/index.html",               "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/flutter_service_worker.js","headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/flutter_bootstrap.js",     "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/flutter.js",               "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/main.dart.js",             "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/version.json",             "headers": [{ "key": "Cache-Control", "value": "no-cache" }] }
```

> この設定により、次回デプロイ後はユーザーがキャッシュを手動削除しなくても自動的に最新版が表示される。

---

## 留意事項

- `Color.withOpacity()` は非推奨。`withValues(alpha: x)` を使うこと（Flutter 3.27+）
- `AnimatedBuilder` の未使用パラメーターは `(_, _)` と書く（Dart 3.7+ のワイルドカード）
- データ永続化は SharedPreferences（`AppStorage.load()` / `AppStorage.save()`）
- プライバシーポリシーは `lib/main.dart` 末尾の `_appPrivacyData` と `AppPrivacyPage` で管理
- 共通のデザイン定数・開発者情報は `~/Desktop/CLAUDE.md` を参照

## SEO 設定（ドメイン: seadice.win）

| ファイル | 役割 |
|---|---|
| `web/index.html` | canonical / OGP / JSON-LD / noscript コンテンツ |
| `web/robots.txt` | クローラー許可 + サイトマップ指定 |
| `web/sitemap.xml` | 全ページ URL リスト |
| `web/manifest.json` | PWA 設定 |
| `firebase.json` | キャッシュヘッダー + セキュリティヘッダー |

**Firebase カスタムドメイン設定（コンソールで手動）:**
1. Firebase コンソール → Hosting → カスタムドメインを追加
2. `seadice.win` を登録
3. DNS プロバイダーに表示される A レコードを登録
4. SSL 証明書の自動発行を待つ（〜24時間）

## Web制作方針（SEO・パフォーマンス）

SEOのためにモバイルファースト・読み込み速度を極限まで高めることを最優先とする。

### 画像の管理

**全ての画像素材は `/Users/hidenori/Developer/Images/` に置かれている。**
サイトで使用する画像はここから取得し、WebPに変換して `p/icons/` に配置すること。

```bash
cwebp -q 85 /Users/hidenori/Developer/Images/image.png -o /Users/hidenori/Developer/SEADICE/p/icons/image.webp
```

## 画像フォーマット
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
- CSS はインラインで minify して記述（外部CSS読み込みゼロ）
- Critical CSS のみインライン記述、不要なスタイルは削除
- 画像には `width` `height` 属性を必ず指定（レイアウトシフト防止）
- `<link rel="preconnect">` と `<link rel="dns-prefetch">` をheadに追加
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

## 絵文字禁止

**コード内での絵文字使用は禁止。**
Flutter Web の読み込み時に絵文字フォントが未ロードで文字化けが発生するため。

- `AppItem.icon` フィールド → 短い文字列（例: `'SRS'`, `'AI'`, `'貿'`）
- UI アイコン → `Icon(Icons.xxx)` （Material Icons を使用）
- ボタンラベル・テキスト → 絵文字を含まないプレーンテキスト
- データ定数（`_visionSlides` 等）→ 絵文字フィールド自体を設けない
