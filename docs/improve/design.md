# デザイン（火曜）

## 目的
読む・魅せる・使うの用事が最短で済む見た目にする。質実剛健（飾りなし）で、どのページも同じサイトだとわかること。

## 良い状態
- p/ のページが read / show / use のどれかで、design/ の CSS が当たっている（`<body class="t-…">`）
- グラデーション・ぼかし・光・影・8pxを超える角丸がない
- 文字のコントラスト4.5:1以上、本文14px以上、タップ領域が十分
- 画像に width/height があり、ファーストビュー以外は loading="lazy"

## 点検
- `<body class="t-` がないページの数（p/index.html と Flutter SPA は除く）
- `linear-gradient` `box-shadow` `backdrop-filter` `border-radius:(9|1[0-9]|[2-9][0-9])px` を含むページの数と場所
- `<img` に width/height がないもの

## すぐ直してよいこと
- 新しいページへの `python3 scripts/apply_page_type.py {read|show|use}` の適用
- 画像の width/height・lazy の付け忘れ
- design/*.css の小さな調整と `--refresh`（見た目が大きく変わらないもの）

## 判断が必要なこと（PRにする）
- 3タイプの形・色・文字の大きさを大きく変えること、ヘッダー・フッターの作り直し

## 次にやること
1. **EVIDENCE の生成ページ（scripts/build_evidence_hub.py の CSS）を質実剛健にする**: 角丸14px・999px・グラデーションのボタンがある。design/ の show か read を当てる形に寄せる
2. **ヘッダー・フッターを全ページ共通にする**（design/README.md「これから」1）
3. **ページの中身の並び順を型にする**（design/README.md「これから」2。使うページから）

## やったこと
- 2026-10-12: 3タイプ（read/show/use）を公開（design/README.md）
