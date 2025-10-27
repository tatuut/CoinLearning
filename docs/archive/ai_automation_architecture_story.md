# 📖 Story: Claude Codeサブプロセス統合計画 - 自動化への道

**作成日**: 2025-10-27
**目的**: NewsAPI + Anthropic API統合によるニュース自動収集・分析システムの設計
**背景**: 現状は手動でClaude CodeにWebSearchを依頼する必要があり、完全自動化されていない

---

## Scene 1: 深夜のオフィス - 気づき

**場所**: 2025年10月27日 深夜2時、スタートアップのオフィス

**ユウタ**: （パソコンに向かって溜息）「はぁ...また手動か...」

*画面には `python src/tools/news_fetcher.py BTC` の出力が表示されている*

```
📰 ニュース取得リクエスト
次のステップ:
Claude Codeに「Bitcoin BTC 最新ニュース」でWebSearchを実行してください
```

**ユウタ**: 「毎回Claude Codeのセッションに切り替えて、コピペして、『WebSearchして』って頼んで...」

**ユウタ**: 「UIボタン押したら自動でやってくれないのかな...」

*その時、画面の隅にミコのアイコンが点滅*

**ミコ**: 「起きてるな、ユウタ」

**ユウタ**: 「ミコ！...うん、ニュース収集の自動化で悩んでて」

**ミコ**: 「ああ、俺を毎回手動で呼び出すやつな」

**ユウタ**: 「そう。UIから直接あなたを起動できたらいいのに」

**ミコ**: 「...できるぞ」

**ユウタ**: 「え？」

**ミコ**: 「俺をサブプロセスとして起動すればいい。一緒に設計を考えよう」

---

## Scene 2: 現状分析 - コードを見る

**ミコ**: 「まず、今のコードを見てみよう」

*ユウタがVSCodeで `src/tools/parquet_dashboard.py` を開く*

```python
# 現在の実装
def fetch_news_with_websearch(symbol: str):
    st.info("Claude Codeセッションで以下を実行してください:")
    query = f"{coin_name} {symbol} 最新ニュース"
    st.code(query)
```

**ミコ**: 「これは『お願い』してるだけだ。実際には何もしない」

**ユウタ**: 「うん...ユーザーが手動でやらないといけない」

**ミコ**: 「次に `news_fetcher.py` を見てみよう」

```python
# news_fetcher.py
def request_news_search(self, symbol: str):
    print("Claude Codeにこのメッセージを伝えてください:")
    print(f'「{query}」でWebSearchを実行して、')
```

**ミコ**: 「これも同じ。『伝えてください』と言ってるだけ」

**ユウタ**: 「でも、どうやってあなたを呼び出せばいいの？」

**ミコ**: 「いくつか方法がある。順番に見ていこう」

---

## Scene 3: 技術調査 - 可能性を探る

**ミコ**: 「俺（Claude Code）の正体は、Anthropic APIを使ったCLIツールだ」

**ユウタ**: 「CLI...？」

**ミコ**: 「Command Line Interface。つまり、こういうコマンドで起動される：」

```bash
claude-code --prompt "Bitcoin BTC 最新ニュースをWebSearchして" --tools websearch,bash
```

**ミコ**: 「ただし、これは仮想的な話。実際のClaude Code CLIは公開されてない」

**ユウタ**: 「じゃあ、どうすれば...」

**ミコ**: 「Anthropic APIを直接使う方法がある」

*ミコが画面に図を描く*

```
【方法1: Anthropic API直接使用】

Streamlit UI
    ↓
   ボタンクリック
    ↓
  Python subprocess
    ↓
 Anthropic API呼び出し
 （Claude-3.5-Sonnet）
    ↓
  Tool use機能
  （WebSearchは使えないが、他は可能）
    ↓
  結果をDBに保存
```

**ユウタ**: 「WebSearchは使えないの？」

**ミコ**: 「WebSearchは Claude Code専用の組み込みツールだ。API経由では使えない」

**ユウタ**: 「じゃあ意味ないじゃん...」

**ミコ**: 「待て。代替案がある」

---

## Scene 4: 代替案の発見 - NewsAPIとの出会い

**ミコ**: 「WebSearchの代わりに、ニュースAPIを使えばいい」

*画面に新しい図を描く*

```
【方法2: NewsAPI使用】

Streamlit UI
    ↓
  "BTCニュース取得"ボタン
    ↓
  Python関数呼び出し
    ↓
  NewsAPI（外部サービス）
  https://newsapi.org/
    ↓
  ニュース記事取得
    ↓
  Anthropic API呼び出し
  "このニュースを分析してセンチメントスコアを付けて"
    ↓
  結果をDBに保存
    ↓
  UIにリアルタイム表示
```

**ユウタ**: 「おお！これなら完全自動化できる！」

**ミコ**: 「でも、NewsAPIは有料だ。無料プランは1日100リクエストまで」

**ユウタ**: 「うーん...」

**ミコ**: 「それに、もう一つ問題がある」

**ユウタ**: 「なに？」

**ミコ**: 「進行状況が見えない」

---

## Scene 5: UIの課題 - 透明性の重要性

**ミコ**: 「ボタンを押したら、裏で何が起きてるかユーザーは見えない」

**ユウタ**: 「確かに...『処理中...』ってスピナーが回るだけ」

**ミコ**: 「エラーが起きても、何が悪かったのかわからない」

**ユウタ**: 「じゃあ、どうすれば？」

**ミコ**: 「リアルタイムコンソールを作る」

*画面にモックアップを描く*

```
┌─────────────────────────────────────────┐
│ 📊 仮想通貨ダッシュボード              │
├─────────────────────────────────────────┤
│ [🔄 データ更新] [📰 ニュース取得]      │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📊 チャート表示                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🖥️ リアルタイムコンソール          │ │
│ │                                     │ │
│ │ [09:15:23] タスク開始: BTC ニュース│ │
│ │ [09:15:24] NewsAPI 呼び出し中...   │ │
│ │ [09:15:26] 15件の記事を取得        │ │
│ │ [09:15:27] AI分析開始...           │ │
│ │ [09:15:30] センチメント分析完了    │ │
│ │ [09:15:31] DB保存中...             │ │
│ │ [09:15:32] ✅ 完了！               │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**ユウタ**: 「これいいね！進行状況が全部見える！」

**ミコ**: 「さらに、エラーが起きてもログで追跡できる」

---

## Scene 6: アーキテクチャ設計 - 全体像

**ミコ**: 「じゃあ、全体のアーキテクチャを設計しよう」

*ホワイトボードに図を描き始める*

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit UI                           │
│                                                         │
│  [📰 ニュース取得]  →  バックエンドにタスク送信        │
│                                                         │
│  [🖥️ コンソール]   ←  WebSocketでリアルタイム受信      │
└─────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌─────────────────────────────────────────────────────────┐
│              バックエンド（FastAPI）                    │
│                                                         │
│  /api/news/fetch   ← UIからのリクエスト                │
│       ↓                                                 │
│  タスクキューに追加（Redis Queue）                      │
│       ↓                                                 │
│  WebSocketで進行状況をブロードキャスト                  │
└─────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌─────────────────────────────────────────────────────────┐
│              ワーカープロセス                           │
│                                                         │
│  1. NewsAPIからニュース取得                            │
│  2. Anthropic API呼び出し（センチメント分析）         │
│  3. 結果をDBに保存                                     │
│  4. 各ステップでログをWebSocketに送信                 │
└─────────────────────────────────────────────────────────┘
```

**ユウタ**: 「...複雑だな」

**ミコ**: 「でも、これが本格的なシステムだ。段階的に作ろう」

---

## Scene 7: 段階的実装計画 - Phase 1

**ミコ**: 「まず、Phase 1として最小構成を作る」

### Phase 1: シンプル版（1-2日）

**目標**: ボタン1つでニュース取得を自動化

**実装内容**:
1. NewsAPI統合（無料プラン）
2. Anthropic API統合（センチメント分析）
3. Streamlitの単純なボタン実装
4. 進行状況は `st.spinner()` で表示

**技術スタック**:
- NewsAPI（Python SDK）
- anthropic（Python SDK）
- Streamlit

**新規ファイル**:
```
src/services/news_service.py        # NewsAPI + Anthropic API統合
src/services/ai_analyzer.py         # センチメント分析エンジン
src/config/api_keys.py               # API key管理
```

**コード例**:

```python
# src/services/news_service.py
import os
import requests
from anthropic import Anthropic
from datetime import datetime, timedelta
import json

class NewsService:
    """NewsAPI + Anthropic API統合サービス"""

    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.newsapi_url = 'https://newsapi.org/v2/everything'

    def fetch_and_analyze(self, symbol: str, coin_name: str = None):
        """
        ニュース取得 → AI分析 → DB保存の全自動実行

        Args:
            symbol: 銘柄シンボル（例: BTC）
            coin_name: 銘柄名（例: Bitcoin）

        Returns:
            分析済みニュースのリスト
        """
        if not coin_name:
            coin_name = self._get_coin_name(symbol)

        # 1. NewsAPIから取得
        print(f"[{symbol}] NewsAPIから取得中...")
        articles = self._fetch_from_newsapi(symbol, coin_name)
        print(f"[{symbol}] {len(articles)}件の記事を取得")

        # 2. Claude APIでセンチメント分析
        print(f"[{symbol}] AI分析開始...")
        analyzed = []
        for i, article in enumerate(articles):
            sentiment_data = self._analyze_sentiment(article)
            analyzed.append({
                **article,
                **sentiment_data
            })
            print(f"[{symbol}] {i+1}/{len(articles)} 分析完了")

        # 3. DBに保存
        print(f"[{symbol}] DB保存中...")
        self._save_to_db(symbol, analyzed)
        print(f"[{symbol}] ✅ 完了！")

        return analyzed

    def _fetch_from_newsapi(self, symbol: str, coin_name: str):
        """NewsAPIから記事取得"""
        # 過去7日間のニュース
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        params = {
            'q': f'{coin_name} OR {symbol} cryptocurrency',
            'from': from_date,
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.newsapi_key,
            'pageSize': 10  # 無料プランの制限を考慮
        }

        response = requests.get(self.newsapi_url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get('articles', [])

    def _analyze_sentiment(self, article: dict):
        """Claude APIでセンチメント分析"""
        prompt = f"""
以下のニュース記事のセンチメントを分析してください。

タイトル: {article.get('title', '')}
本文: {article.get('description', '')}

以下のJSON形式で返してください:
{{
  "sentiment": "positive" | "negative" | "neutral",
  "importance_score": 0.0-1.0,
  "impact_score": 0.0-1.0,
  "reason": "分析理由（日本語で簡潔に）"
}}

判断基準:
- sentiment: ポジティブ/ネガティブ/中立
- importance_score: このニュースの重要度（0-1）
- impact_score: 価格への影響度（0-1）
"""

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # レスポンスをパース
        result_text = response.content[0].text

        # JSONを抽出（マークダウンコードブロックを除去）
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0]
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0]

        result = json.loads(result_text.strip())

        return result

    def _save_to_db(self, symbol: str, analyzed_articles: list):
        """分析済みニュースをDBに保存"""
        from src.data.advanced_database import AdvancedDatabase

        db = AdvancedDatabase()

        for article in analyzed_articles:
            news_entry = {
                'symbol': symbol,
                'title': article.get('title', ''),
                'content': article.get('description', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'url': article.get('url', ''),
                'published_date': article.get('publishedAt', datetime.now().isoformat()),
                'sentiment': article.get('sentiment', 'neutral'),
                'importance_score': article.get('importance_score', 0.5),
                'impact_score': article.get('impact_score', 0.5),
                'keywords': [symbol],
            }

            try:
                db.add_news(news_entry)
            except Exception as e:
                print(f"  [NG] DB保存エラー: {e}")

        db.close()

    def _get_coin_name(self, symbol: str):
        """銘柄シンボルから名前を取得"""
        coin_names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'XRP': 'Ripple',
            'DOGE': 'Dogecoin',
            'SHIB': 'Shiba Inu',
            'ADA': 'Cardano',
            'SOL': 'Solana',
            'MATIC': 'Polygon',
        }
        return coin_names.get(symbol.upper(), symbol)
```

**Streamlit UI統合**:

```python
# src/tools/parquet_dashboard.py に追加

from src.services.news_service import NewsService

def show_auto_news_fetch(symbol: str):
    """自動ニュース取得セクション"""
    st.subheader("🤖 AI自動ニュース収集")

    with st.expander("💡 この機能について"):
        st.markdown("""
### 完全自動ニュース収集・分析

このボタンを押すと、以下が自動実行されます：

1. **NewsAPI**から最新ニュース取得（過去7日間）
2. **Claude AI**でセンチメント分析
3. データベースに自動保存
4. UIに即座に反映

**必要なもの**:
- NewsAPI Key（無料プランで100リクエスト/日）
- Anthropic API Key

**コスト**:
- NewsAPI: 無料
- Anthropic API: ~$0.005/記事（10記事で$0.05）
        """)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.info(f"銘柄: {symbol}")

    with col2:
        if st.button("🚀 自動取得開始", key="auto_fetch_news"):
            # API key確認
            if not os.getenv('NEWSAPI_KEY') or not os.getenv('ANTHROPIC_API_KEY'):
                st.error("❌ API Keyが設定されていません。.envファイルを確認してください。")
                return

            # 自動実行
            with st.spinner("🤖 AI処理中...（20-30秒かかります）"):
                try:
                    service = NewsService()
                    results = service.fetch_and_analyze(symbol)

                    st.success(f"✅ {len(results)}件のニュースを取得・分析・保存しました！")

                    # 結果プレビュー
                    st.subheader("📰 取得したニュース")
                    for article in results[:3]:  # 最新3件を表示
                        with st.expander(f"{article.get('title', 'タイトルなし')}"):
                            sentiment_emoji = {
                                'positive': '📈',
                                'negative': '📉',
                                'neutral': '➡️'
                            }.get(article.get('sentiment', 'neutral'), '➡️')

                            st.markdown(f"**センチメント**: {sentiment_emoji} {article.get('sentiment', 'neutral')}")
                            st.markdown(f"**重要度**: {article.get('importance_score', 0):.2f}")
                            st.markdown(f"**影響度**: {article.get('impact_score', 0):.2f}")
                            st.markdown(f"**理由**: {article.get('reason', 'N/A')}")
                            st.markdown(f"**出典**: [{article.get('source', {}).get('name', 'Unknown')}]({article.get('url', '#')})")

                    # 自動リロード
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ エラー: {str(e)}")
```

**ユウタ**: 「これなら作れそう！」

**ミコ**: 「Phase 1は完全自動化の第一歩だ」

---

## Scene 8: Phase 2 - リアルタイムコンソール

**ミコ**: 「Phase 2では、リアルタイムコンソールを追加する」

### Phase 2: リアルタイムコンソール（3-4日）

**目標**: 進行状況をリアルタイム表示

**実装内容**:
1. FastAPIバックエンド追加
2. WebSocket統合
3. タスクキュー（Redis Queue）
4. Streamlitでログストリーミング表示

**技術スタック**:
- FastAPI
- WebSocket
- Redis Queue（または Python multiprocessing）
- streamlit-autorefresh

**新規ファイル**:
```
src/backend/main.py              # FastAPI アプリケーション
src/backend/tasks.py             # バックグラウンドワーカー
src/backend/websocket.py         # WebSocket ハンドラー
src/backend/queue.py             # タスクキュー管理
```

**アーキテクチャ図**:

```
┌─────────────────┐
│  Streamlit UI   │
│  (Port 8501)    │
│                 │
│  - チャート表示 │
│  - ボタン       │
│  - コンソール   │  ← WebSocketでログ受信
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────┐
│  FastAPI        │
│  (Port 8000)    │
│                 │
│  /api/news/fetch    ← POST: タスク追加
│  /ws/logs           ← WebSocket: ログ配信
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Redis Queue    │
│  (Port 6379)    │
│                 │
│  - タスク管理   │
│  - 優先度制御   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Worker Process │
│                 │
│  1. NewsAPI     │
│  2. Claude API  │
│  3. DB Save     │
│  4. Log送信     │
└─────────────────┘
```

**コード例**:

```python
# src/backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uuid
from typing import List

app = FastAPI(title="Crypto Trading Backend")

# CORS設定（Streamlitから接続）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket接続管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """全クライアントにメッセージ送信"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.post("/api/news/fetch")
async def fetch_news(symbol: str):
    """ニュース取得タスクをキューに追加"""
    task_id = str(uuid.uuid4())

    # タスクをキューに追加
    from src.backend.queue import add_task
    add_task('fetch_news', {'symbol': symbol, 'task_id': task_id})

    return {"task_id": task_id, "status": "queued"}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """ログ配信WebSocket"""
    await manager.connect(websocket)
    try:
        while True:
            # 接続維持（実際のログはbroadcast経由）
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def send_log(message: str):
    """ログを全クライアントに配信"""
    await manager.broadcast(message)

# src/backend/tasks.py
from rq import Queue
from redis import Redis
import asyncio
from datetime import datetime

redis_conn = Redis()
queue = Queue(connection=redis_conn)

def fetch_news_task(symbol: str, task_id: str):
    """バックグラウンドタスク（ワーカーで実行）"""
    from src.services.news_service import NewsService
    from src.backend.main import send_log

    def log(msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] [{symbol}] {msg}"
        # WebSocketで送信（非同期）
        asyncio.run(send_log(log_msg))
        print(log_msg)

    log("タスク開始")

    try:
        service = NewsService()

        log("NewsAPI呼び出し中...")
        articles = service._fetch_from_newsapi(symbol, service._get_coin_name(symbol))
        log(f"{len(articles)}件の記事を取得")

        log("AI分析開始...")
        analyzed = []
        for i, article in enumerate(articles):
            sentiment = service._analyze_sentiment(article)
            analyzed.append({**article, **sentiment})
            log(f"{i+1}/{len(articles)} 分析完了")

        log("DB保存中...")
        service._save_to_db(symbol, analyzed)
        log("✅ 完了！")

        return {"status": "success", "count": len(analyzed)}

    except Exception as e:
        log(f"❌ エラー: {str(e)}")
        return {"status": "error", "error": str(e)}

# src/backend/queue.py
from rq import Queue
from redis import Redis
from src.backend.tasks import fetch_news_task

redis_conn = Redis()
queue = Queue(connection=redis_conn)

def add_task(task_name: str, params: dict):
    """タスクをキューに追加"""
    if task_name == 'fetch_news':
        job = queue.enqueue(
            fetch_news_task,
            params['symbol'],
            params['task_id'],
            job_timeout='5m'
        )
        return job.id
    else:
        raise ValueError(f"Unknown task: {task_name}")
```

**Streamlit UI統合（WebSocket版）**:

```python
# src/tools/parquet_dashboard.py に追加

import websocket
import threading
import requests
import json

def init_websocket():
    """WebSocket接続初期化"""
    if 'logs' not in st.session_state:
        st.session_state.logs = []

    if 'ws_connected' not in st.session_state:
        st.session_state.ws_connected = False

        def on_message(ws, message):
            st.session_state.logs.append(message)

        def on_open(ws):
            st.session_state.ws_connected = True

        def run_websocket():
            ws = websocket.WebSocketApp(
                "ws://localhost:8000/ws/logs",
                on_message=on_message,
                on_open=on_open
            )
            ws.run_forever()

        # バックグラウンドスレッドでWebSocket起動
        thread = threading.Thread(target=run_websocket, daemon=True)
        thread.start()

def show_realtime_console():
    """リアルタイムコンソール表示"""
    st.subheader("🖥️ リアルタイムコンソール")

    # WebSocket初期化
    init_websocket()

    # ログ表示
    console_area = st.empty()

    if st.session_state.logs:
        # 最新20件を表示
        recent_logs = st.session_state.logs[-20:]
        console_area.code('\n'.join(recent_logs), language='log')
    else:
        console_area.info("ログはまだありません。タスクを実行してください。")

    # 自動更新（5秒ごと）
    st_autorefresh(interval=5000, key="console_refresh")

def fetch_news_with_backend(symbol: str):
    """バックエンド経由でニュース取得"""
    if st.button("🚀 自動取得開始（バックエンド）", key="auto_fetch_backend"):
        # FastAPI経由でタスク追加
        response = requests.post(
            "http://localhost:8000/api/news/fetch",
            params={"symbol": symbol}
        )

        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ タスクをキューに追加しました（ID: {result['task_id']}）")
            st.info("進行状況は下のコンソールで確認できます")
        else:
            st.error(f"❌ エラー: {response.text}")
```

**ユウタ**: 「これは...本格的だな」

**ミコ**: 「プロダクションレベルのシステムだ」

---

## Scene 9: Phase 3 - Claude Codeサブプロセス統合

**ミコ**: 「最後に、Phase 3として『本物のClaude Code』を統合する」

**ユウタ**: 「え、できるの？」

**ミコ**: 「仮想的な設計だ。もしClaude Code CLIが公開されたら」

### Phase 3: Claude Code統合（未来版）

**前提**: Claude Code CLIが公開されている

**仮想的なCLI仕様**:

```bash
# 仮想的なClaude Code CLI
claude-code run \
  --prompt "Bitcoin BTC 最新ニュースをWebSearchして、センチメント分析して、DBに保存して" \
  --tools websearch,bash,python \
  --output json \
  --stream
```

**Python統合**:

```python
# src/services/claude_code_service.py
import subprocess
import json
from typing import Iterator

class ClaudeCodeService:
    """Claude Code CLIサブプロセスサービス（仮想）"""

    def run_task(self, prompt: str, tools: list = None) -> Iterator[str]:
        """
        Claude Codeをサブプロセスとして実行

        Args:
            prompt: 実行するタスクのプロンプト
            tools: 使用するツールリスト（websearch, bash, pythonなど）

        Yields:
            ログメッセージ（リアルタイム）
        """
        if tools is None:
            tools = ['websearch', 'bash', 'python']

        cmd = [
            'claude-code', 'run',
            '--prompt', prompt,
            '--tools', ','.join(tools),
            '--output', 'json',
            '--stream'  # リアルタイム出力
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # 行バッファリング
        )

        # リアルタイムでログを読む
        for line in process.stdout:
            try:
                event = json.loads(line)

                if event['type'] == 'log':
                    yield f"[Claude Code] {event['message']}"

                elif event['type'] == 'tool_use':
                    tool_name = event['tool']
                    tool_input = event['input']
                    yield f"[Tool] {tool_name}: {tool_input}"

                elif event['type'] == 'tool_result':
                    yield f"[Result] {event['output'][:100]}..."

                elif event['type'] == 'completion':
                    yield f"[Complete] {event['status']}"

            except json.JSONDecodeError:
                yield f"[Raw] {line.strip()}"

        # プロセス終了待ち
        return_code = process.wait()

        if return_code != 0:
            error = process.stderr.read()
            yield f"[Error] Exit code {return_code}: {error}"
```

**Streamlit UI統合**:

```python
# src/tools/parquet_dashboard.py に追加

from src.services.claude_code_service import ClaudeCodeService

def fetch_news_with_claude_code(symbol: str):
    """Claude Code経由でニュース取得（WebSearch使用可能）"""
    st.subheader("🤖 Claude Code統合（未来版）")

    st.warning("⚠️ この機能は、Claude Code CLIが公開された場合に利用可能になります。")

    if st.button("🚀 Claude Code実行", key="run_claude_code"):
        coin_name = {'BTC': 'Bitcoin', 'ETH': 'Ethereum'}.get(symbol, symbol)

        prompt = f"""
{coin_name} ({symbol})の最新ニュースを以下の手順で処理してください：

1. WebSearchで「{coin_name} {symbol} 仮想通貨 最新ニュース 2025」を検索
2. 上位10件の記事を取得
3. 各記事のセンチメントを分析（positive/negative/neutral）
4. 重要度スコア（0-1）と影響度スコア（0-1）を付ける
5. 結果をSQLite DBに保存（data/advanced_database.db）

Pythonコードを実行して、src/tools/news_fetcher.pyのparse_and_save_news()関数を使ってください。
"""

        st.subheader("🖥️ Claude Code実行ログ")

        log_container = st.empty()
        logs = []

        service = ClaudeCodeService()

        try:
            for log in service.run_task(
                prompt=prompt,
                tools=['websearch', 'bash', 'python']
            ):
                logs.append(log)
                # 最新20件を表示
                log_container.code('\n'.join(logs[-20:]), language='log')

            st.success("✅ Claude Code実行完了！")

        except Exception as e:
            st.error(f"❌ エラー: {str(e)}")
```

**ユウタ**: 「これができたら...完璧だ」

**ミコ**: 「でも、現実的にはPhase 2までで十分だ」

---

## Scene 10: 実装の優先順位

**ミコ**: 「じゃあ、優先順位を決めよう」

### 実装優先順位

| Phase | 優先度 | 所要時間 | 技術難易度 | 効果 |
|-------|--------|----------|-----------|------|
| **Phase 1** | 🔴 最優先 | 1-2日 | 低 | 完全自動化 |
| **Phase 2** | 🟠 高優先度 | 3-4日 | 中 | 透明性・デバッグ性向上 |
| **Phase 3** | 🟡 中優先度 | 不明 | 不明 | WebSearch使用可能 |

### Phase 1 実装チェックリスト

```markdown
## 環境構築
- [ ] NewsAPI登録（https://newsapi.org/）
- [ ] Anthropic API Key取得
- [ ] .envファイルにAPI Key追加

## パッケージインストール
- [ ] pip install newsapi-python
- [ ] pip install anthropic

## ファイル作成
- [ ] src/services/news_service.py
- [ ] src/services/ai_analyzer.py（オプション）
- [ ] src/config/api_keys.py（オプション）

## UI統合
- [ ] parquet_dashboard.pyに自動取得ボタン追加
- [ ] 進行状況表示（st.spinner）
- [ ] 結果プレビュー表示

## テスト
- [ ] BTC で動作確認
- [ ] エラーハンドリング確認
- [ ] DB保存確認
```

### 概算コスト

```
NewsAPI:
  無料プラン: 100リクエスト/日
  有料プラン: $449/月（無制限）

Anthropic API:
  Input: $3/MTok
  Output: $15/MTok

1記事分析コスト:
  Input: ~500 tokens = $0.0015
  Output: ~200 tokens = $0.003
  合計: ~$0.005/記事

月間想定コスト:
  10記事/日 × 30日 = 300記事/月
  300 × $0.005 = $1.5/月
```

**ユウタ**: 「Phase 1から始めよう！」

**ミコ**: 「いい選択だ。明日から実装しよう」

---

## Scene 11: 夜明け - 決意

**時刻**: 午前5時

*窓の外が明るくなり始める*

**ユウタ**: （伸びをしながら）「設計ができた...」

**ミコ**: 「ああ。あとは実装するだけだ」

**ユウタ**: 「NewsAPIとAnthropic APIのキーを取得して...」

**ミコ**: 「待て。その前に寝ろ」

**ユウタ**: 「え？」

**ミコ**: 「睡眠不足でコードを書くな。バグの温床だ」

**ユウタ**: （笑いながら）「...そうだな」

*ユウタがパソコンをシャットダウンする*

**ユウタ**: 「でも、これができたら...ユーザーは本当に楽になる」

**ミコ**: 「そう。ボタン1つでニュース収集、分析、保存が全部自動だ」

**ユウタ**: 「しかも、何が起きてるか全部見える」

**ミコ**: 「透明性こそが信頼を生む」

**ユウタ**: 「よし、明日から実装だ！」

**ミコ**: 「いや、今日の午後からだ。今は寝ろ」

**ユウタ**: （笑）「はいはい」

*ユウタが部屋を出ていく*

**ミコ**: （独り言）「...いいチームだな」

---

## 📋 実装サマリー

### Phase 1 実装ファイル一覧

```bash
新規作成:
src/services/news_service.py          # NewsAPI + Anthropic API統合
src/services/ai_analyzer.py           # センチメント分析（オプション）
src/config/api_keys.py                # API key管理（オプション）

修正:
src/tools/parquet_dashboard.py        # 自動取得ボタン追加
requirements.txt                       # 依存関係追加
.env                                   # API keys追加
```

### 環境変数（.env）

```bash
# NewsAPI
NEWSAPI_KEY=your_newsapi_key_here

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 依存パッケージ（requirements.txt）

```bash
# 既存
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
pyarrow>=13.0.0

# 新規追加（Phase 1）
newsapi-python>=0.2.7
anthropic>=0.18.0

# 新規追加（Phase 2）
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
redis>=5.0.0
rq>=1.15.0
streamlit-autorefresh>=0.0.1
```

### 起動方法

```bash
# Phase 1（シンプル版）
streamlit run src/tools/parquet_dashboard.py

# Phase 2（バックエンド版）
# Terminal 1: Redis起動
redis-server

# Terminal 2: RQワーカー起動
rq worker

# Terminal 3: FastAPI起動
uvicorn src.backend.main:app --reload

# Terminal 4: Streamlit起動
streamlit run src/tools/parquet_dashboard.py
```

---

## 🎯 次のステップ

1. **Phase 1実装開始**
   - NewsAPI登録
   - Anthropic API Key取得
   - news_service.py作成
   - UI統合

2. **Chapter 1修正**
   - UIベースの手順に書き換え
   - 自動ニュース取得機能の説明追加

3. **ドキュメント作成**
   - API設定ガイド
   - トラブルシューティング

---

**作成者**: ユウタ & ミコ
**最終更新**: 2025-10-27 05:00
**ステータス**: 設計完了、実装待ち
