# Claude Agent SDK 統合ガイド

Claude Agent SDK を使ってサーバー経由でClaude Codeと対話するシステムです。

## 📁 構成

```
grass-coin-trader/
├── backend/              # Node.js サーバー（Claude Agent SDK統合）
│   ├── server.js         # Expressサーバー + WebSocket
│   ├── package.json      # 依存関係
│   └── .env.example      # 環境変数テンプレート
│
└── cli/                  # Pythonクライアント
    ├── claude_client.py  # CLIクライアント
    └── requirements.txt  # 依存関係
```

## 🚀 セットアップ

### 1. バックエンド（Node.js）

```bash
cd backend

# 依存関係インストール
npm install

# 環境変数設定
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

**`.env` 設定例:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
PORT=3000
HOST=localhost
CLAUDE_MODEL=claude-sonnet-4-5-20250929
MAX_TURNS=10
```

### 2. CLIクライアント（Python）

```bash
cd cli

# 依存関係インストール
pip install -r requirements.txt
```

## 📡 サーバー起動

```bash
cd backend
npm start
```

**出力例:**
```
============================================================
🚀 Claude Agent SDK Server 起動
============================================================
📡 HTTP Server: http://localhost:3000
🔌 WebSocket: ws://localhost:3000
🔑 API Key: 設定済み ✅
============================================================

利用可能なエンドポイント:
  GET  /health       - ヘルスチェック
  GET  /api/info     - SDK情報取得
  POST /api/query    - REST API (非ストリーミング)
  WS   /             - WebSocket (ストリーミング)
============================================================
```

## 💬 CLIクライアント使用方法

### インタラクティブモード

```bash
cd cli
python claude_client.py
```

**使用例:**
```
🔌 サーバーに接続中: ws://localhost:3000
✅ 接続成功! (ID: abc123)

============================================================
💬 インタラクティブモード
============================================================
プロンプトを入力してEnterで送信
'exit' または 'quit' で終了
============================================================

👤 あなた: Pythonでフィボナッチ数列を実装して

============================================================
📤 送信: Pythonでフィボナッチ数列を実装して
============================================================

🚀 Claude処理開始...

🤖 Claude:
  フィボナッチ数列を実装します...

✅ 処理完了
```

### ワンショットクエリ

```bash
# 基本的な使い方
python claude_client.py --prompt "現在のディレクトリの構造を調べて"

# モデル指定
python claude_client.py --prompt "コードをレビューして" --model claude-sonnet-4-5-20250929

# 最大ターン数指定
python claude_client.py --prompt "バグを修正して" --max-turns 5

# サーバーURL指定
python claude_client.py --server ws://192.168.1.100:3000 --prompt "Hello"
```

## 🔧 REST API使用方法

### ヘルスチェック

```bash
curl http://localhost:3000/health
```

**レスポンス:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-28T10:00:00.000Z",
  "apiKeyConfigured": true
}
```

### SDK情報取得

```bash
curl http://localhost:3000/api/info
```

**レスポンス:**
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "maxTurns": 10,
  "sdkVersion": "latest"
}
```

### 非ストリーミングクエリ

```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, Claude!",
    "options": {
      "maxTurns": 3
    }
  }'
```

## 🔌 WebSocketプロトコル

### 接続

```javascript
const ws = new WebSocket('ws://localhost:3000');
```

### メッセージ形式

**クライアント → サーバー:**

```json
{
  "type": "query",
  "prompt": "プロンプト文字列",
  "options": {
    "model": "claude-sonnet-4-5-20250929",
    "maxTurns": 10,
    "systemPrompt": "カスタムシステムプロンプト",
    "allowedTools": ["Read", "Write", "Bash"]
  }
}
```

**サーバー → クライアント:**

```json
// 接続成功
{
  "type": "connected",
  "connectionId": "abc123",
  "timestamp": "2025-10-28T10:00:00.000Z"
}

// クエリ開始
{
  "type": "query_start",
  "timestamp": "2025-10-28T10:00:01.000Z"
}

// メッセージストリーミング
{
  "type": "message",
  "data": {
    "role": "assistant",
    "content": [
      {
        "type": "text",
        "text": "応答テキスト"
      }
    ]
  },
  "timestamp": "2025-10-28T10:00:02.000Z"
}

// 完了
{
  "type": "query_complete",
  "timestamp": "2025-10-28T10:00:05.000Z"
}

// エラー
{
  "type": "error",
  "error": "エラーメッセージ",
  "timestamp": "2025-10-28T10:00:05.000Z"
}
```

## 📊 Claude Agent SDK オプション

| オプション | 型 | 説明 | デフォルト |
|-----------|-----|------|-----------|
| `model` | string | Claudeモデル | `claude-sonnet-4-5-20250929` |
| `maxTurns` | number | 最大ターン数 | `10` |
| `systemPrompt` | string | システムプロンプト | - |
| `allowedTools` | string[] | 許可するツール | 全て |
| `cwd` | string | 作業ディレクトリ | `process.cwd()` |

## 🛠️ トラブルシューティング

### サーバーが起動しない

```bash
# Node.jsバージョン確認（18以上必要）
node --version

# 依存関係再インストール
cd backend
rm -rf node_modules package-lock.json
npm install
```

### API Key エラー

```bash
# .envファイルを確認
cat backend/.env

# ANTHROPIC_API_KEY が正しく設定されているか確認
# https://console.anthropic.com/ で取得
```

### クライアント接続エラー

```bash
# サーバーが起動しているか確認
curl http://localhost:3000/health

# ポート番号確認
# backend/.env の PORT と一致しているか
```

## 📚 参考リンク

- [Claude Agent SDK ドキュメント](https://docs.claude.com/en/api/agent-sdk/overview)
- [GitHub - claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript)
- [Anthropic API Console](https://console.anthropic.com/)

## 🔐 セキュリティ

- **API Keyの管理**: `.env` ファイルは `.gitignore` に追加済み
- **本番環境**: 環境変数は環境に応じて適切に設定してください
- **ポート開放**: 本番環境では適切なファイアウォール設定を行ってください

---

**Powered by Claude Agent SDK**
