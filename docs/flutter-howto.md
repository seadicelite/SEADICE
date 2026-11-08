# Flutterアプリの作り方（コード・手順・アプリの種類別の規則）

[flutter-app.md](flutter-app.md) から移したコード例・手順・アプリの種類別の規則（2026-11-08）。決まりは flutter-app.md にあり、ここは**その部品を実装するときだけ**該当の節を読む（全部は読まない）。

## 目次

- 部品: [Claude API プロキシ](#claude-api-プロキシcloudflare-workers) / [AIアドバイスの4軸](#aiアドバイスの4軸) / [設定画面の部品](#設定画面の部品) / [Firestoreへのフィードバック送信](#firestoreへのフィードバック送信rest-apisdk不要) / [共有](#共有share_plus-11) / [能動的なレビュー依頼](#能動的なレビュー依頼) / [アップデート通知](#アップデート通知) / [起動画面](#起動画面flutter_native_splash) / [キーボードを閉じる](#キーボードを閉じる) / [日本語フォント](#日本語フォント文字化け対策)
- Flutter Web: [ファビコン・PWA アイコン](#flutter-web-版のファビコンpwa-アイコン) / [キャッシュ設定](#デプロイ後の自動更新キャッシュ設定)
- 申請: [スクリーンショットとApp Storeでの見え方](#スクリーンショットとapp-storeでの見え方の確認)
- アプリの種類別: [通知で行動をうながすテーマの選び方](#通知で行動をうながすテーマの選び方) / [投稿のあるアプリ（SNS型）](#投稿のあるアプリsns型2026-10-24) / [問題集・クイズのアプリ](#問題集クイズのアプリ2026-10-25)

## Claude API プロキシ（Cloudflare Workers）

APIキーをipaに埋め込まず、Cloudflare Workers経由で呼び出す。

- **Worker URL**: `https://claude-proxy.seadice-lite.workers.dev`
- **Workerファイル**: `/Users/hidenori/Developer/hiragana-ai-worker/`
- **APIキー**: Cloudflare Secretsに保存（`ANTHROPIC_API_KEY`）。追加・更新は `wrangler secret put ANTHROPIC_API_KEY`
- **デプロイ**: `cd /Users/hidenori/Developer/hiragana-ai-worker && wrangler deploy`

```dart
const _proxyUrl = 'https://claude-proxy.seadice-lite.workers.dev';

final res = await http.post(
  Uri.parse(_proxyUrl),
  headers: {'content-type': 'application/json'},
  body: jsonEncode({
    'model': 'claude-haiku-4-5-20251001',
    'max_tokens': 200,
    'messages': [{'role': 'user', 'content': 'your prompt'}],
  }),
);
```

## AIアドバイスの4軸

AI相談で行動提案・コーチングを返すときは、理論（なぜ効くか2〜3文）・実践（今すぐの一歩を複数）・継続（続けるコツ2〜3文）・目的達成（続けた先の状態2〜3文）の4軸にする。占い・診断のみで完結するアプリには当てはめない。見本は `yaritai-100`。

- プロンプトで「前置き・後書き不要、JSONオブジェクトのみ出力」と指示し、`{"theory": "...", "practice": ["..."], "continuity": "...", "goal": "...", "related": [...]}` で返させる
- `jsonDecode` の前にコードブロック記号を除去し、`{`〜`}` を抽出してからパースする。失敗時は理論欄に生テキストを出し、機能を止めない
- UIは4つの独立したカード（アイコン付き）。「目的達成」は最後に置き、ほかと見た目で区別する
- 履歴は生JSONでなく、見出し付きの読める形で保存する

## 設定画面の部品

### 1・2（要望・不具合）の見た目

3のまとめカード（通常の `ListTile`）と混ざらないよう、別レイヤーの見た目にする。

- `Card` に `shape: RoundedRectangleBorder(side: BorderSide(color: _accent.withValues(alpha: .4), width: 1.5))` の色付き枠（3は枠なし）
- アイコンを `CircleAvatar`（背景 `_accent.withValues(alpha: .12)`、アイコン色 `_accent`）で包む
- タイトルは `fontWeight: FontWeight.bold`
- 1（要望）は `_accent`、2（不具合）は警告色寄り（`Colors.orangeAccent` や `_accent2`）
- 順は 1→2→`SizedBox(height: 24)`→3

### お問い合わせ（返信が要る相談はメールで）

```dart
ListTile(
  title: const Text('お問い合わせ'),
  onTap: () => launchUrl(Uri.parse(
    'mailto:hi@seadice.win?subject=${Uri.encodeComponent('【アプリ名】へのお問い合わせ')}',
  )),
)
```

### オープンソースライセンス

```dart
ListTile(
  title: const Text('オープンソースライセンス'),
  onTap: () => showLicensePage(context: context),
)
```

## Firestoreへのフィードバック送信（REST API、SDK不要）

Firebase SDK や `GoogleService-Info.plist` は不要。`http` パッケージだけで完結する。

```dart
const _appId = 'アプリ名'; // 例: kateisaien-app3
const _feedbackApiKey = 'AIzaSyDlskgg5EZdoEcj9wP-UxXxXmf-s4JJpcI'; // seadiceweb プロジェクトの公開APIキー
const _feedbackUrl = 'https://firestore.googleapis.com/v1/projects/seadiceweb/databases/(default)/documents/feedback?key=$_feedbackApiKey';

await http.post(
  Uri.parse(_feedbackUrl),
  headers: {'content-type': 'application/json'},
  body: jsonEncode({
    'fields': {
      'message': {'stringValue': text}, // 1〜200文字
      'source': {'stringValue': _appId}, // 不具合は '{appId}-bug'
    },
  }),
);
```

`firestore.rules` の `feedback` は `message`（1〜200文字）と `source`（文字列）があれば誰でも `create` できる。新しいコレクションはルールの追加デプロイが要るので、`feedback` を使い回す。

## 共有（share_plus 11）

`share_plus` は `^11.0.0` 以上、新API `SharePlus.instance.share(ShareParams(...))` で書く。旧 `Share.share` ＋10.x は iPadOS 26 でタップしても無反応になり、2.1(a) で却下された（`curiosity-type` 2026-08）。`sharePositionOrigin` は iPhone でも必ず渡す（`nlp_lab` で配布後に「共有に失敗しました」が出た）。共有ボタンの `ListTile` は `Builder` で包み、その `tileContext` から起点を取る。画面全体や空の矩形にならないよう、非空で画面内に収まる小さな矩形へ丸める `_shareOrigin(context)` ヘルパーを通すのが望ましい（下の例は最小形）。見本は審査通過済みの `enneagram`。

```dart
Future<void> _shareApp(BuildContext context) async {
  try {
    final box = context.findRenderObject() as RenderBox?;
    await SharePlus.instance.share(ShareParams(
      text: '紹介文\nhttps://seadice.win/apps/{appId}/',
      sharePositionOrigin: box != null ? (box.localToGlobal(Offset.zero) & box.size) : null,
    ));
  } catch (e) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('共有に失敗しました ($e)')));
    }
  }
}
```

catch のメッセージには `$e` を含める（固定文だと不具合報告から原因がわからない）。

## 能動的なレビュー依頼

`in_app_review` の `requestReview()`（ネイティブダイアログ）を、コア機能を3回完了した時点で、アプリの生涯で1回だけ呼ぶ。起動直後・機能未体験・不具合報告の直後には呼ばない。設定画面の「App Storeで評価する」ボタンも同じ `requestReview()` を呼んでよく（何度でも可、App Store へは遷移させない）、OSの頻度制限で出ないときは何も起きないだけでよい。

```dart
Future<void> _maybeRequestReview() async {
  final prefs = await SharedPreferences.getInstance();
  if (prefs.getBool('review_requested') ?? false) return;
  final count = (prefs.getInt('completion_count') ?? 0) + 1;
  await prefs.setInt('completion_count', count);
  if (count < 3) return;
  await prefs.setBool('review_requested', true);
  final inAppReview = InAppReview.instance;
  if (await inAppReview.isAvailable()) {
    await inAppReview.requestReview();
  }
}
```

## アップデート通知

起動時に `https://itunes.apple.com/lookup?bundleId=…` の `results[0].version` と `package_info_plus` の版を比べ、古ければ閉じられるダイアログを出す（強制しない）。App Store ID が未定（審査前）なら飛ばす。通信エラーは握り潰す。呼ぶのはホーム画面の初回ビルド後で、最初の一歩を終える前には出さない。

```dart
Future<void> _maybeShowUpdateDialog(BuildContext context) async {
  const bundleId = 'win.seadice.アプリ名';
  const appStoreId = ''; // 審査通過後にIDを設定
  if (appStoreId.isEmpty) return;

  try {
    final res = await http
        .get(Uri.parse('https://itunes.apple.com/lookup?bundleId=$bundleId'))
        .timeout(const Duration(seconds: 5));
    final results = jsonDecode(res.body)['results'] as List;
    if (results.isEmpty) return;
    final latest = results.first['version'] as String;

    final info = await PackageInfo.fromPlatform();
    if (_isNewer(latest, info.version) && context.mounted) {
      await showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('新しいバージョンがあります'),
          content: Text('最新版 $latest が利用可能です。アップデートすると新機能や修正が反映されます。'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('あとで')),
            FilledButton(
              onPressed: () {
                Navigator.pop(ctx);
                launchUrl(Uri.parse('https://apps.apple.com/app/id$appStoreId'));
              },
              child: const Text('アップデートする'),
            ),
          ],
        ),
      );
    }
  } catch (_) {
    // ネットワークエラー等は握り潰し、ダイアログを出さないだけにする
  }
}

bool _isNewer(String latest, String current) {
  final l = latest.split('.').map(int.parse).toList();
  final c = current.split('.').map(int.parse).toList();
  for (var i = 0; i < l.length; i++) {
    final cv = i < c.length ? c[i] : 0;
    if (l[i] != cv) return l[i] > cv;
  }
  return false;
}
```

## 起動画面（flutter_native_splash）

`dev_dependencies` に `flutter_native_splash`。色はアプリの `scaffoldBackgroundColor` と同じ（ダーク固定なら `#05050C`）。

```yaml
flutter_native_splash:
  color: "#05050C"
  android_12:
    color: "#05050C"
```

生成は `flutter pub get && dart run flutter_native_splash:create`。ロゴを使っていたアプリは `image:` の行と `assets/splash/` を消してから生成する。

## キーボードを閉じる

```dart
class KeyboardDismissOnTap extends StatelessWidget {
  final Widget child;
  const KeyboardDismissOnTap({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () => FocusScope.of(context).unfocus(),
      child: child,
    );
  }
}
```

各画面で `Scaffold(body: KeyboardDismissOnTap(child: ...))` のように包む。

## 日本語フォント（文字化け対策）

Flutter Web では Latin フォントが日本語グリフを持たず文字化けする。全アプリで次を行う（**Web では3・4が必須**。5・6だけでは再現することがある）。

1. `/Users/hidenori/Developer/NotoSansJP-VariableFont_wght.ttf` を `assets/fonts/` にコピー
2. `pubspec.yaml` に登録
   ```yaml
   flutter:
     assets:
       - assets/fonts/
     fonts:
       - family: NotoSansJP
         fonts:
           - asset: assets/fonts/NotoSansJP-VariableFont_wght.ttf
   ```
3. 同じファイルを `web/fonts/` にも置く（Web のビルドでは `assets/assets/fonts/...` の二重パスになり CSS から参照できないため）
4. `web/index.html` の `<head>` に宣言（`font-display: block`。`swap` だと一瞬文字化けが見える）
   ```html
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
5. `main()` で `runApp()` より前に先読み
   ```dart
   Future<void> main() async {
     WidgetsFlutterBinding.ensureInitialized();
     final fontLoader = FontLoader('NotoSansJP')
       ..addFont(rootBundle.load('assets/fonts/NotoSansJP-VariableFont_wght.ttf'));
     await fontLoader.load();
     runApp(const MyApp());
   }
   ```
6. `ThemeData` にフォールバック（Latin が優先され、日本語だけ NotoSansJP になる）
   ```dart
   textTheme: GoogleFonts.dmSansTextTheme(ThemeData.dark().textTheme)
       .apply(fontFamilyFallback: ['NotoSansJP']),
   ```

## Flutter Web 版のファビコン・PWA アイコン

青い Flutter ロゴのままにしない。アプリアイコン（1024×1024 PNG）から生成する。

```bash
ICON_SRC="assets/icon/icon.png"  # なければ ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png

sips -s format png -z 32 32  "$ICON_SRC" --out web/favicon.png
sips -s format png -z 192 192 "$ICON_SRC" --out web/icons/Icon-192.png
sips -s format png -z 512 512 "$ICON_SRC" --out web/icons/Icon-512.png
sips -s format png -z 192 192 "$ICON_SRC" --out web/icons/Icon-maskable-192.png
sips -s format png -z 512 512 "$ICON_SRC" --out web/icons/Icon-maskable-512.png
```

## デプロイ後の自動更新（キャッシュ設定）

Flutter Web の `main.dart.js` / `flutter.js` はファイル名にハッシュが付かない。`immutable`（`max-age=31536000`）を付けると1年間古い版が出続けるので、`**/*.@(js|css|wasm)` のような広いグロブで `immutable` を付けない。`firebase.json` の `headers` に次を入れる。

```json
{ "source": "/index.html",               "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/flutter_service_worker.js","headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/flutter_bootstrap.js",     "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/flutter.js",               "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/main.dart.js",             "headers": [{ "key": "Cache-Control", "value": "no-cache" }] },
{ "source": "/version.json",             "headers": [{ "key": "Cache-Control", "value": "no-cache" }] }
```

## スクリーンショットとApp Storeでの見え方の確認

- **スクリーンショット**: 見出し・サイズ・枚数・形は [mockup.md](mockup.md)（見出しを先にユーザーに選んでもらう）。実画面はアプリに `test_screenshots/shots_test.dart` を置き `flutter test test_screenshots/shots_test.dart --update-goldens` で撮る（本物のフォントとサンプルデータ。見本は Spendology）。duo の寸法は mockup.md の表の公式の値
- **ヘッダと検索結果**: `python3 scripts/appstore_preview.py {アプリのフォルダ}` で `store_preview/header.png` と `search.png` を作る。名前・サブタイトルは APPSTORE_SUBMISSION.md から読む（更新用の「変わった項目だけ」のファイルでも、見出しのアプリ名と `ja:` のサブタイトルを読み、カテゴリなどは APPSTORE_DRAFT.md から補う）。テストで描くときは CupertinoSystemText と packages/cupertino_icons/CupertinoIcons にもフォントを読み込ませる（読み込まないと□になる）。申請前に、サブタイトルが切れていないか・1〜3枚目で何のアプリか伝わるかを見る

## 通知で行動をうながすテーマの選び方

通知で小さな行動を届けるテーマ（通知de人生改善など、2026-10-14〜）は、次の3つをすべて満たすものだけ（ユーザー判断）。

1. **研究が強い**: 核の行動にメタ分析か複数のランダム化比較試験がある。1本だけの実験は研究のタブの補足にとどめる（笑う・40秒の休憩・朝の光はこの理由で保留）
2. **届いたその場で、1〜2分でできる**（お風呂・外に出るは外した）。通知を押したら確認の質問をはさまず、すぐ始める（前後の気分を毎回聞くのも「面倒」で外した）
3. **届くと嬉しい**: 注意・責める通知（「スマホを置け」「姿勢が悪い」）にしない。褒める・思い出させる・楽しみを届ける言葉にする（「もし〜なら」の決め方や暗いニュースを見ない、は研究があっても注意型なので入れない）

- 通知の文はそのテーマの研究の範囲だけで書き、研究で確かめられた形に合わせる（未来の自分は「書く」練習が確かめられたので、書くのを基本にする）
- 届く時刻はテーマごとに利用者が決められる（ランダム・決まった時刻・曜日）。初めは2テーマ程度（通知が多いと注意が散る研究 Kushlev 2016 も研究のタブに載せる）
- 研究は EVIDENCE（p/apps/evidence/data/topics.json）から、種類と人数・限界を見て選ぶ。EVIDENCE にない研究は根拠に使わない

## 投稿のあるアプリ（SNS型、2026-10-24〜）

利用者どうしが投稿を見せあうアプリ（見本は栽エンサー、`~/Developer/ライフスタイル系/saiencer`）は、「登録なし」を守ったまま審査 1.2・2.1・5.1.1(v) を通す形にする。

- **ログインは Firebase の匿名ログインだけ**（Sign in with Apple・Google は入れない）。開いた瞬間に全機能が使えるので審査のデモアカウントも要らない。審査メモに「サインイン不要」、App Review の「サインインが必要」はオフ
- **匿名アカウントの自動クリーンアップ（30日で削除）は必ずオフ**（Authentication → 設定）。オンだと使っている人のIDも30日で消える（栽エンサー 2026-10-25）。確認: `curl -s https://identitytoolkit.googleapis.com/admin/v2/projects/{id}/config -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: {id}"` の `autodeleteAnonymousUsers` が false
- 最初に投稿しようとしたとき「みんなの約束」（禁止事項と、通報を24時間以内に確認して削除・投稿を止めること）への同意を取る。投稿・ひとこと・名前には、はっきりした語だけの言葉のフィルターをかける（普通の言葉に部分一致させない）
- 投稿・ひとこと・プロフィールのどれからも「通報」「ブロック」ができる。通報は1人1件（`reports/{対象}_{uid}` とルールで対にする）、3人から通報された投稿は自動で隠す。通報は seadiceweb の feedback（source `{appId}-report`）にも送る
- 投稿停止は `bans/{uid}`（運営だけが作る）に置き、本人のデータ削除では外れないようにする。ブロック一覧などは `users/{uid}/private/` に置き、ほかの人から読めないようにする
- 設定に「すべてのデータを消す」（自分の投稿・写真・送ったひとこと・すてき・ID）
- 審査に出す前に、フィードを運営の実物の投稿で埋めておく（空だと 2.1）
- **Sign in with Apple などを使うときは Release の構成にも entitlements を付ける**（Debug だけで審査のサインインが失敗した、栽エンサー 2026-07）

## 問題集・クイズのアプリ（2026-10-25〜）

- 問題文・正解・解説は端末の記録から読まない。起動のたびに最新の問題データを正とし、学習記録だけを id で引き継ぐ。問題文か正解が変わった問題は記録を引き継がない（ドローン学科試験CBT対策 1.0.x で、79問を直しても既存の利用者に届かなかった）
- 法令・試験の問題は最新の公的な文書（例: 国土交通省の教則）で全問を確かめ、1問ずつ解説と出典（例: 教則3.1.2）を付ける。版と適用日をアプリページに書く
- 答えたあとは自動で次へ進めず、解説を読んでから「次の問題へ」を押す
- 同じ Flutter Web 版をサイトに置いているときは、問題を直したら Web 版も作り直す（`flutter build web --release --base-href /…/`。サイト側の canonical・JSON-LD・デザイン注入は残す）
