# あなたにお願いしたいこと（手動タスク）

Claude やルーティンではできないこと（アカウントにログインして数字を見る、外のAIに聞く、PRのマージ、方針の判断、App Store の作業など）をここにためる。会話を始めると、未対応の件数と上のほうの項目を Claude が知らせる。

- 終わったら `- [x]` にするか、Claude に「〇〇やった」「結果は〜」と伝える（Claude が記録して、次の改善に使う）
- 書き方: `- [ ] 期限か頻度 | 分野 | やること — なぜ必要か（追加日）`。上ほど急ぐ・効くもの

## 未対応

- [ ] すぐ | アプリ | 毎日脳トレ記録 1.1.0（ビルド3）の 5.1.2(i) 指摘に対応する: App Store Connect の「App のプライバシー」で、v1.0 の AdMob の「識別子（デバイスID）」「使用状況データ（広告データ）」と「トラッキングに使用」を削除し、「ユーザーコンテンツ > その他（要望フォーム）・アプリの機能・紐付けなし・トラッキングなし」だけにして公開 → 審査の指摘に英語で返信（文面は会話に出した）。新しいビルドは不要（コードに広告SDK・トラッキングはない） — ラベルが v1.0 の広告入りのままで、ATT なしでトラッキングしていると見なされた（2026-10-15）
- [ ] 近いうちに | アプリ | 通知de人生改善 1.1.0（旧 通知deマインドフルネス、ビルド5）を申請する: ipa はできている（`~/Developer/メンタルヘルス予防系/notify-mindfulness/build/ios/ipa/通知de人生改善.ipa`。同じフォルダの「通知deマインドフルネス.ipa」は前の版なので使わない）。Transporter でアップロードし、App Store Connect でアプリ名・サブタイトル・新機能・説明文・キーワード・審査メモ（`APPSTORE_SUBMISSION.md`、チャットにも出した）を入れ、スクリーンショットを `screenshots/6.3`・`duo`・`ipad` に差し替える（日本語だけ）。App Privacy は変更なし。申請前に、通知を長押しして「やった」が記録されるかを一度試す（2026-10-15）
- [ ] 近いうちに | アプリ | HSPナビ 1.1.0（ビルド5）を申請する: ターミナルで `cd ~/Developer/心理学系/hsp-relationship-check && flutter build ipa --release` → Transporter でアップロード。新機能・説明文・審査メモ・App Privacy は `APPSTORE_SUBMISSION.md`（説明文から「広告視聴で追加」「HSP診断」を外した版。App Privacy は AdMob の「識別子」「使用状況データ」を外し、任意の要望フォームを足す）（1.0 は広告入り、1.1.0 は広告なし）。署名なしビルドは通っている — 今の 1.0 は7月から更新がなく、広告SDK入り・寄付リンクあり（3.1.1 で却下されうる）のまま（2026-10-14）
- [ ] 近いうちに | アプリ | HSPナビのセルフチェックを研究の尺度（HSP-J10）にするため、作者の飯村周平先生（と訳者の髙橋亜希先生）に利用の許諾をお願いする: 依頼文の下書きは `~/Developer/心理学系/hsp-relationship-check/PERMISSION_REQUEST.md`（〔名前〕を埋め、連絡先は researchmap などで確認）。返事が来たら Claude に条件ごと伝える — 論文の項目を許諾なしにアプリやサイトに載せてよい根拠がないため（2026-10-14）
- [ ] 申請前 | アプリ | 「そのリンクちょっと待った」（安心QRを作り替えた新アプリ）の申請準備: ①Google Cloud で Web Risk API を有効にしてAPIキーを作り、`cd ~/Developer/url-check-worker && wrangler secret put WEB_RISK_API_KEY` で入れる（月10万回まで無料。入れるまでは端末内の点検＋AIだけで判定）②（できれば）Anthropic のAPIキーも `wrangler secret put ANTHROPIC_API_KEY` で同じ Worker に入れる（入れるまでは claude-proxy 経由で、混んだときにほかのアプリと回数の上限を分け合う）③アイコンを新しくする（今は安心QRのQRの絵のまま。手のひらの「ちょっと待った」など、希望があれば Claude に）④実機で「貼って確かめる」「QRコードを読む」「写真から読む」と、共有メニュー（メッセージやSafariでリンクを長押し→共有→「ちょっと待った」）を試す。共有メニューは App Group を使うので、Xcode で一度 Runner と ShareCheck の「Signing & Capabilities」を開き、App Groups に group.win.seadice.linkMatta が付いているか確かめる（自動署名なら Archive 時に登録される） ⑤App Store Connect に新規登録（Bundle ID `win.seadice.linkMatta`）。文面は `~/Developer/詐欺予防系/link_matta/APPSTORE_SUBMISSION.md` ⑥安心QR（win.seadice.qrGuard）には返信も再提出もしない — 安心QRが 4.3 で却下され、「AIで危険度を出す」アプリに作り替えたため（2026-10-14）
- [ ] 1.5.0 申請前 | アプリ | App Store Connect で EVIDENCE のアプリ内課金を5つ作る（すべて非消耗型）: `win.seadice.evidence.pack01`「からだと暮らしの常識」160円、`pack02`「人と心」320円、`pack03`「脳と学びと毎日の習慣」540円、`win.seadice.evidence.pack04`「恋愛の科学」320円、`win.seadice.evidence.ultra`「ULTRA」1,500円（今あるパックも今後のパックも全部）。説明は evidence/APPSTORE_SUBMISSION.md の「アプリ内課金」の表（45文字以内。pack04 だけ access.json より短い）。審査用スクショ＝パックのトピックを開いた購入画面。1.5.0 のバージョンに5つとも追加して一緒に提出。値段がその金額で選べなければ近い価格で（2026-10-13）
- [x] 近いうちに | アプリ | 愛着スタイル診断 1.1.0（ビルド6）を申請する: ターミナルで `cd ~/Developer/心理学系/attachment_style && flutter build ipa --release` → Transporter でアップロード。新機能・サブタイトル・説明・キーワード・App Privacy・審査メモは `APPSTORE_SUBMISSION.md`（会話にも出した文面）。サブタイトルと説明が「AIが分析」のままだと中身と合わない。App Privacy は「診断の回答を Claude API に送る」をやめ、任意のフィードバックだけにする。スクリーンショットは「相手を選ぶ」「結果（4つの型の図）」「相性」に入れ替えると伝わりやすい — AIを外して研究の尺度に変え、umbra の記事とつないだ版（2026-10-13） → 2026-10-13 申請済み（ユーザー）
- [x] 近いうちに | アプリ | やめラボ 1.1.0 を申請する: ターミナルで `cd ~/Developer/依存症対策系/yame-lab && flutter build ipa --release` → Transporter でアップロード。「このバージョンの新機能」と、差し替える「説明」「サブタイトル」は会話に出した文面（アプリの中身が「やめたいことを書く」形に変わったため、説明文も変える）。スクリーンショットは「やめたいことを書く」「衝動が来た」「改善」（量のグラフ・ふりかえり）の画面に入れ替えると伝わりやすい。App Privacy は変更なし（記録は端末内だけ、送るのは任意のフィードバックのみ） — 新機能（衝動が来た・量のグラフ・きっかけ・書き出しなど）と、iPad で共有が無反応になる恐れ（share_plus 10）の修正が入る（2026-10-13） → 2026-10-13 申請済み（ユーザー）
- [x] 近いうちに | アプリ | エニアグラム性格診断 1.1.0（AIなし版）を申請する: ターミナルで `flutter build ipa` → アップロード。App Store Connect でアプリ名を「エニアグラム性格診断」（AIを外す）、新機能・審査メモ・App Privacy（AdMob と診断回答を「収集しない」に）を差し替える。中身は 心理学系/enneagram/APPSTORE_SUBMISSION.md の先頭の節 — 今のストア表記は「AI」「Claude API に送信」のままで、実態と合わなくなる（2026-10-13） → 2026-10-13 申請済み（ユーザー）。審査通過の連絡でサイトのAI表記を外す（docs/improve/apps.md）
- [x] 近いうちに | アプリ | Life's RPG 1.1.2（ビルド9）を申請する: 寄付リンクの削除・共有を share_plus 11 の新しい書き方に・Deployment Target 15.0 は Claude が済ませ、署名なしビルドも通った（2026-10-13）。ターミナルで `cd ~/Developer/生産性系/life_is_rpg && flutter build ipa` → アップロード。新機能の文面は「設定画面を整理しました。iPad でアプリの共有が開かないことがある問題を直しました。」— 寄付リンクは審査 3.1.1 で却下された実例があるため → 2026-10-14 申請済み
- [x] 近いうちに | 全体 | firestore.rules に足した belief_counts（一次データ用の匿名カウンター）を本番に反映する: ターミナルで `firebase deploy --only firestore:rules` — Claude からは本番への反映が止められたため（2026-10-12） → 2026-10-13 取り下げ（ユーザーが「データを取りたくない」と判断。belief_counts をルールから消して本番に反映）
- [x] 近いうちに | 全体 | 理念の「ツールやアプリを売る」と、今の方針「ユーザーは無料、払うのは第三者（2026-09-30）」「EVIDENCE の課金は利用者が増えるまで停止」のどちらを優先するか決める — 売り方（買い切り・サブスク・投げ銭・第三者）で、ツールとアプリの作り方が変わる（2026-10-12） → 2026-10-13 EVIDENCE はアプリで売ると決定（機能は全部無料、追加のたびにパックを買い切りで売る、サイトは全部無料）。ただし 1.4.0 は全部無料で出し、パック課金は設計を練ってから（docs/improve/apps.md）
- [x] 近いうちに | 記事 | AI時代の困りごと（ai.seadice.win）のデザインを3案から選ぶ: A 取扱説明書（白×黒罫線×青、症状に番号）／B 相談ログ（チャット風）／C エラー表示（黄色の帯）。見本は https://claude.ai/artifact/A6QpX3bAcBxLaRtuKuSPnW 。おすすめは A。混ぜてもよい — このメディアだけ専用デザインがなく、他の暗いメディアと見分けがつかない（2026-10-13） → 2026-10-13 A に決定・反映済み（seadice-media 28a98538a。media/ai.json の theme・mastheadHtml・extraCss・articleCss）
- [x] 申請前 | アプリ | 安心QR（qr-guard）の申請準備: ①アイコン 1024px を `~/Developer/詐欺予防系/qr_guard/assets/icon/icon.png` に置いて `dart run flutter_launcher_icons`（デザインの希望があれば Claude に）②App Store Connect に新規登録（名前「安心QR - QRコード・バーコード読み取り」、サブタイトル「AI時代の詐欺QRを、開く前にチェック」。プロモーションテキスト「AIで偽サイトは一瞬で作れる時代。開く前に、行き先をひと確認。」。アプリはAIを使っていないので「AIのQRリーダー」とは書かない。似た名前「安心スキャン」が他社にあるため後半とサブタイトルで違いを出す）（Bundle ID `win.seadice.qrGuard`）③ `/release` で提出文面を作る。BOHAN の `/apps/qr-guard/` ページは作成済み（公開前は noindex。審査通過時に bohan.json の安心QR に appStoreId を足すと記事にカードが出る）。実機でカメラ・写真から読む・画像の保存を試す — 読む・作る・検索するがそろい、署名なしビルドまで通っている（2026-10-13）
- [ ] 2026-11はじめ（以後毎月） | EVIDENCE | evidence.md の「AIに聞く質問」10問を ChatGPT・Perplexity・Google AIモードに聞き、SEADICE が出たかを教える — AIでの言及は外のAIに聞くしか測れない（2026-10-12）
- [ ] 2026-11はじめ（以後毎月） | アプリ | App Store Connect のアナリティクスで、アプリ別の ct=seadice のダウンロード数を教える — 11月中旬に Google Play に出す1本を決める材料（2026-10-12）。10月分はとらない（ユーザー判断、2026-10-13）
- [ ] 2026-11上旬 | EVIDENCE | Search Console の「検索パフォーマンス」をクエリ別・ページ別で CSV にして渡す — 1問1ページ19本の順位を見て、5〜20位から直す（2026-10-12）
- [ ] 随時 | 全体 | ルーティンが出した PR（ブランチ routine/…）を GitHub で見てマージかクローズ — 判断が必要な変更だけが PR になる（2026-10-12）



## 終わったこと

- 2026-10-13: 運営者向けツール（appstore-niche・image-resize）を削除（ユーザー判断）
- 2026-10-13: body-language-scan・lifeisrpg のプライバシーポリシーを作成（事実はアプリのソースコードで確認。Claude が対応）
- 2026-10-12: caffeine-cutoff の出典 DOI（10.1016/j.smrv.2023.101764）を手元で確かめてリンク（Claude が対応）
- 2026-10-12: /about/ に運営者名（Hidenori Nakamura、App Store 開発者ページへのリンク）と、AIを使って書いていることを明記（構造化データの founder・FAQ も）
