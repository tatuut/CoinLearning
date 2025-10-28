#!/usr/bin/env python3
"""
Claude Agent SDK Client - CLI Interface

WebSocket経由でバックエンドサーバーと通信し、
Claude Codeとインタラクティブに対話します。
"""

import asyncio
import json
import sys
import websockets
from datetime import datetime
from typing import Optional
import argparse


class ClaudeClient:
    """Claude Agent SDK クライアント"""

    def __init__(self, server_url: str = "ws://localhost:3000"):
        self.server_url = server_url
        self.connection_id: Optional[str] = None

    async def connect(self):
        """サーバーに接続"""
        print(f"🔌 サーバーに接続中: {self.server_url}")
        try:
            self.ws = await websockets.connect(self.server_url)

            # 接続成功メッセージを受信
            welcome = await self.ws.recv()
            data = json.loads(welcome)

            if data.get('type') == 'connected':
                self.connection_id = data.get('connectionId')
                print(f"✅ 接続成功! (ID: {self.connection_id})")
                return True

        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            return False

    async def query(self, prompt: str, options: dict = None):
        """
        Claudeにクエリを送信してストリーミング応答を受信

        Args:
            prompt: プロンプト文字列
            options: クエリオプション（model, maxTurns等）
        """
        if not self.ws:
            print("❌ サーバーに接続していません")
            return

        # クエリメッセージ送信
        message = {
            "type": "query",
            "prompt": prompt,
            "options": options or {}
        }

        print(f"\n{'='*60}")
        print(f"📤 送信: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"{'='*60}\n")

        await self.ws.send(json.dumps(message))

        # ストリーミング応答を受信
        try:
            async for raw_message in self.ws:
                data = json.loads(raw_message)
                await self._handle_message(data)

                # 完了またはエラーで終了
                if data.get('type') in ['query_complete', 'error']:
                    break

        except websockets.exceptions.ConnectionClosed:
            print("\n❌ 接続が切断されました")

    async def _handle_message(self, data: dict):
        """受信メッセージを処理"""
        msg_type = data.get('type')

        if msg_type == 'query_start':
            print("🚀 Claude処理開始...")
            print()

        elif msg_type == 'message':
            # SDKメッセージを表示
            sdk_msg = data.get('data', {})
            self._display_sdk_message(sdk_msg)

        elif msg_type == 'query_complete':
            print(f"\n{'='*60}")
            print("✅ 処理完了")
            print(f"{'='*60}")

        elif msg_type == 'error':
            print(f"\n❌ エラー: {data.get('error')}")
            if data.get('stack'):
                print(f"\nスタックトレース:\n{data.get('stack')}")

    def _display_sdk_message(self, msg: dict):
        """SDKメッセージを見やすく表示"""
        role = msg.get('role', 'unknown')
        content = msg.get('content', [])

        if role == 'assistant':
            print("🤖 Claude:")
            for block in content:
                if block.get('type') == 'text':
                    print(f"  {block.get('text', '')}")
                elif block.get('type') == 'tool_use':
                    tool_name = block.get('name', 'unknown')
                    print(f"  🔧 ツール使用: {tool_name}")
                    print(f"     入力: {json.dumps(block.get('input', {}), indent=2, ensure_ascii=False)}")

        elif role == 'user':
            print("👤 あなた:")
            for block in content:
                if block.get('type') == 'text':
                    print(f"  {block.get('text', '')}")

        elif role == 'tool':
            print("🔧 ツール結果:")
            for block in content:
                if block.get('type') == 'tool_result':
                    print(f"  {block.get('content', '')}")

        print()

    async def interactive_mode(self):
        """インタラクティブモード"""
        print("\n" + "="*60)
        print("💬 インタラクティブモード")
        print("="*60)
        print("プロンプトを入力してEnterで送信")
        print("'exit' または 'quit' で終了")
        print("="*60 + "\n")

        while True:
            try:
                # プロンプト入力
                prompt = input("👤 あなた: ").strip()

                if not prompt:
                    continue

                if prompt.lower() in ['exit', 'quit', 'q']:
                    print("👋 終了します")
                    break

                # クエリ実行
                await self.query(prompt)

            except KeyboardInterrupt:
                print("\n\n👋 中断されました")
                break
            except EOFError:
                break

    async def close(self):
        """接続を閉じる"""
        if self.ws:
            await self.ws.close()
            print("🔌 接続を切断しました")


async def main():
    parser = argparse.ArgumentParser(
        description='Claude Agent SDK Client - サーバー経由でClaude Codeと対話',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # インタラクティブモード
  python claude_client.py

  # サーバーURL指定
  python claude_client.py --server ws://localhost:3000

  # ワンショットクエリ
  python claude_client.py --prompt "Pythonでフィボナッチ数列を実装して"

  # オプション付きクエリ
  python claude_client.py --prompt "コードをレビューして" --max-turns 5
        """
    )

    parser.add_argument(
        '--server',
        default='ws://localhost:3000',
        help='サーバーURL (デフォルト: ws://localhost:3000)'
    )
    parser.add_argument(
        '--prompt', '-p',
        help='ワンショットクエリ（指定しない場合はインタラクティブモード）'
    )
    parser.add_argument(
        '--model',
        help='使用するClaudeモデル'
    )
    parser.add_argument(
        '--max-turns',
        type=int,
        help='最大ターン数'
    )

    args = parser.parse_args()

    # クライアント作成
    client = ClaudeClient(server_url=args.server)

    # サーバー接続
    if not await client.connect():
        sys.exit(1)

    try:
        # オプション構築
        options = {}
        if args.model:
            options['model'] = args.model
        if args.max_turns:
            options['maxTurns'] = args.max_turns

        # ワンショットモード or インタラクティブモード
        if args.prompt:
            # ワンショットクエリ
            await client.query(args.prompt, options)
        else:
            # インタラクティブモード
            await client.interactive_mode()

    finally:
        await client.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 終了")
        sys.exit(0)
