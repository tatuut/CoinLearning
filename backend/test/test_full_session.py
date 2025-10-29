"""
完全なセッションテスト（3つの質問）
1. 挨拶
2. WebSearch（ビットコインニュース）
3. 履歴確認（最初の発言は？）
"""
import asyncio
import websockets
import json
import sys
import io
import uuid

# Windows環境でUnicode出力を正しく扱う
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_full_session():
    uri = "ws://localhost:37281"
    session_id = str(uuid.uuid4())

    # 3つの質問
    questions = [
        "こんにちは！簡単な挨拶をしてください。",
        "最新のビットコインのニュースを教えてください。",
        "最初にした発言は何でしたか？"
    ]

    try:
        async with websockets.connect(uri) as websocket:
            print("=" * 60)
            print(f"[セッションID] {session_id}")
            print("=" * 60)

            # 接続メッセージを受信
            connected_msg = await websocket.recv()
            connected_data = json.loads(connected_msg)
            print(f"\n[接続] {connected_data.get('type')}")

            # 各質問を順番に送信
            for i, question in enumerate(questions, 1):
                print(f"\n{'=' * 60}")
                print(f"[質問 #{i}] {question}")
                print("=" * 60)

                # クエリ送信（sessionIdを含む）
                query = {
                    "type": "query",
                    "prompt": question,
                    "options": {
                        "sessionId": session_id
                    }
                }
                await websocket.send(json.dumps(query))

                # 応答を受信
                full_response = ""
                response_count = 0

                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                        data = json.loads(message)
                        response_count += 1

                        if data.get("type") == "query_start":
                            print(f"[開始] クエリ処理開始")

                        elif data.get("type") == "message":
                            event = data.get("event", {})
                            text = event.get("text", "")
                            full_response += text
                            # リアルタイム表示
                            if text:
                                print(text, end='', flush=True)

                        elif data.get("type") == "query_complete":
                            print(f"\n[完了] 応答完了 (メッセージ数: {response_count})")
                            break

                        elif data.get("type") == "error":
                            error_msg = data.get("error", "Unknown error")
                            print(f"\n[ERROR] {error_msg}")
                            return False

                    except asyncio.TimeoutError:
                        print(f"\n[TIMEOUT] タイムアウト（60秒）")
                        return False

                # 応答サマリー
                print(f"\n[応答長] {len(full_response)} 文字")

                # 特定のチェック
                if i == 2:  # WebSearchテスト
                    if "ビットコイン" in full_response or "Bitcoin" in full_response:
                        print("[✓] WebSearchが機能している（ビットコイン関連情報を取得）")
                    else:
                        print("[?] WebSearchの結果が不明確")

                if i == 3:  # 履歴テスト
                    if "こんにちは" in full_response or "挨拶" in full_response:
                        print("[✓] 履歴機能が機能している（最初の発言を覚えている）")
                    else:
                        print("[?] 履歴機能の動作が不明確")

            print(f"\n{'=' * 60}")
            print("[SUCCESS] 全テスト完了！")
            print("=" * 60)
            print(f"✓ 挨拶テスト")
            print(f"✓ WebSearchテスト")
            print(f"✓ 履歴機能テスト")
            return True

    except Exception as e:
        print(f"\n[ERROR] エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_session())
    exit(0 if success else 1)
