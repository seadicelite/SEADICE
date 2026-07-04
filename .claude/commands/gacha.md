# ニッチアプリ自動生成

SEADICEサイト用に、Claude APIを使ったAIアプリを1本生成してサイトに追加する（1ニッチ = 1アプリ構成。詳細はStep 1参照）。

## Flutterアプリのデザイン差別化（Guideline 4.3(a) スパム対策・必須）

過去に生成したアプリが全て同じ配色・同じナビゲーション構造だったため、Appleから「解約済み開発者アカウントのアプリと類似している」という理由でスパム判定を受け、審査落ちしたことがある。**新規に生成するアプリは、過去に生成した他ニッチのアプリと配色・ナビゲーション構造を重複させない**こと。

**配色パレット候補**（この中から未使用のものを選ぶ。単一の固定パレットを使い回さない）：

| パレット名 | 背景 | アクセント1 | アクセント2 |
|---|---|---|---|
| ダーク・ティール（禁止: 使い切り） | `#05050C` | `#00FFD1` | `#38BDF8` |
| テラコッタ・セージ（禁止: 使い切り） | `#1B140F` | `#E0793F` | `#8FB996` |
| フォレスト・マスタード（禁止: 使い切り） | `#11170F` | `#D9A441` | `#7FA37A` |
| ブラック・アンバー（禁止: 使い切り） | `#0A0806` | `#E89B3D` | `#B85E14` |
| ネイビー・コーラル | `#08111F` | `#FF8B6B` | `#5FB0E8` |
| ウォームグレー・ミント | `#161616` | `#4FD1A5` | `#E8B4B8` |

> 使い切ったパレットは**新規アプリでは使用禁止**。上記以外の新しい配色を自分で考案してもよい。高級感を出したい場合は`LinearGradient`でアクセント2色をグラデーションにするとよい（ボタン・選択中タブなどに適用）。

**ナビゲーション構造・カードレイアウトも過去のアプリと変える**：
- ナビゲーション: `BottomNavigationBar` / 上部`TabBar` / 角丸のピル型セグメントコントロール（`AnimatedContainer`で自作）
- レイアウト: 縦一列の`ListView` / 2列の`GridView` / 画像・写真中心の大きなカード

過去に生成したアプリの構成を`apps-pipeline/apps/`で確認し、同じ組み合わせを避けること。

## Step 0: ジャンル・キーワードの自動選定

`ls p/tools/` を実行して既存のニッチを確認し、**重複しないもの**を候補にする。

候補ジャンルが決まったら、`/Users/hidenori/Developer/keyword-research/` のツールで狙い目度を検証する：

```bash
cd /Users/hidenori/Developer/keyword-research

# 候補となる単体キーワードを keywords.txt に書き、App Store内の競争度を確認
python3 app_store_niche_check.py keywords.txt

# 必要ならGoogle検索での競合状況・関連キーワードも確認
export SERPER_API_KEY="（キーは.envまたは環境変数から読む。ハードコード禁止）"
python3 keyword_research.py keywords.txt
```

判断基準：
- `app_store_niche_check.py` で**競争度「低」**かつ該当アプリ数が0件ではない（実需要はある）ジャンルを優先
- 大手・実績アプリ（レビュー数5000件超、または既知の大手開発者）が上位を占めるジャンルは避ける
- 「〜できない」「〜が苦手」のような悩み型ワードは、単体キーワードでの検索結果と比較して裏付けを取る（App Store内検索は複合フレーズに弱いため、単体キーワードでの結果を優先する）

この調査結果をもとにニッチを1つ選定し、スラッグ（英数字・ハイフンのみ）を決める。例: `hiking`, `study-timer`, `baby-log`

## Step 1: ニッチ定義

**1個のアプリのみを定義する**（方針変更: 2026年7月〜、AI機能を持たないアプリはリリースしない）：
- app: **Claude APIを使ったAIアプリ**（ユーザーの具体的な悩みをAIが解決するもの）。写真・テキスト入力など、そのニッチに合った入力形式でAIに投げ、具体的なアドバイス・診断・提案を返す

> 過去は「メジャー系2本 + AI 1本」の3本構成だったが、AI機能のないアプリは差別化が弱く優先度を下げた。今後はAIを核にした1本に集中する。

このアプリについて以下を定義する：
- アプリ名（30文字以内、日本語）
- サブタイトル（30文字以内、日本語）
- カテゴリ（App Storeカテゴリ、日本語）
- ターゲットユーザー
- 主要機能5つ

App Store登録用テキストは**日本語と英語の2言語のみ**生成する（多言語対応は行わない）：

| コード | 言語 | App Store Connect表記 |
|---|---|---|
| ja | 日本語 | Japanese |
| en | 英語 | English (U.S.) |

各言語で以下を生成：
- アプリ名（30文字以内）
- サブタイトル（30文字以内）
- プロモーション用テキスト（170文字以内）
- 概要（500〜1000文字）
- キーワード（100文字以内、カンマ区切り）

## Step 2: ランディングページ生成

`p/tools/{slug}/index.html` を作成する。

CLAUDE.mdを必ず読んでからHTMLを書く。

ページ構成：
1. Hero: アプリ名 + サブタイトル + ターゲットユーザー説明
2. 課題セクション: このニッチが抱える問題
3. 機能紹介（4〜5個のカード）
4. CTAセクション: `/apps/{slug}/` の詳細ページへのリンク

ルール：
- JS禁止、システムフォント（-apple-system）のみ、CSSはインラインでminify
- favicon: `/favicon.png`
- canonical: `https://seadice.win/tools/{slug}/`
- OGP・JSON-LD（WebPage + BreadcrumbList）
- モバイルファースト、h1は1つ、絵文字禁止
- デザイン: SEADICEブランドカラー（bg #05050C, accent #00FFD1, blue #38BDF8）で統一。これはマーケティングサイトなのでFlutterアプリ側の差別化ルールとは無関係
- 戻るリンク: `href="https://seadice.win/"` （絶対パス）

## Step 3: アプリ詳細ページ生成

`p/apps/{slug}/index.html` を作成する。

以下のセクションを含める：

**Section 1: Hero**
アプリ名（h1）、サブタイトル、「App Store近日公開」バッジ、プライバシーポリシーリンク

**Section 2: App Storeメタデータ（そのままコピペできる形式）**
- 名前（30字以内）
- サブタイトル（30字以内）
- カテゴリ
- プライバシーポリシーURL: `https://seadice.win/privacy/{slug}/`
- プロモーション用テキスト（170字以内）
- 概要（500〜1000字）
- キーワード（100字以内）

**Section 3: 機能一覧**（5つのカードグリッド）

**Section 4: 広告について**（AdMob バナー・インタースティシャル・リワード。AI診断の1日利用回数制限とリワード広告での追加解放についても明記）

**Section 5: 今後実装予定の機能**（3〜5個）

**Section 6: なぜこのアプリが必要か**（マーケティングコピー）

ルール：
- JS禁止、システムフォント、CSSインラインminify
- favicon: `/favicon.png`
- canonical: `https://seadice.win/apps/{slug}/`
- OGP・JSON-LD（SoftwareApplication + BreadcrumbList）
- デザイン: SEADICEブランドカラーで統一、絵文字禁止

## Step 4: プライバシーポリシーページ生成

`p/privacy/{slug}/index.html` を作成する。

含める内容：アプリ名、開発者（SEADICE）、連絡先 hi@seadice.win、収集データ、AdMob サードパーティ、**Claude API（Anthropic）への送信内容の明記**、データ削除方法。日本語。同じSEADICEデザイン。favicon `/favicon.png`。

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

## Step 6: Flutterアプリスケルトン生成

`/Users/hidenori/Developer/apps-pipeline/apps/{slug}/` に以下を作成する（1ニッチ1アプリなので`_app1`等のサフィックスは付けない）。

**pubspec.yaml**:
```yaml
name: {slug}
description: {アプリ説明}
version: 1.0.0+1
environment:
  sdk: ">=3.3.0 <4.0.0"
dependencies:
  flutter:
    sdk: flutter
  google_mobile_ads: ^9.0.0
  shared_preferences: ^2.5.2
  intl: ^0.19.0
  url_launcher: ^6.3.0
  http: ^1.2.0
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
flutter:
  uses-material-design: true
  assets:
    - assets/fonts/
    - assets/i18n/
  fonts:
    - family: NotoSansJP
      fonts:
        - asset: assets/fonts/NotoSansJP-VariableFont_wght.ttf
```

**assets/i18n/** に**日本語・英語の2言語のみ**JSONファイルを作成する：

```
assets/i18n/
  ja.json
  en.json
```

> 多言語対応（10言語）は過去にやっていたが、翻訳ファイルの同期コストが高く運用しきれないため廃止した。日英2言語に絞る。
> 過去は複数アプリでキーを使い回さないルールだったが、1ニッチ1アプリになったので単純にこのアプリのmain.dartで使うキーを決めてから書けばよい。

共通で必要なキー：
```json
{
  "app_name": "アプリ名（各言語）",
  "settings": "設定",
  "about": "このアプリについて",
  "about_app": "アプリ名",
  "version": "バージョン 1.0.0",
  "privacy_policy": "プライバシーポリシー",
  "contact": "お問い合わせ",
  "about_ads": "広告について",
  "ads_description": "AdMob広告の説明文",
  "language": "言語",
  "error_occurred": "エラーが発生しました",
  "no_data": "まだデータがありません",
  "loading": "読み込み中...",
  "save": "保存",
  "cancel": "キャンセル",
  "delete": "削除"
}
```

アプリ固有のキー（タブ名・機能テキスト等）は各アプリの内容に合わせて追加する。
**10言語すべてに同じキーセットを揃えること**（キーの過不足があると `L.t()` が key をそのまま表示する）。

`pubspec.yaml` のassetsに追加：
```yaml
  assets:
    - assets/fonts/
    - assets/i18n/
```

**多言語の実装（`easy_localization`不使用、自前実装）**：

```dart
// main.dartの上部に定義
class L {
  static Map<String, dynamic> _strings = {};
  static final _supported = ['ja','en'];

  static Future<void> load(String code) async {
    final key = _supported.contains(code) ? code : 'en';
    final data = await rootBundle.loadString('assets/i18n/$key.json');
    _strings = jsonDecode(data);
  }

  static String t(String key) => _strings[key]?.toString() ?? key;
}

// main()内でロード（SharedPreferences優先、なければ端末のlocale）
final prefs = await SharedPreferences.getInstance();
final savedLang = prefs.getString('language');
if (savedLang != null) {
  await L.load(savedLang);
} else {
  final locale = WidgetsBinding.instance.platformDispatcher.locale;
  await L.load(locale.languageCode);
}
```

**lib/main.dart**: 動くFlutterアプリを実装する。
- MaterialApp + ダークテーマ、絵文字禁止
- UIテキストはすべて `L.t('key')` で参照（ハードコード禁止）
- BottomNavigation（**4タブ**: アプリ内容に合わせた機能3つ + 最後のタブに「設定」）
- NotoSansJPフォントフォールバック
- AdMob（テストID使用）:
  - App ID: `ca-app-pub-3940256099942544~1458002511`
  - バナー: `ca-app-pub-3940256099942544/2934735716`
  - インタースティシャル: `ca-app-pub-3940256099942544/4411468910`
  - リワード: `ca-app-pub-3940256099942544/1712485313`
- バナー広告をメイン画面下部に常時表示
- インタースティシャルをAI診断実行等の適切なタイミングで表示（表示間隔は最低30秒以上空ける。連続表示はリジェクト原因になる）
- リワードを「広告を見る」ボタンで追加AI診断回数を解放（下記「AI利用回数の制限」参照）
- `main()`で必ず`WidgetsFlutterBinding.ensureInitialized()`を呼ぶ
- **`runApp()` を先に呼び、その後 `try { await MobileAds.instance.initialize(); } catch (_) {}`**（クラッシュ防止）
- `AdWidget` は `SizedBox(height: 50)` でラップ

### App Store審査（Guideline 2.1）対策：必須実装
- **空状態UI**: データが0件のとき「まだデータがありません」などのメッセージを表示。絶対にエラーやクラッシュにしない
- **エラー表示**: catch節で握り潰さない。エラーが起きたらSnackBarまたは画面上にメッセージを表示する
  ```dart
  // 悪い例（握り潰し）
  try { ... } catch (_) {}
  // 良い例
  try { ... } catch (e) {
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('エラーが発生しました')));
  }
  ```
- **ローディング状態**: 非同期処理中は`CircularProgressIndicator`を表示する
- **AdMob初期化のみ握り潰しOK**: `MobileAds.instance.initialize()`のcatchだけは例外的に`catch (_) {}`でよい

### iPhone・iPad・PCレスポンシブ対応：必須実装
- `LayoutBuilder`でブレークポイントを判定してレイアウトを切り替える
  ```dart
  LayoutBuilder(builder: (context, constraints) {
    final isWide = constraints.maxWidth > 600;
    return isWide
      ? GridView(..., crossAxisCount: 2)  // iPad・PC: 2列
      : ListView(...);                     // iPhone: 1列
  })
  ```
- グリッド表示の場合: iPhone=1列、iPad/PC=2〜3列
- テキストサイズ: `clamp`で最小・最大を指定（例: `fontSize: (constraints.maxWidth * 0.04).clamp(14.0, 20.0)`）
- 横幅が広い場合はコンテンツを中央寄せ（`Center` + `ConstrainedBox(maxWidth: 800)`）

### コード品質ルール
- `Color.withOpacity()` は禁止。`withValues(alpha: x)` を使う（Flutter 3.27+）
- `AnimatedBuilder`の未使用パラメーターは `(_, _)` と書く（Dart 3.7+ ワイルドカード）
- 未使用変数の `_` プレフィックスは正しく付ける

### 設定画面（全アプリ共通・必須実装）

BottomNavigationの最後のタブとして `SettingsPage` を実装する。

```dart
class SettingsPage extends StatelessWidget {
  // ListTile形式で縦に並べる
}
```

含める項目：
- **このアプリについて**: アプリ名・バージョン（`package_info_plus`は使わず固定文字列でOK）・開発者（SEADICE）
- **プライバシーポリシー**: `url_launcher` で `https://seadice.win/privacy/{slug}/` を開く
- **公式サイト**: `url_launcher` で `https://seadice.win/` を開く（`L.t('website')`のラベルで表示）
- **お問い合わせ**: `url_launcher` でメール `mailto:hi@seadice.win` を開く。件名にアプリ名を自動挿入する：
  ```dart
  onTap: () => _openUrl(Uri(
    scheme: 'mailto',
    path: 'hi@seadice.win',
    query: 'subject=${Uri.encodeComponent('【{アプリ名}】お問い合わせ')}',
  ).toString()),
  ```
  > 過去に `seadice.home@gmail.com` を使っていたが `hi@seadice.win` に統一した。新規アプリは必ず新しい方を使う。
- **広告について**: AdMobのテスト広告が表示されている旨を説明する `Text` ウィジェット
- **言語選択**: DropdownButtonまたはListTileで日本語・英語の2言語から選択し `SharedPreferences` に保存、即座にUIに反映

ルール：
- `Scaffold` + `ListView` でシンプルに実装する
- セクションは `ListTile(title: Text('...'), leading: Icon(Icons.xxx))` で統一
- `url_launcher` の `launchUrl` は `try-catch` でラップしてエラー時は SnackBar で通知

### main.dartのAI機能仕様（必須。全アプリがAIアプリのため標準仕様）

- ユーザーがそのジャンルに合った条件・悩みを入力する画面（ジャンルに合わせて、テキスト入力フォーム or カメラ/フォトライブラリからの画像入力のいずれか、または両方を選ぶ。写真を判断材料にできるニッチ（片付け・健康・園芸など見た目で判断できるもの）は画像診断を優先する）
- **Cloudflare Workersプロキシ経由**でClaude APIを呼び出す（APIキーはアプリ側不要）
  ```dart
  const _proxyUrl = 'https://claude-proxy.seadice-lite.workers.dev';

  final res = await http.post(
    Uri.parse(_proxyUrl),
    headers: {'content-type': 'application/json'},
    body: jsonEncode({
      'model': 'claude-haiku-4-5-20251001',
      'max_tokens': 500,
      'messages': [{'role': 'user', 'content': prompt}],
      // 画像を送る場合はcontentを配列にしてbase64画像+textを含める
    }),
  );
  ```
- レスポンスをカード形式で表示
- 設定画面にAPIキー入力欄は**不要**（共通の設定画面のみでOK）
- 診断結果の履歴を`SharedPreferences`に保存し、履歴タブで振り返れるようにする（画像診断の場合は`path_provider`でアプリのドキュメントディレクトリに画像を保存し、履歴に写真付きで表示する）

### AI利用回数の制限（必須。API課金コスト対策）

Claude APIは呼び出しごとに課金が発生するため、無制限に使わせない。以下を標準実装とする：

- 1日の無料診断回数の上限を設ける（目安: `_dailyFreeLimit = 5`）
- `SharedPreferences`に`usage_date`（`yyyy-MM-dd`）・`usage_count`・`usage_bonus`を保存し、保存日と今日の日付が異なればカウントをリセットする
- 上限に達したら診断実行前にダイアログを表示し、「広告を見る」でリワード広告視聴後に追加回数（目安: `_bonusPerAd = 3`）を付与する
- 上限到達ダイアログ・残り回数表示のUIテキストは`L.t()`で管理する

**flutter create でプロジェクト初期化とBundle ID設定**:

```bash
cd /Users/hidenori/Developer/apps-pipeline/apps/{slug}
flutter create --org win.seadice --project-name {slug} --platforms ios,android,web . --quiet
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

`CFBundleDisplayName` を日本語アプリ名に設定（`flutter create`後に実行）：
```bash
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName {日本語アプリ名}" ios/Runner/Info.plist
```

ファビコン・PWAアイコンをアプリアイコンから生成：
```bash
ICON_SRC="ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png"
sips -s format png -z 32 32   "$ICON_SRC" --out web/favicon.png
sips -s format png -z 192 192 "$ICON_SRC" --out web/icons/Icon-192.png
sips -s format png -z 512 512 "$ICON_SRC" --out web/icons/Icon-512.png
sips -s format png -z 192 192 "$ICON_SRC" --out web/icons/Icon-maskable-192.png
sips -s format png -z 512 512 "$ICON_SRC" --out web/icons/Icon-maskable-512.png
```

**README.md**: アプリ概要・ターゲット・機能・マネタイズ（AdMob）を記載。

## Step 7: firebase.json にrewrite追加

`firebase.json` の `**` catch-allの直前に以下を追加する：

```json
{"source": "/tools/{slug}/**", "destination": "/tools/{slug}/index.html"},
{"source": "/apps/{slug}/**", "destination": "/apps/{slug}/index.html"},
{"source": "/privacy/{slug}/**", "destination": "/privacy/{slug}/index.html"}
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
git add apps/{slug}/
git commit -m "Add {slug} app skeleton"
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
