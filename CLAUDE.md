# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

SEADICE ポートフォリオ本体（`seadice.win` トップページ）は **静的 HTML** (`p/index.html`)。
Flutter アプリではないので `flutter run` / `flutter build` の対象ではない。

```bash
# デプロイ（p/ の静的ファイルを直接デプロイするだけ）
firebase deploy --only hosting # hosting のみデプロイ（functions の警告を避けるため）
```

> `firebase.json` の `public` は `"p"`。`p/` 配下を直接編集し、そのままデプロイする。ビルドステップは不要。
> 個別の Flutter アプリ（`toite`, `rakuraku`, `boueki-hub/*` など）は各アプリのリポジトリ側で `flutter build web --release` してから `p/該当ディレクトリ/` に配置する。

## Claude API プロキシ（Cloudflare Workers）

FlutterアプリでClaude APIを使うときは、APIキーをipaに埋め込まず、Cloudflare Workers経由で呼び出す。

- **Worker URL**: `https://claude-proxy.seadice-lite.workers.dev`
- **Workerファイル**: `/Users/hidenori/Developer/hiragana-ai-worker/`
- **APIキー**: Cloudflare Secretsに保存（`ANTHROPIC_API_KEY`）
- **デプロイ**: `cd /Users/hidenori/Developer/hiragana-ai-worker && wrangler deploy`

### Flutterアプリでの使い方

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

APIキーの追加・更新:
```bash
cd /Users/hidenori/Developer/hiragana-ai-worker && wrangler secret put ANTHROPIC_API_KEY
```

---

## AIアドバイスの標準フレームワーク（理論・実践・継続・目的達成）

ニッチアプリのAI診断・AI相談機能で「アドバイス」を返す場合、単なる箇条書きの提案で終わらせず、以下の4軸で構造化することを標準とする（診断結果ではなく行動提案・コーチング系の機能に適用。占い・診断のみで完結するアプリには無理に当てはめない）。

- **理論（知識）**: なぜそれが効果的なのか。行動科学・心理学・目標設定理論など、根拠のある知見を2〜3文で
- **実践**: 具体的に今すぐ何をすればいいか。実行可能な次の一歩を複数個
- **継続**: 挫折せず続けるための工夫。習慣化のコツを2〜3文で
- **目的達成**: この行動を続けた先にどんな状態（ゴール）に近づけるのか。短期的な変化と、それが積み重なった先の中長期的な目標達成イメージを2〜3文で

実装パターン（`yaritai-100`で採用。`related`の後に`goal`キーを追加して4軸に拡張する）：
- Claude APIへのプロンプトで「前置き・後書き不要、JSONオブジェクトのみ出力」を指示し、`{"theory": "...", "practice": ["...", "..."], "continuity": "...", "goal": "...", "related": [...]}` のようなキー付きJSONで返させる
- レスポンスは`jsonDecode`前にコードブロック記号（```json等）を除去し、`{`〜`}`の範囲を抽出してからパースする（Claudeが前置きを付けてしまった場合のフォールバック）
- パース失敗時は理論欄に生テキストをそのまま表示するなど、機能停止にしない
- UIは4つの独立したカード（アイコン付き）で表示し、「結果テキストの塊」として一括表示しない。「目的達成」カードは最後に置き、他3カードと視覚的に区別する（例: グラデーション背景やアクセント枠）ことで「ここがゴール」であることを伝える
- 履歴保存時は生JSONではなく、見出し付きの人が読める形式に整形してから保存する

**アプリアイコン未定を理由に品質評価を下げない**: `/improve-app`等でCLAUDE.md準拠チェックを行う際、1024×1024アイコン画像が未作成であることは実装の不備ではなくアセット待ちの状態なので、コード品質・規約準拠の評価軸に含めない（別途ユーザーがアイコン画像を用意した時点で対応する）。

---

## Flutterアプリの設定画面の標準構成

量産している家庭菜園などのニッチアプリでは、設定画面（`SettingsPage`）を以下の構成で統一する。新しいアプリを作る・既存アプリを改修するときはこの並びに揃える。

1. **アプリを一緒に育てませんか？**（最上部、目立つカードで独立配置）
   - タップで `FeedbackFormPage` に遷移。テキストボックス＋送信ボタンのみのシンプルな作り
   - 「ここを改善してほしい」「この機能が欲しい」という要望・アイデア募集の文言に絞る（バグ報告は下記2の専用カードに誘導するため、ここでは触れない）
   - 送信先は既存サイトの Firestore `feedback` コレクションを共用する（アプリごとに新しいコレクション・ルールは作らない）
2. **不具合を報告する**（1のすぐ下、独立したカードで配置）
   - タップで `BugReportFormPage` に遷移。`FeedbackFormPage` と同じ作り（テキストボックス＋送信ボタンのみ）だが、プレースホルダーは「どんな操作をしたときに」「どんな不具合が起きたか」を書いてもらう文言にする
   - 送信先は同じ Firestore `feedback` コレクションを共用し、`source` フィールドを `'{appId}-bug'` にして通常フィードバックと区別する（新規コレクションは作らない）
3. **App Storeで評価する** / **アプリを共有する** / **広告を見て開発者を応援する** / **お問い合わせ** / **関連アプリ** / **SEADICEのホームページ** / **プライバシーポリシー** / **オープンソースライセンス** / **バージョン情報**（1つのCardにまとめる）

### 1・2（フィードバック・不具合報告）の視覚的な強調ルール

3のまとめカード（通常の `ListTile` の並び）と混ざらないよう、1・2は明確に別レイヤーの見た目にする。

- **枠線でアクセントカラーを使う**: `Card` に `shape: RoundedRectangleBorder(side: BorderSide(color: _accent.withValues(alpha: .4), width: 1.5))` のように色付き枠を付ける（3の通常カードは枠なし）
- **アイコンを左に大きめ配置**: `Icon` を `CircleAvatar`（背景 `_accent.withValues(alpha: .12)`、アイコン色 `_accent`）で包み、タイトル横に配置する（3の`ListTile`は装飾なしの標準アイコンでよい）
- **タイトルは太字**: `fontWeight: FontWeight.bold` を必ず指定し、3の項目（通常ウェイト）と区別する
- **1と2で色を変える**: 1（要望）はブランドアクセント（`_accent`）、2（不具合）は警告色寄り（例: `Colors.orangeAccent` や `_accent2`）にして役割の違いを一目で伝える
- **配置順は固定**: 1→2→（余白）→3。3のカードとの間に `SizedBox(height: 24)` 程度の余白を空け、「別枠」であることを視覚的にも伝える

### 「お問い合わせ」

個人的な返信が欲しい問い合わせ用の導線。上記1・2（フィードバック・不具合報告）はFirestoreへの一方通行送信で返信できないため、返信が必要な相談はメールで受ける。

- `url_launcher` で `mailto:hi@seadice.win?subject=【アプリ名】へのお問い合わせ` を開くだけのシンプルな実装
- Firestoreの`feedback`コレクションやアプリ内フォームは使わない（返信先を確保するため素直にメールに寄せる）

```dart
ListTile(
  title: const Text('お問い合わせ'),
  onTap: () => launchUrl(Uri.parse(
    'mailto:hi@seadice.win?subject=${Uri.encodeComponent('【アプリ名】へのお問い合わせ')}',
  )),
)
```

### 「関連アプリ」

**`p/released-apps.json` を唯一の正とする。** ここに載っているアプリだけが「実際にApp Store公開済み」であり、新規アプリ作成時・改修時はこのファイルを見てから関連アプリを選定する。記憶やテンプレートの使い回しで決め打ちしない（過去に、ジャンルの全く異なる心理学系アプリ2本が使い回しで貼られたまま放置される事故があった）。

選定ルール:
- 同じジャンルの公開済みアプリがあれば2〜3個選ぶ
- 同じジャンルがまだ無い場合（新規ジャンルの1本目など）は、`released-apps.json` に載っている中から入手できるアプリを2〜3個選ぶ（ジャンル不一致でも構わない。固定の2本を使い回さない）
- `released-apps.json` が空、または対象アプリ自身しか載っていない場合は「関連アプリ」欄自体を実装しない（空の状態で放置しない）

リンク先: 各項目は `url_launcher` で `released-apps.json` の `appStoreUrl`（App Store直リンク）を開く。`https://seadice.win/apps/{appId}/` へのリンクにはしない（Web経由だとワンクッション増える上、審査中/公開後で行き先が変わる管理コストが発生するため、公開済みと確定しているものは直接App Storeへ）。

新しいアプリがApple審査を通過したら、CLAUDE.mdの「審査通過後のアプリページ更新」の作業とあわせて `p/released-apps.json` にもそのアプリを追加する。これを忘れると次に生成するアプリの関連アプリ欄が古いままになる。

### 「オープンソースライセンス」

Flutter標準の `showLicensePage()` を呼ぶだけでよい。手動でライセンス文を用意する必要はない。

```dart
ListTile(
  title: const Text('オープンソースライセンス'),
  onTap: () => showLicensePage(context: context),
)
```

### 広告はリワード広告のみ（バナー・インタースティシャルは使わない）

新規Flutterアプリでは**リワード広告のみ**を使う。バナー広告・インタースティシャル広告は実装しない。理由: インタースティシャルは操作フローの合間に強制表示されるため体験を損ねやすい。リワードは「見るか見ないかをユーザーが選べる」形だけに絞り、ユーザーの意思で広告視聴→対価（利用回数追加・応援）を得る形に統一する。

- AI診断の利用上限に達したときに出す「広告を見る」ダイアログ、および設定画面の「広告を見て開発者を応援する」（下記）のみが広告の出現ポイント。それ以外（画面遷移時・アプリ起動時・一定時間経過など）に自動で広告を挟まない

### ダークモード固定（ライト/ダーク切り替えは実装しない）

全アプリ**ダークテーマ固定**で統一する。`ThemeMode.system`追従やライトテーマ用の配色は用意せず、設定画面にもテーマ切り替えのトグルを置かない。理由: アプリごとに端末設定追従の分岐・配色ペアを保守するコストが見合わない。`ThemeData`は`ThemeData.dark()`ベースで固定し、`MaterialApp`の`themeMode`は指定しない（デフォルトのままにせず明示的に`ThemeMode.dark`を指定する）。

---

### 「広告を見て開発者を応援する」（リワード広告）

上記3のCard内、「アプリを共有する」の次に配置する。AI診断の利用上限に達したときに出す「広告を見る」ダイアログとは別に、設定画面からいつでも自発的にリワード広告を見られる導線を用意する。

- タップすると `RewardedAd.load()` → 読み込み完了後に即 `show()`。ロード中はアイコンを `CircularProgressIndicator` に差し替える
- 視聴完了（`onUserEarnedReward`）で `usage_bonus`（SharedPreferences、1日の無料回数とは別枠のボーナスカウント）に `_bonusPerAd` を加算し、SnackBarで「応援ありがとうございます！診断回数を追加しました」と表示する
- AI機能を持たないアプリ（今後作らない方針だが念のため）では、代わりに「広告視聴で運営を応援できます」という説明のみのシンプルな御礼SnackBarにする（加算対象がないため）
- ロード失敗時は握り潰さずSnackBarでエラー表示する（`AI利用回数の制限`のリワード広告と同じ規約に従う）
- `SettingsPage` は通常 `StatelessWidget` のままにし、このタイル自体を独立した `StatefulWidget`（例: `SupportDeveloperTile`）として実装して広告インスタンスのライフサイクルを局所化する
- **`_SupportDeveloperTileState` には必ず `dispose()` をオーバーライドしてロード済み広告インスタンスを解放する**。視聴完了後は`ad.dispose()`で解放しているが、視聴中に画面遷移・アプリバックグラウンド化でウィジェットがunmountされると、その解放処理が呼ばれずインスタンスがメモリに残り続ける（過去に22本のアプリでこの実装漏れが見つかった）：
  ```dart
  class _SupportDeveloperTileState extends State<SupportDeveloperTile> {
    RewardedAd? _ad;

    @override
    void dispose() {
      _ad?.dispose();
      super.dispose();
    }
  }
  ```

### Firestoreへのフィードバック送信（REST API、SDK不要）

Firebase SDK（`firebase_core` / `cloud_firestore`）や `GoogleService-Info.plist` の追加は不要。`http` パッケージだけで完結する。

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
      'source': {'stringValue': _appId},
    },
  }),
);
```

> `firestore.rules` の `feedback` コレクションは `message`（1〜200文字の文字列）と `source`（文字列）があれば誰でも `create` できるルールになっている。アプリ側で新しいコレクションを使う場合はルールの追加デプロイが必要になるので、基本は `feedback` を使い回すこと。

### App Store評価・共有

- 評価導線: `url_launcher` で `https://apps.apple.com/app/id{App Store ID}?action=write-review` を開く。審査通過前で ID が未定の場合は `_appStoreId = ''` にしておき、空なら `https://apps.apple.com/` にフォールバックする
- 共有: `share_plus` パッケージの `Share.share('紹介文\nhttps://seadice.win/apps/{appId}/')` を使う（バージョンによっては `SharePlus.instance.share(ShareParams(...))` API になるので `pubspec.yaml` のバージョンに合わせる）
- **`sharePositionOrigin` は必ず指定する**。iPadでのpopover起点座標問題として知られているが、share_plus 10.x系ではiPhoneでも端末・iOSバージョンによって`UIActivityViewController`のpresentationに失敗し例外を投げることがある（`nlp_lab`でApp Store配布後に「共有に失敗しました」エラーが実際に発生した実例あり）。iPad/iPhone問わず必ず渡すこと：
  ```dart
  Future<void> _shareApp(BuildContext context) async {
    try {
      final box = context.findRenderObject() as RenderBox?;
      await Share.share(
        '紹介文\nhttps://seadice.win/apps/{appId}/',
        sharePositionOrigin: box != null ? (box.localToGlobal(Offset.zero) & box.size) : null,
      );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('共有に失敗しました ($e)')));
      }
    }
  }
  ```
  catchブロックのエラーメッセージにも例外詳細（`$e`）を含めること。固定メッセージのみだと不具合報告時に原因を特定できない。

### 能動的なレビュー依頼（ネイティブダイアログ）

設定画面の「App Storeで評価する」（受動導線）とは別に、良い体験をしたタイミングで能動的にネイティブ評価ダイアログを出す。

- `in_app_review` パッケージの `InAppReview.instance.requestReview()` を使う（`SKStoreReviewController`のネイティブダイアログなので自前でUIを作らない。iOSの仕様上、年に一定回数までしか実際には表示されない点を理解した上で呼び出しコード自体は毎回実行してよい）
- **トリガー**: 「診断・クイズ・記録などのコア機能をN回完了した」タイミングにする（例: 3回目の完了時）。起動直後や機能未体験の状態では呼ばない
- `SharedPreferences` に完了回数と「依頼済みフラグ」を保存し、**アプリの生涯で1回だけ**呼び出す（ネイティブダイアログ自体もOS側で頻度制限されるが、アプリ側でも多重に呼ばない）
- 不具合報告直後（`BugReportFormPage`から戻った直後）など、ネガティブな体験の直後には呼ばない

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

呼び出し場所はコア機能の完了処理の末尾（例: クイズ結果表示直前、診断完了時）。

---

## 初回起動オンボーディングダイアログの標準デザイン

新しいアプリを作るときは、初回起動時に1枚だけの軽いウェルカムダイアログ（`showDialog` または `showModalBottomSheet`）を必ず実装する。狙いは「このアプリ、ちゃんと作られているな」と一瞬で感じてもらうこと。装飾を足すより余白を取ることを優先する。

### デザイン原則

- **背景は白（`Colors.white`）**。アプリ全体はダークテーマでも、このダイアログだけは明るい背景にして特別感を出す
- **上部中央にキャラクター/アプリアイコンのイラスト**（正方形、120〜160px程度）。目を惹く要素はここだけに絞る
- **ブランドカラー（`_accent`）はボタンだけに使う**。本文テキストはグレー（`Colors.black87`/`Colors.black54`）で落ち着かせる
- **文章は短く**。見出し1行＋説明1〜2行に収める。長い機能紹介・箇条書きの羅列はしない
- **余白をしっかり取る**（`padding` 24〜32px）。詰め込まない
- **ボタンは1つ**（「はじめる」など）。複数の選択肢や「あとで」的な離脱導線は作らない — 見せて即閉じられるシンプルさを優先する
- **キャラクターイラストに軽いフェード＋拡大アニメーションを付ける**（`TweenAnimationBuilder`で十分。200〜300ms程度、`opacity: 0→1` + `scale: 0.9→1.0`）。「ちゃんと作られてる感」を一段強める演出だが、ダイアログの表示自体を遅延させるほど長くしない
- **AI機能を持つアプリは、説明文の最後に「1日◯回まで無料」の一文を添える**。あとで利用上限に驚いてネガティブレビューになるのを防ぐため、上限があること自体を先に伝えておく

### 絵文字ではなくアイコン/イラストを使う

このプロジェクトは全体で絵文字禁止（Flutter Web 読み込み時に絵文字フォントが未ロードで文字化けするため。上記「絵文字禁止」セクション参照）。「絵文字を1〜3個添えて親しみやすくする」という効果は、`Icon(Icons.xxx, color: _accent)` の小アイコンや、キャラクターイラスト（`Image.asset`）に置き換えて実現する。テキスト中に絵文字文字（😊など）を直接書かない。

### 実装例

```dart
Future<void> _maybeShowOnboarding(BuildContext context) async {
  final prefs = await SharedPreferences.getInstance();
  if (prefs.getBool('onboarding_shown') ?? false) return;
  if (!context.mounted) return;
  await showDialog(
    context: context,
    barrierDismissible: false,
    builder: (ctx) => Dialog(
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(28, 32, 28, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // キャラクター/アプリアイコンのイラスト。フェード＋拡大で軽く演出する
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: 1),
              duration: const Duration(milliseconds: 250),
              builder: (_, t, child) => Opacity(
                opacity: t,
                child: Transform.scale(scale: 0.9 + 0.1 * t, child: child),
              ),
              child: Image.asset('assets/onboarding/character.png', width: 140, height: 140),
            ),
            const SizedBox(height: 20),
            const Text('ようこそ', // 見出しは短く1行
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black87)),
            const SizedBox(height: 10),
            const Text(
              'アプリの目的を1〜2文で簡潔に。', // 説明文も短く
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Colors.black54, height: 1.6),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: _accent, // ブランドカラーはボタンだけ
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () => Navigator.pop(ctx),
                child: const Text('はじめる', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    ),
  );
  await prefs.setBool('onboarding_shown', true);
}
```

`main()` 後の最初のビルド（`WidgetsBinding.instance.addPostFrameCallback`）またはホーム画面の `initState` から呼び出し、`SharedPreferences` で一度きりの表示にする。

---

## アップデート通知（新バージョン案内）の標準実装

新しいアプリを作るとき・既存アプリを改修するときは、起動時にApp Storeの最新バージョンをチェックし、古い場合は更新を促すダイアログを出す仕組みを必ず入れる。ユーザーがApp Storeを自分で確認しに行かなくても新バージョンに気づけるようにするため。

- APIキー不要の `https://itunes.apple.com/lookup?bundleId={バンドルID}` を叩き、レスポンスの `results[0].version` と `package_info_plus` で取得した現在のバージョンを比較する
- 古い場合のみダイアログを表示。強制アップデート（起動ブロック）にはせず、閉じられる任意のダイアログにする（審査中のビルドやネットワーク不調時にアプリが使えなくなるのを避けるため）
- ダイアログの「アップデートする」ボタンは `url_launcher` で `https://apps.apple.com/app/id{App Store ID}` を開く。App Store ID未定（審査通過前）の場合はこの機能自体を一旦スキップしてよい
- チェック処理はネットワークエラー時に握り潰し、ダイアログを出さないだけにする（機能停止・クラッシュさせない）

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

呼び出し場所はオンボーディングダイアログと同様、ホーム画面初回ビルド後（オンボーディングと両方出る場合はオンボーディングの後に呼ぶ）。

---

## 新規アプリを Web に追加するときのチェックリスト

新しいアプリを `seadice.win` に公開する際は、以下を必ず対応すること。
（`firebase.json` の rewrite 追加は不要。静的ディレクトリは index.html があれば自動で配信される。レガシー Flutter SPA パス（`toite`, `rakuraku`, `boueki-hub/*` 等）を新設する場合のみ rewrite が必要）

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

### 2. どこに追加するかの判断基準（重要）

`p/index.html` のトップページには「Apps」（主力アプリ）と「Explore」（ジャンル別）の2つの入口があり、新しいアプリはどちらか一方にしか追加しない。

- **既存ジャンル（kateisaien / fitness / pet-health / danshari / black-psychology）の量産アプリ**
  → トップページは触らない。該当する `p/tools/該当ジャンル/index.html` のグリッドにカードを追加するだけ。Explore 経由で自動的に辿れる。
- **既存ジャンルに当たらない単独の主力アプリ**
  → `p/index.html` の `#apps` セクション（`.apps-grid`）にカードを追加。
- **新しいジャンルそのもの**
  → 新しい `p/tools/新ジャンル/index.html` ハブページを作り、`p/index.html` の `#tools`（Explore）セクションに chip を1つ追加。

### 3. プライバシーポリシーの追加

- `p/privacy/新アプリ名/index.html` を作成
- `p/privacy/index.html` の一覧にリンクを追加

### 4. デプロイ

- `firebase deploy --only hosting`

### 5. 審査通過後のアプリページ更新（ユーザーからの一言トリガー）

新規アプリ作成時点では `p/apps/{appId}/index.html` のバッジは `App Store近日公開` のまま据え置いてよい（App Store IDが未定のため）。**ユーザーが「〇〇（アプリ名）審査通った」と伝えてきたタイミングで**、以下をまとめて対応する。

- App Store IDを確認（不明ならユーザーに聞く）
- バッジ `App Store近日公開` を実際の公開表記に変更
- 「App Storeで見る」ボタン（`https://apps.apple.com/app/id{App Store ID}`）を目立つ位置に追加
- `p/released-apps.json` にそのアプリを追加する（今後作る他アプリの「関連アプリ」欄の選定元になるため必須）
- `firebase deploy --only hosting` でデプロイ

事前に「近日公開」のまま作っておき、公開確定後にこの一括更新だけ行うことで、リリース申請時点での二度手間を避ける。

## App Storeリリース時の出力ルール

`/release`スキル実行時やApp Store Connect登録の準備をするときは、`APPSTORE_SUBMISSION.md`をファイルに書いて終わりにせず、**毎回その内容をチャット上にも直接出力する**こと。ユーザーはファイルを開かず、チャット上でそのままコピペして使いたいため。

出力対象（`APPSTORE_SUBMISSION.md`と同じ内容）:
- 基本情報（アプリ名/サブタイトル/Bundle ID/カテゴリ/年齢制限/価格/プライバシーポリシーURL/サポートURL/著作権）
- キーワード
- プロモーションテキスト
- 説明文
- 審査メモ（App Review Information）
- プライバシー（データの収集項目申告・App Privacy）

アプリ名や機能が後から変わった場合（例: タブ追加、名称変更）は、`APPSTORE_SUBMISSION.md`の該当箇所も更新してから出力する。

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

## 起動スプラッシュ画面（全アプリ共通ロゴ）

新規アプリ作成時・既存アプリ改修時は、Flutter標準の白背景スプラッシュのままにせず、SEADICE共通ロゴ（サイコロマスコット）をネイティブ起動画面に設定する。

- **ロゴ画像**: `/Users/hidenori/Developer/Images/splash.png`（背景色 `#01010B` で塗りつぶし済み、ダークテーマ背景 `#05050C` とほぼ同色）
- **パッケージ**: `flutter_native_splash` を使う（`dev_dependencies` に追加）
- **設定例**（`pubspec.yaml` に追記）:
  ```yaml
  flutter_native_splash:
    color: "#05050C"
    image: assets/splash/splash.png
    android_12:
      color: "#05050C"
      image: assets/splash/splash.png
  ```
  画像は `assets/splash/splash.png` としてアプリ側にコピーして使う（`Images/`から直接参照しない）。
- **生成コマンド**:
  ```bash
  flutter pub get
  dart run flutter_native_splash:create
  ```
- 既存アプリを改修するときは `/improve-app` のチェック項目としてこれも確認し、未対応なら追加する。

## キーボードを閉じられない不具合の防止（全アプリ必須）

多くのアプリで「入力後キーボードが自動で下がらず、次の画面に進めない」不具合が繰り返し発生している。原因はほぼ常に「画面のどこをタップしてもキーボードを閉じる仕組みが入っていない」こと。新規アプリ・既存アプリ改修時は必ず以下を実装する。

- **`TextField`を含む全画面の`Scaffold`の`body`を`GestureDetector`でラップし、`onTap`で`FocusScope.of(context).unfocus()`を呼ぶ**。これを共通Widget化して使い回すと漏れがなくなる：
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
- **入力完了・送信ボタン押下時も明示的に`FocusScope.of(context).unfocus()`を呼ぶ**（`onSubmitted`やボタンの`onPressed`の先頭）。ボタンタップだけでは自動でキーボードが閉じないケースがあるため。
- **`TextField`の`textInputAction`を適切に設定する**（最後のフィールドは`TextInputAction.done`、途中は`TextInputAction.next`）。`onSubmitted`で次のフィールドへの`FocusNode.requestFocus()`または`unfocus()`を必ず書く。

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

> この「外部リクエストゼロ」方針は `p/` 配下の静的サイトに適用されるものであり、**個別のFlutterアプリ内で使う画像には適用されない**。Flutterアプリ（記号辞典・図鑑など、写真素材が必要な機能）ではUnsplashから画像を検索・ダウンロードし、アプリの`assets/`にバンドルして良い。ダウンロードした画像は実行時に外部URLへアクセスするのではなく、`flutter pub get`前に一度取得してローカルアセットとして同梱すること（Unsplash Licenseは商用・非商用利用とも許可、著作権表示は必須ではないが`CREDITS.md`等に撮影者名とURLを残しておくと親切）。

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

## ブログ記事執筆の鉄則（AI検索対策）

SEO に加えて、Google AI Overview や ChatGPT 等の AI 検索に引用されることを目指す。

### 1. 冒頭とすべての見出し直下に「明確な結論」を書く（PREP法）

記事全体の冒頭だけでなく、**各 h2 の直下にも 120文字以内の結論文またはリスト**を必ず置く。
AI はユーザーの質問に対して見出し直下の短い答えを引用しやすい。

```
悪い例:
<h2>アブラムシの駆除方法</h2>
<p>アブラムシは家庭菜園でよく見かける害虫で、さまざまな野菜に被害をもたらします。ここでは...</p>

良い例:
<h2>アブラムシの駆除方法</h2>
<p>アブラムシは水で洗い流すか、木酢液・牛乳スプレーで即効駆除できます。農薬を使わず退治する方法を7つ紹介します。</p>
```

ルール：
- h1 の直後 → 記事全体の結論（「〇〇とは、▲▲のことです」形式）
- **h2 の直後 → そのセクションの結論を 120文字以内で断言。その後に詳細・リスト・表を続ける**
- h2 直下が `<ul>` や `<ol>` になる場合は結論文は不要。リスト自体が答えになるため

### 2. E-E-A-T（専門性・信頼性）を高める

- 年・月を明示する（例：「2026年版」「6月の作業」）
- 具体的な数値・固有名詞を使う（「pH 6.0〜6.5」「苦土石灰 100g/m²」など）
- 「〜と言われています」より「〜です」と断言する
- 根拠のない曖昧な表現（「諸説あります」「場合によっては」）は避ける

### 3. 構造化データ（Schema.org）を必ず設定

以下を JSON-LD で `<head>` 内に記述する（`@graph` 配列でまとめる）：

- `BlogPosting`（記事）: `headline`, `datePublished`, `dateModified`, `author`, `publisher`, `url`
- `BreadcrumbList`: ホーム → ブログ → 記事名の3階層

FAQ を含む記事は `FAQPage` も追加すると AI 引用率が上がる：

```json
{"@type": "FAQPage", "mainEntity": [
  {"@type": "Question", "name": "質問文", "acceptedAnswer": {"@type": "Answer", "text": "回答文"}}
]}
```

### 4. 箇条書き・表・番号リストを積極的に使う

AI は整理された情報をそのまま引用しやすい。

- 手順 → `<ol>` で番号リスト
- 比較・仕様 → `<table>` で表
- ポイントまとめ → `<ul>` で箇条書き
- 見出し直下に必ずリストか表を1つ入れることを意識する

### 記事の HTML 構成チェックリスト

記事を書いたら以下を確認する：

| チェック項目 | 基準 |
|---|---|
| h1 直後に結論文があるか | 1〜2文、断言形 |
| **各 h2 直下に結論文かリストがあるか** | **120文字以内で断言。h2 直下がすぐ `<ul>/<ol>` の場合は不要** |
| description は質問形 + 結論を含むか | 120字以内 |
| h2 の数 | 3〜5個 |
| 本文の文字数 | 800〜1500字 |
| 具体的な数値・固有名詞があるか | 最低3箇所 |
| 箇条書きか表が各 h2 に1つあるか | 必須 |
| tool-cta（アプリへのリンク）があるか | 記事末尾に必須 |
| JSON-LD に BlogPosting + BreadcrumbList があるか | 必須 |
| datePublished / dateModified が記入されているか | `YYYY-MM-DD` 形式 |
| firebase.json に rewrite を追加したか | デプロイ前に必須 |

### 記事を書いた後の修正フロー

1. 上記チェックリストで確認
2. 結論が h1 直後にない → 冒頭 `<p>` を追加・修正
3. 数値・固有名詞が少ない → 具体的な数字に置き換え
4. 箇条書きがない h2 → `<ul>` か `<ol>` を追加
5. firebase.json の rewrite を確認して追加 → `firebase deploy --only hosting`

---

## アフィリエイト商品紹介記事のフォーマット（自動生成ルール）

ユーザーから商品ジャンル名（例:「pH計」「支柱」「防虫ネット」）だけ渡された場合、以下のルールに従って確認なしで記事を1本書き上げ、デプロイまで完了させる。

### 掲載場所（重要）

アフィリエイト商品紹介記事は**ブログ（`/blog/`）ではなく`/reviews/`配下に置く**。理由: `/blog/`（開発ブログ）はトップページのnavから意図的に外されており、フッター経由でしか辿れない。商品比較記事はここに混ぜても発見されないため、`/reviews/`という独立ツリーをトップページのnav・フッター両方に導線を用意して運用する。

- パス: `p/reviews/{カテゴリ}/{スラッグ}/index.html`（カテゴリは `kateisaien` 等、`p/tools/` のジャンルと一致させる）
- カテゴリごとに `p/reviews/{カテゴリ}/index.html`（記事一覧ハブ）を用意し、新しい記事を書いたら**先頭に**カードを追加する
- 新カテゴリで最初の記事を書く場合は、`p/reviews/index.html`（レビュー全体のトップ）にもカテゴリカードを追加する
- 記事のパンくずは `HOME / REVIEWS / {カテゴリ名} / {タイトル}` とし、`REVIEWS`は`/reviews/`、カテゴリ名は`/reviews/{カテゴリ}/`にリンクする
- 関連記事セクションで既存の`/blog/`記事にクロスリンクするのは問題ない（逆方向の`/blog/`側からの言及は不要）

### 基本フォーマット

- **構成**: 価格帯別（安い／中価格／高精度・高価格）ランキング。各帯2〜3商品
- **選定基準の開示**: 「AIが比較した」ことを明記した上で、根拠を具体的に書く。誇張・検証不能な表現（「AIが100サイト以上見て判断」等）は禁止だが、「AIによる比較」自体は隠さず開示する方が読者に親切という方針
  - **本文の地の文に埋め込まず、独立した目立つバッジとして`<h1>`直後（`.body`の一番上）に置く**。CSSクラス`.ai-badge`を使う：
    ```html
    <div class="ai-badge"><strong>AIによる比較調査</strong><span>この記事はAI（Claude）が複数の通販サイトのレビュー・仕様（{比較した軸}）を横断的に比較して作成しました。特定の1サイトの評価や、利益重視になりがちな人の主観に依存していません。</span></div>
    ```
    ```css
    .ai-badge{display:flex;align-items:flex-start;gap:10px;background:rgba(0,255,209,.08);border:1px solid var(--accent);border-radius:12px;padding:14px 18px;margin-bottom:28px;font-size:13px;color:#cbd5e1;line-height:1.6}
    .ai-badge strong{color:var(--accent);font-weight:800;white-space:nowrap}
    ```
  - バッジの直後に続く冒頭の`<p>`は、AI比較の言及を繰り返さず、記事内容の要約（価格帯の分かれ方など）に専念する
- 上記以外の記事構成ルール（h1直後の結論文、各h2直下の結論文、FAQ、関連記事など）は通常のブログ記事執筆ルールに従う

### 商品情報の調査

- 記事を書く前に必ず `WebSearch` で複数の通販サイト（Amazon・楽天・価格.com・メーカー公式など）を調べ、実在する製品・型番・実売価格を確認する
- 価格・型番・仕様を捏造しない。検索で確認できなかった情報は書かない

### Amazonアフィリエイトリンク

- **アソシエイトID**: `hide04261326-22`
- 各商品名にリンクを張る: `https://www.amazon.co.jp/dp/{ASIN}?tag=hide04261326-22`（`target="_blank" rel="nofollow noopener"` を付ける）
- ASINは `WebSearch` で当該商品のAmazon商品ページURLを検索して確認する。**ASINが確認できない商品はリンクを張らずテキストのみ**にする（誤った商品へのリンクを避けるため）
- 楽天・A8等、他ASPへの言及や比較は特に指示がない限り不要（Amazonのみで完結させる）

### 画像について

- 現状は**画像なし**で運用する（サイト全体の「外部リクエストゼロ」方針のため。Amazon商品ページはJS描画で画像URLをスクレイピングできない）
- 将来的にAmazon商品リンクツールで画像URLが提供された場合のみ `<img>` で組み込む

### CTA

- 記事末尾に、ジャンルに関連する既存アプリへの `tool-cta` を設置する（例: 家庭菜園なら `/apps/kateisaien-app10/` の土壌診断ノート）

### SEO・モバイル・速度チェック（毎回必須）

`/blog`スキル（`.claude/commands/blog.md`）の「SEO・モバイル・速度チェック」チェックリストと同じ基準を`/reviews/`記事にも適用する。特に本文中・テーブル内のリンク（Amazonリンク）には`color:#7dd3fc`等で明示的に色指定し、ブラウザ標準の濃い青リンク色を黒背景に乗せない。

### 作業フロー（確認不要で実行する）

1. `ls p/reviews/{カテゴリ}/` で重複テーマがないか確認（カテゴリが未作成なら新規）
2. `WebSearch` で価格帯ごとに2〜3商品ずつ実在製品を調査
3. `p/reviews/{カテゴリ}/{スラッグ}/index.html` を作成（既存記事のCSSテンプレートを流用）
4. `p/reviews/{カテゴリ}/index.html` の先頭にカード追加（新カテゴリなら `p/reviews/index.html` にもカテゴリカード追加）
5. `firebase deploy --only hosting` でデプロイ
6. 記事URLをユーザーに報告

---

## 絵文字禁止

**コード内での絵文字使用は禁止。**
Flutter Web の読み込み時に絵文字フォントが未ロードで文字化けが発生するため。

- `AppItem.icon` フィールド → 短い文字列（例: `'SRS'`, `'AI'`, `'貿'`）
- UI アイコン → `Icon(Icons.xxx)` （Material Icons を使用）
- ボタンラベル・テキスト → 絵文字を含まないプレーンテキスト
- データ定数（`_visionSlides` 等）→ 絵文字フィールド自体を設けない
