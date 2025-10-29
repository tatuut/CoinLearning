import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { spawn } from 'child_process';
import { randomUUID } from 'crypto';

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

// セッション管理
const sessions = new Map(); // sessionId -> { claude: ChildProcess, ws: WebSocket }

/**
 * 新しいClaude Codeインタラクティブセッションを作成
 */
function createClaudeSession(ws, sessionId, options = {}) {
  console.log(`[Session ${sessionId}] 新規Claude Codeセッション作成`);

  // Claude CLIコマンド構築（シンプルな対話モード）
  const args = [
    '--session-id', sessionId
  ];

  // Tool権限設定
  if (options.allowedTools) {
    args.push('--allowed-tools', ...options.allowedTools);
  } else {
    // デフォルトでWebSearchを有効化
    args.push('--allowed-tools', 'WebSearch', 'Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep');
  }

  console.log(`[Session ${sessionId}] コマンド: claude ${args.join(' ')}`);

  // Claude CLIをインタラクティブモードで起動
  const claude = spawn('claude', args, {
    cwd: options.cwd || process.cwd(),
    shell: true,
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // 標準出力からテキストを受信
  claude.stdout.on('data', (chunk) => {
    const text = chunk.toString();
    console.log(`[Session ${sessionId}] stdout:`, text);

    // クライアントにテキスト送信
    ws.send(JSON.stringify({
      type: 'message',
      text: text,
      timestamp: new Date().toISOString()
    }));
  });

  // 標準エラー出力
  claude.stderr.on('data', (chunk) => {
    console.error(`[Session ${sessionId}] stderr:`, chunk.toString());
  });

  // プロセス終了
  claude.on('close', (code) => {
    console.log(`[Session ${sessionId}] プロセス終了: code ${code}`);

    ws.send(JSON.stringify({
      type: 'session_closed',
      code,
      timestamp: new Date().toISOString()
    }));

    // セッション削除
    sessions.delete(sessionId);
  });

  // エラーハンドリング
  claude.on('error', (error) => {
    console.error(`[Session ${sessionId}] エラー:`, error);

    ws.send(JSON.stringify({
      type: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
    }));
  });

  return claude;
}

// ヘルスチェック
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    authMethod: 'Claude CLI (claude login)',
    mode: 'Interactive session with history',
    activeSessions: sessions.size
  });
});

// Claude情報取得
app.get('/api/info', (req, res) => {
  res.json({
    model: 'claude-sonnet-4-5-20250929',
    authMethod: 'Claude CLI (OAuth)',
    maxTurns: 'unlimited (interactive)',
    billing: 'Max 20x Plan (no API charges)',
    mode: 'Interactive session with automatic history management',
    features: ['WebSearch', 'File operations', 'History compression']
  });
});

// WebSocket接続ハンドラー
wss.on('connection', (ws) => {
  let sessionId = null;
  let claudeSession = null;

  console.log(`[WebSocket] 新規接続`);

  // 接続成功メッセージ
  ws.send(JSON.stringify({
    type: 'connected',
    authenticated: true,
    timestamp: new Date().toISOString()
  }));

  // メッセージ受信ハンドラー
  ws.on('message', async (data) => {
    try {
      const message = JSON.parse(data.toString());

      if (message.type === 'start_session') {
        // 新規セッション開始
        sessionId = message.sessionId || randomUUID();
        const options = message.options || {};

        claudeSession = createClaudeSession(ws, sessionId, options);
        sessions.set(sessionId, { claude: claudeSession, ws });

        ws.send(JSON.stringify({
          type: 'session_started',
          sessionId,
          timestamp: new Date().toISOString()
        }));

      } else if (message.type === 'query') {
        // クエリ送信
        if (!claudeSession) {
          // セッションがない場合は自動作成
          sessionId = randomUUID();
          claudeSession = createClaudeSession(ws, sessionId, message.options || {});
          sessions.set(sessionId, { claude: claudeSession, ws });

          ws.send(JSON.stringify({
            type: 'session_started',
            sessionId,
            timestamp: new Date().toISOString()
          }));
        }

        const prompt = message.prompt;
        console.log(`[Session ${sessionId}] プロンプト: ${prompt.substring(0, 100)}...`);

        // プロンプト送信
        claudeSession.stdin.write(prompt + '\n');

        ws.send(JSON.stringify({
          type: 'query_start',
          timestamp: new Date().toISOString()
        }));

      } else if (message.type === 'end_session') {
        // セッション終了
        if (claudeSession) {
          claudeSession.stdin.end();
          claudeSession.kill();
          sessions.delete(sessionId);
        }

        ws.send(JSON.stringify({
          type: 'session_ended',
          timestamp: new Date().toISOString()
        }));

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
    console.log(`[WebSocket] 接続終了 (Session: ${sessionId})`);

    // セッションクリーンアップ
    if (sessionId && sessions.has(sessionId)) {
      const session = sessions.get(sessionId);
      if (session.claude) {
        session.claude.stdin.end();
        session.claude.kill();
      }
      sessions.delete(sessionId);
    }
  });

  // エラーハンドラー
  ws.on('error', (error) => {
    console.error(`[WebSocket] エラー (Session: ${sessionId}):`, error);
  });
});

// サーバー起動
server.listen(PORT, HOST, () => {
  console.log('='.repeat(60));
  console.log('🚀 Claude CLI Server 起動 (Interactive Mode)');
  console.log('='.repeat(60));
  console.log(`📡 HTTP Server: http://${HOST}:${PORT}`);
  console.log(`🔌 WebSocket: ws://${HOST}:${PORT}`);
  console.log(`🔐 認証方式: Claude CLI (claude login)`);
  console.log(`💰 課金: Max 20x Plan (API料金なし)`);
  console.log(`⚙️  実行方式: Interactive session with history`);
  console.log(`🧠 履歴管理: Claude Code自動管理・圧縮`);
  console.log(`🔧 Tool権限: WebSearch, File operations有効`);
  console.log('='.repeat(60));
  console.log('');
  console.log('利用可能なエンドポイント:');
  console.log(`  GET  /health       - ヘルスチェック`);
  console.log(`  GET  /api/info     - 情報取得`);
  console.log(`  WS   /             - WebSocket (セッション管理)`);
  console.log('='.repeat(60));
});
