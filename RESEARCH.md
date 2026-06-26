# RESEARCH.md

調べた内容・技術メモをまとめるファイルです。

---

## MCP（Model Context Protocol）

> Claude Code が外部ツール・サービスと連携するためのプロトコル。

### 概要

Anthropic が策定したオープンプロトコル。MCP サーバーを追加することで、Claude が外部サービスを直接操作できるようになる。

### 主な MCP サーバー例

| サーバー | できること |
|---|---|
| GitHub | PR 作成・Issue 管理・コードレビュー |
| Figma | デザインファイルを読んでコードに変換 |
| Supabase | DB スキーマ確認・クエリ実行 |
| Slack | メッセージ送信・チャンネル検索 |
| Playwright | ブラウザを実際に操作してテスト |
| Firebase | Firestore 操作・デプロイ管理 |

### 設定方法

`~/.claude/settings.json` に追加する。

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

### SEADICE で使えそうなもの

- **Firebase MCP** — Firestore 操作やデプロイをチャットから実行
- **GitHub MCP** — PR・Issue 管理の自動化
- **Figma MCP** — デザインを見ながらそのままコーディング

### 参考

- 公式ドキュメント: https://modelcontextprotocol.io
- Claude Code での設定: `/settings` コマンドまたは `~/.claude/settings.json`

---

## MCP サーバー別セットアップ手順

### 1. GitHub MCP

**必要なもの:** GitHub Personal Access Token

1. https://github.com/settings/tokens で PAT を発行（`repo`, `read:org` スコープ）
2. `~/.claude/settings.json` に追加:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxx"
      }
    }
  }
}
```

**できること:** PR 作成・マージ、Issue 作成・クローズ、コードレビューコメント、ブランチ操作

---

### 2. Figma MCP

**必要なもの:** Figma Personal Access Token

1. Figma → Settings → Account → Personal access tokens でトークン発行
2. `~/.claude/settings.json` に追加:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp"],
      "env": {
        "FIGMA_API_KEY": "figd_xxxx"
      }
    }
  }
}
```

**できること:** Figmaファイルの読み込み、デザイントークン取得、コンポーネント情報確認 → そのままコード生成

> **注意:** `figma-developer-mcp` パッケージは現時点で非公式。Figma 公式 MCP は準備中。

---

### 3. Firebase MCP

**必要なもの:** Firebase CLI + Google アカウント

1. `npm install -g firebase-tools` でインストール済みであること
2. `firebase login` で認証済みであること
3. `~/.claude/settings.json` に追加:

```json
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "@gannonh/firebase-mcp"],
      "env": {
        "FIREBASE_PROJECT_ID": "seadiceweb",
        "SERVICE_ACCOUNT_KEY_PATH": "/path/to/serviceAccountKey.json"
      }
    }
  }
}
```

サービスアカウントキーは Firebase Console → プロジェクト設定 → サービスアカウント → 新しい秘密鍵を生成 で取得。

**できること:** Firestore CRUD、Authentication ユーザー管理、Storage 操作

---

### 4. Playwright MCP

**必要なもの:** Node.js（追加インストール不要、npx で自動取得）

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
```

初回起動時に Playwright のブラウザバイナリが自動ダウンロードされる（数分かかる場合あり）。

**できること:** ブラウザを実際に操作（スクリーンショット、フォーム入力、クリック、ナビゲーション）、E2E テスト自動生成

---

### 5. Supabase MCP

**必要なもの:** Supabase プロジェクト URL + Service Role Key

1. Supabase Dashboard → Settings → API で `URL` と `service_role` キーを確認
2. `~/.claude/settings.json` に追加:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase"],
      "env": {
        "SUPABASE_URL": "https://xxxx.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGci..."
      }
    }
  }
}
```

**できること:** テーブル操作、RLS ポリシー確認、SQL クエリ実行、スキーマ確認

---

### 共通の注意事項

- `settings.json` に複数の MCP サーバーを同時に定義できる
- 設定変更後は Claude Code を再起動する必要あり
- API キー・トークンは絶対にコードにコミットしない（`.gitignore` 等で管理）
- サービスアカウントキーファイルも同様にリポジトリ外で管理する

---
