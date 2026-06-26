# SEADICE TODO

未着手は `[ ]`、進行中は `[~]` で管理します。

---

## 🎯 最優先：仕事依頼受付の整備

### ホームサイト（seadice.win）の構築
- [~] Vision セクションの作成（Hero 直下）
  - [ ] 画像スライドショーの実装（自動 + 手動切替）
  - [ ] 画像を fal.ai MCP で生成（オーダーメイドアプリのイメージ）
  - [ ] `/order` へのリンクボタンを設置
- [ ] Contact フォームの実装（Firebase Functions + SendGrid）
- [ ] About セクションのブラッシュアップ（顔写真 or アバター・スキル・実績）
- [ ] フッターにソーシャルリンク（GitHub / X など）を追加

### オーダーメイドアプリのサンプル（3本）
- [ ] サンプル① の企画・実装・掲載（ジャンル検討中）
- [ ] サンプル② の企画・実装・掲載
- [ ] サンプル③ の企画・実装・掲載
- [ ] 各サンプルに「このアプリを作った経緯・技術スタック」の説明を添える

---

## 🎮 ミニアプリの改善（言い訳ジェネレーターのみ）

- [ ] fal.ai MCP でサムネイル画像を生成・設定
- [ ] 言い訳ジェネレーターの使用回数制限（1日 N 回など）を追加

---

## 🚀 デプロイ・インフラ

- [ ] Google Search Console に登録・サイトマップ提出
- [ ] アクセス解析導入（Firebase Analytics または Plausible）
- [ ] GitHub Actions で `flutter build web` の CI を組む

---

## 🎨 デザイン・UI

- [ ] スクロール進捗バー（画面上部に細いライン）
- [ ] OGP 画像をカスタム画像に差し替え
- [ ] アプリカードのマウス追従 3D チルト効果
- [ ] `prefers-reduced-motion` 対応

---

## 🔍 SEO・AI 検索対応

- [ ] Flutter Web を `--web-renderer html` でビルドして SEO 改善
- [ ] `llms.txt` をルートに配置（AI クローラー向け）
- [ ] `<meta description>` / OGP / JSON-LD の最適化
- [ ] Lighthouse スコア 90+ を達成
