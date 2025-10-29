"""
WebSocketサーバーのテストスクリプト
"""
import asyncio
import websockets
import json
import sys
import io

# Windows環境でUnicode出力を正しく扱う
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_websocket():
    uri = "ws://localhost:37281"

    try:
        async with websockets.connect(uri) as websocket:
            print("OK WebSocket接続成功")

            # 接続メッセージを受信
            connected_msg = await websocket.recv()
            connected_data = json.loads(connected_msg)
            print(f"[MSG] 接続メッセージ: {json.dumps(connected_data, ensure_ascii=False, indent=2)}")

            # クエリ送信
            query = {
                "type": "query",
                "prompt": "こんにちは！簡単な挨拶をしてください。"
            }
            print(f"\n[SEND] クエリ送信: {query['prompt']}")
            await websocket.send(json.dumps(query))

            # 応答を受信
            response_count = 0
            full_response = ""

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    response_count += 1

                    print(f"\n[RECV] 応答 #{response_count}:")
                    print(f"  Type: {data.get('type')}")

                    if data.get("type") == "message":
                        event = data.get("event", {})
                        text = event.get("text", "")
                        full_response += text
                        print(f"  Text: {text}")

                    elif data.get("type") == "query_complete":
                        print("\n[OK] クエリ完了")
                        break

                    elif data.get("type") == "error":
                        error_msg = data.get("error", "Unknown error")
                        print(f"\n[ERROR] エラー: {error_msg}")
                        return False

                    elif data.get("type") == "session_closed":
                        print(f"\n[WARN] セッション終了: code {data.get('code')}")
                        break

                except asyncio.TimeoutError:
                    print("\n[TIMEOUT] タイムアウト（30秒）")
                    break

            print(f"\n[RESPONSE] 完全な応答:\n{full_response}")
            print(f"\n[SUCCESS] テスト成功! (応答数: {response_count})")
            return True

    except Exception as e:
        print(f"\n[ERROR] エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    exit(0 if success else 1)
