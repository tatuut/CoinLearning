import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { query } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';
import os from 'os';
import path from 'path';
import fs from 'fs';

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

// 接続管理
const connections = new Map();

/**
 * Claude Code OAuth トークンを取得
 * Windows: ~/.claude/.credentials.json
 * macOS: ~/.claude/.credentials.json または Keychain
 * Linux: ~/.claude/.credentials.json
 */
function getClaudeCodeToken() {
  // 環境変数から直接取得を試みる
  if (process.env.CLAUDE_CODE_OAUTH_TOKEN) {
    return process.env.CLAUDE_CODE_OAUTH_TOKEN;
  }

  // 設定ファイルから取得を試みる
  const homeDir = os.homedir();
  const credentialsPath = path.join(homeDir, '.claude', '.credentials.json');

  try {
    if (fs.existsSync(credentialsPath)) {
      const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
      // OAuth アクセストークンを取得
      if (credentials.claudeAiOauth?.accessToken) {
        return credentials.claudeAiOauth.accessToken;
      }
    }
  } catch (error) {
    console.warn('[Warning] Claude Code認証情報読み込みエラー:', error.message);
  }

  return null;
}

/**
 * Claude Code認証状態を確認
 */
function checkClaudeCodeAuth() {
  const token = getClaudeCodeToken();

  if (!token) {
    console.warn('⚠️  Claude Code OAuth トークンが見つかりません');
    console.warn('');
    console.warn('以下のコマンドで認証してください:');
    console.warn('  claude login');
    console.warn('');
    console.warn('または、長期トークンを生成して環境変数に設定:');
    console.warn('  claude setup-token');
    console.warn('  export CLAUDE_CODE_OAUTH_TOKEN=<token>');
    return false;
  }

  return true;
}

// ヘルスチェック
app.get('/health', (req, res) => {
  const authOk = checkClaudeCodeAuth();
  res.json({
    status: authOk ? 'ok' : 'warning',
    timestamp: new Date().toISOString(),
    authMethod: 'Claude Plan Max (OAuth)',
    authenticated: authOk
  });
});

// Claude Agent SDK情報取得
app.get('/api/info', (req, res) => {
  res.json({
    model: 'claude-sonnet-4-5-20250929',
    authMethod: 'Claude Plan Max Subscription',
    maxTurns: 10,
    billing: 'Max 20x Plan (no API charges)',
    sdkVersion: 'latest'
  });
});

// WebSocket接続ハンドラー
wss.on('connection', (ws) => {
  const connectionId = Math.random().toString(36).substring(7);
  connections.set(connectionId, ws);

  console.log(`[WebSocket] 新規接続: ${connectionId}`);

  // 認証状態確認
  const authOk = checkClaudeCodeAuth();

  // 接続成功メッセージ
  ws.send(JSON.stringify({
    type: 'connected',
    connectionId,
    authenticated: authOk,
    timestamp: new Date().toISOString()
  }));

  // メッセージ受信ハンドラー
  ws.on('message', async (data) => {
    try {
      const message = JSON.parse(data.toString());

      if (message.type === 'query') {
        await handleClaudeQuery(ws, message);
      } else if (message.type === 'ping') {
        ws.send(JSON.stringify({
          type: 'pong',
          timestamp: new Date().toISOString()
        }));
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

  const token = getClaudeCodeToken();
  if (!token) {
    ws.send(JSON.stringify({
      type: 'error',
      error: 'Claude Code OAuth 認証が必要です。`claude login` を実行してください。',
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

    // 環境変数にトークンを設定（SDKがサブプロセスに渡すため）
    process.env.ANTHROPIC_API_KEY = token;

    // Claude Agent SDK query実行
    const queryOptions = {
      model: options.model || 'claude-sonnet-4-5-20250929',
      maxTurns: options.maxTurns || 10,
      systemPrompt: options.systemPrompt,
      allowedTools: options.allowedTools,
      cwd: options.cwd || process.cwd(),
      includePartialMessages: true,
      ...options
    };

    console.log(`[Claude Query] プロンプト: ${prompt.substring(0, 100)}...`);
    console.log(`[Claude Query] オプション:`, JSON.stringify(queryOptions, null, 2));

    const result = query({
      prompt,
      options: queryOptions
    });

    // ストリーミング結果を順次送信
    for await (const sdkMessage of result) {
      // デバッグ: メッセージ構造を出力
      console.log('[DEBUG] SDK Message:', JSON.stringify(sdkMessage, null, 2));

      // メッセージタイプに応じて処理
      const event = convertSdkMessageToEvent(sdkMessage);

      ws.send(JSON.stringify({
        type: 'message',
        event: event,
        raw: sdkMessage,
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

/**
 * SDK メッセージをイベント形式に変換
 */
function convertSdkMessageToEvent(sdkMessage) {
  const role = sdkMessage.role;
  const content = sdkMessage.content || [];

  // アシスタントメッセージ
  if (role === 'assistant') {
    const textBlocks = content.filter(c => c.type === 'text');
    const toolUseBlocks = content.filter(c => c.type === 'tool_use');

    return {
      type: 'assistant_message',
      text: textBlocks.map(b => b.text).join('\n'),
      toolUses: toolUseBlocks.map(b => ({
        id: b.id,
        name: b.name,
        input: b.input
      }))
    };
  }

  // ツール結果
  if (role === 'user' && content.some(c => c.type === 'tool_result')) {
    const toolResults = content.filter(c => c.type === 'tool_result');
    return {
      type: 'tool_results',
      results: toolResults.map(r => ({
        id: r.tool_use_id,
        content: r.content
      }))
    };
  }

  // その他
  return {
    type: 'unknown',
    role,
    content
  };
}

// REST API: 非ストリーミング版
app.post('/api/query', async (req, res) => {
  const { prompt, options = {} } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'prompt が必要です' });
  }

  if (!checkClaudeCodeAuth()) {
    return res.status(500).json({
      error: 'Claude Code OAuth 認証が必要です',
      hint: 'claude login を実行してください'
    });
  }

  try {
    const queryOptions = {
      model: options.model || 'claude-sonnet-4-5-20250929',
      maxTurns: options.maxTurns || 10,
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
      billing: {
        total_cost_usd: 0,
        note: 'Max 20x Plan - no API charges'
      },
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
  const authOk = checkClaudeCodeAuth();

  console.log('='.repeat(60));
  console.log('🚀 Claude Code Server 起動');
  console.log('='.repeat(60));
  console.log(`📡 HTTP Server: http://${HOST}:${PORT}`);
  console.log(`🔌 WebSocket: ws://${HOST}:${PORT}`);
  console.log(`🔐 認証方式: Claude Plan Max (OAuth)`);
  console.log(`✅ 認証状態: ${authOk ? '認証済み' : '未認証'}`);
  console.log(`💰 課金: Max 20x Plan (API料金なし)`);
  console.log('='.repeat(60));
  console.log('');

  if (!authOk) {
    console.log('⚠️  認証が必要です。以下のコマンドを実行してください:');
    console.log('');
    console.log('  claude login');
    console.log('');
    console.log('または、長期トークンを生成:');
    console.log('  claude setup-token');
    console.log('  export CLAUDE_CODE_OAUTH_TOKEN=<token>');
    console.log('');
    console.log('='.repeat(60));
  } else {
    console.log('利用可能なエンドポイント:');
    console.log(`  GET  /health       - ヘルスチェック`);
    console.log(`  GET  /api/info     - SDK情報取得`);
    console.log(`  POST /api/query    - REST API (非ストリーミング)`);
    console.log(`  WS   /             - WebSocket (ストリーミング)`);
    console.log('='.repeat(60));
  }
});
