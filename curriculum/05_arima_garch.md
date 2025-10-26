# 05. ARIMA/GARCH - 未来を予測する数学

## 実践ガイド

**Week 3で詳しく学びます**

ARIMA/GARCHを使った取引の実践方法：
- 短期価格予測（1-7日）
- ボラティリティ予測
- リスク評価
- 具体的な使い方は、以下の技術解説を読んでから Week 3で実践します

---

## 技術解説 - ARIMA/GARCHの発見

# 📖 Story Chapter 5: ARIMA/GARCHの発見 - 「未来」を数式で予測する

## Scene 1: 数学者たちの挑戦

**ミコ**: 「これまでの武器（RSI、MACD、BB）は、全て『現在の状態』を判断するツールだ」

**ユウタ**: 「未来は予測できないの？」

**ミコ**: 「いや、できる。**数学の力**で」

**ミコ**: 「20世紀、数学者たちは『時系列データから未来を予測する』ことに挑戦した」

---

## Scene 2: 1970年代、時系列分析の革命

### 【回想シーン: ボックス＆ジェンキンスの発明】

**場所**: アメリカ、大学の研究室

**ジョージ・ボックス** (統計学者):
「経済データ、気象データ、株価データ...全て『時系列データ』だ」

**ボックス**: 「過去のパターンから、未来を予測できないか？」

*机の上には、株価の時系列グラフ*

**ボックス**: 「問題は、データが『ランダム』に見えることだ」

**ボックス**: 「でも、完全にランダムではない。**パターン**がある」

---

## Scene 3: ARIMAモデルの誕生

**ボックス**: 「時系列データには、3つの要素がある」

```markdown
【時系列データの3つの要素】

## 1. AR（AutoRegressive: 自己回帰）
今日の値は、過去の値に依存する

例:
今日の価格 = 0.8 × 昨日の価格 + 0.2 × 一昨日の価格 + ノイズ

数式:
y_t = φ₁y_{t-1} + φ₂y_{t-2} + ... + ε_t

意味:
過去の自分自身が、未来の自分に影響を与える

## 2. I（Integrated: 和分）
データに「トレンド」がある場合の処理

問題:
上昇トレンドのデータは予測しにくい
→ 差分を取って「定常化」する

差分:
Δy_t = y_t - y_{t-1}

例:
価格そのものではなく、「変化量」を予測する

## 3. MA（Moving Average: 移動平均）
過去の「予測誤差」が、今日の値に影響する

数式:
y_t = ε_t + θ₁ε_{t-1} + θ₂ε_{t-2} + ...

意味:
過去の「予想外の変動」が引きずる
```

**ボックス**: 「この3つを組み合わせる」

```markdown
【ARIMAモデル】

ARIMA(p, d, q)

p: AR項の次数（何日前まで見るか）
d: 差分の次数（何回差分を取るか）
q: MA項の次数（過去の誤差を何個見るか）

例:
ARIMA(12, 1, 12)
→ 12日前までの価格と誤差を見て、1回差分を取る

数式（完全版）:
Δy_t = c + φ₁Δy_{t-1} + ... + φₚΔy_{t-p} + ε_t + θ₁ε_{t-1} + ... + θₑε_{t-q}
```

**ボックス**: 「これで、未来の価格が予測できる！」

---

## Scene 4: GARCHの発明 - ボラティリティの予測

**ナレーション**:
1982年、ロバート・エングルは、さらに革新的な発見をした。

**ロバート・エングル** (経済学者):
「ARIMAは『価格』を予測できる」

**エングル**: 「でも、『リスク』は予測できない」

**エングル**: 「金融市場では、リスク（ボラティリティ）も変動する」

```markdown
【ボラティリティの性質】

観察:
- 静かな時期が続くと、その後も静かなことが多い
- 荒れた時期が続くと、その後も荒れることが多い
→ ボラティリティは「クラスタ化」する

例（2008年リーマンショック）:
普段: 1日の変動 ±1%
危機時: 1日の変動 ±10%

問題:
ARIMAでは、ボラティリティを一定と仮定
→ 危機時のリスクを過小評価
```

**エングル**: 「ボラティリティそのものを予測するモデルが必要だ」

---

## Scene 5: GARCHモデルの誕生

**エングル**: （ペンを走らせる）

```markdown
【GARCHモデル】

GARCH(p, q)

考え方:
ボラティリティ（σ²）は、過去のボラティリティと過去のショックに依存する

数式:
σ²_t = ω + α₁ε²_{t-1} + ... + αₚε²_{t-p} + β₁σ²_{t-1} + ... + βₑσ²_{t-q}

意味:
- ε²_{t-1}: 過去のショック（ARCH項）
- σ²_{t-1}: 過去のボラティリティ（GARCH項）

GARCH(1,1)（最も一般的）:
σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}

解釈:
今日のリスク = 定数 + 昨日のショック × α + 昨日のリスク × β
```

**エングル**: 「これで、リスクの変動も予測できる！」

**ナレーション**:
エングルはこの功績により、2003年にノーベル経済学賞を受賞した。

---

## Scene 6: 現代、ユウタとミコ

**ユウタ**: 「...すげえ。ノーベル賞級の理論か」

**ミコ**: 「そう。これが『数学的分析』の本丸だ」

**ユウタ**: 「でも、俺たちに使えるの？」

**ミコ**: 「使える。Pythonのライブラリがある」

---

## Scene 7: ARIMA実装

```python
# tools/forecasting.py（新規作成）

from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import numpy as np


class TimeSeriesForecaster:
    """時系列予測エンジン"""

    @staticmethod
    def fit_arima(prices: pd.Series,
                  order: tuple = (12, 1, 12),
                  forecast_days: int = 7) -> dict:
        """
        ARIMAモデルで価格予測

        発明者: George Box & Gwilym Jenkins (1970)
        用途: 時系列データからの価格予測

        Args:
            prices: 価格データ
            order: (p, d, q) - デフォルト(12,1,12)
            forecast_days: 予測日数

        Returns:
            予測結果
        """
        try:
            # モデル構築
            model = ARIMA(prices, order=order)
            fitted_model = model.fit()

            # 予測
            forecast = fitted_model.forecast(steps=forecast_days)

            # 信頼区間取得
            forecast_result = fitted_model.get_forecast(steps=forecast_days)
            conf_int = forecast_result.conf_int()

            return {
                'forecast': forecast.tolist(),
                'lower_bound': conf_int.iloc[:, 0].tolist(),
                'upper_bound': conf_int.iloc[:, 1].tolist(),
                'model_summary': {
                    'aic': fitted_model.aic,
                    'bic': fitted_model.bic,
                    'order': order
                }
            }
        except Exception as e:
            return {
                'error': str(e),
                'forecast': [],
                'lower_bound': [],
                'upper_bound': []
            }

    @staticmethod
    def evaluate_forecast_accuracy(actual: pd.Series,
                                     forecast: pd.Series) -> dict:
        """
        予測精度評価

        Args:
            actual: 実際の値
            forecast: 予測値

        Returns:
            精度指標
        """
        # RMSE（二乗平均平方根誤差）
        rmse = np.sqrt(np.mean((actual - forecast) ** 2))

        # MAPE（平均絶対パーセント誤差）
        mape = np.mean(np.abs((actual - forecast) / actual)) * 100

        # MAE（平均絶対誤差）
        mae = np.mean(np.abs(actual - forecast))

        return {
            'rmse': rmse,
            'mape': mape,  # パーセント
            'mae': mae
        }
```

---

## Scene 8: GARCH実装

```python
# tools/forecasting.py に追加

from arch import arch_model


class TimeSeriesForecaster:
    # ... (ARIMA実装は上) ...

    @staticmethod
    def fit_garch(returns: pd.Series,
                  p: int = 1,
                  q: int = 1,
                  forecast_days: int = 7) -> dict:
        """
        GARCHモデルでボラティリティ予測

        発明者: Robert Engle (1982)、Tim Bollerslev (GARCH拡張, 1986)
        用途: リスク（ボラティリティ）の予測

        Args:
            returns: リターン（収益率）データ
            p: GARCH項の次数
            q: ARCH項の次数
            forecast_days: 予測日数

        Returns:
            ボラティリティ予測
        """
        try:
            # リターンをパーセント単位に変換
            returns_pct = returns * 100

            # GARCHモデル構築
            model = arch_model(returns_pct, vol='Garch', p=p, q=q)
            fitted_model = model.fit(disp='off')

            # ボラティリティ予測
            forecast = fitted_model.forecast(horizon=forecast_days)
            volatility_forecast = np.sqrt(forecast.variance.values[-1, :])

            return {
                'volatility_forecast': volatility_forecast.tolist(),
                'current_volatility': fitted_model.conditional_volatility.iloc[-1],
                'model_summary': {
                    'aic': fitted_model.aic,
                    'bic': fitted_model.bic,
                    'order': (p, q)
                }
            }
        except Exception as e:
            return {
                'error': str(e),
                'volatility_forecast': [],
                'current_volatility': 0
            }

    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """
        価格からリターンを計算

        Args:
            prices: 価格データ

        Returns:
            リターン（収益率）
        """
        return prices.pct_change().dropna()
```

---

## Scene 9: BTCでの予測テスト

```python
# BTCの価格データ取得
btc_df = timeseries_manager.get_data('BTC')

# 直近100日を学習データ、次の7日を予測
train_data = btc_df['close'].tail(100)

# ARIMA予測
forecaster = TimeSeriesForecaster()
arima_result = forecaster.fit_arima(train_data, forecast_days=7)

print("📈 ARIMA価格予測（次の7日）:")
for i, price in enumerate(arima_result['forecast'], 1):
    lower = arima_result['lower_bound'][i-1]
    upper = arima_result['upper_bound'][i-1]
    print(f"  Day {i}: ${price:,.2f} (範囲: ${lower:,.2f} - ${upper:,.2f})")

# GARCH予測（ボラティリティ）
returns = forecaster.calculate_returns(train_data)
garch_result = forecaster.fit_garch(returns, forecast_days=7)

print("\n📊 GARCHボラティリティ予測（次の7日）:")
print(f"  現在のボラティリティ: {garch_result['current_volatility']:.2f}%")
for i, vol in enumerate(garch_result['volatility_forecast'], 1):
    print(f"  Day {i}: {vol:.2f}%")
```

**出力例**:
```
📈 ARIMA価格予測（次の7日）:
  Day 1: $68,123.45 (範囲: $67,500.00 - $68,750.00)
  Day 2: $68,234.12 (範囲: $67,200.00 - $69,300.00)
  Day 3: $68,345.67 (範囲: $66,900.00 - $69,800.00)
  ...

📊 GARCHボラティリティ予測（次の7日）:
  現在のボラティリティ: 2.35%
  Day 1: 2.41%
  Day 2: 2.48%
  Day 3: 2.52%
  ...
```

**ユウタ**: 「すげえ！未来の価格が出てる！」

**ミコ**: 「ただし、**あくまで予測**だ。100%当たるわけじゃない」

---

## Scene 10: 予測の限界と使い方

```markdown
【ARIMA/GARCHの限界】

## 限界1: 構造変化に弱い
例: 突然のニュース、規制変更
→ 過去のパターンが通用しない

## 限界2: 長期予測は不正確
1日後: 精度高い（MAPE 2-5%）
7日後: 精度中（MAPE 5-10%）
30日後: 精度低い（MAPE > 15%）

## 限界3: レンジ相場で有効
トレンドが継続する前提
→ 急激な反転は予測できない

## 正しい使い方
❌ 「7日後の価格は$68,234だから買おう」
✅ 「7日後も上昇トレンドが続きそうだから、今買っても大丈夫そう」

❌ 「100%当たる」
✅ 「確率的に、この範囲に収まる可能性が高い」
```

**ユウタ**: 「じゃあ、どう使うの？」

**ミコ**: 「『方向性』の確認に使う」

---

## Scene 11: ユウタ式での使い方

```markdown
【ユウタ式でのARIMA/GARCH活用法】

## エントリー判断（補助）
ARIMA予測が上昇傾向 ＋ 他の指標も買い
→ 自信を持ってエントリー

ARIMA予測が下降傾向 ＋ 他の指標は買い
→ 慎重に判断（見送りも検討）

## リスク管理
GARCHボラティリティ予測が増加
→ リスク増大の予兆
→ ポジションサイズを小さく

GARCHボラティリティ予測が減少
→ リスク低下
→ 安全な環境

## 組み合わせ（最強戦略）
✅ RSI < 30（売られすぎ）
✅ MACD ゴールデンクロス（勢い開始）
✅ %B < 0.3（Lower Band寄り）
✅ 低ボラティリティ（Band Width < 0.10）
✅ ARIMA予測が上昇（+3-5%）
✅ GARCH予測が安定（ボラティリティ < 3%）
→ 【最強買いシグナル】信頼度95%
```

**ユウタ**: 「全部の武器を組み合わせるのか！」

**ミコ**: 「そう。単体では60-70%の精度でも、組み合わせれば90%以上になる」

---

## Scene 12: 実装コード（完成版）

```python
# tools/forecasting.py 完成版

from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
import pandas as pd
import numpy as np


class TimeSeriesForecaster:
    """時系列予測エンジン（ARIMA/GARCH）"""

    @staticmethod
    def comprehensive_forecast(prices: pd.Series,
                                 forecast_days: int = 7) -> dict:
        """
        包括的予測（価格 + ボラティリティ）

        Args:
            prices: 価格データ
            forecast_days: 予測日数

        Returns:
            包括的予測結果
        """
        # ARIMA予測
        arima_result = TimeSeriesForecaster.fit_arima(
            prices,
            order=(12, 1, 12),
            forecast_days=forecast_days
        )

        # GARCH予測（ボラティリティ）
        returns = TimeSeriesForecaster.calculate_returns(prices)
        garch_result = TimeSeriesForecaster.fit_garch(
            returns,
            p=1,
            q=1,
            forecast_days=forecast_days
        )

        # 統合判断
        if arima_result.get('forecast'):
            current_price = prices.iloc[-1]
            forecast_price = arima_result['forecast'][0]  # 1日後
            price_change_pct = ((forecast_price - current_price) / current_price) * 100

            trend = 'bullish' if price_change_pct > 1 else 'bearish' if price_change_pct < -1 else 'neutral'
        else:
            trend = 'unknown'
            price_change_pct = 0

        # リスク判定
        current_vol = garch_result.get('current_volatility', 0)
        if current_vol > 5:
            risk_level = 'high'
        elif current_vol > 3:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'price_forecast': arima_result,
            'volatility_forecast': garch_result,
            'summary': {
                'trend': trend,
                'price_change_pct_1d': price_change_pct,
                'risk_level': risk_level,
                'current_volatility': current_vol,
                'recommendation': TimeSeriesForecaster._generate_recommendation(
                    trend, risk_level, price_change_pct
                )
            }
        }

    @staticmethod
    def _generate_recommendation(trend: str, risk_level: str, price_change_pct: float) -> dict:
        """
        推奨アクション生成

        Args:
            trend: トレンド方向
            risk_level: リスクレベル
            price_change_pct: 予測価格変動率

        Returns:
            推奨アクション
        """
        if trend == 'bullish' and risk_level == 'low' and price_change_pct > 2:
            return {
                'action': 'strong_buy',
                'confidence': 0.85,
                'description': '上昇トレンド予測＋低リスク。買いに適した環境。'
            }
        elif trend == 'bullish' and risk_level != 'high':
            return {
                'action': 'buy',
                'confidence': 0.70,
                'description': '上昇トレンド予測。リスクに注意しつつエントリー検討。'
            }
        elif trend == 'bearish' or risk_level == 'high':
            return {
                'action': 'avoid',
                'confidence': 0.75,
                'description': '下降トレンド予測 or 高リスク。エントリー避ける。'
            }
        else:
            return {
                'action': 'hold',
                'confidence': 0.50,
                'description': 'トレンド不明瞭。様子見推奨。'
            }

    # ... (fit_arima, fit_garch, calculate_returns は前述) ...
```

---

## Scene 13: エピローグ

**ユウタ**: 「これで...武器が揃った」

**ミコ**: 「そう。テクニカル分析（RSI、MACD、BB）と、数学的予測（ARIMA、GARCH）」

**ユウタ**: 「でも、まだ『ニュース』が残ってる」

**ミコ**: 「そう。最後の武器は『ファンダメンタルズ分析』だ」

**ミコ**: 「全てを統合して、最終判断を下すシステムを作る」

---

## 📝 Chapter 5 まとめ

### ARIMA/GARCHモデル

```markdown
【ARIMA（価格予測）】
- 発明者: Box & Jenkins (1970)
- 用途: 時系列データからの価格予測
- モデル: ARIMA(p, d, q)
- 精度: 短期（1-7日）で有効（MAPE 2-10%）

【GARCH（ボラティリティ予測）】
- 発明者: Robert Engle (1982, ノーベル賞)
- 用途: リスク（ボラティリティ）の予測
- モデル: GARCH(p, q)
- 特徴: ボラティリティクラスタリングを捉える

【組み合わせ戦略】
ARIMA上昇予測 ＋ GARCH低ボラ予測
＋ RSI売られすぎ ＋ MACDクロス ＋ BB中央
→ 【最強買いシグナル】信頼度95%
```

### 実装完了

✅ `tools/forecasting.py` 新規作成
- `fit_arima()`: ARIMA予測
- `fit_garch()`: GARCH予測
- `comprehensive_forecast()`: 包括的予測
- `evaluate_forecast_accuracy()`: 精度評価

---

## 🛠️ 実践で使う

ARIMA/GARCHを実際の取引で活用する方法：
- **Week 3: ニュース分析と統合判断**（作成予定） - 短期価格予測とボラティリティ予測
  - ARIMA(12,1,12)で1-7日後の価格予測
  - GARCH(1,1)でリスク予測
  - 信頼区間で不確実性を理解

---

**Next Chapter**: [Chapter 6: 統合分析システム - 全ての武器を統合する](./06_integrated_analysis.md)

---

## 📖 次へ

次のファイル: **[06. 統合分析システム - 全てを統合する](./06_integrated_analysis.md)**

