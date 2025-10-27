# Phase 2 & 3 実装計画書

**Claude Code SDK統合への道 - ユウタとミコの自動化物語**

---

## 📖 Scene 1: ユウタの現実 - 手動実行の限界

### 朝8時、ユウタの部屋

**ユウタ**: 「ふわぁ...眠い...」

ユウタはスマホのアラームを止め、まずやることがある。

**ユウタ**: 「今日もBTCのニュースチェックしないと...」

ブラウザを開き、CoinDeskを開く。次にBloomberg。次にCoinTelegraph。

**ユウタ**: 「うーん、『BTCが最高値更新』か。ポジティブだな」

メモ帳に記録する。

```
2025-10-27 08:15
BTC: CoinDeskで最高値更新のニュース
センチメント: ポジティブ（+0.8くらい？）
```

**ユウタ**: 「次はETH...」

30分後。

**ユウタ**: 「やっと終わった...授業遅刻しそう」

---

### 夜10時、ユウタの部屋

**ユウタ**: 「また同じ作業か...」

またブラウザを開く。CoinDesk、Bloomberg、CoinTelegraph...

**ユウタ**: 「あれ？昼間に見逃してたニュースがある。『BTCのマイニング規制』って...これ重要じゃん」

**ユウタ**: 「くそ、昼間にこれがあったのか。見逃した...」

**ユウタ**: 「でも、もう夜10時だよ。今から分析しても遅い」

---

### 3日後、限界

**ユウタ**: 「もう無理...」

手動でニュース検索を続けること3日。ユウタは限界に達していた。

**問題点**:
1. **時間がかかる** - 毎回30分
2. **見逃す** - 重要なニュースを見逃す
3. **疲れる** - 毎日2回、朝晩
4. **記録が雑** - メモ帳にテキトーに書くだけ
5. **分析できない** - 過去データと比較できない

**ユウタ**: 「ミコ、なんとかならないの？」

**ミコ**: 「...お前、いい加減気づけよ」

**ユウタ**: 「え？」

**ミコ**: 「そのために、私がいるんだろ？」

---

## 📖 Scene 2: ミコの提案 - Claude Code SDKという解決策

### ミコの提案

**ミコ**: 「お前がやってる作業、全部私にやらせろ」

**ユウタ**: 「え、できるの？」

**ミコ**: 「Claude Code SDKってのがある。これを使えば、私が自動でニュース検索して、分析して、DBに保存できる」

**ユウタ**: 「マジで!?」

**ミコ**: 「ああ。やってることはこうだ：」

```
【Claude Codeが実行すること】

1. WebSearchでBTCのニュースを検索
2. 各記事を読んで内容を分析
3. センチメントスコアを計算（0〜1）
4. save_news_to_dbツールでDBに保存
5. 結果を報告
```

**ユウタ**: 「すげー！じゃあ早速やろう！」

---

### 最初の実装（失敗）

**ミコ**: 「まずは簡単に実装してみるか」

`test_claude_sdk.py`（テスト実装）:
```python
import requests

def fetch_news_sync(symbol):
    """Claude Code SDKを同期的に呼び出し"""
    print(f"📡 Calling Node.js Claude Agent Service for {symbol}...")

    response = requests.post(
        "http://localhost:3000/agent/execute",
        json={"symbol": symbol, "task": "Search and analyze news"},
        timeout=300  # 5分
    )

    print("✅ Done!")
    return response.json()

# 実行
result = fetch_news_sync("BTC")
print(result)
```

**ユウタ**: 「よし、実行してみる！」

```bash
python test_claude_sdk.py
```

**実行結果**:
```
📡 Calling Node.js Claude Agent Service for BTC...
```

**30秒経過...**

**ユウタ**: 「...まだ？」

**1分経過...**

**ユウタ**: 「おい、フリーズしてるぞ？」

**ミコ**: 「フリーズじゃない。Claude Codeが動いてるだけだ」

**ユウタ**: 「でも何も表示されないじゃん！」

**2分経過...**

```
✅ Done!
{'success': True, 'num_turns': 8, 'news_count': 5}
```

**ユウタ**: 「やっと終わった...でも2分も待たされた」

**ユウタ**: 「しかも、途中で何やってるか全然わからない」

---

### 問題の発見

**ミコ**: 「そうだな。問題が3つある」

**問題1: ダッシュボードがフリーズする**
```python
# Streamlitダッシュボードで実行すると...
if st.button("ニュース取得"):
    result = fetch_news_sync("BTC")  # ← ここで2分フリーズ
    st.json(result)
```

**ユウタ**: 「これじゃダッシュボード使えないじゃん！」

**問題2: 進行状況が見えない**

Claude Codeが裏で何をやってるか分からない：
- Turn 1: WebSearch実行中...
- Turn 2: 記事を読んでる...
- Turn 3: 分析中...
- Turn 4: DB保存中...

**ユウタ**: 「途中経過が見たい！」

**問題3: 会話ができない**

もし途中で「もっと詳しく分析して」と言いたくなっても、同期実行だと無理。

**ユウタ**: 「うーん、これじゃダメだな」

**ミコ**: 「だからバックグラウンド実行が必要なんだ」

---

## 📖 Scene 3: バックグラウンド実行の設計

### 解決策の模索

**ミコ**: 「問題を整理するぞ」

```
【解決すべき課題】

課題1: ダッシュボードがフリーズする
  → バックグラウンドで実行する必要がある

課題2: 進行状況が見えない
  → リアルタイムでログを表示したい

課題3: 会話ができない
  → 途中で追加依頼を送れるようにしたい
```

**ユウタ**: 「どうやるの？」

**ミコ**: 「調べたぞ」

---

### 技術調査

**候補1: Celery**
```python
# メリット: 高機能、実績豊富
# デメリット: セットアップが複雑、RabbitMQ必要
```

**ミコ**: 「重すぎる。却下」

**候補2: threading / multiprocessing**
```python
# メリット: 標準ライブラリ
# デメリット: ジョブ管理が大変、永続化できない
```

**ミコ**: 「ジョブが消えたら困る。却下」

**候補3: RQ (Redis Queue)**
```python
# メリット: シンプル、Redisだけ、ジョブ永続化
# デメリット: 高度な機能は少ない
```

**ミコ**: 「これだ！」

---

### アーキテクチャ設計

**ミコ**: 「こういう構成にする」

```
【Phase 2: バックグラウンド実行基盤】

┌─────────────────┐
│  Streamlit UI   │  ← ユーザーがボタンクリック
│  (Port 8501)    │
└────────┬────────┘
         │ HTTP POST /api/jobs/start
         │ {"symbol": "BTC"}
         ↓
┌─────────────────┐
│  FastAPI        │  ← ジョブをキューに追加
│  (Port 8000)    │      job_id を返す
│  /api/jobs      │
└────────┬────────┘
         │ Enqueue
         ↓
┌─────────────────┐
│  Redis Queue    │  ← ジョブキュー
│  (RQ)           │
└────────┬────────┘
         │ Dequeue
         ↓
┌─────────────────┐
│  Worker Process │  ← バックグラウンドで実行
│  (rq worker)    │      ダミージョブ（Phase 2）
└─────────────────┘      Claude Code（Phase 3）
```

**ユウタ**: 「なるほど、ボタンを押したら即座にjob_idが返ってきて、裏で実行されるのか」

**ミコ**: 「そう。ダッシュボードはフリーズしない」

---

### Phase 2実装

**ミコ**: 「まずはPhase 2。インフラだけ作る。実装はダミーでいい」

**Phase 2の目標**:
1. FastAPI + Redis + RQ でバックグラウンドジョブ実行
2. ダミージョブで動作確認
3. Claude Code統合は Phase 3で

---

**依存関係インストール**:
```bash
pip install fastapi uvicorn redis rq python-dotenv
```

**Redisセットアップ**:
```bash
wsl
sudo service redis-server start
```

**.env**:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

---

**`backend/config.py`**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))

settings = Settings()
```

---

**`backend/workers/dummy_worker.py`** - ダミーワーカー:
```python
"""Phase 2: ダミーワーカー（Phase 3でClaude Code実行に置き換え）"""
import time

def dummy_job(symbol: str, job_id: str = None):
    """ダミージョブ（3ステップ、計5秒）"""

    def log(msg):
        print(f"[DUMMY] {msg}")
        # Phase 4でWebSocketログ追加

    log(f"🚀 Job started for {symbol}")

    log("⏳ Step 1/3: Simulating WebSearch...")
    time.sleep(2)
    log("✅ Step 1 done")

    log("⏳ Step 2/3: Simulating analysis...")
    time.sleep(2)
    log("✅ Step 2 done")

    log("⏳ Step 3/3: Simulating DB save...")
    time.sleep(1)
    log("✅ Step 3 done")

    log("🎉 Completed!")

    return {"success": True, "symbol": symbol}
```

---

**`backend/api/jobs.py`** - ジョブAPI:
```python
from fastapi import APIRouter
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from backend.config import settings
from backend.workers.dummy_worker import dummy_job

router = APIRouter()

redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
queue = Queue(connection=redis_conn)

class JobRequest(BaseModel):
    symbol: str

@router.post("/start")
async def start_job(request: JobRequest):
    """ジョブ開始"""
    job = queue.enqueue(
        dummy_job,
        args=(request.symbol,),
        job_timeout='10m'
    )

    return {
        "job_id": job.id,
        "symbol": request.symbol,
        "message": "Job started"
    }

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """ジョブステータス確認"""
    from rq.job import Job
    job = Job.fetch(job_id, connection=redis_conn)

    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result if job.is_finished else None
    }
```

---

**`backend/main.py`** - FastAPIサーバー:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.jobs import router as jobs_router
import uvicorn

app = FastAPI(title="Grass Coin Trader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])

@app.get("/")
async def root():
    return {"message": "Grass Coin Trader API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=True)
```

---

### Phase 2テスト

**ターミナル1: FastAPI起動**:
```bash
python backend/main.py
```

**ターミナル2: RQワーカー起動**:
```bash
rq worker --url redis://localhost:6379
```

**ターミナル3: テスト実行**:
```bash
curl -X POST http://localhost:8000/api/jobs/start \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC"}'
```

**結果**:
```json
{
  "job_id": "abc-123-def",
  "symbol": "BTC",
  "message": "Job started"
}
```

**ターミナル2（RQワーカー）の出力**:
```
[DUMMY] 🚀 Job started for BTC
[DUMMY] ⏳ Step 1/3: Simulating WebSearch...
[DUMMY] ✅ Step 1 done
[DUMMY] ⏳ Step 2/3: Simulating analysis...
[DUMMY] ✅ Step 2 done
[DUMMY] ⏳ Step 3/3: Simulating DB save...
[DUMMY] ✅ Step 3 done
[DUMMY] 🎉 Completed!
```

**ユウタ**: 「動いた！しかも非同期だ！」

**ミコ**: 「Phase 2完成。次はログの可視化だ」

---

## 📖 Scene 4: 進行状況の可視化 - WebSocketの必然性

### 翌日、ユウタの疑問

**ユウタ**: 「ミコ、Phase 2は動いたけど...」

**ユウタ**: 「ターミナルでログが流れるのは見えるけど、ダッシュボードから見れないんだよね」

**ミコ**: 「そうだな。今はターミナルでしか見れない」

**ユウタ**: 「それに、Phase 3でClaude Code使うようになったら、もっと長くなるよね？」

**ミコ**: 「その通りだ」

---

### Claude CodeのAgentic実行を理解する

**ミコ**: 「Claude Codeは**Agenticに動く**んだ」

**ユウタ**: 「Agentic...？」

**ミコ**: 「普通のAPI呼び出しと違って、Claude Codeは**複数ターン**で実行する」

```
【Claude CodeのAgentic実行の例】

Turn 1: 「WebSearchツールでBTCのニュースを検索します」
   → WebSearchツール実行
   → 結果: 5件の記事を発見

Turn 2: 「1つ目の記事を読みます...」
   → 『BTC reaches all-time high of $95,000』
   → センチメント: ポジティブ（+0.9）

Turn 3: 「2つ目の記事を読みます...」
   → 『BTC mining regulations tighten』
   → センチメント: ネガティブ（-0.3）

Turn 4: 「全記事の平均センチメントを計算します」
   → 平均: +0.45

Turn 5: 「save_news_to_dbツールでDBに保存します」
   → DB保存実行
   → 成功

Turn 6: 「完了しました。5件の記事を分析し、平均センチメント+0.45でした」
```

**ユウタ**: 「へー、複数ステップで考えながら実行するんだ」

**ミコ**: 「そう。だから**各ターンの進行状況をリアルタイムで見たい**」

**ユウタ**: 「なるほど！だからWebSocketか！」

---

### WebSocketの実装

**ミコ**: 「WebSocketを追加する」

**`backend/api/websocket.py`**:
```python
"""WebSocket for real-time logging"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)

    async def send_log(self, job_id: str, message: str):
        """ログをWebSocket経由で配信"""
        if job_id in self.active_connections:
            for conn in self.active_connections[job_id]:
                try:
                    await conn.send_json({"type": "log", "message": message})
                except:
                    pass

manager = ConnectionManager()

@router.websocket("/logs/{job_id}")
async def websocket_logs(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
```

---

**ワーカーをWebSocket対応に修正**:

`backend/workers/dummy_worker.py`:
```python
import time
import asyncio

async def async_log(message: str, job_id: str):
    """WebSocketログ送信"""
    from backend.api.websocket import manager
    await manager.send_log(job_id, message)

def dummy_job(symbol: str, job_id: str = None):
    """ダミージョブ（WebSocket対応）"""

    def log(msg):
        print(f"[DUMMY] {msg}")

        # WebSocketで配信
        if job_id:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_log(msg, job_id))
            loop.close()

    log(f"🚀 Job started for {symbol}")
    log("⏳ Step 1/3: Simulating WebSearch...")
    time.sleep(2)
    log("✅ Step 1 done")

    log("⏳ Step 2/3: Simulating analysis...")
    time.sleep(2)
    log("✅ Step 2 done")

    log("⏳ Step 3/3: Simulating DB save...")
    time.sleep(1)
    log("✅ Step 3 done")

    log("🎉 Completed!")

    return {"success": True, "symbol": symbol}
```

---

**ジョブAPI修正（job_idを渡す）**:

`backend/api/jobs.py`:
```python
@router.post("/start")
async def start_job(request: JobRequest):
    """ジョブ開始（job_id付き）"""
    # 一旦エンキューしてjob_idを取得
    job = queue.enqueue(
        dummy_job,
        args=(request.symbol,),
        kwargs={"job_id": None},
        job_timeout='10m'
    )

    # job_idを渡して再エンキュー
    job = queue.enqueue(
        dummy_job,
        args=(request.symbol,),
        kwargs={"job_id": job.id},
        job_timeout='10m'
    )

    return {
        "job_id": job.id,
        "symbol": request.symbol,
        "message": "Job started"
    }
```

---

**`backend/main.py`にWebSocketルーター追加**:
```python
from backend.api.websocket import router as ws_router
app.include_router(ws_router, prefix="/ws", tags=["websocket"])
```

---

### WebSocketテスト

**テスト用HTML（`test_ws.html`）**:
```html
<!DOCTYPE html>
<html>
<head><title>WebSocket Test</title></head>
<body>
    <h1>WebSocket Log Viewer</h1>
    <input type="text" id="jobId" placeholder="Job ID">
    <button onclick="connect()">Connect</button>
    <button onclick="disconnect()">Disconnect</button>
    <pre id="logs" style="height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;"></pre>

    <script>
        let ws;

        function connect() {
            const jobId = document.getElementById('jobId').value;
            if (!jobId) {
                alert('Please enter Job ID');
                return;
            }

            ws = new WebSocket(`ws://localhost:8000/ws/logs/${jobId}`);

            ws.onopen = () => {
                addLog('[WebSocket Connected]');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                addLog(data.message);
            };

            ws.onclose = () => {
                addLog('[WebSocket Disconnected]');
            };
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function addLog(message) {
            const logArea = document.getElementById('logs');
            const timestamp = new Date().toLocaleTimeString();
            logArea.textContent += `[${timestamp}] ${message}\n`;
            logArea.scrollTop = logArea.scrollHeight;
        }
    </script>
</body>
</html>
```

**テスト手順**:
1. FastAPI起動
2. RQワーカー起動
3. curlでジョブ開始、job_idをメモ
4. `test_ws.html`を開いてjob_idを入力
5. 「Connect」クリック
6. リアルタイムでログが流れる

**ユウタ**: 「おお！ブラウザでログが見える！」

**ミコ**: 「これでPhase 3でClaude Codeの実行経過も見れるようになる」

---

## 📖 Scene 5: Claude Code SDK統合 - Phase 3

### Node.jsプロジェクト作成

**ミコ**: 「Phase 3だ。Claude Code SDKを統合する」

```bash
mkdir claude-agent-service
cd claude-agent-service
npm init -y
npm install @anthropic-ai/claude-agent-sdk express cors dotenv sqlite3 zod
```

**.env**:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
PORT=3000
DB_PATH=../data/crypto_data.db
```

---

### Claude Agent実装

**`src/agent.js`**:
```javascript
const { query, createSdkMcpServer } = require('@anthropic-ai/claude-agent-sdk');
const DbSaverTool = require('./tools/db_saver');

class ClaudeAgent {
  constructor() {
    this.dbSaver = new DbSaverTool();
  }

  async executeTask(symbol, task, logCallback) {
    const log = (msg) => {
      console.log(`[AGENT] ${msg}`);
      if (logCallback) logCallback(msg);
    };

    log(`🤖 Claude Code: Starting agentic execution for ${symbol}`);

    // カスタムツールを登録
    const mcpServer = createSdkMcpServer({
      name: 'crypto-tools',
      version: '1.0.0',
      tools: [
        {
          name: 'save_news_to_db',
          description: 'Save news article to database',
          inputSchema: this.dbSaver.getSchema(),
          handler: async (args) => await this.dbSaver.execute(args, log)
        }
      ]
    });

    log('🔧 Tools registered: save_news_to_db');

    // Agentic実行
    const results = [];

    for await (const message of query({
      prompt: `Search for ${symbol} cryptocurrency news and analyze sentiment. Use the save_news_to_db tool to save each article.`,
      options: {
        model: 'claude-sonnet-4-5-20250929',
        maxTurns: 20,
        includePartialMessages: true,
        mcpServers: {
          'crypto-tools': {
            type: 'sdk',
            name: 'crypto-tools',
            instance: mcpServer.instance
          }
        }
      }
    })) {
      if (message.type === 'stream_event') {
        const event = message.event;

        if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
          // テキストストリーム
          log(`💬 ${event.delta.text}`);
        }
      } else if (message.type === 'result') {
        log(`✅ Completed in ${message.num_turns} turns`);
        log(`⏱️  Duration: ${message.duration_ms}ms`);

        return {
          success: true,
          symbol,
          num_turns: message.num_turns,
          duration_ms: message.duration_ms,
          results
        };
      }
    }
  }
}

module.exports = ClaudeAgent;
```

---

**`src/tools/db_saver.js`** - DB保存ツール:
```javascript
const sqlite3 = require('sqlite3').verbose();
const { z } = require('zod');

class DbSaverTool {
  constructor() {
    this.db = new sqlite3.Database(process.env.DB_PATH);
  }

  getSchema() {
    return z.object({
      symbol: z.string().describe('Cryptocurrency symbol'),
      title: z.string().describe('News title'),
      url: z.string().url().optional().describe('Article URL'),
      source: z.string().optional().describe('News source'),
      sentiment_score: z.number().min(0).max(1).describe('Sentiment score (0-1)'),
      published_at: z.string().optional().describe('Publication date')
    });
  }

  async execute(args, logCallback) {
    const log = (msg) => {
      console.log(`[DB_SAVER] ${msg}`);
      if (logCallback) logCallback(msg);
    };

    try {
      log(`💾 Saving: ${args.title}`);
      log(`   Symbol: ${args.symbol}`);
      log(`   Sentiment: ${args.sentiment_score}`);

      await this.saveToDb(args);

      log(`✅ Saved to database`);

      return {
        success: true,
        message: 'News saved',
        data: args
      };
    } catch (error) {
      log(`❌ Error: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  saveToDb(data) {
    return new Promise((resolve, reject) => {
      const query = `
        INSERT INTO news (symbol, title, url, source, sentiment_score, published_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
      `;

      this.db.run(query, [
        data.symbol,
        data.title,
        data.url || null,
        data.source || null,
        data.sentiment_score,
        data.published_at || new Date().toISOString()
      ], function(err) {
        if (err) reject(err);
        else resolve({ id: this.lastID });
      });
    });
  }
}

module.exports = DbSaverTool;
```

---

**`src/server.js`** - Express サーバー:
```javascript
const express = require('express');
const cors = require('cors');
const ClaudeAgent = require('./agent');

const app = express();
app.use(cors());
app.use(express.json());

const agent = new ClaudeAgent();

// セッション管理（会話継続用）
const sessions = {};

app.post('/agent/execute', async (req, res) => {
  const { symbol, task } = req.body;
  const sessionId = `session_${Date.now()}`;

  try {
    const result = await agent.executeTask(symbol, task);

    // セッション保存
    sessions[sessionId] = {
      symbol,
      lastResult: result,
      createdAt: new Date()
    };

    res.json({
      success: true,
      result,
      session_id: sessionId
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/agent/continue', async (req, res) => {
  const { session_id, prompt } = req.body;

  if (!sessions[session_id]) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const session = sessions[session_id];

  try {
    // continue: true で実行
    const result = await agent.continueTask(session.symbol, prompt);

    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'claude-agent-service' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Claude Agent Service on port ${PORT}`);
});
```

---

**`src/agent.js`に`continueTask()`追加**:

```javascript
class ClaudeAgent {
  // ... 既存のコード ...

  async continueTask(symbol, prompt, logCallback) {
    const log = (msg) => {
      console.log(`[AGENT] ${msg}`);
      if (logCallback) logCallback(msg);
    };

    log(`🔄 Continuing conversation for ${symbol}`);
    log(`📝 Additional prompt: ${prompt}`);

    // continue: true で実行
    for await (const message of query({
      prompt,
      options: {
        model: 'claude-sonnet-4-5-20250929',
        maxTurns: 10,
        continue: true,  // ← 会話継続
        includePartialMessages: true,
        mcpServers: {
          'crypto-tools': {
            type: 'sdk',
            name: 'crypto-tools',
            instance: this.mcpServer.instance
          }
        }
      }
    })) {
      if (message.type === 'stream_event') {
        const event = message.event;

        if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
          log(`💬 ${event.delta.text}`);
        }
      } else if (message.type === 'result') {
        log(`✅ Completed in ${message.num_turns} turns`);

        return {
          success: true,
          symbol,
          num_turns: message.num_turns
        };
      }
    }
  }
}
```

---

### FastAPIブリッジ

**`backend/api/claude.py`**:
```python
"""Claude Code API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import asyncio
from redis import Redis
from rq import Queue
from backend.config import settings

router = APIRouter()

redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
queue = Queue(connection=redis_conn)

# セッション管理
sessions = {}

class ClaudeRequest(BaseModel):
    symbol: str
    task: str = "Search and analyze news"

class ClaudeContinueRequest(BaseModel):
    session_id: str
    prompt: str

def claude_job(symbol: str, task: str, job_id: str = None):
    """Claude Code実行ジョブ"""

    def log(msg):
        print(f"[CLAUDE_JOB] {msg}")

        if job_id:
            from backend.api.websocket import manager
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(manager.send_log(job_id, msg))
            loop.close()

    try:
        log(f"🚀 Starting Claude Code execution for {symbol}")

        # Node.jsサービスを呼び出し
        response = requests.post(
            "http://localhost:3000/agent/execute",
            json={"symbol": symbol, "task": task},
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            log("✅ Claude Code execution completed")

            # セッション保存
            if 'session_id' in result:
                sessions[result['session_id']] = {
                    'symbol': symbol,
                    'job_id': job_id
                }

            return result
        else:
            log(f"❌ Error: {response.status_code}")
            return {"success": False, "error": f"Status {response.status_code}"}

    except Exception as e:
        log(f"❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def claude_continue_job(symbol: str, prompt: str, job_id: str = None, session_id: str = None):
    """会話継続ジョブ"""

    def log(msg):
        print(f"[CLAUDE_CONTINUE] {msg}")
        if job_id:
            from backend.api.websocket import manager
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(manager.send_log(job_id, msg))
            loop.close()

    log(f"🔄 Continuing conversation for {symbol}")
    log(f"📝 Additional prompt: {prompt}")

    # Node.jsサービスを呼び出し（continue: true）
    response = requests.post(
        "http://localhost:3000/agent/continue",
        json={
            "session_id": session_id,
            "prompt": prompt
        },
        timeout=300
    )

    if response.status_code == 200:
        log("✅ Continuation completed")
        return response.json()
    else:
        log(f"❌ Error: {response.status_code}")
        return {"success": False, "error": f"Status {response.status_code}"}

@router.post("/execute")
async def execute_claude(request: ClaudeRequest):
    """Claude Code実行開始"""
    job = queue.enqueue(
        claude_job,
        args=(request.symbol, request.task),
        kwargs={"job_id": None},
        job_timeout='10m'
    )

    job = queue.enqueue(
        claude_job,
        args=(request.symbol, request.task),
        kwargs={"job_id": job.id},
        job_timeout='10m'
    )

    return {
        "job_id": job.id,
        "symbol": request.symbol,
        "message": "Claude Code execution started"
    }

@router.post("/continue")
async def continue_claude(request: ClaudeContinueRequest):
    """会話継続実行"""

    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]

    job = queue.enqueue(
        claude_continue_job,
        args=(session['symbol'], request.prompt),
        kwargs={"job_id": None, "session_id": request.session_id},
        job_timeout='10m'
    )

    job = queue.enqueue(
        claude_continue_job,
        args=(session['symbol'], request.prompt),
        kwargs={"job_id": job.id, "session_id": request.session_id},
        job_timeout='10m'
    )

    return {
        "job_id": job.id,
        "session_id": request.session_id,
        "message": "Continuation started"
    }
```

**`backend/main.py`に追加**:
```python
from backend.api.claude import router as claude_router
app.include_router(claude_router, prefix="/api/claude", tags=["claude"])
```

---

### Streamlit UI統合

`src/tools/parquet_dashboard.py`に追加:

```python
import streamlit as st
import requests

def show_claude_execution(symbol: str):
    st.subheader("🤖 Claude Code SDK - Agentic実行")

    # 初回実行
    if st.button("🚀 ニュース分析開始"):
        response = requests.post(
            "http://localhost:8000/api/claude/execute",
            json={"symbol": symbol, "task": "Search and analyze news"}
        )

        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ 開始 Job ID: {data['job_id']}")
            st.session_state["claude_job_id"] = data["job_id"]
            # session_idはジョブ完了後に取得

    # ステータス確認
    if "claude_job_id" in st.session_state:
        job_id = st.session_state["claude_job_id"]

        if st.button("🔄 ステータス確認"):
            response = requests.get(f"http://localhost:8000/api/jobs/status/{job_id}")
            if response.status_code == 200:
                job_data = response.json()
                st.write(f"ステータス: {job_data['status']}")

                if job_data['status'] == 'finished':
                    result = job_data.get('result', {})
                    st.json(result)

                    # session_idを保存
                    if 'session_id' in result:
                        st.session_state["claude_session_id"] = result['session_id']

                    st.balloons()

        st.info(f"💡 WebSocketログ: test_ws.html でJob ID: {job_id} を入力")

    # 会話継続
    if "claude_session_id" in st.session_state:
        st.markdown("---")
        st.subheader("💬 会話継続")

        continue_prompt = st.text_area(
            "追加の指示",
            placeholder="例: さっきの1つ目の記事をもっと詳しく分析して"
        )

        if st.button("▶️ 続きを実行"):
            if continue_prompt:
                response = requests.post(
                    "http://localhost:8000/api/claude/continue",
                    json={
                        "session_id": st.session_state["claude_session_id"],
                        "prompt": continue_prompt
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ 続きを実行中 Job ID: {data['job_id']}")
                    st.session_state["claude_job_id"] = data["job_id"]
```

---

### Phase 3テスト

**ターミナル1**: `python backend/main.py`
**ターミナル2**: `rq worker`
**ターミナル3**: `cd claude-agent-service && npm start`

```bash
curl -X POST http://localhost:8000/api/claude/execute \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "task": "Search and analyze news"}'
```

**WebSocketログ（リアルタイム）**:
```
🚀 Starting Claude Code execution for BTC
🤖 Claude Code: Starting agentic execution for BTC
🔧 Tools registered: save_news_to_db
💬 I'll search for Bitcoin news using WebSearch...
💬 Found 5 recent articles. Let me analyze them...
💬 Article 1: "BTC reaches $95,000"
💾 Saving: BTC reaches $95,000
   Symbol: BTC
   Sentiment: 0.9
✅ Saved to database
💬 Article 2: "Mining regulations tighten"
💾 Saving: Mining regulations tighten
   Symbol: BTC
   Sentiment: -0.3
✅ Saved to database
...
✅ Completed in 8 turns
⏱️  Duration: 45000ms
✅ Claude Code execution completed
```

**ユウタ**: 「すげー！各ターンの進行状況が全部見える！」

---

### 会話継続のテスト

**1. 初回実行完了後、session_idを取得**

**2. 追加依頼**:
```bash
curl -X POST http://localhost:8000/api/claude/continue \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_123", "prompt": "1つ目の記事をもっと詳しく分析して"}'
```

**WebSocketログ**:
```
🔄 Continuing conversation for BTC
📝 Additional prompt: 1つ目の記事をもっと詳しく分析して
💬 1つ目の記事は"BTC reaches $95,000"でした。
💬 この記事を詳しく分析します...
💬 記事の要点:
💬 - BTCが史上最高値$95,000に到達
💬 - 機関投資家の買いが加速
💬 - ETF承認の影響が続いている
💬 センチメント分析: 非常にポジティブ（+0.95）
💬 市場への影響: 短期的に更なる上昇が期待される
✅ Completed in 4 turns
```

**ユウタ**: 「おお！続きから実行できた！UIから対話的に分析できる！」

**ミコ**: 「Phase 3完成だ」

---

## 📖 Scene 6: 完成と振り返り

### 3週間後

**ユウタ**: 「ミコ、すげーよ！」

ユウタは興奮していた。

**ユウタ**: 「もう手動でニュース検索しなくていい。ボタン一つで全部やってくれる」

**ユウタ**: 「しかも、途中経過がリアルタイムで見えるから、何やってるか分かる」

**ユウタ**: 「追加で『もっと詳しく』って言えば、続きから分析してくれる」

**ミコ**: 「満足したか？」

**ユウタ**: 「めっちゃ満足！もう手動には戻れない」

---

### 完成した機能まとめ

```
【Phase 2: バックグラウンド実行基盤】
✅ FastAPI + Redis + RQ
✅ 非同期ジョブ実行
✅ ダッシュボードがフリーズしない

【Phase 3: Claude Code SDK統合】
✅ Node.js + Claude Agent SDK
✅ WebSearch でニュース取得
✅ 自動センチメント分析
✅ DB保存ツール

【Phase 4: WebSocketログ】
✅ Agentic実行の各ターンをリアルタイム表示
✅ Turn 1: WebSearch
✅ Turn 2-N: 記事分析
✅ Turn N+1: DB保存

【Phase 5: 会話継続】
✅ continue: true オプション
✅ UIから追加指示を送信
✅ 前回の実行の続きから分析
```

---

### 設計の振り返り

**なぜバックグラウンド実行？**
- 同期実行だとダッシュボードがフリーズ
- ユーザー体験が悪い
- → Redis + RQ で非同期化

**なぜWebSocket？**
- Claude CodeがAgenticに動く（複数ターン）
- 各ターンの進行状況を見たい
- → WebSocketでリアルタイムログ配信

**なぜ会話継続？**
- 初回実行だけでは不十分な場合がある
- 「もっと詳しく」と追加依頼したい
- → `continue: true` で前回の続きから実行

**全ての機能に必然性があった。**

---

### ユウタの変化

**3週間前**:
- 毎日手動でニュース検索（30分×2回）
- 見逃しが多い
- 記録が雑
- 疲れていた

**今**:
- ボタン一つで自動実行
- 見逃しゼロ
- 全てDB保存
- リアルタイムで監視
- 対話的に深掘り可能

**ユウタ**: 「自動化って最高だな」

**ミコ**: 「まだ始まったばかりだ」

---

## 📋 実装チェックリスト

### Phase 2: バックグラウンド実行
- [ ] Redis インストール＆起動
- [ ] `pip install fastapi uvicorn redis rq python-dotenv`
- [ ] `backend/config.py` 作成
- [ ] `backend/workers/dummy_worker.py` 作成
- [ ] `backend/api/jobs.py` 作成
- [ ] `backend/main.py` 作成
- [ ] FastAPI起動テスト
- [ ] RQワーカー起動テスト
- [ ] curlでジョブ実行テスト

### Phase 3: WebSocket統合
- [ ] `backend/api/websocket.py` 作成
- [ ] `dummy_worker.py` をWebSocket対応に修正
- [ ] `test_ws.html` 作成
- [ ] WebSocketログ表示確認

### Phase 4: Claude Code SDK統合
- [ ] `claude-agent-service/` プロジェクト作成
- [ ] `npm install` 実行
- [ ] `.env` に `ANTHROPIC_API_KEY` 設定
- [ ] `src/agent.js` 作成
- [ ] `src/tools/db_saver.js` 作成
- [ ] `src/server.js` 作成
- [ ] Node.jsサーバー起動テスト
- [ ] `backend/api/claude.py` 作成
- [ ] FastAPI → Node.js ブリッジテスト
- [ ] Claude Code実行＋WebSocketログ確認

### Phase 5: 会話継続
- [ ] セッション管理実装（Python）
- [ ] セッション管理実装（Node.js）
- [ ] `continueTask()` 実装
- [ ] `/api/claude/continue` エンドポイント
- [ ] `/agent/continue` エンドポイント
- [ ] Streamlit UI統合
- [ ] 会話継続テスト

---

## 🎯 実装開始コマンド

```bash
# プロジェクトルート
cd C:\Users\tatut\Documents\playground\grass-coin-trader

# Phase 2: バックグラウンド実行基盤
pip install fastapi uvicorn redis rq python-dotenv requests

# Redisセットアップ
wsl
sudo service redis-server start

# ディレクトリ作成
mkdir backend backend/api backend/workers

# ファイル作成（このドキュメントからコピー）
# - backend/config.py
# - backend/workers/dummy_worker.py
# - backend/api/jobs.py
# - backend/main.py

# テスト
python backend/main.py  # ターミナル1
rq worker --url redis://localhost:6379  # ターミナル2
```

---

## 🎓 次のステップ

**ユウタ**: 「次は何やるの？」

**ミコ**: 「数学的手法の実装だ」

**ユウタ**: 「GRU、LSTM-GARCH？」

**ミコ**: 「そう。Claude Codeでニュース分析は自動化できた。次は価格予測の精度を上げる」

**ユウタ**: 「おお、楽しみ！」

**ミコ**: 「でも、その前にこのドキュメントをしっかり読んで理解しろ」

**ユウタ**: 「了解！」

---

**最終更新**: 2025-10-27
**対象**: Phase 2 & 3 実装計画書（ストーリー完全版 - 会話継続機能付き）
