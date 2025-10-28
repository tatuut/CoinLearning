import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import dotenv from 'dotenv';
import { query } from '@anthropic-ai/claude-agent-sdk';

// 環境変数読み込み
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || 'localhost';

// ミドルウェア
app.use(cors());
app.use(express.json());

// HTTPサーバー作成
const server = createServer(app);

// WebSocketサーバー作成
const wss = new WebSocketServer({ server });

// WebSocket接続管理
const connections = new Map();

// ヘルスチェック
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    apiKeyConfigured: !!process.env.ANTHROPIC_API_KEY
  });
});

// Claude Agent SDK情報取得
app.get('/api/info', (req, res) => {
  res.json({
    model: process.env.CLAUDE_MODEL || 'claude-sonnet-4-5-20250929',
    maxTurns: parseInt(process.env.MAX_TURNS) || 10,
    sdkVersion: 'latest'
  });
});

// WebSocket接続ハンドラー
wss.on('connection', (ws) => {
  const connectionId = Math.random().toString(36).substring(7);
  connections.set(connectionId, ws);

  console.log(`[WebSocket] 新規接続: ${connectionId}`);

  // 接続成功メッセージ
  ws.send(JSON.stringify({
    type: 'connected',
    connectionId,
    timestamp: new Date().toISOString()
  }));

  // メッセージ受信ハンドラー
  ws.on('message', async (data) => {
    try {
      const message = JSON.parse(data.toString());

      if (message.type === 'query') {
        await handleClaudeQuery(ws, message);
      } else if (message.type === 'ping') {
        ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
      }
    } catch (error) {
      console.error('[WebSocket] エラー:', error);
      ws.send(JSON.stringify({
        type: 'error',
        error: error.message,
        timestamp: new Date().toISOString()
      }));
    }
  });

  // 接続終了ハンドラー
  ws.on('close', () => {
    console.log(`[WebSocket] 接続終了: ${connectionId}`);
    connections.delete(connectionId);
  });

  // エラーハンドラー
  ws.on('error', (error) => {
    console.error(`[WebSocket] エラー (${connectionId}):`, error);
  });
});

/**
 * Claude Agent SDKでクエリを実行し、結果をストリーミング
 */
async function handleClaudeQuery(ws, message) {
  const { prompt, options = {} } = message;

  if (!process.env.ANTHROPIC_API_KEY) {
    ws.send(JSON.stringify({
      type: 'error',
      error: 'ANTHROPIC_API_KEY が設定されていません',
      timestamp: new Date().toISOString()
    }));
    return;
  }

  try {
    // クエリ開始通知
    ws.send(JSON.stringify({
      type: 'query_start',
      timestamp: new Date().toISOString()
    }));

    // Claude Agent SDK query実行
    const queryOptions = {
      model: options.model || process.env.CLAUDE_MODEL || 'claude-sonnet-4-5-20250929',
      maxTurns: options.maxTurns || parseInt(process.env.MAX_TURNS) || 10,
      systemPrompt: options.systemPrompt,
      allowedTools: options.allowedTools,
      cwd: options.cwd || process.cwd(),
      ...options
    };

    console.log(`[Claude Query] プロンプト: ${prompt.substring(0, 100)}...`);
    console.log(`[Claude Query] オプション:`, queryOptions);

    const result = query({
      prompt,
      options: queryOptions
    });

    // ストリーミング結果を順次送信
    for await (const sdkMessage of result) {
      // SDKメッセージをクライアントに送信
      ws.send(JSON.stringify({
        type: 'message',
        data: sdkMessage,
        timestamp: new Date().toISOString()
      }));
    }

    // 完了通知
    ws.send(JSON.stringify({
      type: 'query_complete',
      timestamp: new Date().toISOString()
    }));

    console.log('[Claude Query] 完了');

  } catch (error) {
    console.error('[Claude Query] エラー:', error);
    ws.send(JSON.stringify({
      type: 'error',
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    }));
  }
}

// REST API: 非ストリーミング版（シンプルな応答）
app.post('/api/query', async (req, res) => {
  const { prompt, options = {} } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'prompt が必要です' });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY が設定されていません' });
  }

  try {
    const queryOptions = {
      model: options.model || process.env.CLAUDE_MODEL || 'claude-sonnet-4-5-20250929',
      maxTurns: options.maxTurns || parseInt(process.env.MAX_TURNS) || 10,
      systemPrompt: options.systemPrompt,
      allowedTools: options.allowedTools,
      cwd: options.cwd || process.cwd(),
      ...options
    };

    const result = query({
      prompt,
      options: queryOptions
    });

    const messages = [];
    for await (const sdkMessage of result) {
      messages.push(sdkMessage);
    }

    res.json({
      success: true,
      messages,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('[REST Query] エラー:', error);
    res.status(500).json({
      error: error.message,
      stack: error.stack
    });
  }
});

// サーバー起動
server.listen(PORT, HOST, () => {
  console.log('='.repeat(60));
  console.log('🚀 Claude Agent SDK Server 起動');
  console.log('='.repeat(60));
  console.log(`📡 HTTP Server: http://${HOST}:${PORT}`);
  console.log(`🔌 WebSocket: ws://${HOST}:${PORT}`);
  console.log(`🔑 API Key: ${process.env.ANTHROPIC_API_KEY ? '設定済み ✅' : '未設定 ❌'}`);
  console.log('='.repeat(60));
  console.log('');
  console.log('利用可能なエンドポイント:');
  console.log(`  GET  /health       - ヘルスチェック`);
  console.log(`  GET  /api/info     - SDK情報取得`);
  console.log(`  POST /api/query    - REST API (非ストリーミング)`);
  console.log(`  WS   /             - WebSocket (ストリーミング)`);
  console.log('='.repeat(60));
});
