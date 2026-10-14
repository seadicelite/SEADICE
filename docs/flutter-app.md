# Flutterアプリの標準実装

SEADICE の iOS アプリ（Flutter）を新しく作る・改修するときの規則。`/gacha` `/improve-app` `/release` はこのファイルと [CLAUDE.md](../CLAUDE.md) の両方を読んでから作業する。

## 良いアプリの基準（理念から、2026-10-12〜）

CLAUDE.md の理念「ユーザーのために考え抜く」「アプリで人生を改善する」「悩みを解決するアプリを作る」を、アプリの基準にしたもの。作る前・改修の前に、この4つに答えられるかを確かめる。

1. **誰のどんな悩みか**: 悩みを1文で言える（「〇〇な人が、△△で困っている」）。もとになったメディアの記事・EVIDENCE のトピックがある
2. **使い終わったとき何が変わるか**: 状態A → 状態B（Before→After）で言える。数字で見られるならなお良い（続いた日数・減った回数など）
3. **AIのチャットでは済まない理由**: 記録して経過を見る・毎日続ける仕組み・その場でできる道具、のどれかがある（チャットで1回聞けば済むなら、アプリにしない）
4. **悩みの解決を邪魔するものがない**: 広告なし・登録なし・最初の1回が1タップで始められる。根拠は「もとになった研究」として出典つきで示す

### 目標とのつなぎ（アプリは「悩み → メディア → アプリ」の出口、2026-10-12〜）

アプリ単体で完結させず、サイトの流れ（悩み・問題 → メディア → アプリ）に載せる。規則の本体は CLAUDE.md の「アプリとメディアの相互送客」「もとになった研究」欄。アプリ側で守ること:

- **メディアへの戻り口は1本**: メディアのアプリ用ページ `https://{メディア}/apps/{appId}/` だけを入れる（個別記事のURLは入れない）。置き場所は、コア機能を終えた直後の小さなテキストリンク（3回目以降に控えめに）と、設定画面の「関連アプリ」の上の「もっと知る（SEADICEのメディア）」
- **根拠の画面**: 「もとになった研究」を出典つきで1画面入れる（記事にある研究・数字だけ。「証明された」と書かない）。研究は複数を、結論からまだわからないこと・出典まで省略せずに出す（折りたたみ・要約だけにしない）。機能をメインにし、研究は別の画面（タブ）に置いて、機能の各所から該当する研究へ飛べるようにする（2026-10-14、ユーザー判断）
- **データは端末内だけ**: 記録は SharedPreferences に置き、アカウント登録・個人情報の収集は入れない（サイト側の約束と同じ）

改修のときは、ユーザーの声（フィードバック・不具合報告・レビュー）を見て、どの基準が足りていないかから直す。

## 共通のデザイン定数

個別のFlutterアプリ（ダークテーマ固定）で使うブランド色。本書中の `_accent` / `_accent2` はこれを指す。

```dart
const _bg      = Color(0xFF05050C);   // 背景
const _accent  = Color(0xFF00FFD1);   // プライマリアクセント（ティール）
const _accent2 = Color(0xFF38BDF8);   // グラデーション用（ブルー）
const _cardBg  = Color(0xFF0C0C1A);   // カード背景
```

## 基本の約束

- **iOS Deployment Targetは`15.0`にすること（`14.0`以下は使わない、2026-08-09〜）**。Appleは2027年春以降、`MinimumOSVersion`が15.0未満のアプリのアップロード・審査提出を受け付けなくなる（App Store Connectの`ITMS-90068`警告）。`ios/Podfile`の`platform :ios`・`post_install`内の`IPHONEOS_DEPLOYMENT_TARGET`、および`ios/Runner.xcodeproj/project.pbxproj`内の`IPHONEOS_DEPLOYMENT_TARGET`（3箇所）を`15.0`に統一する。`flutter create`直後のデフォルトは`13.0`になっていることがあるので、新規アプリ作成後に必ず確認する（詳細な手順は[gacha.md](.claude/commands/gacha.md)のStep 6参照）。ipa を作る前に `grep -n "DEPLOYMENT_TARGET\|platform :ios" ios/Podfile ios/Runner.xcodeproj/project.pbxproj` で全部 15.0 か確かめる（pbxproj だけ直して Podfile の `post_install` が 14.0 のまま残り、アーカイブが失敗した例あり、2026-10-13 エニアグラム）。
- `Color.withOpacity()` は非推奨。`withValues(alpha: x)` を使うこと（Flutter 3.27+）
- `AnimatedBuilder` の未使用パラメーターは `(_, _)` と書く（Dart 3.7+ のワイルドカード）
- Flutterアプリのデータ永続化は SharedPreferences
- アプリのプライバシーポリシーは `p/privacy/{appId}/index.html`（静的HTML）で管理する（サイト側の手順は CLAUDE.md の「アプリをサイトに載せるとき」）
- 共通のデザイン定数・開発者情報は `~/Desktop/CLAUDE.md` を参照

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

## 新規アプリの企画方針（Before→After型ニッチ、2026-08-08〜）

新規アプリは、広めのジャンル・学術用語（例:「セルフコンパッション」）ではなく、**「〇〇な自分から△△な自分になりたい」という誰でも一言で理解できる対比（Before→After）** を1アプリ1テーマで直接コンセプトにする。

- **狭く具体的な悩みに絞る**: ジャンル名だけで終わらせず、「誰の・どんな具体的な状況の・どんな悩み」まで絞り込んだコンセプトにする（例:「セルフコンパッション」ではなく「仕事のミス直後の自己批判を鎮める」）
- **専門用語を経由しない**: アプリ名・コンセプトは、その悩みを持つ本人が検索しそうな・口に出しそうな平易な言葉に翻訳してから企画する。学術ジャンル名（認知行動療法、セルフコンパッション等）をそのまま前面に出さない
- **「A→B」の対比を一言で言えるか**を企画の分かりやすさのチェックポイントにする（例: 夜更かし脳→早起きできる自分、浪費癖→貯められる自分、飽き性→没頭できる自分）
- 既存の`/tools/`一覧・企画メモと重複しないか確認してから着手する
- **既存アプリのパック・機能追加で済むなら別アプリにしない**（2026-10-13、恋愛の科学が 4.3/4.2.6 で却下）: Appleは「同じアカウントの他アプリの課金・機能追加で出せないか」「コードや素材を共有していないか」を問う。特にEVIDENCEと同じ「研究を3枚のカードで読む」形のアプリは、テーマを変えただけでは別アプリにならない。テーマ別の研究はEVIDENCEのカテゴリかパックとして足す。別アプリにするのは、核となる機能（記録・道具・練習など）がどの既存アプリとも違うときだけ
- **企画の時点で2つ確かめる**（2026-10-14、安心QRが 4.3/4.2.6 で却下され防犯フィルターに統合。同じ却下が2日続いた）: ①同じデータ・リスト・仕組みを使う自分のアプリ（未申請も含む）がないか。あれば、そのアプリの機能として足す（安心QRは防犯フィルターと同じ詐欺リストを使っていた）②App Store にすでに大量にある分野（QRリーダー・電卓・タイマー・メモ・天気など）ではないか。その分野なら、違いがあっても単独のアプリにせず、既存アプリの機能にする。どちらかに当たる企画は、作り始める前にユーザーに「〇〇の機能として足す」案を出す

## Flutterアプリの設定画面の標準構成

量産している家庭菜園などのニッチアプリでは、設定画面（`SettingsPage`）を以下の構成で統一する。新しいアプリを作る・既存アプリを改修するときはこの並びに揃える。

1. **アプリを一緒に育てませんか？**（最上部、目立つカードで独立配置）
   - タップで `FeedbackFormPage` に遷移。テキストボックス＋送信ボタンのみのシンプルな作り
   - 「ここを改善してほしい」「この機能が欲しい」という要望・アイデア募集の文言に絞る（バグ報告は下記2の専用カードに誘導するため、ここでは触れない）
   - 送信先は既存サイトの Firestore `feedback` コレクションを共用する（アプリごとに新しいコレクション・ルールは作らない）
2. **不具合を報告する**（1のすぐ下、独立したカードで配置）
   - タップで `BugReportFormPage` に遷移。`FeedbackFormPage` と同じ作り（テキストボックス＋送信ボタンのみ）だが、プレースホルダーは「どんな操作をしたときに」「どんな不具合が起きたか」を書いてもらう文言にする
   - 送信先は同じ Firestore `feedback` コレクションを共用し、`source` フィールドを `'{appId}-bug'` にして通常フィードバックと区別する（新規コレクションは作らない）
3. **App Storeで評価する** / **アプリを共有する** / **お問い合わせ** / **関連アプリ** / **SEADICEのホームページ** / **プライバシーポリシー** / **オープンソースライセンス** / **バージョン情報**（1つのCardにまとめる）

### 「活動を支援する」

**新規アプリには実装しない（2026-09-30〜）。** アプリから外部の寄付ページ（`https://seadice.win/support/` 等）へ誘導すると、任意の寄付でも Guideline 3.1.1（IAP以外の決済導線）でリジェクトされる（`hiru10` 2026-09-22 の実例）。

- 新規アプリ: 設定画面に「活動を支援する」タイルを置かない。App Store Connectのサポート URL にも `/support/` を指定しない（`https://seadice.win/` にする）
- 既存アプリ: 改修時に `seadice.win/support` へのタイルを見つけたら削除する
- **リリース後に伸びたアプリだけ**、IAP（消耗型の投げ銭）で「活動を支援する」を後付けする。全アプリに課金システムを事前に仕込むことはしない
- 寄付ページ `seadice.win/support/` 自体はWebサイトからの導線としてのみ残す（アプリからはリンクしない）

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

### 広告は一切実装しない（2026-07-30〜方針転換）

新規Flutterアプリ・既存アプリ改修とも**広告機能を一切実装しない**。理由: AdMobアカウントが停止（アカウント自体が使用不能）になったため。単一の広告ネットワークに依存すると審査基準変更や誤検知で全アプリの収益化導線が同時に死ぬリスクがあり、また広告収益で相殺できない状態でAPIキー（Claude API）を使わせる導線を残すと、使われるたびに純粋な赤字になる。

- `google_mobile_ads` 依存・`RewardedAd`関連コード・設定画面の「広告を見て開発者を応援する」（`SupportDeveloperTile`）は実装しない。既存アプリに残っている場合は改修時に削除する（[/improve-app](../../.claude/commands/improve-app.md)のチェック項目を参照）
- AI診断の利用上限に達したときも広告視聴で回数を追加する導線は設けない。上限到達時は広告なしの単純なメッセージ（例:「本日の利用回数の上限に達しました。明日またお試しください」）を表示するだけにする
- Claude APIを使うアプリは、広告ボーナスで水増しされない日次無料回数の上限チェックが唯一のコスト防波堤になる。上限チェックがエラー時に無制限で通す「フェイルオープン」な実装になっていないか必ず確認する
- 開発者への応援導線はアプリ内に置かない（外部の寄付ページへのリンクは Guideline 3.1.1 でリジェクトされる。上記「活動を支援する」参照。伸びたアプリだけIAP投げ銭を後付けする）

### Claude APIを使うアプリの利用回数制限（広告なし運用の標準実装）

広告ボーナスが廃止された今、**日次無料回数のカウンターだけがAPI課金の唯一の防波堤**になる。実装がアプリごとにバラつくと防波堤として機能しないので、以下の形で統一する。

- `SharedPreferences`に「最終利用日」と「当日のカウント」の2値を保存する。呼び出し前に「保存されている日付が今日と違う→カウントを0にリセットしてから判定」という流れにする（日付が変わったら自動でリセットされる設計にし、手動リセット処理は作らない）
- 上限値の目安は**1日3回**（既存アプリのデフォルトを踏襲）。ジャンル・機能の重さに応じて変えてよいが、説明文（App Store説明文・オンボーディング）にも同じ回数を明記する
- **エラー時はフェイルクローズにする**。カウント読み込み・判定処理で例外が起きた場合は「上限に達した」扱いにしてAPI呼び出しをブロックする。広告ボーナス経由の抜け道が無くなった以上、ここがフェイルオープン（判定失敗時に通してしまう）になっているとコスト超過に直結するため、既存アプリの改修時（[/improve-app](../../.claude/commands/improve-app.md)）も含めて必ず確認する
- 上限到達時のメッセージは広告導線なしで統一: 「本日の利用回数の上限に達しました。明日またお試しください」
- カウンターのSharedPreferencesキー名は各アプリで重複しないよう `_appId` を含めるか、アプリごとに独立したキー名にする（プレフィックス無しの汎用キー名だと将来他機能と衝突するリスクがある）

### ダークモード固定（ライト/ダーク切り替えは実装しない）

全アプリ**ダークテーマ固定**で統一する。`ThemeMode.system`追従やライトテーマ用の配色は用意せず、設定画面にもテーマ切り替えのトグルを置かない。理由: アプリごとに端末設定追従の分岐・配色ペアを保守するコストが見合わない。`ThemeData`は`ThemeData.dark()`ベースで固定し、`MaterialApp`の`themeMode`は指定しない（デフォルトのままにせず明示的に`ThemeMode.dark`を指定する）。

例外は、**そのアプリのテーマ（用途）がライトでないと成り立たないとき**だけ（例: 恋愛の科学はライト固定）。例外にする場合も、固定にして切り替えは実装しない。例外にしたアプリは `docs/improve/apps.md` のルールの変更履歴に1行残す。

---

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

- 評価導線: 設定画面の「App Storeで評価する」ボタンは `in_app_review` パッケージの `InAppReview.instance.requestReview()` を呼ぶ（App Storeアプリへの画面遷移はさせない）。OS側の頻度制限で実際にはポップアップが表示されないことがあるが、その場合はボタンを押しても何も起きないだけでよい（App Storeへのフォールバック遷移は実装しない）。ポップアップが出るかどうかはBundle IDごとにOSが個別管理するため、他アプリでの表示履歴とは独立している
- コア機能完了N回目（目安3回）で自動的に呼ぶ「能動的なレビュー依頼」（後述）とロジックを共通化してよい（同じ `maybeRequestReview()`/`requestReview()` 呼び出しを設定ボタンからも叩く形でよく、生涯1回きりの制限とは別に手動ボタンは何度でも呼び出し可）
- 共有: **`share_plus` は `^11.0.0` 以上を使い、必ず新API `SharePlus.instance.share(ShareParams(text: ..., sharePositionOrigin: ...))` で実装する**。旧 `Share.share(...)` 静的API＋`share_plus` 10.x系の組み合わせは、iPadOS 26 で `UIActivityViewController` を presentation できず「タップしても無反応（例外も飛ばないので catch のスナックバーも出ない）」になり、**Apple審査で Guideline 2.1(a) リジェクトを受けた実例あり**（`curiosity-type` 2026-08、iPad Air 11-inch M3 / iPadOS 26.6.1）。新規アプリ・既存アプリ改修とも `pubspec.yaml` が 10.x のままなら `^11.0.0` に上げて `flutter pub get` してから実装する。審査通過済みの `enneagram` が 11.x + 新API の実装リファレンス。
- **`sharePositionOrigin` は必ず指定する**。iPadでのpopover起点座標問題として知られているが、iPhoneでも端末・iOSバージョンによって`UIActivityViewController`のpresentationに失敗し例外を投げることがある（`nlp_lab`でApp Store配布後に「共有に失敗しました」エラーが実際に発生した実例あり）。iPad/iPhone問わず必ず渡すこと。共有ボタンの `ListTile` は `Builder` で包み、その `tileContext`（タイル自身の `RenderBox`）から起点矩形を取る。画面全体・空の矩形にならないよう、非空かつ画面内に収まる小さな矩形へ丸める `_shareOrigin(context)` ヘルパー経由が望ましい：
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

このプロジェクトは全体で絵文字禁止（Flutter Web 読み込み時に絵文字フォントが未ロードで文字化けするため。末尾の「絵文字禁止」セクション参照）。「絵文字を1〜3個添えて親しみやすくする」という効果は、`Icon(Icons.xxx, color: _accent)` の小アイコンや、キャラクターイラスト（`Image.asset`）に置き換えて実現する。テキスト中に絵文字文字（😊など）を直接書かない。

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

## 起動画面（ロゴは出さない、2026-10-13〜）

起動画面には SEADICE のロゴを出さず、アプリの背景色だけにする（ユーザー判断: ロゴは待たされる感じがして、いらない）。iOS は起動画面そのものをなくせないので、アプリの最初の画面と同じ色の無地にして、切り替わりを目立たせない。Flutter 標準の白い起動画面のままにはしない（ダークのアプリで白く光るため）。

- **パッケージ**: `flutter_native_splash`（`dev_dependencies`）
- **設定例**（`pubspec.yaml`。色はアプリの `scaffoldBackgroundColor` と同じにする。ダーク固定なら `#05050C`）:
  ```yaml
  flutter_native_splash:
    color: "#05050C"
    android_12:
      color: "#05050C"
  ```
- **生成**: `flutter pub get && dart run flutter_native_splash:create`。ロゴを使っていたアプリは `image:` の行と `assets/splash/` を消してから生成する
- 既存アプリは、改修するついでに `/improve-app` のチェックでロゴを外す（ロゴを外すためだけの再申請はしない）

## 文字の大きさとレスポンシブ（全アプリ、2026-10-13〜）

「下から出るシートの文字が小さい」「iPad・Macで間延びする」とユーザーから指摘があった（エニアグラム 1.1.0 で修正）。

- **下から出る読みもの（showModalBottomSheet）**: 本文は `fontSize: 16`・`height: 1.8` 以上を明示する（未指定だと14pxになる）。`isScrollControlled: true`・`useSafeArea: true` にし、中身を `SingleChildScrollView` で包んで高さは画面の85%まで（既定だと画面の半分で切れ、長い本文がはみ出す）。`constraints: BoxConstraints(maxWidth: 640)` でiPad・Macでも読みやすい幅にする。見本: 心理学系/enneagram の `_showReadingSheet`
- **タブレット・Mac**: `MaterialApp.builder` で、画面の短い辺が600以上なら `textScaler` を1.15倍にする（端末の文字サイズ設定に掛け合わせる）。本文の列は `ConstrainedBox(maxWidth: 600〜900)` で中央に置く
- **小さすぎる文字を作らない**: 補助テキストも12px以上。タブのラベルなど幅が足りないときだけ11pxまで
- **はみ出しを防ぐ**: アイコン＋見出しの `Row` では、見出しを `Expanded` で包む（英語など長い訳で横にはみ出す）。リリース前に、スマホ幅とiPad幅、日本語と長い言語で結果画面を描画するウィジェットテストを1本置く

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

### 5. `main()` で先読み（Flutter ネイティブ向け保険）
```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final fontLoader = FontLoader('NotoSansJP')
    ..addFont(rootBundle.load('assets/fonts/NotoSansJP-VariableFont_wght.ttf'));
  await fontLoader.load();
  runApp(const MyApp());
}
```

### 6. `ThemeData` にフォールバック設定
```dart
textTheme: GoogleFonts.dmSansTextTheme(ThemeData.dark().textTheme)
    .apply(fontFamilyFallback: ['NotoSansJP']),
```

> Latin フォント（Syne / DM Sans）が優先され、日本語グリフのみ NotoSansJP にフォールバックする。
> **Web では手順3・4が必須**。手順5・6だけでは文字化けが再現することがある。

### フォント先読みの原則（文字化けゼロにするための順序）

文字化けは「フォントが読み込まれる前に描画が始まる」ことで起きる。2段構えで防ぐ。

- **ブラウザ側**: `@font-face` は必ず `font-display: block`（`swap` にすると一瞬文字化けが見える）。手順4の通り
- **Dart側**: `await fontLoader.load()` を `runApp()` より前に置く。手順5の通り

## Flutter Web 版のファビコン・PWA アイコン

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

## スクリーンショットとApp Storeでの見え方の確認（2026-10-13〜）

- **スクリーンショット**: 見出し・サイズ・枚数・形は [mockup.md](mockup.md) に従う（全アプリ共通。見出しを先にユーザーに選んでもらう）。実画面は、アプリに `test_screenshots/shots_test.dart` を置き `flutter test test_screenshots/shots_test.dart --update-goldens` で撮る（本物のフォントとサンプルデータで描く。見本は Spendology）。duo の寸法は App Store Connect に出ている公式の値（mockup.md の表）を使う
- **ヘッダと検索結果**: `python3 scripts/appstore_preview.py {アプリのフォルダ}` で `store_preview/header.png`（アイコン・名前・サブタイトル・年齢/カテゴリ/価格）と `search.png`（検索結果の1行とスクリーンショット3枚）を作る。名前・サブタイトルは APPSTORE_SUBMISSION.md から読む（更新用の「変わった項目だけ」のファイルでも、見出しのアプリ名と `ja:` のサブタイトルを読み、カテゴリなどは APPSTORE_DRAFT.md から補う）。テストで描くときは Cupertino のタブの文字（CupertinoSystemText）とアイコン（packages/cupertino_icons/CupertinoIcons）にもフォントを読み込ませる（読み込まないと□になる。愛着スタイル診断で実際に起きた）。申請前に、サブタイトルが切れていないか・1〜3枚目で何のアプリか伝わるかを見る

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
