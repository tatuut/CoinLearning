# Backend - Claude Code Server (OAuth認証版)

Node.js + Express.js + WebSocket サーバー

**認証方式**: Claude Plan Max（OAuth認証）

---

## 🔐 事前準備

サーバーを起動する前に、Claude Codeで認証してください：

```bash
claude login
```

---

## セットアップ

```bash
# 依存関係インストール
npm install
```

---

## 起動

```bash
npm start
```

開発モード（ファイル変更時に自動再起動）:
```bash
npm run dev
```

---

## エンドポイント

- `GET /health` - ヘルスチェック（認証状態確認）
- `GET /api/info` - SDK情報
- `POST /api/query` - REST API (非ストリーミング)
- `WS /` - WebSocket (ストリーミング)

---

## 環境変数（オプション）

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `PORT` | サーバーポート | `3000` |
| `HOST` | ホスト名 | `localhost` |
| `CLAUDE_CODE_OAUTH_TOKEN` | 長期OAuthトークン（オプション） | 自動検出 |

**注意**: `ANTHROPIC_API_KEY` は使用しません。設定されている場合は削除してください。

---

## OAuth トークンの検出順序

1. 環境変数 `CLAUDE_CODE_OAUTH_TOKEN`
2. 設定ファイル `~/.claude/config.json`
3. macOS: Keychain

---

## トラブルシューティング

### npm install でエラー

Node.js 18以上が必要です:
```bash
node --version
```

### 認証エラー

```bash
# 認証を再実行
claude login

# 認証状態確認
claude --version
```

### 長期トークンが必要な場合

サーバー環境など、対話的な認証ができない場合：

```bash
# 長期トークンを生成
claude setup-token

# 環境変数に設定
export CLAUDE_CODE_OAUTH_TOKEN=<token>
```

---

## 課金

**API料金: $0.00**

Claude Plan Max（Max 20x）のサブスクリプションを使用します。
API料金は発生しません。
