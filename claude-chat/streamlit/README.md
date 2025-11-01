# Claude Code チャットインターフェース

StreamlitベースのClaude Codeチャットインターフェース

## 📋 機能

- ✅ チャット形式でClaude Codeと対話
- ✅ メッセージ履歴の保存（セッション内）
- ✅ 履歴のクリア機能
- ✅ 履歴のJSONダウンロード
- ✅ タイムスタンプ付きメッセージ
- ✅ サーバー接続テスト
- ✅ サーバー情報表示
- ✅ API料金表示（$0.00 - Max 20x Plan）

## 🚀 セットアップ

### 1. 依存関係インストール

```bash
cd ui
pip install -r requirements.txt
```

### 2. バックエンドサーバー起動

別ターミナルで：

```bash
cd backend
npm start
```

サーバーは `http://localhost:3003` で起動します。

### 3. Streamlitアプリ起動

```bash
cd ui
streamlit run claude_chat.py
```

ブラウザが自動的に開き、チャットインターフェースが表示されます。

## 🎯 使い方

### 基本的な使い方

1. **メッセージ入力**: 画面下部の入力欄にメッセージを入力してEnter
2. **履歴表示**: 過去のメッセージが画面に表示されます
3. **履歴クリア**: サイドバーの「🗑️ 履歴をクリア」ボタンで履歴削除
4. **履歴ダウンロード**: サイドバーの「💾 履歴をダウンロード」ボタンでJSON形式で保存

### サーバー設定

- **サーバーURL変更**: サイドバーでURLを変更可能（デフォルト: `http://localhost:3003`）
- **接続テスト**: 「🔍 接続テスト」ボタンでサーバーの状態確認
- **サーバー情報**: 「ℹ️ サーバー情報」ボタンでモデル情報などを表示

## 📁 ファイル構成

```
ui/
├── claude_chat.py      # Streamlitメインアプリ
├── requirements.txt    # Python依存関係
└── README.md           # このファイル
```

## 🔧 API仕様

### POST /api/query

**リクエスト:**
```json
{
  "prompt": "こんにちは"
}
```

**レスポンス:**
```json
{
  "success": true,
  "response": "こんにちは！何かお手伝いできることはありますか？",
  "billing": {
    "total_cost_usd": 0,
    "note": "Max 20x Plan - no API charges"
  },
  "timestamp": "2025-10-28T12:00:00.000Z"
}
```

## 💰 課金について

- **API料金**: $0.00
- **プラン**: Claude Plan Max (Max 20x)
- **制限**: 約900メッセージまたは200〜800プロンプト（5時間ごと）

## 🛠️ トラブルシューティング

### 「接続失敗」エラー

```bash
# バックエンドサーバーが起動しているか確認
cd backend
npm start
```

### タイムアウトエラー

- デフォルトタイムアウト: 120秒
- 長時間かかるクエリの場合は自動的にタイムアウトします

### Streamlitがインストールされていない

```bash
pip install streamlit
```

## 📚 参考リンク

- [Streamlit ドキュメント](https://docs.streamlit.io/)
- [Claude Code ドキュメント](https://docs.claude.com/en/docs/claude-code)

## 🎨 カスタマイズ

### タイムアウト時間変更

`claude_chat.py` の120行目付近：

```python
timeout=120  # 秒数を変更
```

### デフォルトサーバーURL変更

`claude_chat.py` の16行目：

```python
DEFAULT_SERVER_URL = "http://localhost:3003"
```

---

**Powered by Claude Code (Claude Plan Max)**
