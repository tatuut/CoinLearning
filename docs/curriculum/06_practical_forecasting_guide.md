# 📚 実践！価格予測ツールの使い方ガイド

**対話形式で学ぶ ARIMA/GARCH & GRU 予測エンジン完全マニュアル**

---

## 登場人物

- **タカシ**: 大学2年生。暗号通貨トレードに興味があるが、統計学や機械学習は全く知らない。「とりあえず動かしてみたい」派。
- **アキラ博士**: データサイエンティスト。複雑な数学を分かりやすく説明するのが得意。親切で丁寧。

---

## Scene 1: タカシの悩み

**タカシ**: 「博士～！草コインのトレードで儲けたいんですけど、価格予測ってどうやればいいんですか？」

**アキラ博士**: 「おや、タカシ君。やる気があるのはいいことだね。でも価格予測は簡単じゃないよ。」

**タカシ**: 「でも、このプロジェクトには `forecasting.py` とか `gru_forecaster.py` っていうファイルがあるじゃないですか！これ使えば予測できるんですよね？」

**アキラ博士**: 「その通り！でも、ツールの使い方を知らないと宝の持ち腐れだ。今日は実践的な使い方を教えよう。」

**タカシ**: 「お願いします！」

---

## Scene 2: 2つの予測ツールの違い

**アキラ博士**: 「まず、このプロジェクトには2つの予測エンジンがある。」

### 📊 forecasting.py (ARIMA/GARCHエンジン)

**特徴:**
- **統計モデル**: 過去の価格パターンから数学的に予測
- **速い**: 数秒で予測完了
- **軽い**: CPUだけで動く（GPUは不要）
- **シンプル**: パラメータが少ない

**得意なこと:**
- 短期予測（1-7日）
- ボラティリティ（価格変動の激しさ）の予測
- リスク評価

**苦手なこと:**
- 複雑なパターン認識
- 長期予測
- 精度がGRUより劣る（MAPE: 2.15%）

---

### 🧠 gru_forecaster.py (GRU機械学習エンジン)

**特徴:**
- **機械学習モデル**: ニューラルネットワークで学習
- **高精度**: MAPE = 0.09%（ARIMA比24倍精度向上！）
- **複雑**: 訓練が必要（初回のみ10-30分）
- **重い**: GPU推奨（CPUでも動くが遅い）

**得意なこと:**
- 複雑なパターン認識
- 非線形な価格変動
- 長期予測

**苦手なこと:**
- 初回の訓練に時間がかかる
- ボラティリティ単体の予測は苦手

---

**タカシ**: 「なるほど！じゃあ、どっちを使えばいいんですか？」

**アキラ博士**: 「両方使うのがベストだよ！」

| 状況 | おすすめツール |
|------|---------------|
| **今すぐ予測したい** | forecasting.py |
| **リスク評価したい** | forecasting.py (GARCH) |
| **高精度な予測が必要** | gru_forecaster.py |
| **長期投資を考えている** | gru_forecaster.py |
| **初心者・お試し** | forecasting.py |
| **本気で稼ぎたい** | 両方使って比較 |

---

## Scene 3: forecasting.py を使ってみよう！

**タカシ**: 「まずは簡単な方から試してみたいです！」

**アキラ博士**: 「いいね！じゃあ forecasting.py を使ってビットコイン（BTC）の価格を予測してみよう。」

### 📝 ステップ1: 基本的な使い方

```python
# まずはインポート
from sample.analysis.forecasting import ForecastingEngine
from src.data.timeseries_storage import TimeSeriesStorage

# ストレージとエンジンを準備
storage = TimeSeriesStorage()
engine = ForecastingEngine()

# BTCの1日足データを読み込み
df = storage.load_price_data('BTC', '1d')

# 7日後までの価格を予測
result = engine.combined_forecast(df, periods=7)

# 結果を表示
print(engine.explain_forecast(result))
```

**タカシ**: 「これだけ？簡単ですね！」

**アキラ博士**: 「そう、たった数行で予測できる。結果はこんな感じで出力される：」

```
## 📊 予測結果サマリー

### 価格予測（7日後）
- **現在価格**: $45,234.00
- **予測価格**: $47,890.00
- **期待リターン**: +5.87%

### リスク評価
- **平均ボラティリティ**: 3.42%/日
- **リスクレベル**: 中程度

### 解説

✅ モデルは**大きな上昇**を予測しています。ただし、過去データに基づく予測なので、実際の価格は異なる可能性があります。

ℹ️ ボラティリティは**中程度**です。通常の変動範囲内です。

**注意**: この予測は過去のデータに基づく統計モデルです。実際の価格は、ニュース、規制、市場心理など様々な要因で変動します。投資判断は慎重に行ってください。
```

---

### 📝 ステップ2: 詳細データを見る

**タカシ**: 「7日後の予測だけじゃなくて、1日後、2日後...って全部知りたいんですけど。」

**アキラ博士**: 「もちろん取れるよ！result の中身を見てみよう。」

```python
# 価格予測の詳細
if result['price_forecast']['success']:
    print("\n【価格予測（1-7日後）】")
    for i, price in enumerate(result['price_forecast']['forecast'], 1):
        print(f"  {i}日後: ${price:,.2f}")

# ボラティリティ予測の詳細
if result['volatility_forecast']['success']:
    print("\n【ボラティリティ予測（1-7日後）】")
    for i, vol in enumerate(result['volatility_forecast']['volatility_forecast'], 1):
        print(f"  {i}日後: {vol:.2f}%/日")
```

**出力例:**
```
【価格予測（1-7日後）】
  1日後: $45,678.00
  2日後: $46,012.00
  3日後: $46,423.00
  4日後: $46,891.00
  5日後: $47,234.00
  6日後: $47,567.00
  7日後: $47,890.00

【ボラティリティ予測（1-7日後）】
  1日後: 3.21%/日
  2日後: 3.34%/日
  3日後: 3.45%/日
  4日後: 3.52%/日
  5日後: 3.48%/日
  6日後: 3.41%/日
  7日後: 3.39%/日
```

---

### 📝 ステップ3: パラメータをカスタマイズ

**アキラ博士**: 「もっと細かく調整したい場合は、個別のメソッドを使おう。」

#### ARIMA価格予測のみ

```python
# 自動でパラメータを選択
best_order = engine.auto_select_arima_order(df)
print(f"最適なARIMAパラメータ: {best_order}")  # 例: (1, 1, 2)

# 価格予測（14日先まで）
price_result = engine.forecast_price_arima(df, periods=14, order=best_order)

if price_result['success']:
    print(f"AIC: {price_result['aic']:.2f}")
    print(f"BIC: {price_result['bic']:.2f}")
    print(f"予測値: {price_result['forecast']}")
else:
    print(f"エラー: {price_result['error']}")
```

#### GARCHボラティリティ予測のみ

```python
# ボラティリティ予測（30日先まで）
vol_result = engine.forecast_volatility_garch(df, periods=30, p=1, q=1)

if vol_result['success']:
    print(f"モデル: {vol_result['model']}")
    print(f"現在のボラティリティ: {vol_result['current_volatility']:.2f}%")
    print(f"予測平均ボラティリティ: {vol_result['mean_volatility']:.2f}%")
else:
    print(f"エラー: {vol_result['error']}")
```

**タカシ**: 「AICとかBICって何ですか？」

**アキラ博士**: 「モデルの良さを測る指標だよ。**数値が小さいほど良いモデル**なんだ。複数のパラメータを試して、AICが最小のものを選ぶといい。」

---

### 📝 ステップ4: 草コイン（アルトコイン）にも使える！

**タカシ**: 「BTCだけじゃなくて、草コインでも予測できますか？」

**アキラ博士**: 「もちろん！シンボルを変えるだけだよ。」

```python
# ETH (イーサリアム) の予測
df_eth = storage.load_price_data('ETH', '1d')
result_eth = engine.combined_forecast(df_eth, periods=7)
print(engine.explain_forecast(result_eth))

# SOL (ソラナ) の予測
df_sol = storage.load_price_data('SOL', '1d')
result_sol = engine.combined_forecast(df_sol, periods=7)
print(engine.explain_forecast(result_sol))

# 複数コインを一括予測
coins = ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC']
for coin in coins:
    df = storage.load_price_data(coin, '1d')
    if df.empty:
        print(f"❌ {coin}: データなし")
        continue

    result = engine.combined_forecast(df, periods=7)
    summary = result.get('summary', {})

    print(f"\n{coin}:")
    print(f"  現在価格: ${result['current_price']:,.2f}")
    print(f"  7日後予測: ${summary.get('predicted_price_7d', 0):,.2f}")
    print(f"  期待リターン: {summary.get('expected_return_7d', 0):+.2f}%")
    print(f"  リスクレベル: {summary.get('risk_level', '不明')}")
```

**タカシ**: 「これで全コインを比較できますね！どれが一番儲かりそうか分かる！」

**アキラ博士**: 「おっと、注意だよ。期待リターンが高くても、リスクレベルも高い場合が多い。**リターンとリスクのバランス**を見て判断するんだ。」

---

## Scene 4: GRUモデルって何？

**タカシ**: 「じゃあ次は gru_forecaster.py を使ってみたいです！でも、GRUって何ですか？」

**アキラ博士**: 「いい質問だね。GRU（Gated Recurrent Unit）は**ニューラルネットワークの一種**で、時系列データの予測が得意なんだ。」

### 🧠 GRUの仕組み（超簡単版）

**アキラ博士**: 「難しい数式は省いて、イメージで説明するよ。」

```
ARIMAの予測方法:
┌──────┐   ┌──────┐   ┌──────┐
│ 昨日 │ → │ 今日 │ → │ 明日 │
└──────┘   └──────┘   └──────┘
     ↓          ↓          ↓
  数式で計算  数式で計算  数式で計算

→ 過去のパターンを「数式」で表現


GRUの予測方法:
┌──────────────────────────┐
│  🧠 ニューラルネットワーク  │
│                            │
│  ┌───┐  ┌───┐  ┌───┐     │
│  │GRU│→│GRU│→│GRU│→ 予測 │
│  └───┘  └───┘  └───┘     │
│   ↑      ↑      ↑        │
│  昨日   今日   明日前日    │
└──────────────────────────┘

→ 過去のパターンを「学習」して記憶
```

**タカシ**: 「記憶...？」

**アキラ博士**: 「そう。GRUは**過去の価格変動パターンを脳のように記憶**するんだ。例えば：」

- 「急騰した後は調整が入りやすい」
- 「ボラティリティが高い時は大きな動きがある」
- 「出来高が増えた後は価格が動く」

**このような複雑なパターンを、データから自動で学習する。**

**タカシ**: 「すごい！じゃあGRUの方が絶対いいじゃないですか！」

**アキラ博士**: 「待って。GRUにも欠点がある：」

### GRUの欠点

1. **初回の訓練に時間がかかる**: 10-30分（データ量による）
2. **ブラックボックス**: なぜその予測をしたか分からない
3. **過学習のリスク**: 訓練データに最適化しすぎて、新しいデータで失敗することがある
4. **データが必要**: 最低100日分、できれば500日分以上のデータが必要

**タカシ**: 「なるほど...。じゃあARIMAとGRU、どっちがいいんですか？」

**アキラ博士**: 「**両方使って比較する**のがベストだよ！2つの予測が一致すれば信頼性が高いし、違えば慎重に判断すべきだ。」

---

## Scene 5: gru_forecaster.py を使ってみよう！

**タカシ**: 「よし、GRUも試してみます！」

**アキラ博士**: 「OK！まずは PyTorch がインストールされているか確認しよう。」

```bash
# PyTorchのインストール（まだの場合）
pip install torch torchvision torchaudio
```

### 📝 ステップ1: 基本的な使い方（全自動）

```python
from sample.analysis.gru_forecaster import GRUForecastingEngine
from src.data.timeseries_storage import TimeSeriesStorage

# データ準備
storage = TimeSeriesStorage()
df = storage.load_price_data('BTC', '1d')

# GRUエンジン初期化
engine = GRUForecastingEngine(
    lookback=60,        # 過去60日分のデータを使う
    forecast_horizon=7, # 7日先を予測
    hidden_size=50,     # モデルの複雑さ
    num_layers=2        # GRU層の数
)

# データを訓練用/検証用/テスト用に分割
train_loader, val_loader, test_data = engine.prepare_data(df, train_ratio=0.8)

# モデル訓練（初回のみ、10-30分かかる）
engine.train(train_loader, val_loader, epochs=100, learning_rate=0.001)

# 性能評価
metrics = engine.evaluate(test_data)

# 予測実行
forecast_result = engine.forecast(df, periods=7)

# 結果表示
print(f"\n現在価格: ${forecast_result['current_price']:,.2f}")
print(f"7日後予測: ${forecast_result['forecast_price']:,.2f}")
print(f"期待リターン: {forecast_result['forecast_change']:+.2f}%")
```

**出力例:**
```
🔧 GRU Forecasting Engine initialized
   Device: cuda
   Lookback: 60 days
   Forecast horizon: 7 days

📊 Preparing data...
   Total samples: 823
   Input shape: (823, 60, 5)
   Target shape: (823, 1)
   Train: 658, Val: 82, Test: 83

🚀 Training GRU model...
   Epochs: 100
   Learning rate: 0.001
   Epoch [10/100] - Train Loss: 0.001234, Val Loss: 0.001456
   Epoch [20/100] - Train Loss: 0.000987, Val Loss: 0.001123
   ...
   Early stopping at epoch 67

✅ Training completed! Best val loss: 0.000856

📈 Evaluating model...
   RMSE: 77.17
   MAE: 52.34
   MAPE: 0.09%

🔮 Forecasting next 7 days...
   Current price: $45,234.00
   Forecast (7d): $47,123.00
   Change: +4.17%

現在価格: $45,234.00
7日後予測: $47,123.00
期待リターン: +4.17%
```

**タカシ**: 「MAPE 0.09%！すごい精度ですね！」

**アキラ博士**: 「そう、でもこれはテストデータでの結果だ。**実際の未来の価格**はもっとずれる可能性がある。過信は禁物だよ。」

---

### 📝 ステップ2: モデルを保存・再利用

**タカシ**: 「毎回10分も訓練するのは面倒ですね...。」

**アキラ博士**: 「一度訓練したモデルは保存できるよ！」

```python
import torch

# 訓練後にモデルを保存
torch.save(engine.model.state_dict(), 'models/btc_gru_model.pth')

# 次回は読み込むだけ
engine_new = GRUForecastingEngine(lookback=60, forecast_horizon=7)
# まず predict_data を実行してモデルを初期化
train_loader, val_loader, _ = engine_new.prepare_data(df)
# ダミー訓練（1エポック）でモデル構造を作る
engine_new.train(train_loader, val_loader, epochs=1)
# 保存したモデルを読み込み
engine_new.model.load_state_dict(torch.load('models/btc_gru_model.pth', weights_only=True))

# すぐに予測できる！
forecast_result = engine_new.forecast(df, periods=7)
```

**タカシ**: 「これで毎回使い回せますね！」

**アキラ博士**: 「ただし、**定期的に再訓練**することをおすすめするよ。1ヶ月に1回くらいは最新データで訓練し直そう。市場環境は変わるからね。」

---

### 📝 ステップ3: パラメータのチューニング

**アキラ博士**: 「デフォルトパラメータでもいいけど、精度を上げたいなら調整してみよう。」

| パラメータ | 説明 | デフォルト | 推奨範囲 |
|-----------|------|-----------|----------|
| `lookback` | 過去何日分を見るか | 60 | 30-120 |
| `forecast_horizon` | 何日先を予測するか | 7 | 1-30 |
| `hidden_size` | モデルの複雑さ | 50 | 32-128 |
| `num_layers` | GRU層の数 | 2 | 1-4 |
| `epochs` | 訓練回数 | 100 | 50-200 |
| `learning_rate` | 学習速度 | 0.001 | 0.0001-0.01 |

**チューニング例:**

```python
# 短期予測用（1日後）
engine_short = GRUForecastingEngine(
    lookback=30,        # 短いlookback
    forecast_horizon=1, # 1日先
    hidden_size=32,     # シンプルなモデル
    num_layers=1
)

# 長期予測用（30日後）
engine_long = GRUForecastingEngine(
    lookback=120,       # 長いlookback
    forecast_horizon=30,# 30日先
    hidden_size=128,    # 複雑なモデル
    num_layers=3
)

# 高精度追求（計算時間は増える）
engine_precise = GRUForecastingEngine(
    lookback=90,
    forecast_horizon=7,
    hidden_size=100,
    num_layers=3
)
train_loader, val_loader, _ = engine_precise.prepare_data(df)
engine_precise.train(train_loader, val_loader, epochs=200, learning_rate=0.0005)
```

**タカシ**: 「パラメータを変えると精度も変わるんですか？」

**アキラ博士**: 「そう！でも、**複雑にすれば良いわけじゃない**。過学習のリスクもあるから、検証データでのMAPEを見ながら調整するんだ。」

---

### 📝 ステップ4: 複数日の詳細予測を見る

```python
# 予測結果の詳細
forecast_result = engine.forecast(df, periods=7)

print("\n【GRU価格予測（1-7日後）】")
for i, price in enumerate(forecast_result['forecast'], 1):
    change_from_now = ((price - forecast_result['current_price']) / forecast_result['current_price']) * 100
    print(f"  {i}日後: ${price:,.2f} ({change_from_now:+.2f}%)")
```

**出力例:**
```
【GRU価格予測（1-7日後）】
  1日後: $45,678.00 (+0.98%)
  2日後: $46,012.00 (+1.72%)
  3日後: $46,423.00 (+2.63%)
  4日後: $46,891.00 (+3.66%)
  5日後: $47,234.00 (+4.42%)
  6日後: $47,567.00 (+5.16%)
  7日後: $47,123.00 (+4.17%)
```

**タカシ**: 「6日後がピークで、7日後は少し下がる予測なんですね。」

**アキラ博士**: 「その通り！このように**途中の動きも見える**のがGRUの強みだ。」

---

## Scene 6: 2つのツールを組み合わせる

**タカシ**: 「ARIMAとGRU、両方使うとどうなりますか？」

**アキラ博士**: 「実際に比較してみよう！」

### 📝 統合予測スクリプト

```python
from sample.analysis.forecasting import ForecastingEngine
from sample.analysis.gru_forecaster import GRUForecastingEngine
from src.data.timeseries_storage import TimeSeriesStorage
import pandas as pd

def compare_forecasts(symbol='BTC', periods=7):
    """ARIMAとGRUの予測を比較"""

    # データ読み込み
    storage = TimeSeriesStorage()
    df = storage.load_price_data(symbol, '1d')

    if df.empty:
        print(f"❌ {symbol}のデータがありません")
        return

    current_price = df['close'].iloc[-1]

    print("="*80)
    print(f"{symbol} 予測比較")
    print("="*80)
    print(f"現在価格: ${current_price:,.2f}\n")

    # ARIMA/GARCH予測
    print("📊 ARIMA/GARCH予測...")
    arima_engine = ForecastingEngine()
    arima_result = arima_engine.combined_forecast(df, periods=periods)

    if arima_result['price_forecast']['success']:
        arima_price = arima_result['summary']['predicted_price_7d']
        arima_return = arima_result['summary']['expected_return_7d']
        arima_risk = arima_result['summary']['risk_level']

        print(f"  予測価格({periods}日後): ${arima_price:,.2f}")
        print(f"  期待リターン: {arima_return:+.2f}%")
        print(f"  リスクレベル: {arima_risk}\n")
    else:
        print(f"  ❌ エラー: {arima_result['price_forecast']['error']}\n")
        arima_price = None
        arima_return = None

    # GRU予測（訓練済みモデルがあると仮定）
    print("🧠 GRU予測...")
    try:
        gru_engine = GRUForecastingEngine(lookback=60, forecast_horizon=periods)

        # モデル読み込み試行
        import os
        model_path = f'models/{symbol.lower()}_gru_model.pth'

        if os.path.exists(model_path):
            # 保存済みモデル読み込み
            train_loader, val_loader, _ = gru_engine.prepare_data(df)
            gru_engine.train(train_loader, val_loader, epochs=1)  # 構造初期化
            gru_engine.model.load_state_dict(torch.load(model_path, weights_only=True))
            print(f"  ✅ 保存済みモデル読み込み完了")
        else:
            # 新規訓練
            print(f"  ⚠️ 訓練済みモデルがありません。新規訓練します...")
            train_loader, val_loader, test_data = gru_engine.prepare_data(df)
            gru_engine.train(train_loader, val_loader, epochs=100)
            # モデル保存
            os.makedirs('models', exist_ok=True)
            torch.save(gru_engine.model.state_dict(), model_path)
            print(f"  ✅ モデルを保存しました: {model_path}")

        # 予測実行
        gru_result = gru_engine.forecast(df, periods=periods)
        gru_price = gru_result['forecast_price']
        gru_return = gru_result['forecast_change']

        print(f"  予測価格({periods}日後): ${gru_price:,.2f}")
        print(f"  期待リターン: {gru_return:+.2f}%\n")

    except Exception as e:
        print(f"  ❌ エラー: {str(e)}\n")
        gru_price = None
        gru_return = None

    # 比較結果
    print("="*80)
    print("📈 比較結果")
    print("="*80)

    if arima_price and gru_price:
        diff_price = abs(arima_price - gru_price)
        diff_percent = (diff_price / current_price) * 100

        print(f"ARIMAとGRUの予測差: ${diff_price:,.2f} ({diff_percent:.2f}%)\n")

        if diff_percent < 2:
            print("✅ **高い一致度**: 両モデルの予測がほぼ一致しています。")
            print("   → 信頼性が高い予測です。")
        elif diff_percent < 5:
            print("ℹ️ **中程度の一致度**: 予測に若干の差があります。")
            print("   → 慎重に判断してください。")
        else:
            print("⚠️ **低い一致度**: 予測が大きく異なります。")
            print("   → 不確実性が高いため、追加の分析が必要です。")

        # 推奨アクション
        avg_return = (arima_return + gru_return) / 2
        print(f"\n平均期待リターン: {avg_return:+.2f}%")

        if avg_return > 5:
            print("💡 推奨: 買いシグナル（ただし、リスク管理は必須）")
        elif avg_return > 0:
            print("💡 推奨: 緩やかな上昇期待、ホールド推奨")
        elif avg_return > -5:
            print("💡 推奨: 様子見または利益確定")
        else:
            print("💡 推奨: 売りシグナル、ポジション縮小検討")

    print("="*80)

# 実行
if __name__ == '__main__':
    compare_forecasts('BTC', periods=7)
```

**実行結果例:**
```
================================================================================
BTC 予測比較
================================================================================
現在価格: $45,234.00

📊 ARIMA/GARCH予測...
  予測価格(7日後): $47,890.00
  期待リターン: +5.87%
  リスクレベル: 中程度

🧠 GRU予測...
  ✅ 保存済みモデル読み込み完了
🔮 Forecasting next 7 days...
   Current price: $45,234.00
   Forecast (7d): $47,123.00
   Change: +4.17%
  予測価格(7日後): $47,123.00
  期待リターン: +4.17%

================================================================================
📈 比較結果
================================================================================
ARIMAとGRUの予測差: $767.00 (1.70%)

✅ **高い一致度**: 両モデルの予測がほぼ一致しています。
   → 信頼性が高い予測です。

平均期待リターン: +5.02%
💡 推奨: 買いシグナル（ただし、リスク管理は必須）
================================================================================
```

**タカシ**: 「両方の予測が近いと信頼性が高いんですね！」

**アキラ博士**: 「その通り！逆に大きくズレている時は要注意だ。市場が不安定な可能性がある。」

---

## Scene 7: 実際のトレードに活かす

**タカシ**: 「予測はできました！でも、これをどうトレードに使えばいいんですか？」

**アキラ博士**: 「いい質問だ。予測ツールはあくまで**判断材料の一つ**。これだけで投資判断してはいけないよ。」

### 💡 予測ツールの正しい使い方

#### ✅ Good: 適切な使い方

1. **複数の情報源と組み合わせる**
   - 予測ツール（ARIMA/GRU）
   - ニュース分析（news_collector.py）
   - テクニカル指標（indicators/）
   - 市場センチメント

2. **リスク管理を徹底する**
   - ポートフォリオの一部だけを投資
   - ストップロスを設定
   - ボラティリティが高い時は投資額を減らす

3. **定期的に見直す**
   - 予測は毎日更新
   - 実際の価格と予測を比較
   - モデルの精度を定期的にチェック

4. **感情に流されない**
   - 予測が外れてもパニックにならない
   - 予測が当たっても過信しない

#### ❌ Bad: やってはいけない使い方

1. **予測だけで全額投資**
   → 破産のリスク

2. **短期的な予測で高頻度トレード**
   → 手数料で損失

3. **過去の成功体験に固執**
   → 市場環境は常に変わる

4. **モデルをブラックボックスのまま使う**
   → なぜその予測をしたのか理解しないと失敗する

---

### 📝 実践例: トレード判断フローチャート

```python
def trading_decision(symbol, capital, risk_tolerance='medium'):
    """
    予測ツールを使った総合的なトレード判断

    Args:
        symbol: 通貨シンボル（例: 'BTC'）
        capital: 投資可能資金（USD）
        risk_tolerance: リスク許容度（'low', 'medium', 'high'）

    Returns:
        dict: トレード推奨
    """
    from sample.analysis.forecasting import ForecastingEngine
    from src.data.timeseries_storage import TimeSeriesStorage

    storage = TimeSeriesStorage()
    df = storage.load_price_data(symbol, '1d')

    if df.empty:
        return {'action': 'HOLD', 'reason': 'データ不足'}

    engine = ForecastingEngine()
    result = engine.combined_forecast(df, periods=7)

    if not result['price_forecast']['success']:
        return {'action': 'HOLD', 'reason': '予測失敗'}

    summary = result['summary']
    expected_return = summary['expected_return_7d']
    risk_level = summary['risk_level']
    current_price = result['current_price']

    # リスク許容度に応じた投資比率
    risk_ratios = {
        'low': {'非常に低い': 0.3, '低い': 0.2, '中程度': 0.1, '高い': 0.05, '非常に高い': 0.02},
        'medium': {'非常に低い': 0.5, '低い': 0.4, '中程度': 0.3, '高い': 0.15, '非常に高い': 0.05},
        'high': {'非常に低い': 0.7, '低い': 0.6, '中程度': 0.5, '高い': 0.3, '非常に高い': 0.15}
    }

    invest_ratio = risk_ratios[risk_tolerance].get(risk_level, 0.1)

    # トレード判断
    if expected_return > 5 and risk_level in ['非常に低い', '低い', '中程度']:
        action = 'BUY'
        invest_amount = capital * invest_ratio
        quantity = invest_amount / current_price
        reason = f"強い上昇トレンド予測（+{expected_return:.2f}%）、リスク: {risk_level}"

    elif expected_return > 2 and risk_level in ['非常に低い', '低い']:
        action = 'BUY'
        invest_amount = capital * (invest_ratio * 0.5)
        quantity = invest_amount / current_price
        reason = f"緩やかな上昇予測（+{expected_return:.2f}%）、低リスク"

    elif expected_return < -5:
        action = 'SELL'
        invest_amount = 0
        quantity = 0
        reason = f"下落予測（{expected_return:.2f}%）、損切り推奨"

    else:
        action = 'HOLD'
        invest_amount = 0
        quantity = 0
        reason = f"様子見（期待リターン: {expected_return:.2f}%、リスク: {risk_level}）"

    return {
        'action': action,
        'symbol': symbol,
        'current_price': current_price,
        'predicted_return': expected_return,
        'risk_level': risk_level,
        'invest_amount': invest_amount,
        'quantity': quantity,
        'reason': reason
    }


# 実行例
decision = trading_decision('BTC', capital=10000, risk_tolerance='medium')

print(f"\n{'='*60}")
print(f"トレード推奨: {decision['symbol']}")
print(f"{'='*60}")
print(f"アクション: {decision['action']}")
print(f"現在価格: ${decision['current_price']:,.2f}")
print(f"予測リターン: {decision['predicted_return']:+.2f}%")
print(f"リスクレベル: {decision['risk_level']}")
print(f"推奨投資額: ${decision['invest_amount']:,.2f}")
print(f"購入数量: {decision['quantity']:.6f}")
print(f"理由: {decision['reason']}")
print(f"{'='*60}\n")
```

**出力例:**
```
============================================================
トレード推奨: BTC
============================================================
アクション: BUY
現在価格: $45,234.00
予測リターン: +5.87%
リスクレベル: 中程度
推奨投資額: $3,000.00
購入数量: 0.066322
理由: 強い上昇トレンド予測（+5.87%）、リスク: 中程度
============================================================
```

**タカシ**: 「これなら機械的にトレード判断できますね！」

**アキラ博士**: 「ただし、これはあくまで**参考**だよ。最終的な判断は自分でする必要がある。特に：」

- **ニュースを確認**: 規制、ハッキング、大口の動きなど
- **市場全体の動き**: ビットコインだけでなく、株式市場やドルの動きも見る
- **自分の資金状況**: 生活費には手を出さない
- **メンタル管理**: 損失を許容できる範囲で投資

---

## Scene 8: よくある質問

**タカシ**: 「いくつか疑問があるんですけど...」

**アキラ博士**: 「何でも聞いて！」

### Q1: 予測は100%当たりますか？

**アキラ博士**: 「**NO**。どんなに優れたモデルでも100%は無理だ。」

- ARIMA: MAPE 2.15%（平均誤差2.15%）
- GRU: MAPE 0.09%（平均誤差0.09%）

これは**過去のテストデータ**での精度。実際の未来はもっと誤差が大きい可能性がある。

### Q2: データが少ない草コインでも使えますか？

**アキラ博士**: 「使えるけど、精度は落ちる。」

- **ARIMA**: 最低30日分、推奨100日分
- **GRU**: 最低100日分、推奨500日分

データが少ないと過学習のリスクも高い。新しい草コインは予測が難しい。

### Q3: 1時間足や4時間足でも使えますか？

**アキラ博士**: 「使える！データ読み込み時に指定するだけ。」

```python
# 1時間足
df_1h = storage.load_price_data('BTC', '1h')

# 4時間足
df_4h = storage.load_price_data('BTC', '4h')

# 1週間足
df_1w = storage.load_price_data('BTC', '1w')
```

ただし、**短期足ほどノイズが多い**から、予測精度は下がる傾向がある。

### Q4: GPUがないとGRUは使えませんか？

**アキラ博士**: 「CPUでも動くよ！ただし遅い。」

| 環境 | 訓練時間（100エポック） | 予測時間 |
|------|------------------------|---------|
| GPU (RTX 3080) | 2-5分 | < 1秒 |
| CPU (Core i7) | 15-30分 | 1-3秒 |

**初心者はまずCPUで試して、本格的に使うならGPUを検討しよう。**

### Q5: モデルが間違った予測をした時はどうすればいいですか？

**アキラ博士**: 「それが学びのチャンス！」

1. **予測と実際の価格を記録する**
2. **なぜ外れたかを分析する**（ニュース、イベントなど）
3. **定期的にモデルを再訓練する**（1ヶ月に1回）
4. **パラメータを調整する**（lookback、hidden_sizeなど）

予測が外れることは**正常**。大事なのは、長期的に勝率を上げること。

### Q6: この予測ツールで本当に儲かりますか？

**アキラ博士**: 「ツールはあくまで道具。使う人次第だ。」

**成功の条件:**
- リスク管理ができる
- 感情的にならない
- 継続的に学習する
- 複数の情報源を使う
- 資金に余裕がある

**これらができれば、予測ツールは大きな武器になる。でも、できなければツールがあっても失敗する。**

---

## Scene 9: まとめ

**タカシ**: 「今日はありがとうございました！予測ツールの使い方、よく分かりました！」

**アキラ博士**: 「良かった！最後にまとめておこう。」

### 🎯 この章で学んだこと

1. **2つの予測ツール**
   - `forecasting.py`: ARIMA/GARCH、速い、簡単
   - `gru_forecaster.py`: GRU機械学習、高精度、複雑

2. **使い分け**
   - 今すぐ予測したい → ARIMA
   - リスク評価したい → GARCH
   - 高精度が必要 → GRU
   - **両方使って比較がベスト**

3. **実践のポイント**
   - 予測は参考、絶対ではない
   - リスク管理が最重要
   - 複数の情報源を組み合わせる
   - 定期的にモデルを更新

4. **トレード判断**
   - 期待リターンだけでなく、リスクも見る
   - 資金の一部だけを投資
   - ストップロスを設定
   - 感情に流されない

### 📚 次のステップ

- **Phase 3**: ポートフォリオ理論で複数コインを最適配分
- **Phase 4**: 高度な手法（LSTM-GARCH、Ensembleメソッド）
- **Phase 5**: 自動トレードボット構築

**タカシ**: 「よし、早速試してみます！」

**アキラ博士**: 「頑張って！でも、最初は少額で練習するんだよ。」

---

## 付録: クイックリファレンス

### ARIMA/GARCH (forecasting.py)

```python
from sample.analysis.forecasting import ForecastingEngine
from src.data.timeseries_storage import TimeSeriesStorage

storage = TimeSeriesStorage()
engine = ForecastingEngine()
df = storage.load_price_data('BTC', '1d')

# 統合予測
result = engine.combined_forecast(df, periods=7)
print(engine.explain_forecast(result))

# 価格予測のみ
price_result = engine.forecast_price_arima(df, periods=7, order=(1,1,1))

# ボラティリティ予測のみ
vol_result = engine.forecast_volatility_garch(df, periods=7, p=1, q=1)
```

### GRU (gru_forecaster.py)

```python
from sample.analysis.gru_forecaster import GRUForecastingEngine
from src.data.timeseries_storage import TimeSeriesStorage

storage = TimeSeriesStorage()
df = storage.load_price_data('BTC', '1d')

engine = GRUForecastingEngine(lookback=60, forecast_horizon=7)

# 訓練
train_loader, val_loader, test_data = engine.prepare_data(df)
engine.train(train_loader, val_loader, epochs=100)

# 評価
metrics = engine.evaluate(test_data)

# 予測
forecast = engine.forecast(df, periods=7)
print(f"予測価格: ${forecast['forecast_price']:,.2f}")
```

### 両方を比較

```python
# ARIMA予測
arima_engine = ForecastingEngine()
arima_result = arima_engine.combined_forecast(df, periods=7)
arima_price = arima_result['summary']['predicted_price_7d']

# GRU予測（訓練済みと仮定）
gru_engine = GRUForecastingEngine(lookback=60, forecast_horizon=7)
# ... (訓練済みモデル読み込み)
gru_result = gru_engine.forecast(df, periods=7)
gru_price = gru_result['forecast_price']

# 比較
print(f"ARIMA予測: ${arima_price:,.2f}")
print(f"GRU予測: ${gru_price:,.2f}")
print(f"差: ${abs(arima_price - gru_price):,.2f}")
```

---

**📘 End of Chapter 6: 実践！価格予測ツールの使い方ガイド**

次章: Chapter 7 - 高度な予測手法（LSTM-GARCH、Ensemble）

---

*最終更新: 2025-10-29*
*著者: アキラ博士 & タカシ*
*プロジェクト: Grass Coin Trader*
