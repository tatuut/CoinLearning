import { spawn } from 'child_process';
import { randomUUID } from 'crypto';

const sessionId = randomUUID();
const prompt = "こんにちは！簡単な挨拶をしてください。";

const args = [
  '--print',
  '--output-format', 'text',
  '--session-id', sessionId,
  '--allowed-tools', 'WebSearch Read Write Edit Bash Glob Grep'
];

console.log(`[Test] Command: claude ${args.join(' ')}`);
console.log(`[Test] Prompt: ${prompt}\n`);

const claude = spawn('claude', args, {
  cwd: process.cwd(),
  shell: true,
  stdio: ['pipe', 'pipe', 'pipe']
});

// プロンプトをstdinに書き込む
claude.stdin.write(prompt + '\n');
claude.stdin.end();

let stdout_data = '';
let stderr_data = '';

claude.stdout.on('data', (chunk) => {
  const text = chunk.toString();
  stdout_data += text;
  console.log('[STDOUT]', text);
});

claude.stderr.on('data', (chunk) => {
  const text = chunk.toString();
  stderr_data += text;
  console.log('[STDERR]', text);
});

claude.on('close', (code) => {
  console.log(`\n[CLOSE] Exit code: ${code}`);
  console.log(`[STDOUT Total] ${stdout_data.length} chars`);
  console.log(`[STDERR Total] ${stderr_data.length} chars`);

  if (stdout_data) {
    console.log('\n=== STDOUT ===');
    console.log(stdout_data);
  }

  if (stderr_data) {
    console.log('\n=== STDERR ===');
    console.log(stderr_data);
  }
});

claude.on('error', (error) => {
  console.error('[ERROR]', error);
});
