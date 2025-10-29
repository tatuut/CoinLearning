import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { spawn } from 'child_process';

const app = express();
const PORT = process.env.PORT || 3003;
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

// ヘルスチェック
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    authMethod: 'Claude CLI (claude login)',
    mode: 'Direct CLI execution'
  });
});

// Claude情報取得
app.get('/api/info', (req, res) => {
  res.json({
    model: 'claude-sonnet-4-5-20250929',
    authMethod: 'Claude CLI (OAuth)',
    maxTurns: 10,
    billing: 'Max 20x Plan (no API charges)',
    mode: 'Direct CLI execution'
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
    authenticated: true,
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
 * Claude CLIを直接実行してクエリ処理
 */
async function handleClaudeQuery(ws, message) {
  const { prompt, options = {} } = message;

  try {
    // クエリ開始通知
    ws.send(JSON.stringify({
      type: 'query_start',
      timestamp: new Date().toISOString()
    }));

    console.log(`[Claude CLI] プロンプト: ${prompt.substring(0, 100)}...`);

    // セッションIDを生成または使用
    const sessionId = options.sessionId || `session-${Date.now()}-${Math.random().toString(36).substring(7)}`;

    // Claude CLIコマンド構築
    const args = [
      '--print',
      '--output-format', 'text',
      '--session-id', sessionId
    ];

    // Tool権限設定（デフォルトでWebSearchを有効化）
    if (options.allowedTools) {
      args.push('--allowed-tools', ...options.allowedTools);
    } else {
      // デフォルトでWebSearchとファイル操作を有効化
      args.push('--allowed-tools', 'WebSearch', 'Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep');
    }

    // プロンプトを最後に追加
    args.push(prompt);

    console.log(`[Claude CLI] コマンド: claude ${args.join(' ')}`);

    // Claude CLIを子プロセスとして起動
    const claude = spawn('claude', args, {
      cwd: options.cwd || process.cwd(),
      shell: true,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // stdinを即座に閉じる（--printモードなので入力不要）
    claude.stdin.end();

    // 標準出力からテキストを受信
    let fullText = '';
    claude.stdout.on('data', (chunk) => {
      const text = chunk.toString();
      fullText += text;

      // テキストチャンクを送信
      ws.send(JSON.stringify({
        type: 'message',
        event: {
          type: 'assistant_message',
          text: text,
          toolUses: []
        },
        timestamp: new Date().toISOString()
      }));
    });

    // 標準エラー出力
    claude.stderr.on('data', (chunk) => {
      console.error('[Claude CLI] stderr:', chunk.toString());
    });

    // プロセス終了
    claude.on('close', (code) => {
      console.log(`[Claude CLI] プロセス終了: code ${code}`);

      if (code === 0) {
        ws.send(JSON.stringify({
          type: 'query_complete',
          timestamp: new Date().toISOString()
        }));
      } else {
        ws.send(JSON.stringify({
          type: 'error',
          error: `Claude CLI exited with code ${code}`,
          timestamp: new Date().toISOString()
        }));
      }
    });

    // エラーハンドリング
    claude.on('error', (error) => {
      console.error('[Claude CLI] エラー:', error);
      ws.send(JSON.stringify({
        type: 'error',
        error: error.message,
        timestamp: new Date().toISOString()
      }));
    });

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

// REST API: 非ストリーミング版
app.post('/api/query', async (req, res) => {
  const { prompt, options = {} } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'prompt が必要です' });
  }

  try {
    // Claude CLIコマンド構築
    const args = [
      '--print',
      '--output-format', 'text'
    ];

    // オプション追加
    if (options.allowedTools) {
      args.push('--allowed-tools', ...options.allowedTools);
    }

    // プロンプトを最後に追加
    args.push(prompt);

    console.log(`[REST API] プロンプト: ${prompt.substring(0, 100)}...`);

    // Claude CLIを子プロセスとして起動
    const claude = spawn('claude', args, {
      cwd: options.cwd || process.cwd(),
      shell: true,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    claude.stdin.end();

    // 出力を収集
    let fullText = '';
    let errorText = '';

    claude.stdout.on('data', (chunk) => {
      fullText += chunk.toString();
    });

    claude.stderr.on('data', (chunk) => {
      errorText += chunk.toString();
    });

    // プロセス終了を待つ
    claude.on('close', (code) => {
      console.log(`[REST API] Claude CLI終了: code ${code}`);

      if (code === 0) {
        res.json({
          success: true,
          response: fullText,
          billing: {
            total_cost_usd: 0,
            note: 'Max 20x Plan - no API charges'
          },
          timestamp: new Date().toISOString()
        });
      } else {
        res.status(500).json({
          error: `Claude CLI exited with code ${code}`,
          stderr: errorText,
          timestamp: new Date().toISOString()
        });
      }
    });

    // エラーハンドリング
    claude.on('error', (error) => {
      console.error('[REST API] エラー:', error);
      res.status(500).json({
        error: error.message,
        timestamp: new Date().toISOString()
      });
    });

  } catch (error) {
    console.error('[REST API] エラー:', error);
    res.status(500).json({
      error: error.message,
      stack: error.stack
    });
  }
});

// サーバー起動
server.listen(PORT, HOST, () => {
  console.log('='.repeat(60));
  console.log('🚀 Claude CLI Server 起動');
  console.log('='.repeat(60));
  console.log(`📡 HTTP Server: http://${HOST}:${PORT}`);
  console.log(`🔌 WebSocket: ws://${HOST}:${PORT}`);
  console.log(`🔐 認証方式: Claude CLI (claude login)`);
  console.log(`💰 課金: Max 20x Plan (API料金なし)`);
  console.log(`⚙️  実行方式: Direct CLI execution`);
  console.log(`🧠 セッション管理: 有効 (--session-id)`);
  console.log(`🔧 Tool権限: WebSearch, File operations有効`);
  console.log('='.repeat(60));
  console.log('');
  console.log('利用可能なエンドポイント:');
  console.log(`  GET  /health       - ヘルスチェック`);
  console.log(`  GET  /api/info     - 情報取得`);
  console.log(`  POST /api/query    - REST API (非ストリーミング)`);
  console.log(`  WS   /             - WebSocket (ストリーミング)`);
  console.log('='.repeat(60));
});
