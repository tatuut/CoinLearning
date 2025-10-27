# Phase 2 テスト実行手順

Phase 2（バックグラウンドジョブ実行基盤）の動作確認手順です。

## 前提条件

### 1. Redisのインストール（WSL）

```bash
wsl
sudo apt update
sudo apt install redis-server
```

### 2. Redisの起動確認

```bash
wsl
sudo service redis-server start
redis-cli ping
```

**期待される出力**: `PONG`

## テスト実行手順

### ステップ1: 3つのターミナルを開く

- ターミナル1: FastAPI
- ターミナル2: RQ Worker
- ターミナル3: Streamlit

---

### ターミナル1: FastAPI起動

```bash
cd C:\Users\tatut\Documents\playground\grass-coin-trader
python backend/main.py
```

**期待される出力**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**確認**: ブラウザで http://localhost:8000/ にアクセス
→ `{"message":"Grass Coin Trader API","version":"1.0.0"}` が表示されればOK

---

### ターミナル2: RQ Worker起動

```bash
cd C:\Users\tatut\Documents\playground\grass-coin-trader
rq worker --url redis://localhost:6379
```

**期待される出力**:
```
INFO:     Worker started, version 2.6.0
INFO:     Subscribing to default...
INFO:     Worker rq:worker:xxxxx started
```

---

### ターミナル3: Streamlit起動

```bash
cd C:\Users\tatut\Documents\playground\grass-coin-trader
streamlit run src/tools/parquet_dashboard.py
```

**期待される出力**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://xxx.xxx.xxx.xxx:8501
```

---

## 動作確認

### Streamlit UI操作

1. ブラウザで http://localhost:8501 を開く
2. ページ下部の **「🤖 バックグラウンドジョブ実行（リアルタイムログ）」** セクションまでスクロール
3. 仮想通貨を選択（BTC/ETH/XRP）
4. **「🚀 ダミージョブ開始」** ボタンをクリック

### 期待される動作

1. **ジョブ開始メッセージ**:
   ```
   ✅ ジョブ開始！ Job ID: abc-123-def-456...
   ```

2. **ステータス表示**:
   ```
   ⏳ 待機中...
   ↓
   ▶️ 実行中...
   ↓
   ✅ 完了！
   ```

3. **リアルタイムログ** (0.5秒ごとに更新):
   ```
   🚀 Job started for BTC
   ⏳ Step 1/3: Simulating WebSearch...
   ✅ Step 1 done: Found 5 articles
   ⏳ Step 2/3: Simulating analysis...
   ✅ Step 2 done: Average sentiment +0.45
   ⏳ Step 3/3: Simulating DB save...
   ✅ Step 3 done: Saved to database
   🎉 Completed!
   ```

4. **実行結果** (JSON):
   ```json
   {
     "success": true,
     "symbol": "BTC",
     "news_count": 5,
     "avg_sentiment": 0.45
   }
   ```

### ターミナル2（RQ Worker）の出力確認

```
[DUMMY] 🚀 Job started for BTC
[DUMMY] ⏳ Step 1/3: Simulating WebSearch...
[DUMMY] ✅ Step 1 done: Found 5 articles
[DUMMY] ⏳ Step 2/3: Simulating analysis...
[DUMMY] ✅ Step 2 done: Average sentiment +0.45
[DUMMY] ⏳ Step 3/3: Simulating DB save...
[DUMMY] ✅ Step 3 done: Saved to database
[DUMMY] 🎉 Completed!
default: backend.workers.dummy_worker.dummy_job('BTC') (abc-123-def-456...)
```

---

## トラブルシューティング

### エラー: FastAPIサーバーに接続できません

**原因**: FastAPIが起動していない

**解決策**:
1. ターミナル1でFastAPIが起動しているか確認
2. http://localhost:8000/ にアクセスしてAPIが応答するか確認

---

### エラー: Redisに接続できない

**症状**: RQ Worker起動時に `redis.exceptions.ConnectionError`

**解決策**:
```bash
wsl
sudo service redis-server start
redis-cli ping  # → PONG が返ればOK
```

---

### ログが表示されない

**原因**: RQ Workerが起動していない

**解決策**:
1. ターミナル2でRQ Workerが起動しているか確認
2. Worker側のログが流れているか確認

---

## curlでのテスト（オプション）

### ジョブ開始

```bash
curl -X POST http://localhost:8000/api/jobs/start \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"BTC\"}"
```

**期待される出力**:
```json
{
  "job_id": "abc-123-def-456...",
  "symbol": "BTC",
  "message": "Job started"
}
```

### ステータス確認

```bash
curl http://localhost:8000/api/jobs/status/<job_id>
```

### ログ取得

```bash
curl "http://localhost:8000/api/jobs/logs/<job_id>?offset=0"
```

---

## Phase 2完成チェックリスト

- [ ] FastAPIが正常に起動する
- [ ] RQ Workerが正常に起動する
- [ ] Streamlitが正常に起動する
- [ ] ジョブ開始ボタンでジョブが開始される
- [ ] リアルタイムでログが表示される（0.5秒更新）
- [ ] 5秒後にジョブが完了する
- [ ] 実行結果（JSON）が表示される

全てチェックできたら **Phase 2完成** です！

---

## 次のステップ（Phase 3）

Phase 3では:
- ダミーワーカー → Claude Code SDK実行に置き換え
- Node.js + Express サーバー構築
- Claude Agent SDK統合
- WebSearch + センチメント分析 + DB保存の自動化

詳細は `docs/implementation/phase2_phase3_implementation_plan.md` の **Scene 5** を参照してください。

---

**最終更新**: 2025-10-28
**作成者**: Claude Code
