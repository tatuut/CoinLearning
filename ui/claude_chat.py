"""
Claude Code チャットインターフェース

Streamlitを使用したClaude Codeとの対話インターフェース
- チャット履歴の保存
- REST API経由でClaude Codeと通信
- Max 20x Plan（API料金なし）
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict

# ページ設定
st.set_page_config(
    page_title="Claude Code Chat",
    page_icon="🤖",
    layout="wide"
)

# サーバー設定（デフォルト）
DEFAULT_SERVER_URL = "http://localhost:3003"

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

if "server_url" not in st.session_state:
    st.session_state.server_url = DEFAULT_SERVER_URL

# サイドバー
with st.sidebar:
    st.title("⚙️ 設定")

    # サーバーURL設定
    server_url = st.text_input(
        "サーバーURL",
        value=st.session_state.server_url,
        help="Claude CLI ServerのURL"
    )
    st.session_state.server_url = server_url

    # ヘルスチェック
    if st.button("🔍 接続テスト"):
        try:
            response = requests.get(f"{server_url}/health", timeout=5)
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
            response = requests.get(f"{server_url}/api/info", timeout=5)
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
st.caption("Claude Plan Max (Max 20x) - API料金なし")

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
        with st.spinner("🤔 Claude Code が考え中..."):
            try:
                # REST APIリクエスト
                response = requests.post(
                    f"{st.session_state.server_url}/api/query",
                    json={"prompt": prompt},
                    timeout=120  # 2分タイムアウト
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_response = data.get("response", "")

                    # アシスタントメッセージ表示
                    st.markdown(assistant_response)

                    # 課金情報表示
                    if "billing" in data:
                        billing = data["billing"]
                        st.caption(f"💰 課金: ${billing['total_cost_usd']} ({billing['note']})")

                    # タイムスタンプ
                    response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.caption(f"🕐 {response_timestamp}")

                    # アシスタントメッセージを履歴に追加
                    assistant_message = {
                        "role": "assistant",
                        "content": assistant_response,
                        "timestamp": response_timestamp
                    }
                    st.session_state.messages.append(assistant_message)

                else:
                    error_msg = f"❌ エラー: {response.status_code}\n\n{response.text}"
                    st.error(error_msg)

                    # エラーメッセージも履歴に追加
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

# フッター
st.divider()
st.caption("🚀 Powered by Claude Code (Claude Plan Max)")
