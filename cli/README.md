# CLI - Claude Code Client

Python製CLIクライアント（Claude Plan Max OAuth認証）

---

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt
```

---

## 事前準備

バックエンドサーバーが起動している必要があります：

```bash
# backend/ ディレクトリで
npm start
```

サーバーが `claude login` で認証済みであることを確認してください。

---

## 使用方法

### インタラクティブモード

```bash
python claude_client.py
```

対話形式でClaude Codeと会話できます。

### ワンショットクエリ

```bash
python claude_client.py --prompt "Pythonでフィボナッチ数列を実装して"
```

### オプション

```bash
# モデル指定
python claude_client.py --prompt "Hello" --model claude-sonnet-4-5-20250929

# 最大ターン数指定
python claude_client.py --prompt "バグ修正" --max-turns 5

# サーバーURL指定
python claude_client.py --server ws://192.168.1.100:3000
```

---

## ヘルプ

```bash
python claude_client.py --help
```

---

## 必須条件

- Python 3.8以上
- バックエンドサーバーが起動していること
- サーバーが `claude login` で認証済みであること

---

## 課金

**API料金: $0.00**

Claude Plan Max（OAuth認証）を使用します。
