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
from datetime import datetime
from src.data.timeseries_storage import TimeSeriesStorage
from src.config.exchange_api import MEXCAPI
from src.data.advanced_database import AdvancedDatabase


# ページ設定
st.set_page_config(
    page_title="仮想通貨データダッシュボード",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 用語説明の辞書
GLOSSARY = {
    "ローソク足": """
**ローソク足チャート（Candlestick Chart）**

価格の動きを視覚的に表現したチャートです。1本のローソクで以下の4つの価格を表示します：

- **始値（Open）**: その期間の最初の価格
- **高値（High）**: その期間の最高価格
- **安値（Low）**: その期間の最安価格
- **終値（Close）**: その期間の最後の価格

**色の意味**:
- 🟢 緑（または白）: 終値 > 始値（価格が上昇）
- 🔴 赤（または黒）: 終値 < 始値（価格が下落）

長方形の部分を「実体」、上下の細い線を「ヒゲ」と呼びます。
    """,

    "Bollinger Bands": """
**ボリンジャーバンド（Bollinger Bands）**

1980年代にジョン・ボリンジャーが開発した指標です。価格のボラティリティ（変動の激しさ）を視覚化します。

**3本の線**:
- **中央線（BB Mid）**: 20日移動平均線
- **上限線（BB Upper）**: 中央線 + （標準偏差 × 2）
- **下限線（BB Lower）**: 中央線 - （標準偏差 × 2）

**使い方**:
- 価格が上限に近い → ボラティリティが高い、買われすぎの可能性
- 価格が下限に近い → ボラティリティが高い、売られすぎの可能性
- バンドが狭い → 相場が静か、ブレイクアウト（急変動）の前兆かも
- バンドが広い → 相場が激しく動いている

統計学的には、価格の95%がこのバンド内に収まると言われています。
    """,

    "SMA": """
**SMA（Simple Moving Average / 単純移動平均線）**

過去N日間の終値の平均を線で結んだものです。トレンド（方向性）を把握するために使います。

**計算式**: （過去N日の終値の合計）÷ N

**例**: SMA(20) = 過去20日間の平均価格

**使い方**:
- 価格がSMAより上 → 上昇トレンド
- 価格がSMAより下 → 下降トレンド
- 短期SMA（例: 20日）が長期SMA（例: 50日）を上抜け → ゴールデンクロス（買いシグナル）
- 短期SMAが長期SMAを下抜け → デッドクロス（売りシグナル）
    """,

    "RSI": """
**RSI（Relative Strength Index / 相対力指数）**

1978年にJ. Welles Wilder Jr.が開発した指標です。「買われすぎ」「売られすぎ」を0〜100の数値で判断します。

**計算式**: RSI = 100 - (100 / (1 + RS))
- RS = 過去14日間の平均上昇幅 ÷ 平均下落幅

**判断基準**:
- **RSI > 70**: 買われすぎ → 価格が下がるかも（売りを検討）
- **RSI < 30**: 売られすぎ → 価格が上がるかも（買いを検討）
- **RSI = 50付近**: 中立

**注意**: RSIが70以上でもさらに上昇することもあるので、他の指標と組み合わせて判断しましょう。
    """,

    "MACD": """
**MACD（Moving Average Convergence Divergence / 移動平均収束拡散法）**

1970年代にGerald Appelが開発した指標です。トレンドの方向と強さを判断します。

**3つの要素**:
- **MACDライン（青）**: 短期EMA(12) - 長期EMA(26)
- **シグナルライン（オレンジ）**: MACDの9日移動平均
- **ヒストグラム（棒グラフ）**: MACD - シグナル

**使い方**:
- MACDがシグナルを上抜け → 買いシグナル（ゴールデンクロス）
- MACDがシグナルを下抜け → 売りシグナル（デッドクロス）
- ヒストグラムが大きい → トレンドが強い
- ヒストグラムが小さい → トレンドが弱い

**注意**: トレンドがない相場（レンジ相場）ではダマシが多くなります。
    """,

    "現在価格": "その銘柄の最新の取引価格です。リアルタイムで変動します。",

    "平均価格": "表示期間内の全ての終値の平均です。その期間の「平均的な価格水準」を表します。",

    "期間最高": "表示期間内で記録した最も高い価格です。",

    "期間最安": "表示期間内で記録した最も低い価格です。",

    "平均リターン": """
**平均リターン（Average Return）**

1日あたりの平均的な価格変動率（％）です。

**計算式**: （当日終値 - 前日終値）÷ 前日終値 × 100

**例**:
- +2.5% → 平均して1日あたり2.5%上昇
- -1.2% → 平均して1日あたり1.2%下落

**注意**: 過去のデータなので、将来もこの通りになるとは限りません。
    """,

    "標準偏差": """
**標準偏差（Standard Deviation / ボラティリティ）**

価格の「ブレ幅」を表します。リスクの大きさを測る指標です。

**意味**:
- 標準偏差が大きい → 価格の変動が激しい（ハイリスク・ハイリターン）
- 標準偏差が小さい → 価格の変動が穏やか（ローリスク・ローリターン）

**例**:
- 標準偏差 10% → 1日あたり±10%程度の変動
- 標準偏差 2% → 1日あたり±2%程度の変動

仮想通貨は株式よりも標準偏差が大きい（=変動が激しい）傾向があります。
    """,
}


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
    """データ読み込み"""
    storage = get_storage()
    return storage.load_price_data(symbol, interval)


def fetch_latest_data(symbol: str):
    """最新データをAPIから取得してParquetに保存"""
    try:
        api = MEXCAPI()
        storage = get_storage()

        # 1日足データを取得
        klines = api.get_klines(f"{symbol}USDT", interval='1d', limit=30)

        if klines:
            storage.save_price_data(symbol, '1d', klines)
            return True, f"✅ {symbol}の最新データを取得・保存しました（{len(klines)}件）"
        else:
            return False, f"❌ データが取得できませんでした"
    except Exception as e:
        return False, f"❌ エラー: {str(e)}"


def fetch_and_save_news(symbol: str):
    """ニュースを取得してMarkdownで保存"""
    try:
        db = AdvancedDatabase()
        news_dir = Path('data/news')
        news_dir.mkdir(parents=True, exist_ok=True)

        # DBからニュースを取得
        news_list = db.get_recent_news(symbol, limit=10, days=30)

        if not news_list:
            db.close()
            return False, f"❌ {symbol}のニュースが見つかりません（DBに登録されていません）"

        # 銘柄ごとのディレクトリ作成
        symbol_dir = news_dir / symbol
        symbol_dir.mkdir(exist_ok=True)

        saved_count = 0
        for news in news_list:
            # ファイル名作成
            pub_date = news.get('published_date', datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d_%H-%M-%S')
            except:
                date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            news_id = news.get('id', 'unknown')
            filename = f"{date_str}_{news_id}.md"
            filepath = symbol_dir / filename

            # 既に存在する場合はスキップ
            if filepath.exists():
                continue

            # センチメントマッピング
            sentiment_map = {
                'very_positive': '📈 非常にポジティブ',
                'positive': '↗️ ポジティブ',
                'neutral': '➡️ 中立',
                'negative': '↘️ ネガティブ',
                'very_negative': '📉 非常にネガティブ',
            }

            # Markdown作成
            md_content = f"""# {news.get('title', 'タイトルなし')}

**出典**: {news.get('source', 'Unknown')}
**公開日**: {pub_date[:19]}
**URL**: {news.get('url', 'N/A')}

---

## センチメント

{sentiment_map.get(news.get('sentiment', 'neutral'), '➡️ 中立')}

**スコア詳細**:
- 重要度: {news.get('importance_score', 0):.3f}
- 影響力: {news.get('impact_score', 0):.3f}

---

## 本文

{news.get('content', '（本文なし）')}

---

**保存日時**: {datetime.now().isoformat()}
"""

            # ファイル保存
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

            saved_count += 1

        db.close()

        if saved_count > 0:
            return True, f"✅ {saved_count}件のニュースを保存しました"
        else:
            return True, f"ℹ️ 新しいニュースはありませんでした（既に保存済み）"

    except Exception as e:
        return False, f"❌ エラー: {str(e)}"


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
            'RSI（相対力指数）',
            'MACD（移動平均収束拡散法）'
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
        go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper（上限）',
                  line=dict(color='rgba(250, 128, 114, 0.5)', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Mid'], name='BB Mid（中央線）',
                  line=dict(color='orange', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower（下限）',
                  line=dict(color='rgba(250, 128, 114, 0.5)', width=1),
                  fill='tonexty'),
        row=1, col=1
    )

    # 移動平均線
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_20'], name='SMA(20)　20日移動平均',
                  line=dict(color='blue', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_50'], name='SMA(50)　50日移動平均',
                  line=dict(color='green', width=1)),
        row=1, col=1
    )

    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
        row=2, col=1
    )
    # RSIの基準線
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1,
                 annotation_text="買われすぎ（70）")
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1,
                 annotation_text="売られすぎ（30）")

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
        st.metric("現在価格", f"${df['close'].iloc[-1]:,.2f}",
                 help=GLOSSARY["現在価格"])
        st.metric("平均価格", f"${df['close'].mean():,.2f}",
                 help=GLOSSARY["平均価格"])

    with col2:
        st.metric("期間最高", f"${df['high'].max():,.2f}",
                 help=GLOSSARY["期間最高"])
        st.metric("期間最安", f"${df['low'].min():,.2f}",
                 help=GLOSSARY["期間最安"])

    with col3:
        returns = df['close'].pct_change()
        st.metric("平均リターン", f"{returns.mean()*100:.2f}%",
                 help=GLOSSARY["平均リターン"])
        st.metric("標準偏差（ボラティリティ）", f"{returns.std()*100:.2f}%",
                 help=GLOSSARY["標準偏差"])

    with col4:
        rsi = df['RSI'].iloc[-1]
        st.metric("RSI(14)", f"{rsi:.2f}",
                 help=GLOSSARY["RSI"])

        if rsi > 70:
            st.warning("⚠️ 買われすぎ")
        elif rsi < 30:
            st.success("✅ 売られすぎ")
        else:
            st.info("ℹ️ 中立")


def show_news(symbol):
    """ニュース一覧表示"""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📰 保存されたニュース")

    with col2:
        if st.button("🔄 ニュース取得・保存", key="fetch_news"):
            with st.spinner("ニュースを取得中..."):
                success, message = fetch_and_save_news(symbol)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    news_dir = Path(f'data/news/{symbol}')

    if not news_dir.exists():
        st.info(f"{symbol}のニュースはまだ保存されていません。「ニュース取得・保存」ボタンをクリックしてください。")
        return

    news_files = sorted(news_dir.glob('*.md'), reverse=True)

    if not news_files:
        st.info(f"{symbol}のニュースはまだ保存されていません。「ニュース取得・保存」ボタンをクリックしてください。")
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

    # 用語集ボタン
    with st.expander("📖 用語集（わからない言葉をクリック）"):
        glossary_tabs = st.tabs(list(GLOSSARY.keys()))
        for i, (term, explanation) in enumerate(GLOSSARY.items()):
            with glossary_tabs[i]:
                st.markdown(explanation)

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
    selected_symbol = st.sidebar.selectbox("銘柄", symbols,
                                          help="分析したい仮想通貨を選択してください")

    # 時間足選択
    intervals = sorted(set([f['interval'] for f in files if f['symbol'] == selected_symbol]))
    selected_interval = st.sidebar.selectbox("時間足", intervals,
                                            help="1d=1日足、4h=4時間足など")

    # 表示期間
    limit = st.sidebar.slider("表示期間（直近N件）", 10, 500, 100,
                             help="チャートに表示するデータの件数を選択")

    st.sidebar.markdown("---")

    # 更新ボタン
    if st.sidebar.button("🔄 最新データ取得", key="update_data"):
        with st.spinner(f"{selected_symbol}の最新データを取得中..."):
            success, message = fetch_latest_data(selected_symbol)
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)

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

    # チャート説明
    with st.expander("💡 チャートの見方", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**ローソク足**")
            st.markdown(GLOSSARY["ローソク足"])
        with col2:
            st.markdown("**Bollinger Bands**")
            st.markdown(GLOSSARY["Bollinger Bands"])
        with col3:
            st.markdown("**移動平均線（SMA）**")
            st.markdown(GLOSSARY["SMA"])

    # チャート表示
    fig = plot_candlestick_chart(df, selected_symbol, selected_interval)
    st.plotly_chart(fig, width='stretch')

    st.markdown("---")

    # データテーブル
    with st.expander("📋 データテーブル", expanded=False):
        st.dataframe(
            df[['open', 'high', 'low', 'close', 'volume', 'RSI', 'MACD']].tail(20),
            width='stretch'
        )

    st.markdown("---")

    # ニュース表示
    show_news(selected_symbol)

    st.markdown("---")
    st.caption("Powered by Streamlit | Data: Parquet Files")


if __name__ == '__main__':
    main()
