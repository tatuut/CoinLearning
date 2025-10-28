# CLI - Claude Client

Python製CLIクライアント（WebSocket経由でバックエンドと通信）

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt
```

## 使用方法

### インタラクティブモード

```bash
python claude_client.py
```

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

## ヘルプ

```bash
python claude_client.py --help
```

## 必須条件

- Python 3.8以上
- バックエンドサーバーが起動していること
