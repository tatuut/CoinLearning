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
import requests
import time
from src.data.timeseries_storage import TimeSeriesStorage
from src.config.exchange_api import MEXCAPI
from src.data.advanced_database import AdvancedDatabase
from src.analysis.forecasting import ForecastingEngine


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


def show_forecast(df, symbol):
    """ARIMA/GARCH予測を表示"""
    st.subheader("🔮 価格予測（ARIMA/GARCH）")

    with st.expander("💡 予測機能について"):
        st.markdown("""
### ARIMA/GARCH予測とは？

**ARIMA（自己回帰和分移動平均モデル）**:
- 過去の価格データから将来の価格を予測
- 1970年にBox & Jenkinsが開発
- 時系列データの予測に広く使われている

**GARCH（一般化自己回帰条件付き分散不均一モデル）**:
- ボラティリティ（価格変動の激しさ）を予測
- 1982年にRobert Engleが開発（ノーベル経済学賞受賞）
- リスク管理に重要

**注意**: これは過去データに基づく統計モデルです。実際の価格は様々な要因で変動します。
        """)

    if len(df) < 100:
        st.warning("⚠️ 予測には最低100日分のデータが必要です（現在: {len(df)}日分）")
        return

    # 予測実行ボタン
    if st.button("🔮 7日間の価格とリスクを予測", key="run_forecast"):
        with st.spinner("予測計算中...（20-30秒かかります）"):
            engine = ForecastingEngine()

            # 全データを読み込み（予測精度向上のため）
            storage = get_storage()
            full_df = storage.load_price_data(symbol, '1d')

            if len(full_df) >= 100:
                result = engine.combined_forecast(full_df, periods=7)

                # 予測説明
                st.markdown(engine.explain_forecast(result))

                # 予測チャート
                if result['price_forecast']['success']:
                    st.markdown("---")
                    st.markdown("### 📈 価格予測チャート")

                    # 予測値のプロット
                    fig = go.Figure()

                    # 過去30日の実績
                    historical_data = full_df.tail(30)
                    fig.add_trace(go.Scatter(
                        x=historical_data.index,
                        y=historical_data['close'],
                        mode='lines',
                        name='実績価格',
                        line=dict(color='blue', width=2)
                    ))

                    # 予測値
                    forecast_dates = pd.date_range(
                        start=historical_data.index[-1] + pd.Timedelta(days=1),
                        periods=7,
                        freq='D'
                    )
                    forecasts = result['price_forecast']['forecast']

                    fig.add_trace(go.Scatter(
                        x=forecast_dates,
                        y=forecasts,
                        mode='lines+markers',
                        name='予測価格',
                        line=dict(color='red', width=2, dash='dash')
                    ))

                    # 信頼区間
                    if 'conf_int_lower' in result['price_forecast']:
                        fig.add_trace(go.Scatter(
                            x=forecast_dates,
                            y=result['price_forecast']['conf_int_upper'],
                            mode='lines',
                            line=dict(width=0),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast_dates,
                            y=result['price_forecast']['conf_int_lower'],
                            mode='lines',
                            line=dict(width=0),
                            fillcolor='rgba(255, 0, 0, 0.2)',
                            fill='tonexty',
                            name='95%信頼区間',
                            hoverinfo='skip'
                        ))

                    fig.update_layout(
                        title=f'{symbol} 価格予測（7日間）',
                        xaxis_title='日付',
                        yaxis_title='価格 ($)',
                        height=400,
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, width='stretch')

                    # 予測値テーブル
                    st.markdown("### 📋 予測値詳細")
                    forecast_df = pd.DataFrame({
                        '日付': forecast_dates.strftime('%Y-%m-%d'),
                        '予測価格': [f"${p:,.2f}" for p in forecasts],
                    })
                    if 'conf_int_lower' in result['price_forecast']:
                        forecast_df['下限（95%）'] = [f"${p:,.2f}" for p in result['price_forecast']['conf_int_lower']]
                        forecast_df['上限（95%）'] = [f"${p:,.2f}" for p in result['price_forecast']['conf_int_upper']]

                    st.dataframe(forecast_df, width='stretch')

                # ボラティリティ予測
                if result['volatility_forecast']['success']:
                    st.markdown("---")
                    st.markdown("### 📊 ボラティリティ予測")

                    vol_data = result['volatility_forecast']

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "現在のボラティリティ",
                            f"{vol_data['current_volatility']:.2f}%/日",
                            help="過去データから計算した現在の価格変動率"
                        )
                    with col2:
                        st.metric(
                            "予測平均ボラティリティ（7日間）",
                            f"{vol_data['mean_volatility']:.2f}%/日",
                            help="今後7日間の予測される平均的な価格変動率"
                        )

            else:
                st.error("❌ データ不足：予測には最低100日分のデータが必要です")

    else:
        st.info("👆 ボタンをクリックして予測を実行してください")


def show_job_with_realtime_logs():
    """リアルタイムログ付きジョブ実行"""

    st.subheader("🤖 バックグラウンドジョブ実行（リアルタイムログ）")

    with st.expander("💡 この機能について"):
        st.markdown("""
### バックグラウンドジョブとは？

Phase 2で実装したバックグラウンド実行基盤のデモです。

**仕組み**:
1. ボタンクリック → FastAPIにジョブ開始リクエスト
2. RQ Workerがバックグラウンドで実行（5秒、3ステップ）
3. 0.5秒ごとにログをポーリング
4. リアルタイムでログ表示

**Phase 3では**:
- ダミージョブ → Claude Code SDK実行に置き換え
- ニュース検索＆分析を自動化
        """)

    # シンボル選択
    symbol = st.selectbox("仮想通貨を選択", ["BTC", "ETH", "XRP"], key="job_symbol")

    # ジョブ開始ボタン
    if st.button("🚀 ダミージョブ開始", key="start_job"):
        # ジョブ開始API呼び出し
        try:
            response = requests.post(
                "http://localhost:8000/api/jobs/start",
                json={"symbol": symbol},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state["job_id"] = data["job_id"]
                st.session_state["log_offset"] = 0
                st.session_state["job_running"] = True
                st.session_state["all_logs"] = []
                st.success(f"✅ ジョブ開始！ Job ID: {data['job_id']}")
                st.rerun()
            else:
                st.error(f"❌ エラー: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ FastAPIサーバーに接続できません。`python backend/main.py`を起動してください。")
        except Exception as e:
            st.error(f"❌ エラー: {str(e)}")

    # ジョブ実行中の表示
    if st.session_state.get("job_running", False):
        job_id = st.session_state["job_id"]
        offset = st.session_state.get("log_offset", 0)

        # ログ取得API呼び出し
        try:
            log_response = requests.get(
                f"http://localhost:8000/api/jobs/logs/{job_id}",
                params={"offset": offset},
                timeout=5
            )

            if log_response.status_code == 200:
                log_data = log_response.json()

                # ステータス表示
                status = log_data["status"]
                if status == "queued":
                    st.info("⏳ 待機中...")
                elif status == "started":
                    st.warning("▶️ 実行中...")
                elif status == "finished":
                    st.success("✅ 完了！")
                    st.session_state["job_running"] = False
                elif status == "failed":
                    st.error("❌ 失敗")
                    st.session_state["job_running"] = False
                elif status == "not_found":
                    st.error("❌ ジョブが見つかりません")
                    st.session_state["job_running"] = False

                # ログ表示
                if log_data["logs"]:
                    st.markdown("### 📝 リアルタイムログ")

                    # 全ログを蓄積して表示
                    st.session_state["all_logs"].extend(log_data["logs"])
                    st.session_state["log_offset"] = log_data["total_logs"]

                    # コードブロックで表示
                    st.code("\n".join(st.session_state["all_logs"]), language="")

                # 結果表示
                if log_data["result"]:
                    st.markdown("### 🎯 実行結果")
                    st.json(log_data["result"])

                # 未完了なら0.5秒後にリロード
                if log_data["has_more"]:
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.error(f"❌ ログ取得エラー: {log_response.status_code}")
                st.session_state["job_running"] = False

        except requests.exceptions.ConnectionError:
            st.error("❌ FastAPIサーバーに接続できません")
            st.session_state["job_running"] = False
        except Exception as e:
            st.error(f"❌ エラー: {str(e)}")
            st.session_state["job_running"] = False


def show_news(symbol):
    """ニュース一覧表示"""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📰 保存されたニュース")

    with col2:
        if st.button("🔄 DBから読込", key="fetch_news"):
            with st.spinner("ニュースを取得中..."):
                success, message = fetch_and_save_news(symbol)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    # ニュース検索のヘルプ
    with st.expander("💡 新しいニュースを取得する方法"):
        coin_name = {
            'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'XRP': 'Ripple',
            'DOGE': 'Dogecoin', 'SHIB': 'Shiba Inu'
        }.get(symbol, symbol)

        st.markdown(f"""
### 方法1: Claude Codeで検索

Claude Codeセッションで以下を実行：

```python
# ニュース検索クエリを生成
python src/tools/news_fetcher.py {symbol}
```

Claude CodeがWebSearchを実行し、自動的にニュースをDBに保存します。

### 方法2: 手動で追加

```bash
python src/tools/news_fetcher.py {symbol} --add-manual \\
  --title "ニュースタイトル" \\
  --content "ニュース本文" \\
  --url "https://example.com/news"
```

### 検索クエリ例

`{coin_name} {symbol} 仮想通貨 最新ニュース 2025`
        """)

        # 検索クエリをコピー用に表示
        query = f"{coin_name} {symbol} 仮想通貨 最新ニュース 2025"
        st.code(query, language="text")

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

    # バックグラウンドジョブ実行（Phase 2）
    show_job_with_realtime_logs()

    st.markdown("---")

    # ニュース表示
    show_news(selected_symbol)

    st.markdown("---")

    # 価格予測（ARIMA/GARCH）
    show_forecast(df, selected_symbol)

    st.markdown("---")
    st.caption("Powered by Streamlit | Data: Parquet Files")


if __name__ == '__main__':
    main()
