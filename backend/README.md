# Backend - Claude Agent SDK Server

Node.js + Express.js + WebSocket サーバー

## セットアップ

```bash
# 依存関係インストール
npm install

# 環境変数設定
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

## 起動

```bash
npm start
```

開発モード（ファイル変更時に自動再起動）:
```bash
npm run dev
```

## エンドポイント

- `GET /health` - ヘルスチェック
- `GET /api/info` - SDK情報
- `POST /api/query` - REST API (非ストリーミング)
- `WS /` - WebSocket (ストリーミング)

## 必須環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `ANTHROPIC_API_KEY` | Anthropic API Key | `sk-ant-api03-xxxxx` |
| `PORT` | サーバーポート | `3000` |
| `HOST` | ホスト名 | `localhost` |
| `CLAUDE_MODEL` | Claudeモデル | `claude-sonnet-4-5-20250929` |
| `MAX_TURNS` | 最大ターン数 | `10` |

## トラブルシューティング

### npm install でエラー

Node.js 18以上が必要です:
```bash
node --version
```

### ANTHROPIC_API_KEY エラー

https://console.anthropic.com/ でAPI Keyを取得してください。
