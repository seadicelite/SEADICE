# CLAUDE.md

SEADICE（シーダイス）のリポジトリ。中身は **seadice.win の静的サイト（`p/`）** と、その運用スクリプト。iOSアプリ（Flutter）は各アプリのフォルダで作り、規則だけをここに置いている。このファイルは毎回読まれるので短く保ち、詳しいことは下の表のファイルに書く。

## ブランド: 誠実（2026-10-15）

> **誠実なサービスで、信頼に応える。**
> AIを活用して社会の問題を見つけ、独自のデータとアプリで解決する。

- 誠実の中身は[七ヶ条](p/promise/index.html)。言葉でなく行動（確かめる・盛らない・売らない・集めない・直す）で示す。「安心・安全」のような誰でも言える言葉は掲げない
- 外向けは「会社」でなく「スタジオ」。トップの大見出しは「ASIの時代を、乗り越える。」（2026-11-06）
- 2行目の使い方・「SI時代」の意味などは [docs/strategy.md](docs/strategy.md)

## 理念（2026-10-12、すべての判断の土台）

1. ユーザーのために考えて、考えて考え抜く
2. それをサービスとして提供する
3. アプリで人生を改善する
4. どんな時でも前向きで、野心を1歩ずつ
5. 関心ごとを商品として、ツールやアプリを売る
6. ユーザーの悩みや問題を中心にメディアを作り
7. それをサポート・解決するアプリやツールを売る

流れは **悩み・問題 → メディア（知る） → ツール・アプリ（解決する） → 人生が良くなる**。迷ったら「これはユーザーの悩みを解決するか」「考え抜いたか」で決める。

## 目標（詳細は [docs/strategy.md](docs/strategy.md)）

- **目指す姿**: AIに紹介され、検索でも1位を取る**生きたサイト**（中身・数字・リンクが今も正しく、毎週少しずつ良くなる）
- **作るもの = AIが補えない部分**: 動く道具・続ける記録（端末内）・一次データ（自分で数えた数字）・確かめた出典・体系と網羅・手元に残るもの。1ページ1つの用事、そのページだけで済む。似たページは増やさずまとめる
- **AIは調べて照らし合わせる係**。文章の量産には使わない。主張ごとに出典・確かめた日・まだわからないことを書く
- **作るものはデータで決める**: ニッチで古参・競合が少ない所。調べた問題は [docs/problems/](docs/problems/README.md) にためる
- **小手先のSEOに賭けない**。変わりにくいもの（出典・一次データ・道具・誠実さ）に力を使い、効いたかは自分の数字で見る
- **見る数字**（PV・滞在時間は追わない）: 1. AIでの言及（最重要、月1回）2. `ct=seadice` からのアプリDL 3. Search Console のクリック 4. App Store の売上

## 毎日の前進（詳細は [docs/strategy.md](docs/strategy.md)・[docs/improve/](docs/improve/README.md)）

- 頼まれた作業が終わったら、その分野（ルール・デザイン・記事・ツール・アプリ・EVIDENCE）の docs/improve/ の「次にやること」と「ルールの次にやること」を1つずつ進め、「やったこと」「ルールの変更履歴」に日付つきで書く。同じ問題が二度出たらルールで防ぐ
- 作業中に見つけた小さく安全な改善はその場で直して報告する。収益・公開範囲・削除に関わるものだけ先に確認する。直せないものは「次にやること」へ
- 人の手が必要なことは [docs/improve/manual.md](docs/improve/manual.md) にためる（会話のたびに件数は知らせない）。ユーザーが結果を伝えたら該当分野に記録して行を消す
- 毎朝9時のルーティン（`trig_017jfhSdcKQDa8cbe8dM8Fgs`、月〜土）が分野を回して点検する

## どの規則がどこにあるか

| 作業 | 読むもの |
|---|---|
| サイト（`p/`）のページを作る・直す | [docs/site.md](docs/site.md)（3タイプ・12項目・画像・SEO）＋ [design/README.md](design/README.md) |
| 何を作るか・次に何をやるか・数字の記録 | [docs/strategy.md](docs/strategy.md) |
| ブラウザツール・診断を作る・直す | [docs/tools.md](docs/tools.md) |
| ブログ・レビュー記事を書く | [docs/writing.md](docs/writing.md) |
| App Store のスクリーンショット | [docs/mockup.md](docs/mockup.md) |
| Flutterアプリを作る・改修する・申請する | [docs/flutter-app.md](docs/flutter-app.md)（最初に「アプリ開発の流れと役」） |
| アプリをサイトに載せる・審査通過時の更新 | [docs/app-publish.md](docs/app-publish.md)（「〇〇審査通った」で読む。EVIDENCE追加は `/evidence {appId}`） |
| メディア・サイト・アプリ全部に共通 | [docs/neuro.md](docs/neuro.md)（脳科学マーケティングの原則。確かさA・Bだけ使う） |
| 社会の問題を調べる（事業データベース） | [docs/problems/README.md](docs/problems/README.md) |

## 全作業に共通する約束

- **絵文字禁止**（コード・ページとも。Flutter Web で文字化けし、質実剛健にも合わない。アイコンはインラインSVG／`Icon(Icons.xxx)`、`AppItem.icon` は `'SRS'` `'貿'` のような短い文字列）
- **広告・アフィリエイトは載せない**
- **登録・個人情報の収集はしない**（漏れたときに対応できる体制がないため、2026-11-03）。原則ログインなし。端末をまたぐ・課金を共通にする・荒らし対策が要るときだけ Apple／Google ログインで uid だけを保存し、メールは読まない。保存するものはプライバシーポリシーに全部書く。利用者からデータを集めない（匿名集計・カウンターも。例外はAPIの呼び出し回数と、本人が公開する投稿だけ）
- 「科学的に証明された」と書かない（[七ヶ条](p/promise/index.html)）
- **稼ぐ（2026-10-25〜）**: 事業なので稼げるかを先に考える。アプリは作る前に需要とお金を払う理由を確かめる。道具は無料、続けて使う機能やAIはサブスク。「嘘をつかない・盛らない・言い切らない」は守る
- **脳科学マーケティングを土台にする（2026-11-07〜）**: 原則は [docs/neuro.md](docs/neuro.md)。操る仕掛け（偽の残り数・煽り・やめにくい作り・依存させる報酬）は使わず、ぶつかったら誠実を取る
- **リスクベースの設計（2026-11-03〜）**: 作る前にリスクを洗い出し、持たない・上限を付ける・止められるようにする・残りは書いて受け入れる（詳細は [docs/strategy.md](docs/strategy.md)）
- App Store 提出情報は `APPSTORE_SUBMISSION.md` に書くだけでなくチャットにも出す（ユーザーはコピペする）

## 仕上げ前の点検役（[.claude/agents/](.claude/agents/)）

中〜大の作業（新しいページ・ツール・アプリ機能・ルール変更）は、コミット前に点検役に見せる。点検役は疑問を出すだけ。受け取ったら1件ずつ「取り入れる／棄却（理由を一言）」を決める。差し戻しは1回まで。誤字・リンク1本には使わない。

| 作業 | 呼ぶもの |
|---|---|
| 新しいページ・ツール・診断 | `critic` ＋ `design`（用事が1ページで済むか見るなら ＋ `user`） |
| ログイン・投稿・課金・Firebase・外部API・firebase.json | ＋ `security`（作る前と仕上げ前） |
| 研究・統計を引くページ | ＋ `source-check` |
| アプリ | [docs/flutter-app.md](docs/flutter-app.md) の「アプリ開発の流れと役」 |
| 次に何をやるか迷ったとき | `growth` |
| 何で稼ぐか・値段・新しいアプリの企画の前 | `business`（競合の確認は `market`） |
| 新しいアプリ・ツール・大きなページの設計 | `neuro`（新しいアプリでは必ず） |
| アプリにウィジェットを足す | `widget`（自分で実装まで行う。commit・提出は呼んだ側） |

## コマンドと運用

```bash
firebase deploy --only hosting   # p/ をそのまま配信（ビルド不要）
python3 scripts/apply_page_type.py {read|show|use} p/…/index.html   # 新しいページにデザインを当てる（必ず）
python3 scripts/apply_page_type.py --refresh                         # design/ を直した後に全ページへ反映
python3 scripts/check_released_apps.py && python3 scripts/build_apps_page.py   # 審査通過時のアプリ一覧更新
```

- **main は手元とクラウドの2か所から更新される**。作業前に `git pull`、手元でデプロイしたら必ず push する（しないと Actions のデプロイで本番が巻き戻る）。他の作業の未コミット変更があるときは自分の変更だけコミットし、きれいな worktree からデプロイする。IndexNow は push 後に Actions が自動で通知する
- `firebase.json` の `public` は `"p"`。静的ディレクトリは `index.html` を置けば配信される（全体を `/index.html` に飛ばす rewrite はソフト404になるので入れない）
- Flutter Web アプリ（`toite`, `rakuraku`, `boueki-hub/*` など）は各アプリ側で `flutter build web --release` して `p/該当ディレクトリ/` に置く。`canvaskit/` フォルダは消す

## サイトの構成（seadice.win）

- トップ: `p/index.html`（**頼まれない限り触らない**。デザイン注入の対象外）
- アプリ紹介: `p/tools/{appId}/`（`p/apps/` は一覧と一部の旧ページ）／ブラウザツール: `p/tools/{toolId}/` ／ ジャンル別ハブ: `p/tools/{ジャンル}/`
- 診断: `p/diagnosis/` ／ EVIDENCE: `p/evidence-series/` ／ ブログ: `p/blog/` ／ プライバシー: `p/privacy/{appId}/`
- 運営者情報: `p/about/` ／ 七ヶ条: `p/promise/` ／ 寄付: `p/support/`（アプリからはリンクしない）
- 公開済みアプリ一覧（関連アプリ選定の唯一の正）: `p/released-apps.json` ／ AI向け: `p/llms.txt` ／ 404: `p/404.html`
- デザインは**質実剛健**（グラデーション・ぼかし・光・影なし、角丸8px以下）。ページは read / show / use の3タイプ（[docs/site.md](docs/site.md)）。文字はできる限り減らし、アイコン・図にする
