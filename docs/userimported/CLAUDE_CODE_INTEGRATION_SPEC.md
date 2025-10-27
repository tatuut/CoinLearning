# Claude Code統合仕様書

## 概要

ASSOCIATEシステムでは、Anthropic社が提供する`@anthropic-ai/claude-agent-sdk`を使用して、Claude Code機能を統合しています。これはサブプロセス起動ではなく、SDKライブラリによる統合です。

## 関連ファイル

- `backend/services/providers/claude_code/claude_code_builder.js` - メインビルダー
- `backend/services/providers/claude_code/custom_tools.js` - ツール変換層
- `backend/tools/core/agent_caller.js` - エージェント間通信（SDK依存しない）

## 1. Claude Agent SDK統合アーキテクチャ

### 1.1 ClaudeCodeBuilderクラス

**パッケージ**: `@anthropic-ai/claude-agent-sdk`

**主要インポート**:
```javascript
import { query, createSdkMcpServer, tool } from '@anthropic-ai/claude-agent-sdk';
```

### 1.2 メインストリーミング関数

```javascript
async *stream(messages, tools, config, run)
```

**処理フロー**:
1. UnifiedMessageをプロンプトに変換
2. ASSOCIATEツールをSDK MCP Serverに登録
3. Claude Code `query()`実行
4. SDKストリームをUnified SSEに変換

## 2. query()関数の設定仕様

### 2.1 基本設定

```javascript
query({
  prompt: string,              // ユーザーメッセージ
  options: {
    model: string,            // デフォルト: 'claude-sonnet-4-5-20250929'
    maxTurns: number,         // Action Map maxLoopCountと同期
    continue: boolean,        // Phase遷移時の会話継続
    includePartialMessages: true, // ストリーミング有効化
    cwd: string,              // 作業ディレクトリ
    abortController: AbortController
  }
})
```

### 2.2 MCP Server登録

ASSOCIATEの既存ツールをSDK MCPツールとして公開：

```javascript
mcpServers: {
  'associate-tools': {
    type: 'sdk',
    name: 'associate-tools',
    instance: mcpServer.instance
  }
}
```

**createSdkMcpServer()の引数**:
```javascript
{
  name: 'associate-tools',
  version: '1.0.0',
  tools: [...] // getAllAssociateToolsForClaudeCode()の戻り値
}
```

## 3. パーミッションシステム

### 3.1 Permission Mode（Phase別）

```javascript
const phaseMap = {
  'preparation': 'plan',      // 計画のみ（実行しない）
  'execution': 'default',     // ユーザー確認あり
  'finalization': 'acceptEdits' // ファイル編集自動承認
};
```

### 3.2 カスタム許可関数

```javascript
canUseTool: async (toolName, input, opts) => {
  // 1. WebSocket経由でpermission_requestイベント送信
  // 2. Promise作成＆Map保存
  // 3. 30秒タイムアウト待機
  // 4. ユーザー応答 → {behavior: 'allow'/'deny', updatedInput}
}
```

**permission_requestイベント**:
```javascript
{
  type: 'permission_request',
  requestId: string,
  toolName: string,
  toolInput: object,
  timestamp: ISO8601
}
```

**ユーザー応答処理**:
```javascript
handlePermissionResponse(requestId, decision, updatedInput)
```

### 3.3 タイムアウト処理

- デフォルト: 30秒
- タイムアウト時の挙動: `{behavior: 'deny', message: 'Permission request timeout (30s)', interrupt: false}`

## 4. Hooks（イベント配信）

### 4.1 PreToolUse Hook

```javascript
PreToolUse: [async (input, toolUseID) => {
  run.queue.broadcast({
    type: 'tool_start',
    payload: {
      id: toolUseID,
      name: input.tool_name,
      input: input.tool_input
    }
  });
  return { continue: true };
}]
```

### 4.2 PostToolUse Hook

```javascript
PostToolUse: [async (input, toolUseID) => {
  run.queue.broadcast({
    type: 'tool_result',
    payload: {
      id: toolUseID,
      name: input.tool_name,
      result: input.tool_response
    }
  });
  return { continue: true };
}]
```

## 5. ツール変換層（custom_tools.js）

### 5.1 ASSOCIATEツールのラップ

```javascript
function wrapAssociateTool(toolName, session, context, agentConfig) {
  const tool = toolRegistry.get(toolName);

  return async (args) => {
    const result = await tool.executor(args, session, context, agentConfig);

    // エラーチェック＆レスポンス変換
    if (result.isError) {
      return { content: [{ type: 'text', text: result.error }], isError: true };
    }

    return { content: [{ type: 'text', text: contentText }], isError: false };
  };
}
```

### 5.2 Zodスキーマ定義

Claude Code SDKが要求するZodスキーマ形式：

```javascript
import { z } from 'zod';

export const associateToolSchemas = {
  directory_lister: z.object({
    targetPath: z.string().optional().describe('Directory path to list'),
    depth: z.number().optional().describe('Maximum depth for listing'),
    excludePatterns: z.array(z.string()).optional().describe('Patterns to exclude'),
    query: z.string().optional().describe('Search query'),
    searchMode: z.enum(['substring', 'glob', 'regex']).optional().describe('Search mode')
  }),

  file_reader: z.object({
    path: z.string().describe('File path to read'),
    offset: z.number().optional().describe('Start line number'),
    limit: z.number().optional().describe('Number of lines to read')
  }),

  text_edit_tool: z.object({
    path: z.string().describe('File path to edit'),
    edits: z.array(z.object({
      old_text: z.string().describe('Text to replace'),
      new_text: z.string().describe('New text'),
      all_occurrences: z.boolean().optional().describe('Replace all occurrences')
    })).describe('Array of edit operations')
  }),

  agent_caller: z.object({
    target_agent: z.string().describe('Target agent name'),
    message: z.string().describe('Message to send to agent'),
    context: z.record(z.any()).optional().describe('Additional context')
  }),

  datetime: z.object({
    format: z.string().optional().describe('Date format string'),
    timezone: z.string().optional().describe('Timezone')
  }),

  attempt_completion: z.object({
    result: z.string().describe('Completion result'),
    success: z.boolean().optional().describe('Whether completion was successful')
  })
};
```

### 5.3 Claude Code SDKツール作成

```javascript
function createAssociateToolForClaudeCode(
  toolName,
  description,
  schema,
  session,
  context,
  agentConfig
) {
  return {
    name: toolName,
    description,
    inputSchema: schema.shape,
    handler: wrapAssociateTool(toolName, session, context, agentConfig)
  };
}
```

### 5.4 全ツール変換

```javascript
function getAllAssociateToolsForClaudeCode(session, context, agentConfig) {
  const tools = [];

  for (const [toolName, tool] of toolRegistry.entries()) {
    if (associateToolSchemas[toolName]) {
      tools.push(
        createAssociateToolForClaudeCode(
          toolName,
          tool.definition.description || `ASSOCIATE ${toolName} tool`,
          associateToolSchemas[toolName],
          session,
          context,
          agentConfig
        )
      );
    }
  }

  return tools;
}
```

## 6. ストリーミングイベント変換

### 6.1 SDK Message → Unified SSE変換

```javascript
async *convertToUnifiedSSE(sdkMessage, run) {
  switch (sdkMessage.type) {
    case 'stream_event':
      yield* this.handleStreamEvent(sdkMessage);
      break;

    case 'assistant':
      yield* this.handleAssistantMessage(sdkMessage);
      break;

    case 'result':
      yield this.handleResultMessage(sdkMessage);
      break;
  }
}
```

### 6.2 ストリーミングイベント処理

```javascript
async *handleStreamEvent(sdkMessage) {
  const event = sdkMessage.event;

  switch (event.type) {
    case 'content_block_delta':
      if (event.delta.type === 'text_delta') {
        yield {
          type: 'text_delta',
          payload: { text: event.delta.text }
        };
      } else if (event.delta.type === 'input_json_delta') {
        yield {
          type: 'tool_input_delta',
          payload: { partial_json: event.delta.partial_json }
        };
      }
      break;

    case 'message_start':
      yield { type: 'message_start', payload: {} };
      break;

    case 'message_stop':
      yield { type: 'message_stop', payload: {} };
      break;

    case 'content_block_stop':
      yield { type: 'content_block_stop', payload: {} };
      break;
  }
}
```

### 6.3 結果メッセージ処理

```javascript
handleResultMessage(sdkMessage) {
  return {
    type: 'run_complete',
    payload: {
      success: sdkMessage.subtype === 'success',
      duration_ms: sdkMessage.duration_ms,
      num_turns: sdkMessage.num_turns,
      total_cost_usd: 0, // Max 20倍プラン: 料金0円
      usage: {
        input_tokens: sdkMessage.usage?.input_tokens || 0,
        output_tokens: sdkMessage.usage?.output_tokens || 0,
        cache_creation_input_tokens: sdkMessage.usage?.cache_creation_input_tokens || 0,
        cache_read_input_tokens: sdkMessage.usage?.cache_read_input_tokens || 0
      }
    }
  };
}
```

## 7. AbortController統合

### 7.1 中断処理

```javascript
constructor(config) {
  this.abortController = null;
  this.currentQuery = null;
}

async *stream(messages, tools, config, run) {
  this.abortController = new AbortController();

  this.currentQuery = query({
    // ...
    abortController: this.abortController
  });

  try {
    for await (const sdkMessage of this.currentQuery) {
      yield* this.convertToUnifiedSSE(sdkMessage, run);
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      yield { type: 'error', payload: { message: 'Query aborted by user' } };
    } else {
      throw error;
    }
  }
}
```

### 7.2 クリーンアップ

```javascript
cleanup() {
  if (this.abortController) {
    this.abortController.abort();
    this.abortController = null;
  }

  // 未処理の許可リクエストをクリア
  for (const [requestId, request] of this.permissionRequests.entries()) {
    if (request.timeout) clearTimeout(request.timeout);
    request.resolve({
      behavior: 'deny',
      message: 'Provider cleanup',
      interrupt: true
    });
  }
  this.permissionRequests.clear();
}
```

## 8. メッセージ変換

### 8.1 UnifiedMessage → プロンプト

```javascript
convertMessagesToPrompt(messages) {
  const userMessages = messages.filter(m => m.role === 'user');
  if (userMessages.length === 0) return '';

  // 最新のユーザーメッセージを取得
  const latestMessage = userMessages[userMessages.length - 1];
  const textContents = latestMessage.content.filter(c => c.type === 'text');

  return textContents.map(c => c.text).join('\n');
}
```

## 9. 依存パッケージ

```json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^x.x.x",
    "zod": "^3.x.x",
    "uuid": "^9.x.x"
  }
}
```

## 10. 使用例

### 10.1 プロバイダーとして使用

```javascript
const builder = new ClaudeCodeBuilder(config);

for await (const event of builder.stream(messages, tools, config, run)) {
  // Unified SSEイベント処理
  console.log(event.type, event.payload);
}

builder.cleanup();
```

### 10.2 パーミッション応答

```javascript
// WebSocketメッセージハンドラー内
if (message.type === 'permission_response') {
  builder.handlePermissionResponse(
    message.requestId,
    message.decision, // 'allow' or 'deny'
    message.updatedInput
  );
}
```

## 11. 制約事項

1. **料金**: Max 20倍プランのため、常に`total_cost_usd: 0`で返却
2. **MCP Serverタイプ**: SDK MCPのみサポート（Stdio MCPは非対応）
3. **ツール登録**: `associateToolSchemas`に定義されたツールのみSDKに公開
4. **プロンプト変換**: 最新のユーザーメッセージのみをプロンプトとして使用

## 12. 外部持ち出し時の考慮事項

この統合方式を他のプロジェクトで再利用する場合：

1. **パッケージインストール**: `npm install @anthropic-ai/claude-agent-sdk zod uuid`
2. **ツールレジストリ**: 独自のツールレジストリ実装が必要
3. **WebSocket/Queue**: パーミッション＆イベント配信の代替実装が必要
4. **Run管理**: ASSOCIATEの`Run`オブジェクトに相当する実行コンテキスト管理が必要
5. **Unified SSE**: 独自のイベント形式を使用する場合は変換層の調整が必要

---

**最終更新**: 2025-10-27
**対象バージョン**: ASSOCIATE backend (Phase 2実装)
