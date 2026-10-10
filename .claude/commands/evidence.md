---
description: アプリをEVIDENCEシリーズ（研究にもとづくアプリ）に追加する。紐づくメディア記事の出典から「もとになった研究」欄を作り、一覧の再生成とデプロイまで行う
argument-hint: <appId ...> | 引数なしで候補一覧
---

# /evidence — EVIDENCEシリーズにアプリを足す

`$ARGUMENTS` のアプリ（スペース区切りで複数可）を順に処理する。**確認なしで最後まで実行する。** 引数なしなら `python3 scripts/evidence.py candidates` を実行し、「候補」のアプリをすべて処理する。

呼び名は「EVIDENCEシリーズ」「研究にもとづくアプリ」。ユーザーが「科学が証明するアプリ」と言っても同じ意味として扱い、ページには「証明」と書かない（CLAUDE.md 7）。

## 手順（1アプリあたり）

1. `git pull --ff-only`（初回だけ）
2. `python3 scripts/evidence.py sources {appId}` で材料を出す。出るのは、紐づくメディア記事ごとの出典（DOI）と数字入りの文、アプリページの見出し（機能の手がかり）
   - 「どのメディアの apps[] にも無い」と出たら、CLAUDE.md 6 の手順でメディア側にアプリと記事を紐づけてからやり直す。テーマの合う記事が無ければ、そのアプリは見送ってユーザーに伝える（論文を新しく探して足さない）
   - 「紹介ページなし」なら見送る
3. 材料から2〜3件を選び、scratchpad に JSON を書く。選び方:
   - アプリの機能と1対1で対応するもの（機能に関係ない研究は入れない）
   - DOIがある論文を優先する。同じ論文を2回使わない
   - `find` は研究でわかったことを一文で、材料にある数字（人数・件数・%）を入れる。材料にない数字は書かない。「〜が示された」「〜していた」のように研究の結果として書き、アプリの効果のようには書かない
   - `src` は「著者 (年), 誌名」。3人以上なら「et al.」
   - `feature` はアプリの機能名（「アプリの〇〇」）
   ```json
   {"items": [{"find": "...", "src": "Gollwitzer & Sheeran (2006), Advances in Experimental Social Psychology",
               "feature": "アプリの「代替行動」登録", "article": "記事slug", "doi": "10.xxxx/..."}]}
   ```
4. `python3 scripts/evidence.py add {appId} {jsonのパス}` で欄を入れる（CTAの直前に入り、CSSが無ければ足される。記事・DOIが材料と合わないと止まるので、そのときはJSONを直す）
5. 全アプリが終わったら、まとめて:
   ```bash
   cd scripts && python3 build_evidence_page.py && python3 build_apps_page.py && cd ..
   ```
6. `git add` は触ったファイルだけ（`p/tools/{appId}/index.html` `p/evidence-series/` `p/apps/index.html` と新しい `p/icons/apps/*.webp`）。コミットして `git push origin main`（GitHub Actions が Hosting にデプロイする。`firebase deploy` は手元から叩かない）
7. 報告は短く: 追加したアプリと研究件数、見送ったアプリと理由、一覧の URL https://seadice.win/evidence-series/

## してはいけないこと

- 記事にない研究・数値を足す（捏造禁止）。`add` の照合をすり抜けるためにJSONの記事やDOIを書き換えない
- 「証明」「証明済み」「科学的に効果がある」と書く。チェック・盾・メダル等の認証風マークを付ける
- すでに欄があるアプリに `add` する（直すときはページを直接編集し、5以降を実行）
