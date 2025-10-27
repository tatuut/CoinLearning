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

**ミコ**: 「まずはバックグラウンド実行の技術を調べた」

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

**ミコ**: 「これだ！シンプルで十分」

**ユウタ**: 「Redis Queue...？」

**ミコ**: 「まず基本から説明する」

---

### ステップ1: FastAPIとは何か

**ミコ**: 「今のtest_claude_sdk.pyは、ローカルでしか動かない」

**ユウタ**: 「うん」

**ミコ**: 「Streamlitダッシュボードから呼びたいよな？」

**ユウタ**: 「そりゃそうだ」

**ミコ**: 「だから**REST API**が必要なんだ」

```
【REST APIとは】

HTTP経由で他のプログラムから呼び出せる関数みたいなもの。

例:
  curl http://localhost:8000/api/jobs/start
  → 関数が実行される
  → 結果がJSONで返ってくる
```

**ユウタ**: 「なるほど、HTTP経由で呼べるようにするのか」

**ミコ**: 「そう。FastAPIはPythonでREST APIを作るフレームワークだ」

---

### ステップ2: 最小限のFastAPI起動

**ミコ**: 「まず最小限のAPIを作ってみる」

**依存関係インストール**:
```bash
pip install fastapi uvicorn
```

**最小限のAPI（`backend/main.py`）**:
```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
```

**ミコ**: 「これだけ」

**ユウタ**: 「シンプルだな」

**起動**:
```bash
mkdir backend
python backend/main.py
```

**出力**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**別のターミナルでテスト**:
```bash
curl http://localhost:8000/
```

**結果**:
```json
{"message": "Hello World"}
```

**ユウタ**: 「おお、動いた！」

**ミコ**: 「これがFastAPIの基本だ」

---

### ステップ3: Redisとは何か

**ミコ**: 「次はRedis」

**ユウタ**: 「Redis...？」

**ミコ**: 「**超高速なメモリ上のデータベース**だ」

```
【Redisの役割】

通常のDB（SQLite、PostgreSQL等）:
  → ディスクに保存、永続化、遅い

Redis:
  → メモリに保存、超高速、揮発性（再起動で消える）
  → でも設定で永続化も可能

用途:
  - キャッシュ
  - セッション管理
  - **ジョブキュー** ← 今回はこれ
```

**ユウタ**: 「ジョブキュー...？」

**ミコ**: 「こういうことだ」

```
【ジョブキューの動き】

1. FastAPIがジョブをRedisに登録（Enqueue）
   Redis: ["ジョブ1", "ジョブ2", "ジョブ3"]

2. 別プロセス（Worker）がジョブを取り出す（Dequeue）
   Worker: 「ジョブ1を実行しま〜す」

3. 実行完了
   Worker: 「ジョブ1完了！次はジョブ2」
```

**ユウタ**: 「なるほど！Redisが仲介役になるのか」

**ミコ**: 「その通り」

---

### ステップ4: Redisセットアップ

**Redisインストール（WSL）**:
```bash
wsl
sudo apt update
sudo apt install redis-server
```

**Redis起動**:
```bash
sudo service redis-server start
```

**動作確認**:
```bash
redis-cli ping
```

**結果**:
```
PONG
```

**ユウタ**: 「PONG...？」

**ミコ**: 「Redisが動いてる証拠だ」

---

### ステップ5: RQとは何か

**ミコ**: 「次はRQ（Redis Queue）」

**ユウタ**: 「Redisを使ったキューライブラリってこと？」

**ミコ**: 「そう。Redisだけだとキュー機能が素朴すぎる。RQはジョブ管理を簡単にする」

```
【RQの機能】

1. ジョブの登録（Enqueue）
   queue.enqueue(dummy_job, args=("BTC",))

2. ジョブステータス管理
   - queued（待機中）
   - started（実行中）
   - finished（完了）
   - failed（失敗）

3. ジョブの結果保存
   job.result → {"success": True, "symbol": "BTC"}

4. タイムアウト設定
   job_timeout='10m' → 10分で自動終了
```

**ユウタ**: 「便利じゃん！」

**ミコ**: 「だからRQを使う」

---

### ステップ6: 最小限のジョブを作る

**ミコ**: 「まず最小限のジョブを作ってみる」

**RQインストール**:
```bash
pip install redis rq
```

**最小限のワーカー（`backend/workers/simple_worker.py`）**:
```python
import time

def simple_job(name):
    """超シンプルなジョブ"""
    print(f"Hello, {name}!")
    time.sleep(2)  # 2秒待つ
    print(f"Goodbye, {name}!")
    return {"message": f"Job for {name} completed"}
```

**ミコ**: 「これだけ。2秒待って終わる」

**ユウタ**: 「シンプルだな」

---

### ステップ7: ジョブをテスト実行

**テストスクリプト（`test_rq.py`）**:
```python
from redis import Redis
from rq import Queue
from backend.workers.simple_worker import simple_job

# Redisに接続
redis_conn = Redis(host='localhost', port=6379)

# キュー作成
queue = Queue(connection=redis_conn)

# ジョブを登録
job = queue.enqueue(simple_job, args=("ユウタ",))

print(f"ジョブ登録完了！ Job ID: {job.id}")
print(f"ステータス: {job.get_status()}")
```

**ターミナル1: ワーカー起動**:
```bash
mkdir backend/workers
rq worker --url redis://localhost:6379
```

**出力**:
```
INFO:     Worker started, version 1.15.1
INFO:     Subscribing to default...
```

**ターミナル2: ジョブ登録**:
```bash
python test_rq.py
```

**出力**:
```
ジョブ登録完了！ Job ID: 1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p
ステータス: queued
```

**ターミナル1（ワーカー側）の出力**:
```
Hello, ユウタ!
（2秒待機）
Goodbye, ユウタ!
default: backend.workers.simple_worker.simple_job('ユウタ') (1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p)
```

**ユウタ**: 「おお！別プロセスで実行された！」

**ミコ**: 「そう。これがバックグラウンド実行だ」

---

### ステップ8: 仕組みの理解

**ミコ**: 「今の流れを整理するぞ」

```
【バックグラウンド実行の流れ】

1. test_rq.py が queue.enqueue() を実行
   → Redisにジョブ情報を登録
   → 即座に完了（ブロックしない）

2. 別プロセス（rq worker）が常に監視
   → Redisに新しいジョブがあるか確認
   → あったら取り出して実行

3. 実行完了
   → 結果をRedisに保存
   → 次のジョブを待つ
```

**ユウタ**: 「なるほど！だからメインプログラムはフリーズしないんだ」

**ミコ**: 「その通り」

---

### ステップ9: FastAPIと統合

**ミコ**: 「次はFastAPIから呼べるようにする」

**ユウタ**: 「さっきのtest_rq.pyの中身をAPIにするってこと？」

**ミコ**: 「正解」

**FastAPIにジョブAPIを追加（`backend/api/jobs.py`）**:
```python
from fastapi import APIRouter
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from backend.workers.simple_worker import simple_job

router = APIRouter()

# Redisに接続
redis_conn = Redis(host='localhost', port=6379)
queue = Queue(connection=redis_conn)

class JobRequest(BaseModel):
    name: str

@router.post("/start")
async def start_job(request: JobRequest):
    """ジョブ開始"""
    job = queue.enqueue(simple_job, args=(request.name,))

    return {
        "job_id": job.id,
        "name": request.name,
        "status": job.get_status(),
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

**ミコ**: 「2つのエンドポイントを作った」

```
1. POST /api/jobs/start
   → ジョブを登録して job_id を返す

2. GET /api/jobs/status/{job_id}
   → ジョブのステータスと結果を返す
```

**ユウタ**: 「なるほど！」

---

### ステップ10: FastAPIルーター登録

**`backend/main.py`を更新**:
```python
from fastapi import FastAPI
from backend.api.jobs import router as jobs_router
import uvicorn

app = FastAPI(title="Grass Coin Trader API")

# ジョブAPIを登録
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])

@app.get("/")
async def root():
    return {"message": "Grass Coin Trader API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
```

**ミコ**: 「`include_router()`でジョブAPIを追加した」

**ユウタ**: 「prefix="/api/jobs"ってことは、/api/jobs/startでアクセスできるのか」

**ミコ**: 「そう」

---

### ステップ11: テスト実行

**ターミナル1: FastAPI起動**:
```bash
python backend/main.py
```

**ターミナル2: RQワーカー起動**:
```bash
mkdir backend/api
rq worker --url redis://localhost:6379
```

**ターミナル3: ジョブ開始**:
```bash
curl -X POST http://localhost:8000/api/jobs/start \
  -H "Content-Type: application/json" \
  -d '{"name": "ユウタ"}'
```

**結果**:
```json
{
  "job_id": "abc-123-def",
  "name": "ユウタ",
  "status": "queued",
  "message": "Job started"
}
```

**ターミナル2（ワーカー）の出力**:
```
Hello, ユウタ!
（2秒待機）
Goodbye, ユウタ!
```

**ターミナル3: ステータス確認**:
```bash
curl http://localhost:8000/api/jobs/status/abc-123-def
```

**結果**:
```json
{
  "job_id": "abc-123-def",
  "status": "finished",
  "result": {"message": "Job for ユウタ completed"}
}
```

**ユウタ**: 「おお！API経由でバックグラウンドジョブが実行できた！」

**ミコ**: 「これが基本だ」

---

### ステップ12: ダミージョブに置き換え

**ミコ**: 「次は、Claude Code実行をシミュレートするダミージョブに置き換える」

**ユウタ**: 「Claude Codeっぽい動きをする偽物ってこと？」

**ミコ**: 「そう。Phase 3でClaude Codeに置き換える前に、まず動作確認」

**ダミーワーカー（`backend/workers/dummy_worker.py`）**:
```python
"""Phase 2: ダミーワーカー（Claude Code実行をシミュレート）"""
import time

def dummy_job(symbol: str):
    """Claude Code実行をシミュレート（3ステップ、計5秒）"""

    print(f"🚀 Job started for {symbol}")

    # Step 1: WebSearch シミュレート
    print("⏳ Step 1/3: Simulating WebSearch...")
    time.sleep(2)
    print("✅ Step 1 done: Found 5 articles")

    # Step 2: Analysis シミュレート
    print("⏳ Step 2/3: Simulating analysis...")
    time.sleep(2)
    print("✅ Step 2 done: Average sentiment +0.45")

    # Step 3: DB Save シミュレート
    print("⏳ Step 3/3: Simulating DB save...")
    time.sleep(1)
    print("✅ Step 3 done: Saved to database")

    print("🎉 Completed!")

    return {
        "success": True,
        "symbol": symbol,
        "news_count": 5,
        "avg_sentiment": 0.45
    }
```

**ミコ**: 「Claude Codeの動きをシミュレートした」

```
【シミュレートしている動作】

Step 1: WebSearchツールでニュース検索（2秒）
  → "Found 5 articles"

Step 2: 記事を分析（2秒）
  → "Average sentiment +0.45"

Step 3: DBに保存（1秒）
  → "Saved to database"
```

**ユウタ**: 「なるほど、Phase 3で本物に置き換えるわけか」

---

### ステップ13: APIを更新

**`backend/api/jobs.py`を更新**:
```python
from fastapi import APIRouter
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from backend.workers.dummy_worker import dummy_job  # ← 変更

router = APIRouter()

redis_conn = Redis(host='localhost', port=6379)
queue = Queue(connection=redis_conn)

class JobRequest(BaseModel):
    symbol: str  # ← nameからsymbolに変更

@router.post("/start")
async def start_job(request: JobRequest):
    """ジョブ開始"""
    job = queue.enqueue(
        dummy_job,  # ← 変更
        args=(request.symbol,),
        job_timeout='10m'  # ← タイムアウト追加
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

**ミコ**: 「変更点は3つ」

```
1. simple_job → dummy_job
2. name → symbol（仮想通貨用に変更）
3. job_timeout='10m' 追加（長時間ジョブ対策）
```

---

### ステップ14: 環境変数管理

**ミコ**: 「最後に、設定をハードコードから環境変数に移す」

**ユウタ**: 「なんで？」

**ミコ**: 「本番環境とテスト環境でRedisのホストが違うかもしれない」

**環境変数ファイル（`.env`）**:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

**依存関係追加**:
```bash
pip install python-dotenv
```

**設定ファイル（`backend/config.py`）**:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # .envファイルを読み込む

class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))

settings = Settings()
```

**`backend/api/jobs.py`を更新**:
```python
from backend.config import settings  # ← 追加

redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)  # ← 変更
```

**`backend/main.py`を更新**:
```python
from backend.config import settings  # ← 追加

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=True)
```

**ミコ**: 「これで設定を一箇所で管理できる」

---

### ステップ15: CORS設定

**ミコ**: 「最後にCORS設定」

**ユウタ**: 「CORS...？」

**ミコ**: 「Cross-Origin Resource Sharingの略。ブラウザのセキュリティ制約だ」

```
【CORSとは】

問題:
  Streamlit（http://localhost:8501）から
  FastAPI（http://localhost:8000）を呼ぶと
  → ブラウザが「異なるドメインだからダメ！」とブロック

解決:
  FastAPIに「Streamlitからのアクセスを許可する」と設定
```

**`backend/main.py`に追加**:
```python
from fastapi.middleware.cors import CORSMiddleware  # ← 追加

app = FastAPI(title="Grass Coin Trader API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 全てのドメインを許可（開発用）
    allow_credentials=True,
    allow_methods=["*"],  # 全てのHTTPメソッドを許可
    allow_headers=["*"],  # 全てのヘッダーを許可
)

app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
```

**ミコ**: 「これでStreamlitから呼べる」

---

### Phase 2 完成テスト

**ユウタ**: 「じゃあ最終テストだ！」

**ターミナル1: FastAPI起動**:
```bash
python backend/main.py
```

**出力**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**ターミナル2: RQワーカー起動**:
```bash
rq worker --url redis://localhost:6379
```

**出力**:
```
INFO:     Worker started
INFO:     Subscribing to default...
```

**ターミナル3: ジョブ開始**:
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

**ターミナル2（ワーカー）の出力**:
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

**ターミナル3: ステータス確認**:
```bash
curl http://localhost:8000/api/jobs/status/abc-123-def
```

**結果**:
```json
{
  "job_id": "abc-123-def",
  "status": "finished",
  "result": {
    "success": true,
    "symbol": "BTC",
    "news_count": 5,
    "avg_sentiment": 0.45
  }
}
```

**ユウタ**: 「完璧！バックグラウンドで実行されて、結果も取得できた！」

**ミコ**: 「Phase 2完成だ」

---

### まとめ: Phase 2で作ったもの

**ミコ**: 「Phase 2で何を作ったか整理するぞ」

```
【Phase 2実装内容】

1. FastAPI - REST APIサーバー
   - HTTP経由でジョブを実行できる
   - /api/jobs/start → ジョブ開始
   - /api/jobs/status/{job_id} → ステータス確認

2. Redis - 高速データストア
   - ジョブキューとして使用
   - Workerとの仲介役

3. RQ (Redis Queue) - ジョブ管理
   - ジョブの登録・実行・ステータス管理
   - タイムアウト管理

4. Worker - バックグラウンド実行
   - 別プロセスでジョブを実行
   - メインプロセス（FastAPI）はフリーズしない

5. ダミージョブ - Claude Code実行をシミュレート
   - Step 1: WebSearch
   - Step 2: Analysis
   - Step 3: DB Save
   - Phase 3で本物のClaude Codeに置き換え
```

**ユウタ**: 「分かった！段階的に作ったから理解しやすかった」

**ミコ**: 「次はWebSocketでログを可視化する」

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
