# 📊 数学的分析手段 - 完全ガイド

草コイントレーダーで利用可能な分析手法の全体像

---

## 📁 ディレクトリ構成

```
src/
├── analysis/          # 分析・予測ロジック
│   ├── indicators/    # テクニカル指標
│   ├── correlation_analyzer.py
│   ├── forecasting.py
│   └── gru_forecaster.py
├── data/             # データ管理
│   └── timeseries_storage.py  # RSI, MACD等も実装済み
└── tools/            # ユーティリティ
```

---

## 🎯 利用可能な分析手法

### **カテゴリ1: テクニカル指標（既存実装）**

#### **RSI - 相対力指数**
- **場所**: `src/data/timeseries_storage.py`
- **用途**: 買われすぎ・売られすぎの判定
- **数式**: `RSI = 100 - (100 / (1 + RS))`
  - RS = 平均上昇幅 / 平均下降幅
- **使い方**:
  ```python
  from src.data.timeseries_storage import TimeSeriesStorage
  storage = TimeSeriesStorage()
  df = storage.load_price_data('BTC', '1m')
  rsi = storage.calculate_rsi(df, period=14)
  ```
- **解釈**:
  - RSI > 70: 買われすぎ → 売りシグナル
  - RSI < 30: 売られすぎ → 買いシグナル

---

#### **MACD - 移動平均収束拡散**
- **場所**: `src/data/timeseries_storage.py`
- **用途**: トレンドの方向と強さの判定
- **数式**:
  - MACD = EMA(12) - EMA(26)
  - Signal = EMA(MACD, 9)
  - Histogram = MACD - Signal
- **使い方**:
  ```python
  macd, signal, histogram = storage.calculate_macd(df)
  ```
- **解釈**:
  - MACD > Signal: 買いシグナル
  - MACD < Signal: 売りシグナル

---

#### **ボリンジャーバンド**
- **場所**: `src/data/timeseries_storage.py`
- **用途**: ボラティリティと価格の位置関係
- **数式**:
  - 中心線 = SMA(20)
  - 上限 = SMA + (2 × 標準偏差)
  - 下限 = SMA - (2 × 標準偏差)
- **使い方**:
  ```python
  upper, middle, lower = storage.calculate_bollinger_bands(df, period=20, std_dev=2)
  ```
- **解釈**:
  - 価格が上限に接触 → 買われすぎ
  - 価格が下限に接触 → 売られすぎ

---

#### **ATR - 平均真の範囲**
- **場所**: `src/analysis/indicators/atr.py`
- **用途**: ボラティリティの測定
- **数式**: `ATR = EMA(True Range, 14)`
  - True Range = max(高値-安値, |高値-前日終値|, |安値-前日終値|)
- **解釈**: 値が大きいほどボラティリティが高い

---

#### **OBV - オンバランスボリューム**
- **場所**: `src/analysis/indicators/obv.py`
- **用途**: 出来高による価格予測
- **数式**:
  - 終値 > 前日終値: OBV += 出来高
  - 終値 < 前日終値: OBV -= 出来高
- **解釈**: OBV上昇 → 買い圧力増加

---

#### **ストキャスティクス**
- **場所**: `src/analysis/indicators/stochastic.py`
- **用途**: モメンタム分析
- **数式**:
  - %K = (終値 - 最安値) / (最高値 - 最安値) × 100
  - %D = %Kの移動平均
- **解釈**:
  - %K > 80: 買われすぎ
  - %K < 20: 売られすぎ

---

### **カテゴリ2: 統計分析（既存実装）**

#### **相関分析**
- **場所**: `src/analysis/correlation_analyzer.py`
- **用途**: 銘柄間の関係性分析
- **機能**:
  - 相関係数計算（-1 ～ +1）
  - ベータ値計算（市場との連動性）
  - 共分散行列
- **使い方**:
  ```python
  from src.analysis.correlation_analyzer import CorrelationAnalyzer
  analyzer = CorrelationAnalyzer()
  corr_matrix = analyzer.analyze_market(['BTC', 'ETH', 'XRP'])
  ```

---

#### **ボラティリティ分析**
- **場所**: `src/data/timeseries_storage.py`
- **用途**: リスク測定
- **数式**: `σ = sqrt(平均((価格 - 平均価格)^2))`
- **解釈**: 値が大きいほどリスクが高い

---

### **カテゴリ3: 時系列予測（既存実装）**

#### **ARIMA予測**
- **場所**: `src/analysis/forecasting.py`
- **用途**: 伝統的な時系列予測
- **精度**: MAPE = 2.15%（2024年研究）
- **使い方**:
  ```python
  from src.analysis.forecasting import ForecastingEngine
  engine = ForecastingEngine()
  forecast = engine.forecast_arima('BTC', days=7)
  ```

---

#### **GRU予測（最先端）**
- **場所**: `src/analysis/gru_forecaster.py`
- **用途**: 深層学習による高精度予測
- **精度**: MAPE = 0.09%（ARIMAの**24倍**精度）
- **参考**: `curriculum/07_advanced_mathematical_methods.md`
- **使い方**:
  ```python
  from src.analysis.gru_forecaster import GRUForecaster
  forecaster = GRUForecaster()
  predictions = forecaster.predict('BTC', horizon=24)
  ```

---

### **カテゴリ4: ニュース分析（既存実装）**

#### **ニュース収集・スコアリング**
- **場所**:
  - `src/analysis/news_collector.py` - ニュース収集
  - `src/analysis/scoring_engine.py` - スコアリング
- **用途**: 市場センチメント分析
- **機能**:
  - ニュース影響力スコア計算
  - センチメント分析
  - イベント検出

---

## 🚀 ダッシュボードからの使い方

### **現在の状態（手動実装）**
`dashboard/main.py`で個別に実装が必要

### **今後の実装（自動検出）**
```python
# src/analysis/配下のツールを自動検出
# ダッシュボードで選択可能に
```

---

## 📚 学習リソース

### **基礎から学ぶ**
1. `curriculum/02_rsi.md` - RSIの基礎
2. `curriculum/03_macd.md` - MACDの基礎
3. `curriculum/04_bollinger_bands.md` - ボリンジャーバンドの基礎

### **中級**
4. `curriculum/05_arima_garch.md` - ARIMA/GARCH予測
5. `curriculum/06_integrated_analysis.md` - 統合分析

### **高度な手法**
6. `curriculum/07_advanced_mathematical_methods.md` - GRU/LSTM
7. `curriculum/06_practical_forecasting_guide.md` - 実践予測ガイド

---

## 🎯 次のステップ

### **データ取得完了後**
1. ダッシュボードで取得したデータを確認
2. 各分析手法を試す
3. カリキュラムで数学的背景を学ぶ
4. 独自の分析手法を追加

### **推奨学習順序**
```
1. RSI（最もシンプル）
   ↓
2. MACD（トレンド分析）
   ↓
3. ボリンジャーバンド（ボラティリティ）
   ↓
4. 相関分析（複数銘柄の関係）
   ↓
5. ARIMA予測（伝統的手法）
   ↓
6. GRU予測（最先端）
```

---

## 💡 Tips

### **分析手法の選び方**
- **短期トレード**: RSI, ストキャスティクス
- **中期トレード**: MACD, ボリンジャーバンド
- **長期トレード**: 相関分析, GRU予測
- **リスク管理**: ATR, ボラティリティ分析

### **組み合わせ例**
1. **デイトレード**: RSI + MACD + OBV
2. **スイングトレード**: MACD + ボリンジャーバンド + ATR
3. **ポジショントレード**: 相関分析 + GRU予測 + ニュース分析

---

**最終更新**: 2025-11-01
**次の更新**: ダッシュボード自動検出機能実装後
