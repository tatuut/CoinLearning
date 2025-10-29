import { spawn } from 'child_process';
import { randomUUID } from 'crypto';

const sessionId = randomUUID();

console.log(`[Test] Session ID: ${sessionId}\n`);

// 最初のクエリ（セッション作成）
console.log("=".repeat(60));
console.log("[Query 1] Creating new session");
console.log("=".repeat(60));

const prompt1 = "こんにちは！簡単な挨拶をしてください。";
const args1 = [
  '--print',
  '--output-format', 'text',
  '--session-id', sessionId,
  '--allowed-tools', 'WebSearch Read Write Edit Bash Glob Grep'
];

const claude1 = spawn('claude', args1, {
  cwd: process.cwd(),
  shell: true,
  stdio: ['pipe', 'pipe', 'pipe']
});

claude1.stdin.write(prompt1 + '\n');
claude1.stdin.end();

let stdout1 = '';
claude1.stdout.on('data', (chunk) => {
  stdout1 += chunk.toString();
  process.stdout.write(chunk);
});

claude1.stderr.on('data', (chunk) => {
  console.error('[STDERR 1]', chunk.toString());
});

claude1.on('close', async (code1) => {
  console.log(`\n[Close 1] Exit code: ${code1}\n`);

  if (code1 !== 0) {
    console.error('[FAIL] First query failed');
    process.exit(1);
  }

  // 2秒待つ
  await new Promise(resolve => setTimeout(resolve, 2000));

  // 2番目のクエリ（--resumeを使用）
  console.log("=".repeat(60));
  console.log("[Query 2] Resuming session with --resume");
  console.log("=".repeat(60));

  const prompt2 = "最初に何と言いましたか？";
  const args2 = [
    '--print',
    '--output-format', 'text',
    '--resume', sessionId,
    '--allowed-tools', 'WebSearch Read Write Edit Bash Glob Grep'
  ];

  console.log(`[Command] claude ${args2.join(' ')}\n`);

  const claude2 = spawn('claude', args2, {
    cwd: process.cwd(),
    shell: true,
    stdio: ['pipe', 'pipe', 'pipe']
  });

  claude2.stdin.write(prompt2 + '\n');
  claude2.stdin.end();

  let stdout2 = '';
  claude2.stdout.on('data', (chunk) => {
    stdout2 += chunk.toString();
    process.stdout.write(chunk);
  });

  claude2.stderr.on('data', (chunk) => {
    console.error('[STDERR 2]', chunk.toString());
  });

  claude2.on('close', (code2) => {
    console.log(`\n[Close 2] Exit code: ${code2}\n`);

    if (code2 === 0) {
      console.log("=" * 60);
      console.log("[SUCCESS] Resume test passed!");
      if (stdout2.includes('こんにちは') || stdout2.includes('挨拶')) {
        console.log("[✓] Session history preserved!");
      }
    } else {
      console.error("[FAIL] Second query failed");
      process.exit(1);
    }
  });
});
