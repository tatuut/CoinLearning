# Phase 2 & 3 実装計画書

**Claude Code SDK統合への道**

---

## 📖 Scene 1: 2つのフェーズ、1つの目標

### ユウタの疑問

**ユウタ**: 「ミコ、Phase 2とPhase 3って何が違うの？」

**ミコ**: 「Phase 2は『基礎インフラ』、Phase 3は『Claude Code統合』だ」

**ミコ**: 「Phase 2を先に作らないと、Phase 3は動かない」

**ユウタ**: 「なんで？」

**ミコ**: 「説明するぞ」

---

### アーキテクチャの全体像

```
【Phase 2完成時】
┌─────────────────┐
│  Streamlit UI   │  ← ユーザーが操作
│  (Port 8501)    │
└────────┬────────┘
         │ HTTP POST /api/news/fetch
         ↓
┌─────────────────┐
│  FastAPI        │  ← Python バックエンド
│  (Port 8000)    │
│  - /api/news    │
│  - /ws/logs     │  ← WebSocket（リアルタイムログ）
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Redis Queue    │  ← バックグラウンドジョブ
│  (RQ)           │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Worker Process │  ← ニュース取得実行
│  - NewsAPI      │
│  - Claude API   │
│  - DB保存       │
└─────────────────┘
```

**ユウタ**: 「Phase 2だけでも動くんだ」

**ミコ**: 「そう。NewsAPIとClaude APIを使えば、完全自動でニュース取得できる」

**ミコ**: 「でも、お前は『Claude Code SDK』を使いたいんだろ？」

**ユウタ**: 「うん！WebSearch機能を使いたい」

---

```
【Phase 3完成時（Phase 2の上に追加）】
┌─────────────────┐
│  Streamlit UI   │  ← ユーザーが操作
│  (Port 8501)    │
└────────┬────────┘
         │ HTTP POST /api/claude-code/execute
         ↓
┌─────────────────┐
│  FastAPI        │  ← Python バックエンド
│  (Port 8000)    │
│  - /api/news    │  (Phase 2)
│  - /api/claude-code/execute  │  (Phase 3追加)
│  - /ws/logs     │
└────────┬────────┘
         │ HTTP POST /agent/execute
         ↓
┌─────────────────┐
│  Node.js        │  ← JavaScript マイクロサービス
│  Express Server │
│  (Port 3000)    │
│                 │
│  Claude Agent   │
│  SDK            │
│  - query()      │
│  - WebSearch    │
│  - Custom Tools │
└─────────────────┘
```

**ユウタ**: 「Phase 3では、Node.jsサーバーを追加するのか」

**ミコ**: 「そう。Claude Agent SDKはNode.js（JavaScript）だけだから」

**ミコ**: 「Pythonから → Node.jsに依頼 → Claude Code SDK実行 → 結果を返す」

**ユウタ**: 「複雑だな...」

**ミコ**: 「だから**Phase 2を先に完成させる**。Phase 2が動けば、Phase 3は『Node.js追加するだけ』だ」

---

### 実装順序

```markdown
【実装ステップ】

## Phase 2（3-4日）
1. FastAPI基礎（API作成）
2. Redis Queue統合（バックグラウンド実行）
3. WebSocket統合（リアルタイムログ）
4. Streamlit UI統合（ボタン追加）
5. テスト

## Phase 3（3-5日）
6. Node.js Express サーバー作成
7. Claude Agent SDK統合
8. カスタムツール実装（DB保存、分析）
9. FastAPI → Node.js ブリッジ
10. Streamlit UI拡張
11. テスト
12. 統合テスト
```

**ユウタ**: 「Phase 2から始めよう！」

---

## 📖 Scene 2: Phase 2 実装計画

### Phase 2の目標

**ミコ**: 「Phase 2で実現すること：」

```markdown
【Phase 2の目標】

1. FastAPI REST APIサーバー構築
2. Redis + RQ でバックグラウンドジョブ実行基盤
3. WebSocketでリアルタイムログ配信
4. Streamlit UIから API呼び出し
5. **実際のニュース取得はPhase 3で実装**（Phase 2はインフラのみ）

【重要】
Phase 2では、NewsAPIやClaude APIは使いません。
ダミーデータでインフラが動くことを確認するだけです。

Phase 3でClaude Code SDKのWebSearchを使って、
実際のニュース取得を実装します。

【技術スタック】
- FastAPI（Python）: REST API
- Redis Queue（RQ）: バックグラウンドジョブ
- WebSocket: リアルタイム通信
- Streamlit: UI
```

---

### Phase 2のファイル構成

**ユウタ**: 「どんなファイルを作るの？」

**ミコ**: 「こうだ」

```
grass-coin-trader/
├── backend/                     【新規作成】
│   ├── __init__.py
│   ├── main.py                  # FastAPIメインサーバー
│   ├── api/
│   │   ├── __init__.py
│   │   ├── news.py              # ニュース取得API（Phase 2: ダミー）
│   │   └── websocket.py         # WebSocketエンドポイント
│   ├── workers/
│   │   ├── __init__.py
│   │   └── news_worker.py       # バックグラウンドワーカー（Phase 2: ダミー）
│   └── config.py                # 設定ファイル
│
├── src/tools/
│   └── parquet_dashboard.py     【既存・修正】
│       ↑ ニュース自動取得ボタン追加
│
├── requirements.txt             【既存・追記】
│   ↑ fastapi, uvicorn, redis, rq, websockets追加
│
├── .env                         【新規作成】
│   ↑ APIキー保存
│
└── README.md                    【既存・更新】
    ↑ Phase 2セットアップ手順追加
```

**ユウタ**: 「結構増えるな」

**ミコ**: 「でも1つ1つは短いファイルだ。順番に作る」

---

### Phase 2の実装手順（概要）

```markdown
【Phase 2実装ステップ】

## ステップ1: FastAPI基礎（1日目）
- FastAPIプロジェクト構築
- `/api/news/fetch` エンドポイント作成
- 簡単なテスト（curl or Postman）

## ステップ2: Redis Queue統合（1日目）
- Redisインストール
- RQ（Redis Queue）セットアップ
- バックグラウンドワーカー実装
- ジョブキュー動作確認

## ステップ3: WebSocket統合（2日目）
- WebSocketエンドポイント実装
- リアルタイムログ配信
- Streamlitからログ受信

## ステップ4: Streamlit UI統合（2日目）
- ダッシュボードにボタン追加
- FastAPI呼び出し
- WebSocketでログ表示

## ステップ5: テスト（3-4日目）
- エンドツーエンドテスト
- エラーハンドリング
- ログ改善
```

---

## 📖 Scene 3: Phase 2 ステップ1 - FastAPI基礎

### FastAPIプロジェクトの作成

**ミコ**: 「まずはFastAPIの骨組みを作る」

#### 1. 必要なパッケージをインストール

```bash
cd C:\Users\tatut\Documents\playground\grass-coin-trader

pip install fastapi uvicorn redis rq websockets python-dotenv requests
```

**出力例**:
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 redis-5.0.1 rq-1.16.0 websockets-12.0 python-dotenv-1.0.0 requests-2.31.0
```

**注意**: NewsAPIやAnthropic APIは使いません（Phase 3でNode.js側でClaude SDK使用）

---

#### 2. `.env` ファイルを作成

```bash
# プロジェクトルートに作成
touch .env
```

**.env の内容**:
```bash
# Redis設定
REDIS_HOST=localhost
REDIS_PORT=6379

# FastAPI設定
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

**ユウタ**: 「NewsAPIのキーは？」

**ミコ**: 「Phase 2では不要だ。Phase 3でNode.js側に設定する」

---

#### 3. `backend/config.py` - 設定ファイル

```python
"""
Configuration settings for the backend
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    """Application settings"""

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

    # FastAPI
    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))

    # Database
    DB_PATH = "data/crypto_data.db"

    # Node.js Claude Agent Service
    CLAUDE_AGENT_URL = os.getenv("CLAUDE_AGENT_URL", "http://localhost:3000")

settings = Settings()
```

**注意**: NewsAPIやAnthropic APIの設定は削除しました（Phase 3でNode.js側で管理）

---

#### 4. `backend/main.py` - FastAPIメインサーバー

```python
"""
FastAPI main server for Grass Coin Trader backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Grass Coin Trader API",
    description="Backend API for cryptocurrency analysis",
    version="1.0.0"
)

# CORS設定（StreamlitからアクセスできるようにCORS許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限すべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Grass Coin Trader API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# APIルーターを後で追加
# from backend.api.news import router as news_router
# app.include_router(news_router, prefix="/api/news", tags=["news"])

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True  # 開発時のみ（ファイル変更で自動リロード）
    )
```

---

#### 5. テスト実行

```bash
# FastAPIサーバーを起動
python backend/main.py
```

**期待される出力**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**別ターミナルでテスト**:
```bash
curl http://localhost:8000/
```

**期待される出力**:
```json
{
  "message": "Grass Coin Trader API",
  "version": "1.0.0",
  "status": "running"
}
```

**ユウタ**: 「おお、動いた！」

**ミコ**: 「よし。FastAPIの基礎はできた」

---

## 📖 Scene 4: Phase 2 ステップ2 - Redis Queue統合

### Redisのセットアップ

**ミコ**: 「次はバックグラウンドジョブのためにRedisを入れる」

#### 1. Redisをインストール（Windows）

**Option A: WSL2経由（推奨）**
```bash
# WSL2でUbuntuを起動
wsl

# Redis インストール
sudo apt update
sudo apt install redis-server

# Redis起動
sudo service redis-server start

# 確認
redis-cli ping
# 出力: PONG
```

**Option B: Windows版Redis（簡易版）**
```bash
# Chocolatey経由
choco install redis-64

# または、GitHub Releasesからダウンロード
# https://github.com/tporadowski/redis/releases
```

**ユウタ**: 「Redisって何？」

**ミコ**: 「インメモリデータベース。キューの管理に使う」

---

#### 2. `backend/workers/news_worker.py` - バックグラウンドワーカー（ダミー実装）

```python
"""
Background worker for news fetching (Phase 2: Infrastructure only)

Phase 2では、実際のニュース取得は行いません。
ダミーデータでインフラが正しく動作することを確認します。

Phase 3でClaude Code SDKを統合し、実際のニュース取得を実装します。
"""
import time
from typing import Dict, Any
from backend.config import settings

def fetch_news_job(symbol: str, log_callback=None) -> Dict[str, Any]:
    """
    Background job to fetch news for a symbol (Phase 2: Dummy implementation)

    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC')
        log_callback: Optional callback for logging

    Returns:
        Result dictionary
    """
    def log(message: str):
        """Helper to log messages"""
        if log_callback:
            log_callback(message)
        print(f"[NEWS_WORKER] {message}")

    try:
        log(f"🚀 Starting news fetch for {symbol}...")
        log("⚠️  Phase 2: Using dummy data (no actual API calls)")

        # ステップ1: ダミーニュース生成
        log("📰 Step 1/3: Generating dummy news data...")
        time.sleep(2)  # シミュレーション
        news_items = [
            {"title": f"{symbol} reaches new high", "source": "CoinDesk (Dummy)"},
            {"title": f"{symbol} adoption increases", "source": "Bloomberg (Dummy)"}
        ]
        log(f"✅ Generated {len(news_items)} dummy articles")

        # ステップ2: ダミーセンチメントスコア
        log("🤖 Step 2/3: Calculating dummy sentiment score...")
        time.sleep(2)  # シミュレーション
        sentiment_score = 0.75
        log(f"✅ Dummy sentiment score: {sentiment_score}")

        # ステップ3: （実際にはDBに保存しない）
        log("💾 Step 3/3: Simulating database save...")
        time.sleep(1)  # シミュレーション
        log("✅ (Phase 2: DB save skipped)")

        log("🎉 News fetch simulation completed!")
        log("💡 Phase 3でClaude Code SDKを統合し、実際のニュース取得を実装します")

        return {
            "success": True,
            "symbol": symbol,
            "news_count": len(news_items),
            "sentiment_score": sentiment_score,
            "phase": "Phase 2 (Dummy)",
            "note": "Actual implementation will be done in Phase 3 with Claude Code SDK"
        }

    except Exception as e:
        log(f"❌ Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
```

**重要**: Phase 2では、NewsAPIやClaude APIは一切使いません。ダミーデータで動作確認するだけです。

---

#### 3. `backend/api/news.py` - ニュース取得API

```python
"""
News API endpoints
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from backend.config import settings
from backend.workers.news_worker import fetch_news_job

router = APIRouter()

# Redis接続
redis_conn = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# RQキュー
queue = Queue(connection=redis_conn)

class NewsFetchRequest(BaseModel):
    """Request model for news fetching"""
    symbol: str

class NewsFetchResponse(BaseModel):
    """Response model for news fetching"""
    job_id: str
    symbol: str
    message: str

@router.post("/fetch", response_model=NewsFetchResponse)
async def fetch_news(request: NewsFetchRequest):
    """
    Start background news fetching job

    Args:
        request: NewsFetchRequest with symbol

    Returns:
        NewsFetchResponse with job_id
    """
    try:
        # ジョブをキューに追加
        job = queue.enqueue(
            fetch_news_job,
            args=(request.symbol,),
            job_timeout='10m',  # 10分でタイムアウト
            result_ttl=3600     # 結果を1時間保持
        )

        return NewsFetchResponse(
            job_id=job.id,
            symbol=request.symbol,
            message=f"News fetch started for {request.symbol}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status

    Args:
        job_id: Job ID

    Returns:
        Job status and result
    """
    try:
        from rq.job import Job

        job = Job.fetch(job_id, connection=redis_conn)

        return {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "error": str(job.exc_info) if job.is_failed else None
        }

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")
```

---

#### 4. `backend/main.py` を更新（ルーター追加）

```python
# ... 既存のコード ...

# APIルーターを追加
from backend.api.news import router as news_router
app.include_router(news_router, prefix="/api/news", tags=["news"])

# ... 残りのコード ...
```

---

#### 5. RQワーカーを起動

**ターミナル1: FastAPIサーバー**
```bash
python backend/main.py
```

**ターミナル2: RQワーカー**
```bash
cd C:\Users\tatut\Documents\playground\grass-coin-trader
rq worker --url redis://localhost:6379
```

**期待される出力（ターミナル2）**:
```
Worker rq:worker:12345 started with PID 67890
Listening on default...
```

---

#### 6. テスト実行

**ターミナル3: curlでテスト**
```bash
curl -X POST http://localhost:8000/api/news/fetch \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"BTC\"}"
```

**期待される出力**:
```json
{
  "job_id": "abc123-def456-ghi789",
  "symbol": "BTC",
  "message": "News fetch started for BTC"
}
```

**ターミナル2（RQワーカー）の出力**:
```
[NEWS_WORKER] Starting news fetch for BTC...
[NEWS_WORKER] Step 1/3: Fetching news from NewsAPI...
[NEWS_WORKER] ✓ Found 2 news articles
[NEWS_WORKER] Step 2/3: Analyzing sentiment with Claude...
[NEWS_WORKER] ✓ Sentiment score: 0.75
[NEWS_WORKER] Step 3/3: Saving to database...
[NEWS_WORKER] ✓ Saved to database
[NEWS_WORKER] ✅ News fetch completed successfully
default: backend.workers.news_worker.fetch_news_job('BTC') (abc123-def456-ghi789)
```

**ジョブステータス確認**:
```bash
curl http://localhost:8000/api/news/job/abc123-def456-ghi789
```

**期待される出力**:
```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "finished",
  "result": {
    "success": true,
    "symbol": "BTC",
    "news_count": 2,
    "sentiment_score": 0.75
  },
  "error": null
}
```

**ユウタ**: 「すげー！バックグラウンドで動いてる！」

**ミコ**: 「これがRedis Queueの力だ」

---

## 📖 Scene 5: Phase 2 ステップ3 - WebSocket統合

### リアルタイムログ配信

**ミコ**: 「次はWebSocketでログをリアルタイム配信する」

#### 1. `backend/api/websocket.py` - WebSocketエンドポイント

```python
"""
WebSocket endpoints for real-time logging
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

router = APIRouter()

# アクティブな接続を管理
active_connections: Dict[str, Set[WebSocket]] = {}

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()

        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()

        self.active_connections[job_id].add(websocket)
        print(f"[WS] Client connected to job {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        """Disconnect a WebSocket client"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)

            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

        print(f"[WS] Client disconnected from job {job_id}")

    async def send_log(self, job_id: str, message: str):
        """Send log message to all clients subscribed to job_id"""
        if job_id in self.active_connections:
            disconnected = set()

            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json({
                        "type": "log",
                        "message": message
                    })
                except Exception as e:
                    print(f"[WS] Error sending to client: {e}")
                    disconnected.add(connection)

            # Remove disconnected clients
            for conn in disconnected:
                self.active_connections[job_id].discard(conn)

manager = ConnectionManager()

@router.websocket("/logs/{job_id}")
async def websocket_logs(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time logs

    Args:
        websocket: WebSocket connection
        job_id: Job ID to subscribe to
    """
    await manager.connect(websocket, job_id)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()

            # Echo back (optional)
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket, job_id)
```

---

#### 2. `backend/workers/news_worker.py` を更新（WebSocketログ対応）

```python
"""
Background worker for news fetching (with WebSocket logging)
"""
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from backend.config import settings

async def async_log(message: str, job_id: str):
    """Send log message via WebSocket"""
    from backend.api.websocket import manager
    await manager.send_log(job_id, message)

def fetch_news_job(symbol: str, job_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Background job to fetch news for a symbol

    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC')
        job_id: Optional job ID for WebSocket logging

    Returns:
        Result dictionary
    """
    def log(message: str):
        """Helper to log messages"""
        print(f"[NEWS_WORKER] {message}")

        # WebSocketログ送信
        if job_id:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(async_log(message, job_id))
                loop.close()
            except Exception as e:
                print(f"[NEWS_WORKER] WebSocket log error: {e}")

    try:
        log(f"🚀 Starting news fetch for {symbol}...")

        # ステップ1: NewsAPIでニュース取得
        log("📰 Step 1/3: Fetching news from NewsAPI...")
        time.sleep(2)  # シミュレーション
        news_items = [
            {"title": "BTC reaches new high", "source": "CoinDesk"},
            {"title": "BTC adoption increases", "source": "Bloomberg"}
        ]
        log(f"✅ Found {len(news_items)} news articles")

        # ステップ2: Claude APIでセンチメント分析
        log("🤖 Step 2/3: Analyzing sentiment with Claude...")
        time.sleep(2)  # シミュレーション
        sentiment_score = 0.75
        log(f"✅ Sentiment score: {sentiment_score}")

        # ステップ3: DBに保存
        log("💾 Step 3/3: Saving to database...")
        time.sleep(1)  # シミュレーション
        log("✅ Saved to database")

        log("🎉 News fetch completed successfully!")

        return {
            "success": True,
            "symbol": symbol,
            "news_count": len(news_items),
            "sentiment_score": sentiment_score
        }

    except Exception as e:
        log(f"❌ Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

#### 3. `backend/api/news.py` を更新（job_id渡す）

```python
# ... 既存のコード ...

@router.post("/fetch", response_model=NewsFetchResponse)
async def fetch_news(request: NewsFetchRequest):
    """
    Start background news fetching job
    """
    try:
        # ジョブをキューに追加（job_idを渡す）
        job = queue.enqueue(
            fetch_news_job,
            args=(request.symbol,),
            kwargs={"job_id": None},  # 後でjob.idを渡す
            job_timeout='10m',
            result_ttl=3600
        )

        # job_idを更新
        job.kwargs = {"job_id": job.id}
        job.save()

        # 再度エンキュー（job_id付き）
        job = queue.enqueue(
            fetch_news_job,
            args=(request.symbol,),
            kwargs={"job_id": job.id},
            job_timeout='10m',
            result_ttl=3600
        )

        return NewsFetchResponse(
            job_id=job.id,
            symbol=request.symbol,
            message=f"News fetch started for {request.symbol}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

#### 4. `backend/main.py` を更新（WebSocketルーター追加）

```python
# ... 既存のコード ...

# WebSocketルーターを追加
from backend.api.websocket import router as websocket_router
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])

# ... 残りのコード ...
```

---

#### 5. テスト実行

**HTML WebSocketクライアント（テスト用）**

`test_websocket.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <h1>WebSocket Log Viewer</h1>
    <div>
        <label>Job ID: <input type="text" id="jobId" placeholder="Enter job ID"></label>
        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
    </div>
    <div id="logs" style="margin-top: 20px; border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll;">
        <pre id="logContent"></pre>
    </div>

    <script>
        let ws = null;

        function connect() {
            const jobId = document.getElementById('jobId').value;
            if (!jobId) {
                alert('Please enter a job ID');
                return;
            }

            ws = new WebSocket(`ws://localhost:8000/ws/logs/${jobId}`);

            ws.onopen = () => {
                appendLog('[Connected]');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'log') {
                    appendLog(data.message);
                }
            };

            ws.onclose = () => {
                appendLog('[Disconnected]');
            };

            ws.onerror = (error) => {
                appendLog(`[Error] ${error}`);
            };
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function appendLog(message) {
            const logContent = document.getElementById('logContent');
            const timestamp = new Date().toLocaleTimeString();
            logContent.textContent += `[${timestamp}] ${message}\n`;

            // Auto-scroll
            const logsDiv = document.getElementById('logs');
            logsDiv.scrollTop = logsDiv.scrollHeight;
        }
    </script>
</body>
</html>
```

**テスト手順**:
1. FastAPIサーバー起動
2. RQワーカー起動
3. curlでニュース取得開始、job_idをメモ
4. `test_websocket.html` をブラウザで開く
5. job_idを入力して「Connect」
6. リアルタイムでログが表示される

**ユウタ**: 「おお！ログがリアルタイムで流れてる！」

**ミコ**: 「これでユーザーは進行状況を見れるようになった」

---

## 📖 Scene 6: Phase 2 ステップ4 - Streamlit UI統合

### ダッシュボードにボタン追加

**ミコ**: 「最後に、Streamlitダッシュボードと統合する」

#### 1. `src/tools/parquet_dashboard.py` を更新

既存ファイルに以下を追加：

```python
import streamlit as st
import requests
import json
from typing import Optional
import asyncio
import websockets

# ... 既存のコード ...

def show_news_automation(symbol: str):
    """
    ニュース自動取得セクション

    Args:
        symbol: 暗号通貨シンボル
    """
    st.markdown("---")
    st.subheader("📰 ニュース自動取得")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🚀 ニュース取得開始", key=f"fetch_news_{symbol}"):
            # FastAPI に POST リクエスト
            try:
                response = requests.post(
                    "http://localhost:8000/api/news/fetch",
                    json={"symbol": symbol},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    job_id = data["job_id"]

                    st.success(f"✅ ニュース取得を開始しました！")
                    st.info(f"Job ID: {job_id}")

                    # セッションステートに保存
                    st.session_state["current_job_id"] = job_id
                    st.session_state["show_logs"] = True

                else:
                    st.error(f"❌ エラー: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ FastAPIサーバーに接続できません。サーバーが起動しているか確認してください。")
            except Exception as e:
                st.error(f"❌ エラー: {str(e)}")

    with col2:
        st.info("📝 ボタンを押すと、バックグラウンドでニュース取得が開始されます。進行状況はログで確認できます。")

    # ログ表示セクション
    if st.session_state.get("show_logs", False):
        show_job_logs()

def show_job_logs():
    """
    ジョブログを表示
    """
    job_id = st.session_state.get("current_job_id")

    if not job_id:
        return

    st.markdown("---")
    st.subheader("📊 実行ログ")

    # ログコンテナ
    log_container = st.empty()

    # ジョブステータス確認ボタン
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🔄 ステータス更新"):
            try:
                response = requests.get(
                    f"http://localhost:8000/api/news/job/{job_id}",
                    timeout=10
                )

                if response.status_code == 200:
                    job_data = response.json()
                    status = job_data["status"]

                    if status == "finished":
                        st.success("✅ 完了")
                        result = job_data.get("result", {})
                        st.json(result)
                    elif status == "failed":
                        st.error("❌ 失敗")
                        st.error(job_data.get("error", "Unknown error"))
                    elif status == "started":
                        st.info("⏳ 実行中...")
                    else:
                        st.warning(f"ステータス: {status}")
                else:
                    st.error(f"❌ エラー: {response.status_code}")

            except Exception as e:
                st.error(f"❌ エラー: {str(e)}")

    with col2:
        if st.button("❌ ログを閉じる"):
            st.session_state["show_logs"] = False
            st.rerun()

    with col3:
        st.info(f"Job ID: {job_id}")

    # WebSocketログ表示（簡易版）
    st.markdown("### リアルタイムログ")
    st.info("💡 ヒント: WebSocketログを見るには、別ブラウザタブで `test_websocket.html` を開いてください。")

# メイン関数に追加
def main():
    # ... 既存のコード ...

    # ニュース自動取得セクションを追加
    show_news_automation(selected_symbol)

    # ... 残りのコード ...
```

---

#### 2. テスト実行

```bash
# ターミナル1: FastAPI
python backend/main.py

# ターミナル2: RQ Worker
rq worker --url redis://localhost:6379

# ターミナル3: Streamlit
streamlit run src/tools/parquet_dashboard.py
```

**ダッシュボード操作**:
1. ブラウザで http://localhost:8501 にアクセス
2. 銘柄選択（例: BTC）
3. 「🚀 ニュース取得開始」ボタンをクリック
4. Job IDが表示される
5. 「🔄 ステータス更新」で進行状況確認
6. 完了したら結果が表示される

**ユウタ**: 「ダッシュボードから起動できた！」

**ミコ**: 「Phase 2完成だ！」

---

## 📖 Scene 7: Phase 2 まとめ

### Phase 2で実現したこと

**ミコ**: 「Phase 2を振り返るぞ」

```markdown
【Phase 2の成果】

✅ FastAPI REST API作成
   - /api/news/fetch: ニュース取得開始
   - /api/news/job/{job_id}: ジョブステータス確認
   - /ws/logs/{job_id}: WebSocketログ配信

✅ Redis Queue統合
   - バックグラウンドでニュース取得実行
   - ジョブキュー管理

✅ WebSocket統合
   - リアルタイムログ配信

✅ Streamlit UI統合
   - ダッシュボードにボタン追加
   - ジョブステータス確認

【技術スタック】
- FastAPI: REST API + WebSocket
- Redis + RQ: ジョブキュー
- Streamlit: UI

【ファイル構成】
backend/
├── main.py
├── config.py
├── api/
│   ├── news.py
│   └── websocket.py
└── workers/
    └── news_worker.py
```

**ユウタ**: 「でも、まだNewsAPIは使ってないよね？」

**ミコ**: 「そう。今はシミュレーションだ」

**ミコ**: 「Phase 3で、Claude Code SDKと統合したら、NewsAPIの代わりにWebSearchを使う」

---

## 📖 Scene 8: Phase 3 実装計画

### Phase 3の目標

**ミコ**: 「Phase 3では、Node.jsサーバーを追加して、Claude Agent SDKを統合する」

```markdown
【Phase 3の目標】

1. Node.js Express サーバー作成
2. Claude Agent SDK統合
   - query() 関数でタスク実行
   - WebSearch ツール使用
3. カスタムツール実装
   - DB保存ツール
   - ニュース分析ツール
4. FastAPI → Node.js ブリッジ
5. Streamlit UI拡張
6. 統合テスト

【技術スタック】
- Node.js + Express
- @anthropic-ai/claude-agent-sdk
- Zod（スキーマ検証）
- SQLite3（Node.js用）
```

---

### Phase 3のファイル構成

```
grass-coin-trader/
├── backend/                     【既存・Phase 2】
│   ├── main.py
│   ├── api/
│   │   ├── news.py
│   │   ├── websocket.py
│   │   └── claude_code.py       【新規追加】
│   └── ...
│
├── claude-agent-service/        【新規作成・Phase 3】
│   ├── package.json
│   ├── package-lock.json
│   ├── .env
│   ├── src/
│   │   ├── server.js            # Express サーバー
│   │   ├── claude_agent.js      # Claude Agent SDK統合
│   │   ├── tools/
│   │   │   ├── db_saver.js      # DB保存ツール
│   │   │   └── news_analyzer.js # ニュース分析ツール
│   │   └── config.js            # 設定
│   └── README.md
│
└── ...
```

---

### Phase 3の実装手順（概要）

```markdown
【Phase 3実装ステップ】

## ステップ1: Node.js プロジェクト作成（1日目）
- package.json作成
- Claude Agent SDK インストール
- Express サーバー基礎

## ステップ2: Claude Agent SDK統合（1-2日目）
- query() 関数実装
- WebSearch テスト
- ストリーミング対応

## ステップ3: カスタムツール実装（2日目）
- DB保存ツール（Zod + SQLite3）
- ニュース分析ツール

## ステップ4: FastAPI ブリッジ（3日目）
- /api/claude-code/execute エンドポイント
- Node.js へHTTP POST
- WebSocket ログ統合

## ステップ5: Streamlit UI拡張（3日目）
- 「Claude Code実行」ボタン追加
- ログ表示

## ステップ6: テスト（4-5日目）
- エンドツーエンドテスト
- エラーハンドリング
```

---

## 📖 Scene 9: Phase 3 ステップ1 - Node.jsプロジェクト作成

### Node.jsプロジェクトのセットアップ

**ミコ**: 「Node.jsプロジェクトを作る」

#### 1. プロジェクトディレクトリ作成

```bash
cd C:\Users\tatut\Documents\playground\grass-coin-trader

mkdir claude-agent-service
cd claude-agent-service

# package.json 作成
npm init -y
```

---

#### 2. 必要なパッケージをインストール

```bash
npm install @anthropic-ai/claude-agent-sdk express cors dotenv sqlite3 zod
```

**出力例**:
```
added 245 packages, and audited 246 packages in 15s
```

---

#### 3. `.env` ファイル作成

`claude-agent-service/.env`:
```bash
# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Server settings
PORT=3000
HOST=0.0.0.0

# Database
DB_PATH=../data/crypto_data.db

# Python backend
PYTHON_BACKEND_URL=http://localhost:8000
```

---

#### 4. `src/config.js` - 設定ファイル

```javascript
/**
 * Configuration for Claude Agent Service
 */
require('dotenv').config();

module.exports = {
  // Anthropic API
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',

  // Server
  PORT: parseInt(process.env.PORT) || 3000,
  HOST: process.env.HOST || '0.0.0.0',

  // Database
  DB_PATH: process.env.DB_PATH || '../data/crypto_data.db',

  // Python backend
  PYTHON_BACKEND_URL: process.env.PYTHON_BACKEND_URL || 'http://localhost:8000'
};
```

---

#### 5. `src/server.js` - Express サーバー基礎

```javascript
/**
 * Express server for Claude Agent Service
 */
const express = require('express');
const cors = require('cors');
const config = require('./config');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'claude-agent-service',
    version: '1.0.0'
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Claude Agent Service',
    version: '1.0.0',
    endpoints: [
      'GET /health',
      'POST /agent/execute'
    ]
  });
});

// Start server
app.listen(config.PORT, config.HOST, () => {
  console.log(`🚀 Claude Agent Service running on http://${config.HOST}:${config.PORT}`);
});
```

---

#### 6. `package.json` にスクリプト追加

```json
{
  "name": "claude-agent-service",
  "version": "1.0.0",
  "description": "Claude Code SDK integration service",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js"
  },
  "keywords": ["claude", "agent", "sdk"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^x.x.x",
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "sqlite3": "^5.1.6",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

---

#### 7. テスト実行

```bash
npm start
```

**期待される出力**:
```
🚀 Claude Agent Service running on http://0.0.0.0:3000
```

**別ターミナルでテスト**:
```bash
curl http://localhost:3000/health
```

**期待される出力**:
```json
{
  "status": "healthy",
  "service": "claude-agent-service",
  "version": "1.0.0"
}
```

**ユウタ**: 「Node.jsサーバーが動いた！」

**ミコ**: 「よし。次はClaude Agent SDKを統合する」

---

## 📖 Scene 10: Phase 3 ステップ2 - Claude Agent SDK統合

### Claude Agent SDKの基本実装

**ミコ**: 「いよいよClaude Agent SDKを使う」

#### 1. `src/claude_agent.js` - Claude Agent SDK統合

```javascript
/**
 * Claude Agent SDK integration
 */
const { query } = require('@anthropic-ai/claude-agent-sdk');
const config = require('./config');

class ClaudeAgentService {
  constructor() {
    this.apiKey = config.ANTHROPIC_API_KEY;
  }

  /**
   * Execute a task using Claude Code SDK
   *
   * @param {string} symbol - Cryptocurrency symbol
   * @param {string} task - Task description
   * @param {Function} logCallback - Callback for logging
   * @returns {Promise<Object>} - Result
   */
  async executeTask(symbol, task, logCallback = console.log) {
    const log = (message) => {
      console.log(`[CLAUDE_AGENT] ${message}`);
      if (logCallback) logCallback(message);
    };

    try {
      log(`🚀 Starting Claude Code execution for ${symbol}...`);
      log(`📋 Task: ${task}`);

      // プロンプト作成
      const prompt = this.createPrompt(symbol, task);
      log(`📝 Prompt created`);

      // Claude Code実行（ストリーミング）
      log(`🤖 Executing Claude Code SDK...`);

      const results = [];

      for await (const message of query({
        prompt,
        options: {
          model: 'claude-sonnet-4-5-20250929',
          maxTurns: 20,
          includePartialMessages: true,
          // TODO: mcpServers追加（Step 3で実装）
        }
      })) {
        // メッセージタイプに応じた処理
        if (message.type === 'stream_event') {
          const event = message.event;

          if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
            // テキストストリーム
            const text = event.delta.text;
            log(`💬 ${text}`);
          }
        } else if (message.type === 'assistant') {
          // アシスタントメッセージ
          log(`✅ Assistant response received`);
          results.push(message);
        } else if (message.type === 'result') {
          // 最終結果
          log(`🎉 Execution completed!`);
          log(`   Turns: ${message.num_turns}`);
          log(`   Duration: ${message.duration_ms}ms`);

          return {
            success: true,
            symbol,
            task,
            num_turns: message.num_turns,
            duration_ms: message.duration_ms,
            results
          };
        }
      }

    } catch (error) {
      log(`❌ Error: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Create prompt for Claude Code
   *
   * @param {string} symbol - Cryptocurrency symbol
   * @param {string} task - Task description
   * @returns {string} - Prompt
   */
  createPrompt(symbol, task) {
    return `
You are a cryptocurrency news analyst.

Symbol: ${symbol}
Task: ${task}

Instructions:
1. Search for recent news about ${symbol} using WebSearch
2. Analyze the sentiment of each news article
3. Calculate an overall sentiment score (0-1)
4. Save the results to the database

Please execute this task step by step.
`.trim();
  }
}

module.exports = ClaudeAgentService;
```

---

#### 2. `src/server.js` にエンドポイント追加

```javascript
// ... 既存のコード ...

const ClaudeAgentService = require('./claude_agent');
const claudeAgent = new ClaudeAgentService();

// Agent execution endpoint
app.post('/agent/execute', async (req, res) => {
  const { symbol, task } = req.body;

  if (!symbol || !task) {
    return res.status(400).json({
      error: 'Missing required fields: symbol, task'
    });
  }

  try {
    // Execute in background (simplified - no job queue yet)
    const result = await claudeAgent.executeTask(symbol, task);

    res.json({
      success: true,
      result
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ... 残りのコード ...
```

---

#### 3. テスト実行

```bash
# Node.js サーバー起動
npm start
```

**別ターミナルでテスト**:
```bash
curl -X POST http://localhost:3000/agent/execute \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "task": "Search for latest news and analyze sentiment"}'
```

**期待される出力**:
```
[CLAUDE_AGENT] 🚀 Starting Claude Code execution for BTC...
[CLAUDE_AGENT] 📋 Task: Search for latest news and analyze sentiment
[CLAUDE_AGENT] 📝 Prompt created
[CLAUDE_AGENT] 🤖 Executing Claude Code SDK...
[CLAUDE_AGENT] 💬 I'll search for recent Bitcoin news...
[CLAUDE_AGENT] 💬 Using WebSearch tool...
[CLAUDE_AGENT] ✅ Assistant response received
[CLAUDE_AGENT] 🎉 Execution completed!
[CLAUDE_AGENT]    Turns: 5
[CLAUDE_AGENT]    Duration: 12345ms
```

**ユウタ**: 「Claude Code SDK が動いてる！」

**ミコ**: 「よし。次はカスタムツールを追加する」

---

## 📖 Scene 11: Phase 3 ステップ3 - カスタムツール実装

### DB保存ツールの実装

**ミコ**: 「Claude Codeに『DB保存』機能を教える」

#### 1. `src/tools/db_saver.js` - DB保存ツール

```javascript
/**
 * Database saver tool for Claude Code
 */
const sqlite3 = require('sqlite3').verbose();
const { z } = require('zod');
const config = require('../config');

// Zodスキーマ定義
const SaveNewsSchema = z.object({
  symbol: z.string().describe('Cryptocurrency symbol (e.g., BTC)'),
  title: z.string().describe('News article title'),
  url: z.string().url().optional().describe('Article URL'),
  source: z.string().optional().describe('News source'),
  sentiment_score: z.number().min(0).max(1).describe('Sentiment score (0-1)'),
  published_at: z.string().optional().describe('Publication date (ISO 8601)')
});

class DbSaverTool {
  constructor() {
    this.db = new sqlite3.Database(config.DB_PATH);
  }

  /**
   * Get tool definition for Claude Code SDK
   */
  getToolDefinition() {
    return {
      name: 'save_news_to_db',
      description: 'Save news article to database with sentiment analysis',
      inputSchema: SaveNewsSchema
    };
  }

  /**
   * Execute tool
   *
   * @param {Object} args - Tool arguments
   * @param {Function} logCallback - Logging callback
   * @returns {Promise<Object>} - Result
   */
  async execute(args, logCallback = console.log) {
    const log = (message) => {
      console.log(`[DB_SAVER] ${message}`);
      if (logCallback) logCallback(message);
    };

    try {
      // Zodバリデーション
      const validated = SaveNewsSchema.parse(args);

      log(`💾 Saving news to database...`);
      log(`   Symbol: ${validated.symbol}`);
      log(`   Title: ${validated.title}`);
      log(`   Sentiment: ${validated.sentiment_score}`);

      // DB保存
      await this.saveToDatabase(validated);

      log(`✅ Saved successfully`);

      return {
        success: true,
        message: 'News saved to database',
        data: validated
      };

    } catch (error) {
      log(`❌ Error: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Save to database
   *
   * @param {Object} data - Validated data
   * @returns {Promise<void>}
   */
  saveToDatabase(data) {
    return new Promise((resolve, reject) => {
      const query = `
        INSERT INTO news (symbol, title, url, source, sentiment_score, published_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
      `;

      this.db.run(
        query,
        [
          data.symbol,
          data.title,
          data.url || null,
          data.source || null,
          data.sentiment_score,
          data.published_at || new Date().toISOString()
        ],
        function(err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id: this.lastID });
          }
        }
      );
    });
  }

  /**
   * Close database connection
   */
  close() {
    this.db.close();
  }
}

module.exports = DbSaverTool;
```

---

#### 2. `src/claude_agent.js` にツール統合

```javascript
// ... 既存のコード ...

const { query, createSdkMcpServer } = require('@anthropic-ai/claude-agent-sdk');
const DbSaverTool = require('./tools/db_saver');

class ClaudeAgentService {
  constructor() {
    this.apiKey = config.ANTHROPIC_API_KEY;
    this.dbSaver = new DbSaverTool();
  }

  async executeTask(symbol, task, logCallback = console.log) {
    // ... 既存のログ処理 ...

    try {
      // カスタムツールを作成
      const mcpServer = createSdkMcpServer({
        name: 'crypto-tools',
        version: '1.0.0',
        tools: [
          {
            name: 'save_news_to_db',
            description: this.dbSaver.getToolDefinition().description,
            inputSchema: this.dbSaver.getToolDefinition().inputSchema.shape,
            handler: async (args) => {
              return await this.dbSaver.execute(args, logCallback);
            }
          }
        ]
      });

      log(`🔧 Custom tools registered`);

      // Claude Code実行（ツール付き）
      for await (const message of query({
        prompt,
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
        // ... 既存のメッセージ処理 ...
      }

    } catch (error) {
      // ... エラー処理 ...
    } finally {
      this.dbSaver.close();
    }
  }

  // ... 残りのコード ...
}
```

---

#### 3. テスト実行

```bash
curl -X POST http://localhost:3000/agent/execute \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "task": "Search for latest Bitcoin news, analyze sentiment, and save to database using save_news_to_db tool"}'
```

**期待される出力**:
```
[CLAUDE_AGENT] 🚀 Starting Claude Code execution for BTC...
[CLAUDE_AGENT] 🔧 Custom tools registered
[CLAUDE_AGENT] 🤖 Executing Claude Code SDK...
[CLAUDE_AGENT] 💬 I'll search for Bitcoin news...
[CLAUDE_AGENT] 💬 Found 3 articles. Analyzing sentiment...
[DB_SAVER] 💾 Saving news to database...
[DB_SAVER]    Symbol: BTC
[DB_SAVER]    Title: Bitcoin reaches new all-time high
[DB_SAVER]    Sentiment: 0.85
[DB_SAVER] ✅ Saved successfully
[CLAUDE_AGENT] 🎉 Execution completed!
```

**ユウタ**: 「Claude CodeがDBに保存してる！」

**ミコ**: 「完璧だ。次はFastAPIと統合する」

---

## 📖 Scene 12: Phase 3 ステップ4 - FastAPI ブリッジ

### PythonからNode.jsを呼び出す

**ミコ**: 「FastAPIに新しいエンドポイントを追加して、Node.jsに橋渡しする」

#### 1. `backend/api/claude_code.py` - Claude Codeエンドポイント

```python
"""
Claude Code API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import requests
from backend.config import settings

router = APIRouter()

# Redis接続
redis_conn = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

queue = Queue(connection=redis_conn)

class ClaudeCodeRequest(BaseModel):
    """Request model for Claude Code execution"""
    symbol: str
    task: str = "Search for latest news and analyze sentiment"

class ClaudeCodeResponse(BaseModel):
    """Response model for Claude Code execution"""
    job_id: str
    symbol: str
    task: str
    message: str

def execute_claude_code_job(symbol: str, task: str, job_id: str = None):
    """
    Background job to execute Claude Code

    Args:
        symbol: Cryptocurrency symbol
        task: Task description
        job_id: Optional job ID for logging

    Returns:
        Result dictionary
    """
    import time

    def log(message: str):
        """Log helper"""
        print(f"[CLAUDE_CODE_JOB] {message}")

        # WebSocketログ送信
        if job_id:
            # TODO: WebSocketログ統合
            pass

    try:
        log(f"🚀 Executing Claude Code for {symbol}...")
        log(f"📋 Task: {task}")

        # Node.jsサービスに POST リクエスト
        log("📡 Calling Node.js Claude Agent Service...")

        response = requests.post(
            "http://localhost:3000/agent/execute",
            json={"symbol": symbol, "task": task},
            timeout=300  # 5分
        )

        if response.status_code == 200:
            result = response.json()
            log("✅ Claude Code execution completed")
            return result
        else:
            log(f"❌ Error: {response.status_code}")
            return {
                "success": False,
                "error": f"Node.js service error: {response.status_code}"
            }

    except requests.exceptions.ConnectionError:
        log("❌ Cannot connect to Node.js service")
        return {
            "success": False,
            "error": "Cannot connect to Node.js Claude Agent Service (Port 3000)"
        }
    except Exception as e:
        log(f"❌ Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/execute", response_model=ClaudeCodeResponse)
async def execute_claude_code(request: ClaudeCodeRequest):
    """
    Start Claude Code execution

    Args:
        request: ClaudeCodeRequest

    Returns:
        ClaudeCodeResponse with job_id
    """
    try:
        # ジョブをキューに追加
        job = queue.enqueue(
            execute_claude_code_job,
            args=(request.symbol, request.task),
            kwargs={"job_id": None},
            job_timeout='10m',
            result_ttl=3600
        )

        # job_idを更新して再エンキュー
        job = queue.enqueue(
            execute_claude_code_job,
            args=(request.symbol, request.task),
            kwargs={"job_id": job.id},
            job_timeout='10m',
            result_ttl=3600
        )

        return ClaudeCodeResponse(
            job_id=job.id,
            symbol=request.symbol,
            task=request.task,
            message=f"Claude Code execution started for {request.symbol}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

#### 2. `backend/main.py` にルーター追加

```python
# ... 既存のコード ...

# Claude Codeルーターを追加
from backend.api.claude_code import router as claude_code_router
app.include_router(claude_code_router, prefix="/api/claude-code", tags=["claude-code"])

# ... 残りのコード ...
```

---

#### 3. テスト実行

**ターミナル1: Node.js**
```bash
cd claude-agent-service
npm start
```

**ターミナル2: FastAPI**
```bash
cd ..
python backend/main.py
```

**ターミナル3: RQ Worker**
```bash
rq worker --url redis://localhost:6379
```

**ターミナル4: curlテスト**
```bash
curl -X POST http://localhost:8000/api/claude-code/execute \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "task": "Search for latest news and save to database"}'
```

**期待される出力（ターミナル3・RQワーカー）**:
```
[CLAUDE_CODE_JOB] 🚀 Executing Claude Code for BTC...
[CLAUDE_CODE_JOB] 📋 Task: Search for latest news and save to database
[CLAUDE_CODE_JOB] 📡 Calling Node.js Claude Agent Service...
[CLAUDE_CODE_JOB] ✅ Claude Code execution completed
```

**期待される出力（ターミナル1・Node.js）**:
```
[CLAUDE_AGENT] 🚀 Starting Claude Code execution for BTC...
[CLAUDE_AGENT] 🔧 Custom tools registered
[CLAUDE_AGENT] 🤖 Executing Claude Code SDK...
[DB_SAVER] 💾 Saving news to database...
[DB_SAVER] ✅ Saved successfully
[CLAUDE_AGENT] 🎉 Execution completed!
```

**ユウタ**: 「3つのサービスが連携してる！」

**ミコ**: 「これがマイクロサービスアーキテクチャだ」

---

## 📖 Scene 13: Phase 3 ステップ5 - Streamlit UI拡張

### ダッシュボードにClaude Codeボタン追加

**ミコ**: 「最後に、ダッシュボードからClaude Code SDKを実行できるようにする」

#### `src/tools/parquet_dashboard.py` に追加

```python
# ... 既存のコード ...

def show_claude_code_automation(symbol: str):
    """
    Claude Code SDK自動実行セクション

    Args:
        symbol: 暗号通貨シンボル
    """
    st.markdown("---")
    st.subheader("🤖 Claude Code SDK - 高度な分析")

    st.info("""
    💡 **Claude Code SDKとは？**

    WebSearch機能を使って、リアルタイムで最新ニュースを検索し、
    センチメント分析を行い、自動でDBに保存します。

    **Phase 2との違い**:
    - Phase 2: NewsAPI（外部API）を使用
    - Phase 3: Claude CodeのWebSearch（より柔軟）
    """)

    col1, col2 = st.columns([1, 3])

    with col1:
        task_type = st.selectbox(
            "タスク選択",
            [
                "ニュース検索＋センチメント分析",
                "カスタムタスク"
            ]
        )

        if task_type == "カスタムタスク":
            custom_task = st.text_area(
                "タスク内容",
                "Search for latest news, analyze sentiment, and save to database"
            )
        else:
            custom_task = "Search for latest news about cryptocurrency, analyze sentiment, and save to database using save_news_to_db tool"

        if st.button("🚀 Claude Code実行", key=f"execute_claude_{symbol}"):
            try:
                response = requests.post(
                    "http://localhost:8000/api/claude-code/execute",
                    json={"symbol": symbol, "task": custom_task},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    job_id = data["job_id"]

                    st.success(f"✅ Claude Code実行を開始しました！")
                    st.info(f"Job ID: {job_id}")

                    st.session_state["current_claude_job_id"] = job_id
                    st.session_state["show_claude_logs"] = True

                else:
                    st.error(f"❌ エラー: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ FastAPIサーバーに接続できません。")
            except Exception as e:
                st.error(f"❌ エラー: {str(e)}")

    with col2:
        st.markdown("""
        **実行内容**:
        1. 🔍 WebSearchで最新ニュース検索
        2. 🤖 Claude AIでセンチメント分析
        3. 💾 結果をDBに自動保存
        4. 📊 ダッシュボードで表示

        **所要時間**: 約30秒〜2分
        """)

    # ログ表示
    if st.session_state.get("show_claude_logs", False):
        show_claude_job_logs()

def show_claude_job_logs():
    """Claude Codeジョブログ表示"""
    job_id = st.session_state.get("current_claude_job_id")

    if not job_id:
        return

    st.markdown("---")
    st.subheader("📊 Claude Code 実行ログ")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🔄 ステータス更新", key="update_claude_status"):
            try:
                response = requests.get(
                    f"http://localhost:8000/api/news/job/{job_id}",
                    timeout=10
                )

                if response.status_code == 200:
                    job_data = response.json()
                    status = job_data["status"]

                    if status == "finished":
                        st.success("✅ 完了")
                        result = job_data.get("result", {})

                        if result.get("success"):
                            st.json(result.get("result", {}))
                            st.balloons()
                        else:
                            st.error(f"❌ エラー: {result.get('error')}")
                    elif status == "failed":
                        st.error("❌ 失敗")
                        st.error(job_data.get("error"))
                    elif status == "started":
                        st.info("⏳ 実行中...")
                    else:
                        st.warning(f"ステータス: {status}")
                else:
                    st.error(f"❌ エラー: {response.status_code}")

            except Exception as e:
                st.error(f"❌ エラー: {str(e)}")

    with col2:
        if st.button("❌ ログを閉じる", key="close_claude_logs"):
            st.session_state["show_claude_logs"] = False
            st.rerun()

    with col3:
        st.info(f"Job ID: {job_id}")

# main()に追加
def main():
    # ... 既存のコード ...

    # Phase 2: ニュース自動取得
    show_news_automation(selected_symbol)

    # Phase 3: Claude Code SDK
    show_claude_code_automation(selected_symbol)

    # ... 残りのコード ...
```

---

#### テスト実行

```bash
# ターミナル1: Node.js
cd claude-agent-service && npm start

# ターミナル2: FastAPI
python backend/main.py

# ターミナル3: RQ Worker
rq worker --url redis://localhost:6379

# ターミナル4: Streamlit
streamlit run src/tools/parquet_dashboard.py
```

**ダッシュボード操作**:
1. http://localhost:8501 にアクセス
2. 銘柄選択（BTC）
3. 「🤖 Claude Code SDK」セクションまでスクロール
4. 「🚀 Claude Code実行」ボタンをクリック
5. 「🔄 ステータス更新」で進行状況確認
6. 完了したら結果表示＋🎈

**ユウタ**: 「ダッシュボードから全部できる！」

**ミコ**: 「Phase 3完成だ！」

---

## 📖 Scene 14: エピローグ - 完成とこれから

### Phase 2 & 3の成果

**ミコ**: 「振り返るぞ」

```markdown
【Phase 2 & 3で実現したこと】

## Phase 2（FastAPI + Redis + WebSocket）
✅ REST API作成
✅ バックグラウンドジョブ実行
✅ WebSocketログ配信
✅ Streamlit UI統合

## Phase 3（Node.js + Claude Agent SDK）
✅ Node.js Express サーバー
✅ Claude Agent SDK統合
✅ WebSearch機能
✅ カスタムツール（DB保存）
✅ 3-tierアーキテクチャ
✅ エンドツーエンド統合

【最終アーキテクチャ】
Streamlit (Port 8501)
    ↓ HTTP
FastAPI (Port 8000)
    ↓ HTTP
Node.js (Port 3000)
    ↓ SDK
Claude Code
    ↓ Tools
Database (SQLite)
```

---

### 実装完了チェックリスト

```markdown
【Phase 2チェックリスト】
- [x] FastAPI プロジェクト作成
- [x] Redis + RQ セットアップ
- [x] WebSocket統合
- [x] Streamlit UI統合
- [x] エンドツーエンドテスト

【Phase 3チェックリスト】
- [x] Node.js プロジェクト作成
- [x] Claude Agent SDK インストール
- [x] query()関数実装
- [x] カスタムツール実装（DB保存）
- [x] FastAPI ブリッジ
- [x] Streamlit UI拡張
- [x] 統合テスト

【今後の拡張】
- [ ] ニュース分析ツール追加
- [ ] 予測モデル統合ツール
- [ ] マルチシンボル対応
- [ ] エラーハンドリング強化
- [ ] ログUI改善（リアルタイム表示）
```

---

### ユウタの感想

**ユウタ**: 「めっちゃ長かったけど、最後まで作れた！」

**ミコ**: 「3つのサービスが連携して動いてるからな」

**ユウタ**: 「でも、これで自動的にニュース取得できるようになった」

**ミコ**: 「次は、数学手法（GRU、LSTM-GARCH）を実装するぞ」

**ユウタ**: 「おお、AI予測だ！」

**ミコ**: 「その前に、このドキュメントを読んで理解しろ」

**ユウタ**: 「了解！」

---

## 📚 参考資料

### 公式ドキュメント

1. **FastAPI**: https://fastapi.tiangolo.com/
2. **Redis Queue (RQ)**: https://python-rq.org/
3. **Claude Agent SDK**: （内部仕様書参照）
4. **Express.js**: https://expressjs.com/
5. **Zod**: https://zod.dev/

### プロジェクト内ドキュメント

1. `docs/userimported/CLAUDE_CODE_INTEGRATION_SPEC.md` - Claude Agent SDK仕様書
2. `docs/ai_automation_architecture_story_v2.md` - アーキテクチャ設計ストーリー

---

## 🎯 次のステップ

このドキュメントを読んだら、以下を実行してください：

```bash
# Phase 2実装開始
cd C:\Users\tatut\Documents\playground\grass-coin-trader

# 1. 依存関係インストール（NewsAPI/Anthropic APIは不要）
pip install fastapi uvicorn redis rq websockets python-dotenv requests

# 2. Redisセットアップ（WSL2）
wsl
sudo service redis-server start
exit

# 3. .env作成（Phase 2はNewsAPI不要）
# プロジェクトルートに.envファイルを作成
# 内容:
#   REDIS_HOST=localhost
#   REDIS_PORT=6379
#   FASTAPI_HOST=0.0.0.0
#   FASTAPI_PORT=8000

# 4. backend/構造を作成
mkdir backend
mkdir backend/api
mkdir backend/workers

# 5. ファイル作成（このドキュメントのコードをコピー）
# - backend/config.py
# - backend/main.py
# - backend/api/news.py
# - backend/api/websocket.py
# - backend/workers/news_worker.py

# 6. テスト実行
python backend/main.py  # ターミナル1
rq worker --url redis://localhost:6379  # ターミナル2
```

**重要**:
- Phase 2では、NewsAPIやClaude APIは使いません
- ダミーデータでインフラの動作確認のみ行います
- Phase 3でClaude Code SDKを統合し、実際のニュース取得を実装します

---

**最終更新**: 2025-10-27
**対象バージョン**: Phase 2 & 3 実装計画書

---

# 🎉 準備完了！

このドキュメントを読み終えたら、Phase 2の実装を開始してください。

ステップバイステップで進めれば、必ず完成します！

**Good luck! 🚀**
