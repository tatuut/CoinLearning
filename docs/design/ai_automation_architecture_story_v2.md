# 📖 Story: Claude Code SDK統合計画 - 本格的な自動化への道（改訂版）

**作成日**: 2025-10-27
**改訂日**: 2025-10-27
**目的**: `@anthropic-ai/claude-agent-sdk` を使った完全自動化システムの設計
**背景**: Claude Code CLIは非公開だが、SDKが存在し統合可能

**重要**: `@anthropic-ai/claude-agent-sdk` の実在が判明したため、Phase 3が実装可能になりました！

---

## Scene 1-8: （前半部分は同じ）

*Scene 1-8は `ai_automation_architecture_story.md` と同じ内容です。*

**要約**:
- Scene 1-2: 現状の課題（手動実行の限界）
- Scene 3-4: NewsAPI発見
- Scene 5-6: アーキテクチャ設計
- Scene 7: Phase 1設計（NewsAPI + Anthropic API）
- Scene 8: Phase 2設計（FastAPI + WebSocket）

---

## Scene 9: 重大な発見 - Claude Agent SDKの存在

**時刻**: 午前3時

*ユウタがドキュメントを読み漁っている*

**ユウタ**: 「ミコ、見てくれ！」

**ミコ**: 「どうした？」

**ユウタ**: 「`@anthropic-ai/claude-agent-sdk` っていうパッケージを見つけた！」

*画面にNPMパッケージのドキュメントが表示される*

```bash
npm install @anthropic-ai/claude-agent-sdk
```

**ミコ**: 「...なんだこれは」

**ユウタ**: 「Claude Codeの機能を、Node.jsから使えるSDKみたいだ」

**ミコ**: 「CLIじゃなくて、SDKか...」

*ミコが急いでドキュメントを読む*

**ミコ**: 「これだ...これがあれば、Phase 3が実装できる！」

**ユウタ**: 「マジで!?」

---

## Scene 10: SDK仕様の調査

**ミコ**: 「ドキュメントを見てみよう」

*`CLAUDE_CODE_INTEGRATION_SPEC.md` を開く*

### SDK の主要機能

```javascript
import { query, createSdkMcpServer, tool } from '@anthropic-ai/claude-agent-sdk';

// 1. query() - Claude Codeにタスクを実行させる
const result = await query({
  prompt: "Bitcoin BTC 最新ニュースをWebSearchして分析して",
  options: {
    model: 'claude-sonnet-4-5-20250929',
    maxTurns: 50,
    includePartialMessages: true,  // ストリーミング
    cwd: process.cwd()
  }
});

// 2. createSdkMcpServer() - カスタムツールを登録
const mcpServer = createSdkMcpServer({
  name: 'crypto-tools',
  version: '1.0.0',
  tools: [
    {
      name: 'save_to_db',
      description: 'Save news to SQLite database',
      inputSchema: { /* Zodスキーマ */ },
      handler: async (args) => { /* 実装 */ }
    }
  ]
});
```

**ユウタ**: 「これ...Pythonじゃないな」

**ミコ**: 「Node.js（JavaScript）だ。つまり、バックエンドが必要になる」

---

## Scene 11: 新しいアーキテクチャ - 3層構造

**ミコ**: 「アーキテクチャを再設計しよう」

*ホワイトボードに新しい図を描く*

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit UI (Python)                      │
│              Port 8501                                  │
│                                                         │
│  [📰 AI自動取得] ボタン                                │
│  [🖥️ リアルタイムコンソール]                           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP POST
                     ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                   │
│              Port 8000                                  │
│                                                         │
│  /api/claude-code/execute   ← タスク実行リクエスト    │
│  /ws/logs                   ← WebSocket（ログ配信）   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP POST
                     ↓
┌─────────────────────────────────────────────────────────┐
│          Node.js Service (JavaScript)                   │
│          Port 3000                                      │
│                                                         │
│  POST /execute                                          │
│       ↓                                                 │
│  @anthropic-ai/claude-agent-sdk                         │
│       ↓                                                 │
│  query() → WebSearch実行                                │
│       ↓                                                 │
│  カスタムツール（DB保存）                               │
└─────────────────────────────────────────────────────────┘
```

**ユウタ**: 「3層か...」

**ミコ**: 「そう。Streamlit（Python） → FastAPI（Python） → Node.js（SDK）」

**ユウタ**: 「なんでNode.jsが必要なの？」

**ミコ**: 「SDKがNode.js専用だからだ。でも、マイクロサービスとして分離すれば管理しやすい」

---

## Scene 12: Phase 3 設計（SDK版）

### Phase 3: Claude Agent SDK統合（3-5日）

**目標**: WebSearchを含む完全自動化

**実装内容**:
1. Node.jsマイクロサービス作成
2. `@anthropic-ai/claude-agent-sdk` 統合
3. カスタムツール登録（DB保存）
4. FastAPIとの連携
5. リアルタイムログストリーミング

**技術スタック**:
- Node.js + Express
- `@anthropic-ai/claude-agent-sdk`
- Zod（スキーマ定義）
- WebSocket（ログ配信）
- FastAPI（Pythonブリッジ）

**新規ファイル**:
```
backend/nodejs/
├── package.json
├── src/
│   ├── server.js              # Express サーバー
│   ├── claude_agent.js        # SDK統合
│   ├── tools/
│   │   ├── db_saver.js        # DB保存ツール
│   │   └── news_analyzer.js   # ニュース分析ツール
│   └── websocket.js           # ログ配信
```

---

## Scene 13: Node.jsサービス実装

**ミコ**: 「Node.jsサービスのコードを設計しよう」

### 13.1 基本構造

```javascript
// backend/nodejs/src/server.js
import express from 'express';
import { ClaudeAgentService } from './claude_agent.js';
import { WebSocketServer } from 'ws';

const app = express();
const port = 3000;

app.use(express.json());

// WebSocketサーバー
const wss = new WebSocketServer({ port: 3001 });

// Claude Agent Service
const agentService = new ClaudeAgentService(wss);

// タスク実行エンドポイント
app.post('/execute', async (req, res) => {
  const { symbol, task } = req.body;

  try {
    const result = await agentService.executeTask(symbol, task);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Node.js service running on port ${port}`);
});
```

### 13.2 Claude Agent統合

```javascript
// backend/nodejs/src/claude_agent.js
import { query, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

export class ClaudeAgentService {
  constructor(wss) {
    this.wss = wss;  // WebSocketサーバー
    this.db = null;
  }

  async init() {
    // SQLite DB接続
    this.db = await open({
      filename: '../../data/advanced_database.db',
      driver: sqlite3.Database
    });
  }

  async executeTask(symbol, task) {
    // ログ配信関数
    const log = (message) => {
      const logMsg = {
        type: 'log',
        timestamp: new Date().toISOString(),
        message
      };

      // 全WebSocketクライアントに配信
      this.wss.clients.forEach(client => {
        if (client.readyState === 1) { // OPEN
          client.send(JSON.stringify(logMsg));
        }
      });
    };

    log(`[${symbol}] タスク開始`);

    // カスタムツールを作成
    const mcpServer = createSdkMcpServer({
      name: 'crypto-tools',
      version: '1.0.0',
      tools: [
        this.createDbSaverTool(symbol, log),
        this.createNewsAnalyzerTool(log)
      ]
    });

    // プロンプト生成
    const prompt = this.generatePrompt(symbol, task);

    log(`[${symbol}] Claude Agent実行中...`);

    // Claude Code実行（ストリーミング）
    const results = [];

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
      // ストリーミングメッセージ処理
      if (message.type === 'stream_event') {
        const event = message.event;

        if (event.type === 'content_block_delta') {
          if (event.delta.type === 'text_delta') {
            log(`[Claude] ${event.delta.text}`);
          }
        }
      }

      if (message.type === 'result') {
        log(`[${symbol}] 完了！ターン数: ${message.num_turns}`);
        results.push(message);
      }
    }

    return { success: true, results };
  }

  createDbSaverTool(symbol, log) {
    return {
      name: 'save_news_to_db',
      description: 'Save analyzed news articles to SQLite database',
      inputSchema: z.object({
        articles: z.array(z.object({
          title: z.string(),
          content: z.string(),
          url: z.string().optional(),
          source: z.string().optional(),
          published_date: z.string(),
          sentiment: z.enum(['positive', 'negative', 'neutral']),
          importance_score: z.number().min(0).max(1),
          impact_score: z.number().min(0).max(1)
        }))
      }).shape,

      handler: async (args) => {
        log(`[DB] ${args.articles.length}件のニュースを保存中...`);

        const stmt = await this.db.prepare(`
          INSERT INTO news (
            symbol, title, content, source, url, published_date,
            sentiment, importance_score, impact_score, keywords,
            collected_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        let saved = 0;
        for (const article of args.articles) {
          try {
            await stmt.run(
              symbol,
              article.title,
              article.content,
              article.source || 'WebSearch',
              article.url || '',
              article.published_date,
              article.sentiment,
              article.importance_score,
              article.impact_score,
              JSON.stringify([symbol]),
              new Date().toISOString()
            );
            saved++;
          } catch (error) {
            log(`[DB Error] ${error.message}`);
          }
        }

        await stmt.finalize();
        log(`[DB] ✅ ${saved}件保存完了`);

        return {
          content: [{
            type: 'text',
            text: `Successfully saved ${saved} articles to database`
          }],
          isError: false
        };
      }
    };
  }

  createNewsAnalyzerTool(log) {
    return {
      name: 'analyze_news_sentiment',
      description: 'Analyze sentiment of news articles',
      inputSchema: z.object({
        articles: z.array(z.object({
          title: z.string(),
          description: z.string()
        }))
      }).shape,

      handler: async (args) => {
        log(`[Analyzer] ${args.articles.length}件を分析中...`);

        // ここでは簡易的な実装
        // 実際にはClaude API呼び出しなどを行う

        return {
          content: [{
            type: 'text',
            text: `Analyzed ${args.articles.length} articles`
          }],
          isError: false
        };
      }
    };
  }

  generatePrompt(symbol, task) {
    const coinNames = {
      'BTC': 'Bitcoin',
      'ETH': 'Ethereum',
      'XRP': 'Ripple'
    };

    const coinName = coinNames[symbol] || symbol;

    return `
${coinName} (${symbol})の最新ニュースを収集・分析して、データベースに保存してください。

## タスク手順

1. **WebSearchで検索**
   - クエリ: "${coinName} ${symbol} cryptocurrency news 2025"
   - 最新10件の記事を取得

2. **センチメント分析**
   各記事について以下を判定：
   - sentiment: positive/negative/neutral
   - importance_score: 0.0-1.0（重要度）
   - impact_score: 0.0-1.0（価格への影響度）

3. **データベース保存**
   - save_news_to_db ツールを使用
   - 全記事を一括保存

## 出力形式

最終的に、以下の形式でsave_news_to_dbツールを呼び出してください：

\`\`\`json
{
  "articles": [
    {
      "title": "記事タイトル",
      "content": "記事本文または要約",
      "url": "記事URL",
      "source": "ソース名",
      "published_date": "ISO8601形式",
      "sentiment": "positive",
      "importance_score": 0.8,
      "impact_score": 0.7
    }
  ]
}
\`\`\`

必ずsave_news_to_dbツールを使ってデータベースに保存してください。
`;
  }
}
```

**ユウタ**: 「これで、WebSearchが使えるようになるのか！」

**ミコ**: 「そう。しかもカスタムツールでDB保存も自動化できる」

---

## Scene 14: FastAPIブリッジ

**ミコ**: 「次に、FastAPIからNode.jsサービスを呼び出すブリッジを作る」

```python
# src/backend/nodejs_bridge.py
import requests
import websocket
import json
import threading
from typing import Callable

class NodeJsBridge:
    """Node.js Claude Agent Serviceへのブリッジ"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.ws_url = "ws://localhost:3001"
        self.log_callbacks = []

    def execute_task(self, symbol: str, task: str = "news_collection"):
        """
        Node.jsサービスでタスク実行

        Args:
            symbol: 銘柄シンボル
            task: タスク種別

        Returns:
            実行結果
        """
        response = requests.post(
            f"{self.base_url}/execute",
            json={"symbol": symbol, "task": task},
            timeout=300  # 5分
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Node.js service error: {response.text}")

    def connect_websocket(self, on_log: Callable):
        """
        WebSocket接続してログを受信

        Args:
            on_log: ログ受信時のコールバック関数
        """
        def on_message(ws, message):
            try:
                data = json.loads(message)
                on_log(data)
            except:
                pass

        def run_ws():
            ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=on_message
            )
            ws.run_forever()

        thread = threading.Thread(target=run_ws, daemon=True)
        thread.start()


# src/backend/main.py（FastAPI）に追加
from src.backend.nodejs_bridge import NodeJsBridge

nodejs_bridge = NodeJsBridge()

@app.post("/api/claude-code/execute")
async def execute_claude_code(symbol: str):
    """Claude Code経由でニュース収集"""
    try:
        result = nodejs_bridge.execute_task(symbol, "news_collection")
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.websocket("/ws/claude-logs")
async def websocket_claude_logs(websocket: WebSocket):
    """Claude Code実行ログをストリーミング"""
    await websocket.accept()

    def on_log(data):
        # Node.jsからのログをStreamlitに転送
        asyncio.run(websocket.send_json(data))

    nodejs_bridge.connect_websocket(on_log)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
```

---

## Scene 15: Streamlit UI統合

**ミコ**: 「最後に、StreamlitからFastAPIを呼び出すUIを作る」

```python
# src/tools/parquet_dashboard.py に追加

import requests
import websocket
import json
import threading

def show_claude_code_integration(symbol: str):
    """Claude Code SDK統合（完全自動化）"""
    st.subheader("🤖 Claude Code SDK統合（WebSearch対応）")

    with st.expander("💡 この機能について"):
        st.markdown("""
### Claude Agent SDK統合

この機能は`@anthropic-ai/claude-agent-sdk`を使用して、以下を**完全自動化**します：

1. **WebSearch**でニュース検索（Claude Code組み込み機能）
2. **AI分析**でセンチメント・スコア計算
3. **カスタムツール**で自動DB保存
4. **リアルタイムログ**で進行状況表示

**必要な環境**:
- Node.js サービス（Port 3000）
- Anthropic API Key

**Phase 1/2との違い**:
- Phase 1: NewsAPI（外部API、WebSearch不可）
- Phase 2: FastAPI + Redis Queue
- **Phase 3**: Claude Code SDK（WebSearch可能、カスタムツール使用可）
        """)

    # WebSocket接続（ログ受信）
    if 'claude_logs' not in st.session_state:
        st.session_state.claude_logs = []

    def connect_websocket():
        def on_message(ws, message):
            data = json.loads(message)
            st.session_state.claude_logs.append(
                f"[{data['timestamp'][:19]}] {data['message']}"
            )

        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws/claude-logs",
            on_message=on_message
        )

        thread = threading.Thread(target=ws.run_forever, daemon=True)
        thread.start()

    # WebSocket初回接続
    if 'ws_connected' not in st.session_state:
        connect_websocket()
        st.session_state.ws_connected = True

    # 実行ボタン
    col1, col2 = st.columns([3, 1])

    with col1:
        st.info(f"銘柄: {symbol}")

    with col2:
        if st.button("🚀 完全自動実行", key="claude_code_execute"):
            # FastAPI経由でNode.jsサービスを呼び出し
            with st.spinner("Claude Code実行中..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/claude-code/execute",
                        params={"symbol": symbol},
                        timeout=300
                    )

                    if response.status_code == 200:
                        result = response.json()

                        if result['success']:
                            st.success("✅ 完全自動収集・分析・保存が完了しました！")
                            st.json(result['result'])
                        else:
                            st.error(f"❌ エラー: {result.get('error', 'Unknown error')}")
                    else:
                        st.error(f"❌ API エラー: {response.text}")

                except Exception as e:
                    st.error(f"❌ 接続エラー: {str(e)}")

    # リアルタイムコンソール
    st.subheader("🖥️ リアルタイムコンソール")

    console_container = st.empty()

    if st.session_state.claude_logs:
        recent_logs = st.session_state.claude_logs[-30:]
        console_container.code('\n'.join(recent_logs), language='log')
    else:
        console_container.info("ログはまだありません。タスクを実行してください。")

    # 自動更新
    st_autorefresh(interval=2000, key="claude_console_refresh")
```

**ユウタ**: 「これで...完璧だ！」

**ミコ**: 「WebSearchもカスタムツールも、全部使える」

---

## Scene 16: 実装の優先順位（改訂版）

**ミコ**: 「改めて、優先順位を整理しよう」

### 実装優先順位（改訂版）

| Phase | 優先度 | 所要時間 | 技術難易度 | 効果 | 備考 |
|-------|--------|----------|-----------|------|------|
| **Phase 1** | 🔴 最優先 | 1-2日 | 低 | 完全自動化（NewsAPI） | Python のみ |
| **Phase 2** | 🟠 高優先度 | 3-4日 | 中 | 透明性・デバッグ性 | Python + Redis |
| **Phase 3** | 🟡 中優先度 | 3-5日 | 中〜高 | WebSearch使用可能 | Python + Node.js |

### Phase 3 実装チェックリスト

```markdown
## Node.js環境構築
- [ ] Node.js インストール（v18以上推奨）
- [ ] npm プロジェクト初期化
- [ ] パッケージインストール

## パッケージインストール
```bash
cd backend/nodejs
npm init -y
npm install express @anthropic-ai/claude-agent-sdk zod sqlite sqlite3 ws
```

## ファイル作成
- [ ] backend/nodejs/src/server.js
- [ ] backend/nodejs/src/claude_agent.js
- [ ] backend/nodejs/src/tools/db_saver.js
- [ ] backend/nodejs/src/websocket.js

## Python統合
- [ ] src/backend/nodejs_bridge.py
- [ ] FastAPI にエンドポイント追加
- [ ] WebSocket統合

## Streamlit UI
- [ ] parquet_dashboard.py に統合セクション追加
- [ ] WebSocket接続
- [ ] リアルタイムコンソール

## 起動
```bash
# Terminal 1: Node.js Service
cd backend/nodejs
node src/server.js

# Terminal 2: FastAPI
uvicorn src.backend.main:app --reload

# Terminal 3: Streamlit
streamlit run src/tools/parquet_dashboard.py
```

## テスト
- [ ] Node.jsサービス単体テスト
- [ ] FastAPIブリッジ動作確認
- [ ] Streamlit UI から実行
- [ ] WebSearch動作確認
- [ ] DB保存確認
```

### 概算コスト（Phase 3）

```
Anthropic API（Claude Code SDK）:
  同じくClaude-3.5-Sonnet使用
  Input: $3/MTok
  Output: $15/MTok

1タスクのコスト（WebSearch含む）:
  Input: ~2,000 tokens = $0.006
  Output: ~1,000 tokens = $0.015
  合計: ~$0.021/タスク

月間想定コスト:
  1タスク/日 × 30日 = 30タスク/月
  30 × $0.021 = $0.63/月

Phase 1（NewsAPI版）と比較:
  Phase 1: $1.5/月（10記事×30日）
  Phase 3: $0.63/月（1タスク×30日）
  → Phase 3の方が安い！
```

---

## Scene 17: 夜明け - 新たな可能性

**時刻**: 午前6時

*窓の外が明るくなっている*

**ユウタ**: （目を輝かせながら）「これ...すごくない？」

**ミコ**: 「ああ。WebSearchが使えるってことは...」

**ユウタ**: 「NewsAPIいらないじゃん」

**ミコ**: 「そう。しかも、カスタムツールで何でもできる」

*ミコがホワイトボードに書く*

```
【Claude Agent SDKで実現できること】

✅ WebSearch（Claude Code組み込み）
✅ カスタムツール（DB保存、分析、計算...）
✅ ストリーミング（リアルタイム進行状況）
✅ 複雑なタスクの自動実行（最大50ターン）

【Phase 1（NewsAPI版）との違い】

Phase 1:
- NewsAPI必須（有料）
- 単純なニュース取得のみ
- Pythonのみで完結

Phase 3（SDK版）:
- 外部API不要（WebSearch組み込み）
- 複雑なタスク自動化
- カスタムツール自由
- Node.js必要
```

**ユウタ**: 「でも、Node.jsが必要ってのがネックだな...」

**ミコ**: 「確かに。マイクロサービス管理が必要になる」

**ユウタ**: 「どっちを実装すべき？」

**ミコ**: 「段階的にだ」

---

## Scene 18: 最終的な実装戦略

**ミコ**: 「現実的な実装順序を決めよう」

### 推奨実装順序

```markdown
## ステップ1: Phase 1（1-2日）
NewsAPI + Anthropic API

理由:
✅ Pythonのみで完結
✅ 実装が簡単
✅ すぐに動く
❌ NewsAPI有料（無料プラン制限あり）

## ステップ2: Phase 2（3-4日）
FastAPI + WebSocket + リアルタイムコンソール

理由:
✅ Phase 1の拡張
✅ 透明性向上
✅ Pythonのみで完結
✅ デバッグ容易

## ステップ3: Phase 3 検討
Claude Agent SDK統合（Node.js）

導入タイミング:
- NewsAPIの制限に困ったら
- WebSearchが必須になったら
- カスタムツールが必要になったら

理由:
✅ WebSearch使用可能
✅ カスタムツール自由
✅ コストが安い
❌ Node.js環境が必要
❌ 管理が複雑
```

**ユウタ**: 「最初はPhase 1、必要になったらPhase 3に移行、って感じか」

**ミコ**: 「そう。段階的に進化させる」

**ユウタ**: 「わかった。じゃあ、Phase 1から始めよう」

**ミコ**: 「その前に寝ろ」

**ユウタ**: （笑）「...はい」

---

## 📋 実装サマリー（3 Phase比較）

### Phase 1: NewsAPI版（Python単体）

```bash
実装ファイル:
src/services/news_service.py
src/tools/parquet_dashboard.py（修正）

依存:
pip install newsapi-python anthropic

コスト: $1.5/月
難易度: ⭐（低）
完成度: 80%（WebSearch不可）
```

### Phase 2: リアルタイムコンソール版

```bash
実装ファイル:
src/backend/main.py（FastAPI）
src/backend/tasks.py（ワーカー）
src/backend/websocket.py

依存:
pip install fastapi uvicorn redis rq websockets

コスト: $1.5/月（同じ）
難易度: ⭐⭐（中）
完成度: 90%（透明性向上）
```

### Phase 3: Claude Agent SDK版

```bash
実装ファイル（Python）:
src/backend/nodejs_bridge.py
src/backend/main.py（修正）

実装ファイル（Node.js）:
backend/nodejs/src/server.js
backend/nodejs/src/claude_agent.js
backend/nodejs/src/tools/db_saver.js

依存:
# Python
pip install requests websocket-client

# Node.js
npm install express @anthropic-ai/claude-agent-sdk zod sqlite sqlite3 ws

コスト: $0.63/月（安い！）
難易度: ⭐⭐⭐（中〜高）
完成度: 100%（WebSearch + カスタムツール）
```

---

## 🎯 次のステップ

### 即座に始められること

1. **Phase 1実装**
   - NewsAPI登録
   - news_service.py作成
   - UI統合

2. **ドキュメント作成**
   - Phase 1実装ガイド
   - Phase 3実装ガイド（将来用）

3. **Chapter 1修正**
   - UIベースに書き換え

### 将来的な選択肢

- NewsAPIの制限に困ったら → Phase 3検討
- リアルタイムログが欲しい → Phase 2実装
- WebSearchが必須 → Phase 3実装

---

**作成者**: ユウタ & ミコ
**最終更新**: 2025-10-27 06:00
**ステータス**: 設計完了（3 Phase全て実装可能）
**推奨**: Phase 1 → Phase 2 → Phase 3 の順で実装
