# ニッチアプリ自動生成

SEADICEサイト用のニッチアプリを1セット生成してサイトに追加する。

## Flutterアプリのデザイン差別化（Guideline 4.3(a) スパム対策・必須）

過去に生成したアプリが全て同じ配色・同じナビゲーション構造だったため、Appleから「解約済み開発者アカウントのアプリと類似している」という理由でスパム判定を受け、審査落ちしたことがある。**新規に生成する3アプリ（app1/app2/app3）は、それぞれ異なる配色・異なるナビゲーション構造にする**こと。同一ニッチ内の3アプリ同士でも使い回し禁止。過去に生成した他ニッチのアプリとも配色を重複させない。

**配色パレット候補**（この中から未使用のものを選ぶ。単一の固定パレットを使い回さない）：

| パレット名 | 背景 | アクセント1 | アクセント2 |
|---|---|---|---|
| ダーク・ティール（禁止: 使い切り） | `#05050C` | `#00FFD1` | `#38BDF8` |
| テラコッタ・セージ | `#1B140F` | `#E0793F` | `#8FB996` |
| フォレスト・マスタード | `#11170F` | `#D9A441` | `#7FA37A` |
| ディープパープル・ゴールド | `#12081F` | `#C9A0FF` | `#F2C572` |
| ネイビー・コーラル | `#08111F` | `#FF8B6B` | `#5FB0E8` |
| ウォームグレー・ミント | `#161616` | `#4FD1A5` | `#E8B4B8` |

> 「ダーク・ティール」は既存アプリ群で使い切っているため**新規アプリでは使用禁止**。上記以外の新しい配色を自分で考案してもよい。

**ナビゲーション構造も分散させる**（3アプリすべて`BottomNavigationBar`にしない）：
- `BottomNavigationBar`（標準）
- 上部`TabBar`
- 角丸のピル型セグメントコントロール（`AnimatedContainer`で自作）

**カードレイアウトも分散させる**（`ListView`一辺倒にしない）：
- 縦一列の`ListView`
- 2列の`GridView`
- 画像中心のカード（`ClipRRect` + `Image.asset`を大きく配置）

3アプリを作る際は、上記パレット・ナビゲーション・レイアウトの組み合わせをそれぞれ変えること。

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

**3個のアプリを定義する**：
- app1・app2: メジャー系（そのニッチで需要が広いアプリ）
- app3: **Claude APIを使ったAIアプリ**（ユーザーの具体的な悩みをAIが解決するもの）

各アプリについて以下を定義する：
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

## Step 3: アプリ詳細ページ生成（3個）

`p/apps/{slug}-app1/index.html` 〜 `p/apps/{slug}-app3/index.html` を作成する。

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

## Step 4: プライバシーポリシーページ生成（3個）

`p/privacy/{slug}-app1/index.html` 〜 `p/privacy/{slug}-app3/index.html` を作成する。

各ページに含める：アプリ名、開発者（SEADICE）、連絡先 seadice.home@gmail.com、収集データ、AdMob/Firebase サードパーティ、データ削除方法。日本語。同じSEADICEデザイン。favicon `/favicon.png`。

app3（AIアプリ）はClaude APIへのテキスト送信についても明記する。

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

## Step 6: Flutterアプリスケルトン生成（3個）

`/Users/hidenori/Developer/apps-pipeline/apps/{slug}_app1/` 〜 `{slug}_app3/` に以下を作成する。

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
  shared_preferences: ^2.5.2
  intl: ^0.19.0
  url_launcher: ^6.3.0
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

app3（AIアプリ）のみ追加依存：
```yaml
  http: ^1.2.0
```

**assets/i18n/** に**日本語・英語の2言語のみ**JSONファイルを作成する：

```
assets/i18n/
  ja.json
  en.json
```

> **重要**: アプリごとにキーが異なる。app1・app2・app3のJSONを共通テンプレートからコピーしない。
> 各アプリのmain.dartで使うキーを先に決めてから、そのキーに合わせてJSONを書くこと。
> 例: app1がtab_log/tab_historyなら、app2はtab_record/tab_graphという別のキーを使う。
> 多言語対応（10言語）は過去にやっていたが、翻訳ファイルの同期コストが高く運用しきれないため廃止した。日英2言語に絞る。

各アプリで共通するキー（全アプリ必須）：
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
- インタースティシャルをタスク完了等の適切なタイミングで表示（表示間隔は最低30秒以上空ける。連続表示はリジェクト原因になる）
- リワードを「広告を見る」ボタンでプレミアム機能解放
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
- **プライバシーポリシー**: `url_launcher` で `https://seadice.win/privacy/{slug}-appN/` を開く
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

app3（AIアプリ）のmain.dartの追加仕様：
- ユーザーがそのジャンルに合った条件（サイズ・環境・好み・目的など）を入力するフォーム画面（ジャンルに合わせた入力項目にする）
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
    }),
  );
  ```
- レスポンスをカード形式で表示
- 設定画面にAPIキー入力欄は**不要**（共通の設定画面のみでOK）

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
- `MobileAds.instance.initialize()` は必ず `runApp()` の後にtry-catchで呼ぶ
- `CFBundleDisplayName` は必ず日本語アプリ名を設定する
