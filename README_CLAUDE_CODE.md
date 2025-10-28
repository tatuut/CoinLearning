# Claude Code 統合ガイド（Claude Plan Max版）

Claude Plan Maxのサブスクリプション認証を使用してClaude Codeと対話するシステムです。

**重要**: このシステムはAPI Keyではなく、**Claude Plan Max（OAuth認証）**を使用します。API料金は発生しません。

---

## 📁 構成

```
grass-coin-trader/
├── backend/              # Node.js サーバー（Claude Agent SDK統合）
│   ├── server.js         # Expressサーバー + WebSocket
│   └── package.json      # 依存関係
│
└── cli/                  # Pythonクライアント
    ├── claude_client.py  # CLIクライアント
    └── requirements.txt  # 依存関係
```

---

## 🔐 認証方法

### Claude Code OAuth認証（必須）

サーバーを起動する前に、Claude Codeで認証してください：

```bash
# Claude Code CLI認証
claude login
```

これにより、Claude Plan Maxのサブスクリプション認証が完了します。

#### 長期トークンの生成（オプション）

サーバー環境で永続的に使用する場合：

```bash
# 長期トークンを生成
claude setup-token

# 環境変数に設定
export CLAUDE_CODE_OAUTH_TOKEN=<取得したトークン>
```

---

## 🚀 セットアップ

### 1. バックエンド（Node.js）

```bash
cd backend

# 依存関係インストール
npm install
```

**必要な環境:**
- Node.js 18以上
- `claude login` で認証済み

### 2. CLIクライアント（Python）

```bash
cd cli

# 依存関係インストール
pip install -r requirements.txt
```

**必要な環境:**
- Python 3.8以上

---

## 📡 サーバー起動

```bash
cd backend
npm start
```

**出力例（認証済みの場合）:**
```
============================================================
🚀 Claude Code Server 起動
============================================================
📡 HTTP Server: http://localhost:3000
🔌 WebSocket: ws://localhost:3000
🔐 認証方式: Claude Plan Max (OAuth)
✅ 認証状態: 認証済み
💰 課金: Max 20x Plan (API料金なし)
============================================================

利用可能なエンドポイント:
  GET  /health       - ヘルスチェック
  GET  /api/info     - SDK情報取得
  POST /api/query    - REST API (非ストリーミング)
  WS   /             - WebSocket (ストリーミング)
============================================================
```

**出力例（未認証の場合）:**
```
⚠️  認証が必要です。以下のコマンドを実行してください:

  claude login

または、長期トークンを生成:
  claude setup-token
  export CLAUDE_CODE_OAUTH_TOKEN=<token>
```

---

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
🔐 認証: Claude Plan Max

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

🚀 Claude Code 処理開始...

🤖 Claude Code:
  フィボナッチ数列を実装します...

🔧 ツール使用: Write
   入力: {
     "path": "fibonacci.py",
     "content": "def fib(n): ..."
   }

============================================================
✅ 処理完了
💰 課金: $0.00 (Max 20x Plan)
============================================================
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

---

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
  "authMethod": "Claude Plan Max (OAuth)",
  "authenticated": true
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
  "authMethod": "Claude Plan Max Subscription",
  "maxTurns": 10,
  "billing": "Max 20x Plan (no API charges)",
  "sdkVersion": "latest"
}
```

### 非ストリーミングクエリ

```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, Claude Code!",
    "options": {
      "maxTurns": 3
    }
  }'
```

**レスポンス:**
```json
{
  "success": true,
  "messages": [...],
  "billing": {
    "total_cost_usd": 0,
    "note": "Max 20x Plan - no API charges"
  },
  "timestamp": "2025-10-28T10:00:00.000Z"
}
```

---

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
    "allowedTools": ["Read", "Write", "Bash"],
    "cwd": "/path/to/working/directory"
  }
}
```

**サーバー → クライアント:**

```json
// 接続成功
{
  "type": "connected",
  "connectionId": "abc123",
  "authenticated": true,
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
  "event": {
    "type": "assistant_message",
    "text": "応答テキスト",
    "toolUses": [
      {
        "id": "tool_123",
        "name": "Read",
        "input": {"path": "file.py"}
      }
    ]
  },
  "raw": {...},
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

---

## 📊 Claude Agent SDK オプション

| オプション | 型 | 説明 | デフォルト |
|-----------|-----|------|-----------|
| `model` | string | Claudeモデル | `claude-sonnet-4-5-20250929` |
| `maxTurns` | number | 最大ターン数 | `10` |
| `systemPrompt` | string | システムプロンプト | - |
| `allowedTools` | string[] | 許可するツール | 全て |
| `cwd` | string | 作業ディレクトリ | `process.cwd()` |
| `includePartialMessages` | boolean | ストリーミング有効化 | `true` |

---

## 💰 課金について

**API料金: $0.00**

このシステムはClaude Plan Max（Max 20x）のサブスクリプションを使用します。
API料金は一切発生しません。

### Max 20x Planの制限

- 約900メッセージ または 200〜800プロンプト（5時間ごと）
- 週あたり約240〜480時間（Sonnet 4）
- 週あたり約24〜40時間（Opus 4）

---

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

### 認証エラー

```bash
# Claude Code認証を再実行
claude login

# 認証状態確認
claude --version

# 長期トークンが必要な場合
claude setup-token
```

### クライアント接続エラー

```bash
# サーバーが起動しているか確認
curl http://localhost:3000/health

# 認証状態確認
curl http://localhost:3000/api/info
```

### ANTHROPIC_API_KEY 警告

もし `ANTHROPIC_API_KEY` 環境変数が設定されている場合、Claude CodeはAPI Key認証を優先します。
サブスクリプション認証を使用するには：

```bash
# 環境変数を削除
unset ANTHROPIC_API_KEY

# .bashrc や .zshrc から削除
# export ANTHROPIC_API_KEY=... の行を削除またはコメントアウト
```

---

## 📚 参考リンク

- [Claude Agent SDK ドキュメント](https://docs.claude.com/en/api/agent-sdk/overview)
- [Claude Code 使い方](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [GitHub - claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript)

---

## 🔐 セキュリティ

- **OAuth トークン**: `~/.claude/config.json` に保存（macOS: Keychain）
- **環境変数**: `CLAUDE_CODE_OAUTH_TOKEN` は安全に管理してください
- **ポート開放**: 本番環境では適切なファイアウォール設定を行ってください

---

## ⚖️ API Key認証との違い

| 項目 | Claude Plan Max (OAuth) | API Key |
|------|------------------------|---------|
| 認証方法 | `claude login` | `ANTHROPIC_API_KEY` |
| 課金 | サブスクリプション内（$0） | 従量課金 |
| 使用制限 | Max 20x Planの制限 | クレジット残高 |
| 推奨用途 | 個人開発・学習 | 商用・大規模利用 |

---

**Powered by Claude Code (Claude Plan Max)**

サブスクリプションでAPI料金を気にせず開発！
