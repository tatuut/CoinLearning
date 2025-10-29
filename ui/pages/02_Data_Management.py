"""
データ管理ページ

1分足データの取得・管理機能
- 初回全取得
- 差分更新
- データサマリー表示
"""

import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import subprocess
import threading
import queue

# プロジェクトルートをパスに追加
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sample.data.minute_data_collector import MinuteDataCollector
from sample.data.timeseries_storage import TimeSeriesStorage

# ページ設定
st.set_page_config(
    page_title="Data Management",
    page_icon="📊",
    layout="wide"
)

# セッション状態の初期化
if "data_collection_running" not in st.session_state:
    st.session_state.data_collection_running = False

if "collection_output" not in st.session_state:
    st.session_state.collection_output = []


def run_data_collection(symbols: list, days: int = None):
    """
    データ収集をバックグラウンドで実行

    Args:
        symbols: 通貨シンボルリスト
        days: 初回取得日数
    """
    collector = MinuteDataCollector()

    # 進捗を格納
    results = collector.collect_multiple_symbols(symbols, days=days)

    st.session_state.data_collection_running = False
    st.session_state.collection_output.append("✅ データ収集完了！")

    return results


# タイトル
st.title("📊 データ管理")
st.caption("1分足データの取得・管理")

# タブ
tab1, tab2, tab3 = st.tabs(["📥 データ取得", "📈 データサマリー", "⚙️ 設定"])

# ==================== タブ1: データ取得 ====================
with tab1:
    st.header("📥 1分足データ取得")

    col1, col2 = st.columns([2, 1])

    with col1:
        # 通貨選択
        available_symbols = ["BTC", "ETH", "SOL", "AVAX", "MATIC", "BNB", "ADA", "DOT", "LINK", "UNI"]

        selected_symbols = st.multiselect(
            "通貨を選択",
            options=available_symbols,
            default=["BTC", "ETH", "SOL"],
            help="複数選択可能"
        )

        # 取得日数
        days = st.number_input(
            "初回取得日数（既存データがある場合は差分更新）",
            min_value=1,
            max_value=365,
            value=7,
            help="初回のみ適用。2回目以降は自動的に差分のみ取得します"
        )

        # 実行ボタン
        if st.button("🚀 データ取得開始", type="primary", disabled=st.session_state.data_collection_running):
            if not selected_symbols:
                st.error("通貨を選択してください")
            else:
                st.session_state.data_collection_running = True
                st.session_state.collection_output = []

                with st.spinner("データ取得中..."):
                    try:
                        # subprocessで実行してエンコーディング問題を回避
                        symbols_str = ','.join(selected_symbols)
                        cmd = [
                            'python',
                            'sample/data/minute_data_collector.py',
                            '--symbols', symbols_str,
                            '--days', str(days)
                        ]

                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='replace',
                            timeout=300,
                            cwd=project_root
                        )

                        if result.returncode == 0:
                            st.success("✅ データ収集完了！")

                            # 結果をパース（簡易版：ファイルから読み込み）
                            storage = TimeSeriesStorage()
                            results = {}
                            for symbol in selected_symbols:
                                try:
                                    df = storage.load_price_data(symbol, '1m')
                                    results[symbol] = len(df) if not df.empty else 0
                                except:
                                    results[symbol] = 0

                            # 結果表示
                            st.subheader("取得結果")
                            result_df = pd.DataFrame([
                                {"通貨": symbol, "取得件数": count}
                                for symbol, count in results.items()
                            ])
                            st.dataframe(result_df, use_container_width=True)

                            # ログ表示
                            with st.expander("実行ログ"):
                                st.code(result.stdout)
                        else:
                            st.error(f"エラーが発生しました（Exit code: {result.returncode}）")
                            st.code(result.stderr)

                        st.session_state.data_collection_running = False

                    except subprocess.TimeoutExpired:
                        st.error("タイムアウト: 5分以上かかりました")
                        st.session_state.data_collection_running = False
                    except Exception as e:
                        st.error(f"エラーが発生しました: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        st.session_state.data_collection_running = False

    with col2:
        st.info("""
**使い方:**

1. 取得したい通貨を選択
2. 初回取得日数を設定
3. 「データ取得開始」をクリック

**初回 vs 差分更新:**
- 初回: 指定日数分を全取得
- 2回目以降: 最終取得時刻以降のみ取得
        """)

    # 進捗ログ
    if st.session_state.collection_output:
        st.subheader("📝 実行ログ")
        for line in st.session_state.collection_output:
            st.text(line)

# ==================== タブ2: データサマリー ====================
with tab2:
    st.header("📈 保存済みデータサマリー")

    # リフレッシュボタン
    if st.button("🔄 更新"):
        st.rerun()

    try:
        storage = TimeSeriesStorage()
        price_dir = storage.price_dir

        # 1分足ファイルを検索
        files = list(price_dir.glob("*_1m.parquet"))

        if not files:
            st.warning("保存済みデータがありません")
        else:
            summary_data = []

            for file in files:
                symbol = file.stem.replace('_1m', '')

                try:
                    df = storage.load_price_data(symbol, '1m')

                    if df.empty:
                        continue

                    first_time = df.index[0]
                    last_time = df.index[-1]
                    count = len(df)
                    days = (last_time - first_time).days
                    file_size = file.stat().st_size / 1024  # KB

                    summary_data.append({
                        "通貨": symbol,
                        "件数": f"{count:,}",
                        "期間": f"{days}日",
                        "開始": first_time.strftime('%Y-%m-%d %H:%M'),
                        "最終": last_time.strftime('%Y-%m-%d %H:%M'),
                        "ファイルサイズ": f"{file_size:.1f} KB"
                    })

                except Exception as e:
                    st.error(f"{symbol}: エラー ({e})")

            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)

                # 統計
                st.subheader("📊 統計")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("通貨数", len(summary_data))

                with col2:
                    total_count = sum(int(item["件数"].replace(',', '')) for item in summary_data)
                    st.metric("総データ件数", f"{total_count:,}")

                with col3:
                    total_size = sum(float(item["ファイルサイズ"].replace(' KB', '')) for item in summary_data)
                    st.metric("総ファイルサイズ", f"{total_size:.1f} KB")

            # チャート表示オプション
            st.subheader("📉 データプレビュー")

            if summary_data:
                preview_symbol = st.selectbox(
                    "通貨を選択",
                    options=[item["通貨"] for item in summary_data]
                )

                if preview_symbol:
                    df = storage.load_price_data(preview_symbol, '1m')

                    if not df.empty:
                        # 最新100件を表示
                        st.write(f"**{preview_symbol}** 最新100件")

                        # データフレームをチャート用に準備
                        chart_data = df['close'].tail(100)

                        if len(chart_data) > 0:
                            st.line_chart(chart_data, height=400)
                        else:
                            st.warning("表示するデータがありません")

                        # 詳細データ
                        with st.expander("詳細データを表示"):
                            st.dataframe(df.tail(100), use_container_width=True)
                    else:
                        st.warning(f"{preview_symbol} のデータがありません")

    except Exception as e:
        st.error(f"エラー: {str(e)}")

# ==================== タブ3: 設定 ====================
with tab3:
    st.header("⚙️ 設定")

    st.subheader("📁 データ保存先")

    storage = TimeSeriesStorage()
    data_dir = storage.data_dir

    st.code(str(data_dir))

    col1, col2 = st.columns(2)

    with col1:
        st.metric("価格データ", len(list(storage.price_dir.glob("*.parquet"))))

    with col2:
        total_size = sum(f.stat().st_size for f in storage.price_dir.glob("*.parquet"))
        st.metric("総容量", f"{total_size / 1024:.1f} KB")

    st.divider()

    st.subheader("🔧 高度な設定")

    # データ削除（危険）
    with st.expander("⚠️ データ削除（危険）"):
        st.warning("この操作は元に戻せません！")

        delete_symbol = st.selectbox(
            "削除する通貨",
            options=[""] + [f.stem.replace('_1m', '') for f in storage.price_dir.glob("*_1m.parquet")]
        )

        if st.button("🗑️ 削除", type="secondary"):
            if delete_symbol:
                file_path = storage.price_dir / f"{delete_symbol}_1m.parquet"
                if file_path.exists():
                    file_path.unlink()
                    st.success(f"✅ {delete_symbol} のデータを削除しました")
                    st.rerun()
            else:
                st.error("通貨を選択してください")

# フッター
st.divider()
st.caption("🚀 Powered by Grass Coin Trader")
