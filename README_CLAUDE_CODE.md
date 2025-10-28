# Claude Code 統合ガイド（CLI直接実行版）

Claude Plan Maxのサブスクリプション認証を使用して、**別のClaude Codeインスタンス**と対話するシステムです。

**特徴**:
- ✅ Claude CLI（`claude`コマンド）を直接実行
- ✅ API料金 $0.00（サブスクリプション内）
- ✅ 別プロセスでClaude Codeが動作

---

## 📁 構成

```
grass-coin-trader/
├── backend/              # Node.js サーバー
│   ├── server-cli.js     # Claude CLI直接実行版（推奨）
│   ├── server.js         # Claude Agent SDK版（実験的）
│   └── package.json      # 依存関係
│
└── cli/                  # Pythonクライアント
    ├── claude_client.py  # CLIクライアント
    └── requirements.txt  # 依存関係
```

---

## 🔐 認証方法

### Claude Code OAuth認証（必須）

```bash
# Claude Code CLI認証
claude login
```

これにより、Claude Plan Maxのサブスクリプション認証が完了します。

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
- `claude` コマンドがパスに存在

### 2. CLIクライアント（Python）

```bash
cd cli

# 依存関係インストール
pip install -r requirements.txt
```

---

## 📡 サーバー起動

```bash
cd backend
npm start
```

**出力例:**
```
============================================================
🚀 Claude CLI Server 起動
============================================================
📡 HTTP Server: http://localhost:3003
🔌 WebSocket: ws://localhost:3003
🔐 認証方式: Claude CLI (claude login)
💰 課金: Max 20x Plan (API料金なし)
⚙️  実行方式: Direct CLI execution
============================================================

利用可能なエンドポイント:
  GET  /health       - ヘルスチェック
  GET  /api/info     - 情報取得
  WS   /             - WebSocket (ストリーミング)
============================================================
```

デフォルトポート: **3003**

---

## 💬 CLIクライアント使用方法

### インタラクティブモード

```bash
cd cli
python claude_client.py
```

### ワンショットクエリ

```bash
# 基本的な使い方
python claude_client.py --prompt "このプロジェクトのREADMEを読んで要約して"

# ファイル操作
python claude_client.py --prompt "src/ディレクトリの構造を調べて"

# コード生成
python claude_client.py --prompt "Pythonでフィボナッチ数列を実装して"
```

**使用例:**
```
🔌 サーバーに接続中: ws://localhost:3003
✅ 接続成功! (ID: abc123)
🔐 認証: Claude Plan Max

============================================================
📤 送信: こんにちは！
============================================================

🚀 Claude Code 処理開始...

🤖 Claude Code:
  こんにちは！何かお手伝いできることはありますか？

============================================================
✅ 処理完了
💰 課金: $0.00 (Max 20x Plan)
============================================================
```

---

## 🔧 API使用方法

### ヘルスチェック

```bash
curl http://localhost:3003/health
```

**レスポンス:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-28T10:00:00.000Z",
  "authMethod": "Claude CLI (claude login)",
  "mode": "Direct CLI execution"
}
```

### 情報取得

```bash
curl http://localhost:3003/api/info
```

---

## 📊 実装方式

### CLI直接実行（server-cli.js）- 推奨 ✅

**仕組み:**
1. Node.jsサーバーがWebSocket接続を受け付け
2. `claude --print --output-format text` コマンドを子プロセスとして起動
3. Claude CLIの出力をリアルタイムでストリーミング

**メリット:**
- ✅ シンプルで確実
- ✅ Claude CLIの全機能が使える
- ✅ 認証が自動的に機能
- ✅ 安定動作

**制限事項:**
- Claude CLIがインストールされている必要がある
- `claude login` で認証済みである必要がある

### Agent SDK（server.js）- 実験的 ⚠️

**仕組み:**
1. `@anthropic-ai/claude-agent-sdk` の `query()` 関数を使用
2. 内部でClaude Code CLIをサブプロセスとして起動
3. SDKメッセージをストリーミング

**状態:**
- ⚠️ Windows環境でクラッシュ問題あり
- ⚠️ 認証トークンの受け渡しに問題
- 現在は非推奨

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

### Claude CLIエラー

```bash
# Claude CLIが正常に動作するか確認
claude --version

# 認証を再実行
claude login

# 手動でテスト
claude --print "こんにちは"
```

### ポート競合

デフォルトポート3003が使用中の場合：

```bash
# 別のポートで起動
PORT=3004 npm start

# クライアント側でもポート指定
python claude_client.py --server ws://localhost:3004
```

---

## 🔄 複数インスタンス起動

異なるポートで複数のClaude Codeインスタンスを起動できます：

```bash
# ターミナル1
cd backend
PORT=3003 npm start

# ターミナル2
cd backend
PORT=3004 npm start

# ターミナル3
cd backend
PORT=3005 npm start
```

クライアントから使い分け：

```bash
python claude_client.py --server ws://localhost:3003 --prompt "タスク1"
python claude_client.py --server ws://localhost:3004 --prompt "タスク2"
python claude_client.py --server ws://localhost:3005 --prompt "タスク3"
```

---

## 📚 参考リンク

- [Claude Code ドキュメント](https://docs.claude.com/en/docs/claude-code)
- [Claude CLI 使い方](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)

---

## 🔐 セキュリティ

- **OAuth トークン**: `~/.claude/.credentials.json` に保存
- **ポート開放**: ローカルホスト (localhost) のみで起動
- **本番環境**: 本番環境での使用は推奨しません（個人用途専用）

---

**Powered by Claude Code (Claude Plan Max)**

サブスクリプションでAPI料金を気にせず、複数のClaude Codeインスタンスを起動！
