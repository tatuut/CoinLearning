"""
Parquet閲覧WebUI（Streamlit）

インタラクティブなダッシュボードでparquetデータを可視化
"""

import sys
import os
# ルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from src.data.timeseries_storage import TimeSeriesStorage


# ページ設定
st.set_page_config(
    page_title="仮想通貨データダッシュボード",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def get_storage():
    """TimeSeriesStorageインスタンス取得（キャッシュ）"""
    return TimeSeriesStorage()


def get_available_files():
    """利用可能なparquetファイル一覧"""
    storage = get_storage()
    info = storage.get_storage_info()

    files = []
    for item in info['prices']:
        # ファイル名から銘柄と時間足を抽出
        # 例: BTC_1d.parquet → symbol=BTC, interval=1d
        name = item['file'].replace('.parquet', '')
        parts = name.split('_')
        if len(parts) == 2:
            symbol, interval = parts
            files.append({
                'symbol': symbol,
                'interval': interval,
                'rows': item['rows'],
                'size_kb': item['size_kb']
            })

    return files


def load_data(symbol: str, interval: str):
    """データ読み込み（キャッシュ）"""
    storage = get_storage()
    return storage.load_price_data(symbol, interval)


def calculate_indicators(df, storage):
    """テクニカル指標計算"""
    if df.empty:
        return df

    # RSI
    df['RSI'] = storage.calculate_rsi(df, period=14)

    # MACD
    macd, signal, hist = storage.calculate_macd(df)
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = hist

    # Bollinger Bands
    bb_mid, bb_upper, bb_lower = storage.calculate_bollinger_bands(df)
    df['BB_Mid'] = bb_mid
    df['BB_Upper'] = bb_upper
    df['BB_Lower'] = bb_lower

    # 移動平均線
    df['SMA_20'] = storage.calculate_moving_average(df, window=20)
    df['SMA_50'] = storage.calculate_moving_average(df, window=50)
    df['EMA_20'] = storage.calculate_ema(df, span=20)

    return df


def plot_candlestick_chart(df, symbol, interval):
    """ローソク足チャート + Bollinger Bands + 移動平均線"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(
            f'{symbol} - {interval} ローソク足チャート',
            'RSI',
            'MACD'
        )
    )

    # ローソク足
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='価格'
        ),
        row=1, col=1
    )

    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                  line=dict(color='rgba(250, 128, 114, 0.5)', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Mid'], name='BB Mid',
                  line=dict(color='orange', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                  line=dict(color='rgba(250, 128, 114, 0.5)', width=1),
                  fill='tonexty'),
        row=1, col=1
    )

    # 移動平均線
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_20'], name='SMA(20)',
                  line=dict(color='blue', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_50'], name='SMA(50)',
                  line=dict(color='green', width=1)),
        row=1, col=1
    )

    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
        row=2, col=1
    )
    # RSIの基準線
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # MACD
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='orange')),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df['MACD_Hist'], name='Histogram'),
        row=3, col=1
    )

    # レイアウト
    fig.update_layout(
        height=900,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )

    fig.update_yaxes(title_text="価格 ($)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)

    return fig


def show_statistics(df, symbol):
    """統計情報表示"""
    st.subheader("📊 統計情報")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("現在価格", f"${df['close'].iloc[-1]:,.2f}")
        st.metric("平均価格", f"${df['close'].mean():,.2f}")

    with col2:
        st.metric("期間最高", f"${df['high'].max():,.2f}")
        st.metric("期間最安", f"${df['low'].min():,.2f}")

    with col3:
        returns = df['close'].pct_change()
        st.metric("平均リターン", f"{returns.mean()*100:.2f}%")
        st.metric("標準偏差", f"{returns.std()*100:.2f}%")

    with col4:
        rsi = df['RSI'].iloc[-1]
        st.metric("RSI(14)", f"{rsi:.2f}")

        if rsi > 70:
            st.warning("⚠️ 買われすぎ")
        elif rsi < 30:
            st.success("✅ 売られすぎ")
        else:
            st.info("ℹ️ 中立")


def show_news(symbol):
    """ニュース一覧表示"""
    st.subheader("📰 保存されたニュース")

    news_dir = Path(f'data/news/{symbol}')

    if not news_dir.exists():
        st.info(f"{symbol}のニュースはまだ保存されていません")
        return

    news_files = sorted(news_dir.glob('*.md'), reverse=True)

    if not news_files:
        st.info(f"{symbol}のニュースはまだ保存されていません")
        return

    st.write(f"保存件数: {len(news_files)}件")

    # 最新5件を表示
    for i, filepath in enumerate(news_files[:5]):
        with st.expander(f"📄 {filepath.stem}", expanded=(i == 0)):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                st.markdown(content)


def main():
    st.title("📊 仮想通貨データダッシュボード")
    st.markdown("---")

    # サイドバー
    st.sidebar.header("⚙️ 設定")

    # 利用可能なファイル取得
    files = get_available_files()

    if not files:
        st.error("❌ Parquetファイルが見つかりません")
        st.info("""
        データを収集してください:
        ```bash
        python crypto_analyst.py BTC
        ```
        """)
        return

    # 銘柄選択
    symbols = sorted(set([f['symbol'] for f in files]))
    selected_symbol = st.sidebar.selectbox("銘柄", symbols)

    # 時間足選択
    intervals = sorted(set([f['interval'] for f in files if f['symbol'] == selected_symbol]))
    selected_interval = st.sidebar.selectbox("時間足", intervals)

    # 表示期間
    limit = st.sidebar.slider("表示期間（直近N件）", 10, 500, 100)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ 情報")
    for f in files:
        if f['symbol'] == selected_symbol and f['interval'] == selected_interval:
            st.sidebar.write(f"データ数: {f['rows']:,}行")
            st.sidebar.write(f"サイズ: {f['size_kb']}KB")

    # データ読み込み
    storage = get_storage()
    df = load_data(selected_symbol, selected_interval)

    if df.empty:
        st.error(f"❌ {selected_symbol}_{selected_interval} のデータが読み込めません")
        return

    # 直近N件に制限
    df = df.tail(limit)

    # テクニカル指標計算
    df = calculate_indicators(df, storage)

    # 統計情報
    show_statistics(df, selected_symbol)

    st.markdown("---")

    # チャート表示
    fig = plot_candlestick_chart(df, selected_symbol, selected_interval)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # データテーブル
    with st.expander("📋 データテーブル", expanded=False):
        st.dataframe(
            df[['open', 'high', 'low', 'close', 'volume', 'RSI', 'MACD']].tail(20),
            use_container_width=True
        )

    st.markdown("---")

    # ニュース表示
    show_news(selected_symbol)

    st.markdown("---")
    st.caption("Powered by Streamlit | Data: Parquet Files")


if __name__ == '__main__':
    main()
