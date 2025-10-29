"""
Claude Code チャットインターフェース

Streamlitを使用したClaude Codeとの対話インターフェース
- チャット履歴の保存
- REST API / WebSocket 切り替え可能
- Max 20x Plan（API料金なし）
"""

import streamlit as st
import requests
import json
import asyncio
import websockets
from datetime import datetime
from typing import List, Dict
import threading

# ページ設定
st.set_page_config(
    page_title="Claude Code Chat",
    page_icon="🤖",
    layout="wide"
)

# サーバー設定（デフォルト）
DEFAULT_SERVER_URL = "http://localhost:37281"
DEFAULT_WS_URL = "ws://localhost:37281"

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

if "server_url" not in st.session_state:
    st.session_state.server_url = DEFAULT_SERVER_URL

if "ws_url" not in st.session_state:
    st.session_state.ws_url = DEFAULT_WS_URL

if "connection_mode" not in st.session_state:
    st.session_state.connection_mode = "REST API"

# WebSocket接続関数
async def websocket_query(ws_url: str, prompt: str, placeholder):
    """WebSocketでクエリを送信し、ストリーミング応答を受信"""
    full_response = ""

    try:
        async with websockets.connect(ws_url) as websocket:
            # 接続確認メッセージを受信
            connected_msg = await websocket.recv()
            connected_data = json.loads(connected_msg)

            if connected_data.get("type") != "connected":
                return None, f"接続エラー: {connected_data}"

            # クエリ送信
            await websocket.send(json.dumps({
                "type": "query",
                "prompt": prompt
            }))

            # ストリーミング応答を受信
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if data.get("type") == "message":
                        event = data.get("event", {})
                        if event.get("type") == "assistant_message":
                            text = event.get("text", "")
                            full_response += text
                            # リアルタイム更新
                            placeholder.markdown(full_response + "▌")

                    elif data.get("type") == "query_complete":
                        # 完了
                        placeholder.markdown(full_response)
                        break

                    elif data.get("type") == "error":
                        error_msg = data.get("error", "Unknown error")
                        return None, f"エラー: {error_msg}"

                except websockets.exceptions.ConnectionClosed:
                    break

            return full_response, None

    except Exception as e:
        return None, f"WebSocket接続エラー: {str(e)}"

def run_websocket_query(ws_url: str, prompt: str, placeholder):
    """同期的にWebSocketクエリを実行"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(websocket_query(ws_url, prompt, placeholder))
        return result
    finally:
        loop.close()

# サイドバー
with st.sidebar:
    st.title("⚙️ 設定")

    # 接続モード選択
    st.subheader("🔌 接続モード")
    connection_mode = st.radio(
        "接続方式を選択",
        ["REST API", "WebSocket"],
        index=0 if st.session_state.connection_mode == "REST API" else 1,
        help="REST API: 応答完了後に一括表示\nWebSocket: リアルタイムストリーミング表示"
    )
    st.session_state.connection_mode = connection_mode

    if connection_mode == "REST API":
        st.info("📦 REST API モード\n\n応答が完了してから一括で表示されます。")
    else:
        st.info("⚡ WebSocket モード\n\nリアルタイムでストリーミング表示されます。")

    st.divider()

    # サーバーURL設定
    if connection_mode == "REST API":
        server_url = st.text_input(
            "サーバーURL",
            value=st.session_state.server_url,
            help="Claude CLI ServerのURL"
        )
        st.session_state.server_url = server_url
    else:
        ws_url = st.text_input(
            "WebSocket URL",
            value=st.session_state.ws_url,
            help="Claude CLI ServerのWebSocket URL"
        )
        st.session_state.ws_url = ws_url

    # ヘルスチェック
    if st.button("🔍 接続テスト"):
        try:
            response = requests.get(f"{st.session_state.server_url.replace('ws://', 'http://')}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.success("✅ 接続成功!")
                st.json(data)
            else:
                st.error(f"❌ 接続失敗: {response.status_code}")
        except Exception as e:
            st.error(f"❌ エラー: {str(e)}")

    # サーバー情報
    if st.button("ℹ️ サーバー情報"):
        try:
            response = requests.get(f"{st.session_state.server_url.replace('ws://', 'http://')}/api/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.json(data)
            else:
                st.error(f"❌ 取得失敗: {response.status_code}")
        except Exception as e:
            st.error(f"❌ エラー: {str(e)}")

    st.divider()

    # 履歴管理
    st.subheader("📝 履歴管理")

    # メッセージ数表示
    st.info(f"メッセージ数: {len(st.session_state.messages)}")

    # 履歴クリア
    if st.button("🗑️ 履歴をクリア", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    # 履歴をJSONとしてダウンロード
    if st.session_state.messages:
        history_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
        st.download_button(
            label="💾 履歴をダウンロード",
            data=history_json,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# メインエリア
st.title("🤖 Claude Code Chat")
mode_emoji = "📦" if st.session_state.connection_mode == "REST API" else "⚡"
st.caption(f"{mode_emoji} {st.session_state.connection_mode} モード | Claude Plan Max (Max 20x) - API料金なし")

# チャット履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # タイムスタンプ表示（小さく）
        if "timestamp" in message:
            st.caption(f"🕐 {message['timestamp']}")

# ユーザー入力
if prompt := st.chat_input("メッセージを入力..."):
    # ユーザーメッセージを履歴に追加
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    }
    st.session_state.messages.append(user_message)

    # ユーザーメッセージ表示
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"🕐 {timestamp}")

    # アシスタント応答取得
    with st.chat_message("assistant"):
        # 接続モードに応じて処理を分岐
        if st.session_state.connection_mode == "REST API":
            # REST APIモード
            with st.spinner("🤔 Claude Code が考え中..."):
                try:
                    response = requests.post(
                        f"{st.session_state.server_url}/api/query",
                        json={"prompt": prompt},
                        timeout=120
                    )

                    if response.status_code == 200:
                        data = response.json()
                        assistant_response = data.get("response", "")

                        st.markdown(assistant_response)

                        if "billing" in data:
                            billing = data["billing"]
                            st.caption(f"💰 課金: ${billing['total_cost_usd']} ({billing['note']})")

                        response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.caption(f"🕐 {response_timestamp}")

                        assistant_message = {
                            "role": "assistant",
                            "content": assistant_response,
                            "timestamp": response_timestamp
                        }
                        st.session_state.messages.append(assistant_message)

                    else:
                        error_msg = f"❌ エラー: {response.status_code}\n\n{response.text}"
                        st.error(error_msg)

                        error_message = {
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.messages.append(error_message)

                except requests.exceptions.Timeout:
                    timeout_msg = "⏱️ タイムアウト: サーバーからの応答がありません（120秒）"
                    st.error(timeout_msg)

                    error_message = {
                        "role": "assistant",
                        "content": timeout_msg,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.messages.append(error_message)

                except Exception as e:
                    error_msg = f"❌ エラーが発生しました:\n\n```\n{str(e)}\n```"
                    st.error(error_msg)

                    error_message = {
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.messages.append(error_message)

        else:
            # WebSocketモード
            placeholder = st.empty()
            placeholder.markdown("⚡ 接続中...")

            try:
                result, error = run_websocket_query(st.session_state.ws_url, prompt, placeholder)

                if error:
                    st.error(error)
                    error_message = {
                        "role": "assistant",
                        "content": error,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.messages.append(error_message)
                else:
                    st.caption("💰 課金: $0.00 (Max 20x Plan)")
                    response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.caption(f"🕐 {response_timestamp}")

                    assistant_message = {
                        "role": "assistant",
                        "content": result,
                        "timestamp": response_timestamp
                    }
                    st.session_state.messages.append(assistant_message)

            except Exception as e:
                error_msg = f"❌ WebSocketエラー:\n\n```\n{str(e)}\n```"
                st.error(error_msg)

                error_message = {
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.messages.append(error_message)

# フッター
st.divider()
st.caption("🚀 Powered by Claude Code (Claude Plan Max)")
