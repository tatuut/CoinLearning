# Phase 2 & 3 実装計画書

**Claude Code SDK統合への道**

---

## 📖 Scene 1: 全体像 - WebSocketの真の目的

### Phase 2 & 3の関係

**Phase 2（インフラ構築）**:
- FastAPI + Redis + WebSocket
- バックグラウンドジョブ実行基盤
- ダミージョブで動作確認のみ

**Phase 3（Claude Code SDK統合）**:
- Node.js + Claude Agent SDK
- Claude CodeがAgenticに実行
- 実行経過をWebSocketで表示

### なぜWebSocketが必要か？

**ユウタ**: 「なんでWebSocketを使うの？ニュース取得は一瞬じゃないの？」

**ミコ**: 「違う。Claude Codeは**Agenticに動く**んだ」

**ミコ**: 「普通のAPI呼び出しとは違う。複数のステップを踏む：」

```
【Claude CodeのAgentic実行例】

Turn 1: WebSearchツールを使ってBTCのニュースを検索
   → 5件の記事を発見

Turn 2: 各記事を読んで分析
   → センチメントスコアを計算

Turn 3: save_news_to_dbツールでDB保存
   → 保存完了

Turn 4: 結果をまとめて報告
```

**ユウタ**: 「あ、複数回やりとりするのか」

**ミコ**: 「そう。だから**各ターンの進行状況をリアルタイムで見たい**」

**ミコ**: 「WebSocketはそのために使う」

---

### アーキテクチャ図

```
【Phase 2完成時】
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │ HTTP POST /api/jobs/start
         ↓
┌─────────────────┐
│  FastAPI        │
│  - /api/jobs    │
│  - /ws/logs     │  ← WebSocket
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Redis Queue    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Worker (Dummy) │  ← ダミージョブ
└─────────────────┘
```

```
【Phase 3完成時】
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │ HTTP POST /api/claude/execute
         ↓
┌─────────────────┐
│  FastAPI        │
│  - /api/claude  │
│  - /ws/logs     │  ← Agentic実行のログ
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────┐
│  Node.js        │
│  Express        │
│  Claude SDK     │
│  - query()      │  ← Agentic実行
│  - WebSearch    │
│  - Custom Tools │
└─────────────────┘
```

---

## 📖 Scene 2: Phase 2 - インフラ構築

### 目標

**Phase 2はインフラのみ。実装はダミー。**

1. FastAPI REST API
2. Redis + RQ（バックグラウンドジョブ）
3. WebSocket（ログ配信）
4. Streamlit UI連携

### ファイル構成

```
backend/
├── main.py              # FastAPIサーバー
├── config.py            # 設定
├── api/
│   ├── jobs.py          # ジョブAPI
│   └── websocket.py     # WebSocket
└── workers/
    └── dummy_worker.py  # ダミーワーカー
```

### 実装手順

**1. 依存関係インストール**
```bash
pip install fastapi uvicorn redis rq websockets python-dotenv
```

**2. Redisセットアップ**
```bash
wsl
sudo service redis-server start
```

**3. .env作成**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

**4. コード作成**

`backend/config.py`:
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

`backend/workers/dummy_worker.py`:
```python
"""
Dummy worker for Phase 2 infrastructure testing
"""
import time
import asyncio

async def async_log(message: str, job_id: str):
    """WebSocketログ送信"""
    from backend.api.websocket import manager
    await manager.send_log(job_id, message)

def dummy_job(symbol: str, job_id: str = None):
    """ダミージョブ（Phase 3でClaude Code実行に置き換え）"""

    def log(msg):
        print(f"[DUMMY] {msg}")
        if job_id:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_log(msg, job_id))
            loop.close()

    log(f"🚀 Dummy job started for {symbol}")
    log("⏳ Step 1/3...")
    time.sleep(2)
    log("✅ Step 1 done")

    log("⏳ Step 2/3...")
    time.sleep(2)
    log("✅ Step 2 done")

    log("⏳ Step 3/3...")
    time.sleep(1)
    log("✅ Step 3 done")

    log("🎉 Completed!")

    return {"success": True, "symbol": symbol}
```

`backend/api/websocket.py`:
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

`backend/api/jobs.py`:
```python
"""Job API"""
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
    job = queue.enqueue(
        dummy_job,
        args=(request.symbol,),
        kwargs={"job_id": None},
        job_timeout='10m'
    )

    # Re-enqueue with job_id
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

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    from rq.job import Job
    job = Job.fetch(job_id, connection=redis_conn)

    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result if job.is_finished else None
    }
```

`backend/main.py`:
```python
"""FastAPI main server"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.jobs import router as jobs_router
from backend.api.websocket import router as ws_router
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
app.include_router(ws_router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "Grass Coin Trader API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=True)
```

**5. テスト**

ターミナル1:
```bash
python backend/main.py
```

ターミナル2:
```bash
rq worker --url redis://localhost:6379
```

ターミナル3:
```bash
curl -X POST http://localhost:8000/api/jobs/start \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC"}'
```

WebSocketテスト用HTML（`test_ws.html`）:
```html
<!DOCTYPE html>
<html>
<head><title>WS Test</title></head>
<body>
    <h1>WebSocket Log Viewer</h1>
    <input type="text" id="jobId" placeholder="Job ID">
    <button onclick="connect()">Connect</button>
    <pre id="logs"></pre>
    <script>
        let ws;
        function connect() {
            const jobId = document.getElementById('jobId').value;
            ws = new WebSocket(`ws://localhost:8000/ws/logs/${jobId}`);
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                document.getElementById('logs').textContent += data.message + '\n';
            };
        }
    </script>
</body>
</html>
```

**Phase 2完了チェック**:
- ✅ FastAPI起動
- ✅ RQワーカー起動
- ✅ ジョブ開始できる
- ✅ WebSocketでログが流れる

---

## 📖 Scene 3: Phase 3 - Claude Code SDK統合

### 目標

**Phase 2のインフラの上に、Claude Code SDKを統合する。**

1. Node.js Express サーバー作成
2. Claude Agent SDK統合
3. カスタムツール（DB保存）
4. FastAPI → Node.js ブリッジ

### ファイル構成

```
claude-agent-service/
├── package.json
├── .env
└── src/
    ├── server.js        # Express
    ├── agent.js         # Claude SDK
    └── tools/
        └── db_saver.js  # DB保存ツール
```

### 実装手順

**1. Node.jsプロジェクト作成**

```bash
mkdir claude-agent-service
cd claude-agent-service
npm init -y
npm install @anthropic-ai/claude-agent-sdk express cors dotenv sqlite3 zod
```

**2. .env作成**

```bash
ANTHROPIC_API_KEY=your_key_here
PORT=3000
DB_PATH=../data/crypto_data.db
```

**3. コード作成**

`src/agent.js`:
```javascript
const { query, createSdkMcpServer } = require('@anthropic-ai/claude-agent-sdk');

class ClaudeAgent {
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
      tools: [/* DB保存ツールなど */]
    });

    // Agentic実行
    for await (const message of query({
      prompt: `Search for ${symbol} news and analyze sentiment`,
      options: {
        model: 'claude-sonnet-4-5-20250929',
        maxTurns: 20,
        includePartialMessages: true,
        mcpServers: {
          'crypto-tools': { type: 'sdk', name: 'crypto-tools', instance: mcpServer.instance }
        }
      }
    })) {
      if (message.type === 'stream_event' && message.event.type === 'content_block_delta') {
        log(`💬 ${message.event.delta.text}`);
      } else if (message.type === 'result') {
        log(`✅ Completed in ${message.num_turns} turns`);
        return { success: true, num_turns: message.num_turns };
      }
    }
  }
}

module.exports = ClaudeAgent;
```

`src/server.js`:
```javascript
const express = require('express');
const cors = require('cors');
const ClaudeAgent = require('./agent');

const app = express();
app.use(cors());
app.use(express.json());

const agent = new ClaudeAgent();

app.post('/agent/execute', async (req, res) => {
  const { symbol, task } = req.body;
  const result = await agent.executeTask(symbol, task);
  res.json({ success: true, result });
});

app.listen(3000, () => console.log('🚀 Node.js Claude Agent Service on port 3000'));
```

**4. FastAPIブリッジ作成**

`backend/api/claude.py`:
```python
"""Claude Code API"""
from fastapi import APIRouter
from pydantic import BaseModel
import requests
from redis import Redis
from rq import Queue
from backend.config import settings

router = APIRouter()

redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
queue = Queue(connection=redis_conn)

class ClaudeRequest(BaseModel):
    symbol: str
    task: str = "Search and analyze news"

def claude_job(symbol: str, task: str, job_id: str = None):
    """Claude Code実行ジョブ"""
    import time
    import asyncio

    def log(msg):
        print(f"[CLAUDE_JOB] {msg}")
        if job_id:
            from backend.api.websocket import manager
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(manager.send_log(job_id, msg))
            loop.close()

    log(f"🚀 Starting Claude Code execution for {symbol}")

    # Node.jsサービスを呼び出し
    response = requests.post(
        "http://localhost:3000/agent/execute",
        json={"symbol": symbol, "task": task},
        timeout=300
    )

    if response.status_code == 200:
        log("✅ Claude Code execution completed")
        return response.json()
    else:
        log(f"❌ Error: {response.status_code}")
        return {"success": False, "error": f"Status {response.status_code}"}

@router.post("/execute")
async def execute_claude(request: ClaudeRequest):
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
```

`backend/main.py`に追加:
```python
from backend.api.claude import router as claude_router
app.include_router(claude_router, prefix="/api/claude", tags=["claude"])
```

**5. テスト**

ターミナル1: `python backend/main.py`
ターミナル2: `rq worker`
ターミナル3: `cd claude-agent-service && npm start`

```bash
curl -X POST http://localhost:8000/api/claude/execute \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "task": "Search and analyze news"}'
```

WebSocketで実行経過が見える（複数ターン）。

---

## 📖 Scene 4: Streamlit UI統合

`src/tools/parquet_dashboard.py`に追加:

```python
import streamlit as st
import requests

def show_claude_execution(symbol: str):
    st.subheader("🤖 Claude Code SDK - Agentic実行")

    if st.button("🚀 実行開始"):
        response = requests.post(
            "http://localhost:8000/api/claude/execute",
            json={"symbol": symbol, "task": "Search and analyze news"}
        )

        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ 開始しました Job ID: {data['job_id']}")
            st.session_state["claude_job_id"] = data["job_id"]

    if "claude_job_id" in st.session_state:
        job_id = st.session_state["claude_job_id"]

        if st.button("🔄 ステータス確認"):
            response = requests.get(f"http://localhost:8000/api/jobs/status/{job_id}")
            if response.status_code == 200:
                job_data = response.json()
                st.write(f"ステータス: {job_data['status']}")
                if job_data['status'] == 'finished':
                    st.json(job_data['result'])

        st.info(f"💡 WebSocketログを見るには test_ws.html を開いてJob ID: {job_id} を入力")
```

---

## 📖 Scene 5: まとめ

### Phase 2 & 3の成果

**Phase 2（インフラ）**:
✅ FastAPI + Redis + WebSocket構築
✅ バックグラウンドジョブ実行
✅ ダミージョブで動作確認

**Phase 3（Claude Code SDK）**:
✅ Node.js + Claude Agent SDK統合
✅ Agenticに実行（複数ターン）
✅ WebSearchでニュース取得
✅ カスタムツール（DB保存）
✅ 実行経過をWebSocketで表示

### WebSocketの真の価値

**Claude CodeのAgentic実行経過をリアルタイムで見れる**:
- Turn 1: WebSearchでニュース検索
- Turn 2: 各記事を分析
- Turn 3: save_news_to_dbツールで保存
- Turn 4: 結果報告

各ターンの思考プロセス、ツール使用、結果がリアルタイムで見える。

### チェックリスト

**Phase 2**:
- [ ] FastAPIサーバー起動
- [ ] Redisセットアップ
- [ ] RQワーカー起動
- [ ] ダミージョブ実行成功
- [ ] WebSocketでログ表示成功

**Phase 3**:
- [ ] Node.jsサーバー起動
- [ ] Claude Agent SDK動作
- [ ] FastAPI→Node.jsブリッジ動作
- [ ] Agentic実行でWebSearch成功
- [ ] 実行経過がWebSocketで表示
- [ ] DB保存ツール動作

---

## 🎯 実装開始

```bash
# Phase 2開始
cd C:\Users\tatut\Documents\playground\grass-coin-trader

# 1. 依存関係
pip install fastapi uvicorn redis rq websockets python-dotenv requests

# 2. Redis起動
wsl
sudo service redis-server start

# 3. ファイル作成
mkdir backend backend/api backend/workers
# このドキュメントのコードをコピー

# 4. テスト
python backend/main.py
rq worker --url redis://localhost:6379
```

---

**最終更新**: 2025-10-27
**対象**: Phase 2 & 3 実装計画書（簡潔版）
