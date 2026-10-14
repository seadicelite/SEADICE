---
description: シーダイスが出る短い広告動画（YouTube Shorts 縦・10〜15秒）を作る・作り直す。/video {テーマ} / /video all / /video new {テーマ}
---

# /video — 短い広告動画

`$ARGUMENTS` が テーマのキー（kosodate 等）なら1本、`all` なら全テーマ、`new {メディアslug}` なら新しいテーマを足して1本作る。`app {appId}` ならアプリ紹介を1本作る。

## 置き場所（調べ直さない）

| もの | 場所 |
|---|---|
| スクリプト・設定 | `scripts/video/`（make_theme_ad.py＋themes.json・make_app_ad.py＋apps.json・make_ad.py・make_assets.py） |
| 元絵・書き出し先 | `~/Developer/Images/seadice-character/`（元絵 seadice-original.png、動画は youtube/ad-{キー}.mp4） |
| BGM | `~/Developer/youtube-auto/shorts/Linen_and_Slow_Light.mp3`（既定） |
| 道具・アプリの候補 | seadice-media の `media/{slug}.json` の `toolbox`（共有リポジトリなので pull しない。`git show origin/main:media/{slug}.json` で読む） |
| アプリのアイコン | `p/icons/apps/{appId}.webp` |

## 手順

1. テーマ別（12.5秒）: `python3 scripts/video/make_theme_ad.py {キー}`。全部は themes.json のキーを順に回す
2. 新しいテーマ: themes.json に1件足してから1.を実行。書くのは `theme`（問いかけ2行。1行目が青）・`items`（道具・アプリ3つ。アプリは `icon` と `"tag": "アプリ"`）・`media`（メディア名）・`url`。道具は toolbox から、そのテーマの悩みに一番効くもの2つ＋公開済みアプリ1つを選ぶ（未公開アプリは入れない）
3. アプリ紹介（約15秒）: `python3 scripts/video/make_app_ad.py {appId}`。apps.json に1件（hook: アプリの中にある問いかけ2行 / screens: 素の画面 `{アプリ}/screenshots/raw/*.png` と説明3つ / icon / name / lead / promise / store）。説明の数字はアプリのデータ（assets/topics.json 等）で確かめたものだけ。画面の件数表示など変わりうる数字は説明に書かない。出力は app-{appId}.mp4
4. SEADICE 全体の広告（15秒）は `make_ad.py`、チャンネル用の素材（アイコン・バナー・透かし等）は `make_assets.py`。台本を変えるときだけ中の `CARDS` を直す
5. 確認は1回だけ: 各動画から 1.5秒・8秒・11.5秒の3コマを取り出し、全テーマを1枚に並べて見る（文字のはみ出し・重なりだけ）。動画を1コマずつ何度も見ない
6. 報告: 作ったファイルと、入れた道具3つを表で。再生と音はユーザーに見てもらう

## 守ること

- 文言は「研究をもとにした」まで。「科学的に証明された」「証明済み」は使わない（7ヶ条）
- 見た目は白地・黒の細い罫線・青1色（#1A44C2）。絵文字なし。青い文字には下線も付ける
- 文字は中央の上寄り（y 700〜1350）。Shorts の右のボタンと下の題名に隠れる位置に置かない
- 新しい絵（ポーズ違い）は作れない。元絵を切り抜く・動かす・並べるだけ

## 作り直しどき

新しいアプリが審査を通った・メディアに道具が増えた・新メディアができたときに、該当テーマの動画を作り直すか提案する。
