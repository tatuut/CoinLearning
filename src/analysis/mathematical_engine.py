"""
数学的分析エンジン（Layer 1）

客観的な数値データから定量的スコアを算出します。
これが全ての分析の基礎となります。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np
from src.analysis.forecasting import ForecastingEngine


class MathematicalAnalysisEngine:
    """数学的分析エンジン（Layer 1: 客観的事実）"""

    def __init__(self):
        self.forecasting_engine = ForecastingEngine()

    def analyze(self, symbol: str, price_data: pd.DataFrame) -> dict:
        """
        客観的な数学的分析

        Args:
            symbol: 銘柄シンボル
            price_data: 価格データ（OHLCV）

        Returns:
            {
                'technical_score': float,     # テクニカル指標スコア
                'forecast_score': float,      # 予測モデルスコア
                'volatility_score': float,    # ボラティリティスコア
                'momentum_score': float,      # モメンタムスコア
                'base_score': float,          # 基本スコア（加重平均）
                'details': dict               # 詳細データ
            }
        """

        # 1. テクニカル指標スコア
        technical = self._calculate_technical_score(price_data)

        # 2. 予測モデルスコア
        forecast = self._calculate_forecast_score(price_data)

        # 3. ボラティリティスコア
        volatility = self._calculate_volatility_score(price_data)

        # 4. モメンタムスコア
        momentum = self._calculate_momentum_score(price_data)

        # 5. 基本スコア（加重平均）
        base_score = (
            technical['score'] * 0.35 +
            forecast['score'] * 0.35 +
            volatility['score'] * 0.15 +
            momentum['score'] * 0.15
        )

        return {
            'technical_score': technical['score'],
            'forecast_score': forecast['score'],
            'volatility_score': volatility['score'],
            'momentum_score': momentum['score'],
            'base_score': base_score,
            'details': {
                **technical['details'],
                **forecast['details'],
                **volatility['details'],
                **momentum['details']
            }
        }

    def _calculate_technical_score(self, df: pd.DataFrame) -> dict:
        """
        テクニカル指標からスコア算出

        指標:
        - RSI(14): 買われすぎ/売られすぎ
        - MACD: トレンド転換
        - Bollinger Bands: ボラティリティとポジション
        """

        rsi = self._calculate_rsi(df, period=14)
        macd_data = self._calculate_macd(df)
        bb_data = self._calculate_bollinger_bands(df)

        # スコアリングルール
        score = 0.0

        # RSI評価（0.4の重み）
        if 30 < rsi < 70:
            # 中立ゾーン: 50に近いほど高得点
            score += 0.4 * (1 - abs(rsi - 50) / 20)
        elif rsi <= 30:
            # 売られすぎ → 反発期待
            score += 0.6
        else:  # rsi >= 70
            # 買われすぎ → 注意
            score += 0.2

        # MACD評価（0.4の重み）
        macd_signal = macd_data['signal']
        macd_strength = macd_data['strength']

        if macd_signal == 'buy':
            score += 0.4 * macd_strength
        elif macd_signal == 'sell':
            score += 0.1
        else:  # neutral
            score += 0.25

        # Bollinger Bands評価（0.2の重み）
        bb_position = bb_data['position']

        if bb_position == 'middle':
            score += 0.2  # 安定
        elif bb_position == 'lower':
            score += 0.3  # 下限付近 → 反発期待
        elif bb_position == 'upper':
            score += 0.1  # 上限付近 → 過熱感
        else:  # 'below_lower' or 'above_upper'
            score += 0.15

        return {
            'score': min(score, 1.0),
            'details': {
                'rsi': rsi,
                'macd': macd_data,
                'bollinger': bb_data
            }
        }

    def _calculate_forecast_score(self, df: pd.DataFrame) -> dict:
        """
        予測モデルからスコア算出

        モデル: ARIMA/GARCH
        """

        try:
            result = self.forecasting_engine.combined_forecast(df, periods=7)

            if not result['price_forecast']['success']:
                return {
                    'score': 0.5,
                    'details': {
                        'current_price': float(df['close'].iloc[-1]),
                        'forecast_price_7d': None,
                        'forecast_return_7d': None,
                        'error': result['price_forecast'].get('error', 'Unknown')
                    }
                }

            current_price = result['current_price']
            forecast_price = result['price_forecast']['forecast'][-1]
            forecast_return = (forecast_price - current_price) / current_price

            # スコアリングルール
            if forecast_return > 0.1:  # +10%以上
                score = 0.95
            elif forecast_return > 0.05:  # +5-10%
                score = 0.80
            elif forecast_return > 0.02:  # +2-5%
                score = 0.60 + (forecast_return - 0.02) / 0.03 * 0.2
            elif forecast_return > 0:  # 0-2%
                score = 0.50 + forecast_return / 0.02 * 0.1
            elif forecast_return > -0.02:  # 0 to -2%
                score = 0.40 + forecast_return / 0.02 * 0.1
            elif forecast_return > -0.05:  # -2% to -5%
                score = 0.30 + (forecast_return + 0.05) / 0.03 * 0.1
            else:  # -5%以下
                score = 0.10

            return {
                'score': score,
                'details': {
                    'current_price': current_price,
                    'forecast_price_7d': forecast_price,
                    'forecast_return_7d': forecast_return,
                    'arima_order': result['price_forecast'].get('model_order', None),
                    'aic': result['price_forecast'].get('aic', None)
                }
            }

        except Exception as e:
            return {
                'score': 0.5,
                'details': {
                    'current_price': float(df['close'].iloc[-1]),
                    'forecast_price_7d': None,
                    'forecast_return_7d': None,
                    'error': str(e)
                }
            }

    def _calculate_volatility_score(self, df: pd.DataFrame) -> dict:
        """
        ボラティリティからリスクスコア算出

        低ボラティリティ = 高スコア（安全）
        """

        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * 100  # パーセント表示

        # スコアリングルール
        if volatility < 1.5:
            score = 0.9
            risk_level = "非常に低い"
        elif volatility < 3.0:
            score = 0.7
            risk_level = "低い"
        elif volatility < 5.0:
            score = 0.5
            risk_level = "中程度"
        elif volatility < 10.0:
            score = 0.3
            risk_level = "高い"
        else:
            score = 0.1
            risk_level = "非常に高い"

        return {
            'score': score,
            'details': {
                'volatility': volatility,
                'risk_level': risk_level
            }
        }

    def _calculate_momentum_score(self, df: pd.DataFrame) -> dict:
        """
        モメンタムスコア算出

        短期・中期・長期のリターンを評価
        """

        # 各期間のリターン
        returns_7d = df['close'].pct_change(7).iloc[-1] if len(df) >= 7 else 0
        returns_30d = df['close'].pct_change(30).iloc[-1] if len(df) >= 30 else 0
        returns_90d = df['close'].pct_change(90).iloc[-1] if len(df) >= 90 else 0

        # スコアリングルール
        score = 0.0

        # 各期間でプラスなら加点
        if returns_7d > 0:
            score += 0.3
        if returns_30d > 0:
            score += 0.4
        if returns_90d > 0:
            score += 0.3

        # ボーナス: 加速トレンド（短期 > 中期 > 長期）
        if len(df) >= 90:
            if returns_7d > returns_30d > returns_90d > 0:
                score += 0.2

        return {
            'score': min(score, 1.0),
            'details': {
                'returns_7d': returns_7d,
                'returns_30d': returns_30d,
                'returns_90d': returns_90d,
                'is_accelerating': returns_7d > returns_30d > returns_90d > 0 if len(df) >= 90 else False
            }
        }

    # ===== テクニカル指標の計算 =====

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """RSI計算"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return float(rsi.iloc[-1])

    def _calculate_macd(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> dict:
        """MACD計算"""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        # シグナル判定
        if histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0:
            signal_type = 'buy'
            strength = min(abs(histogram.iloc[-1]) / df['close'].iloc[-1] * 100, 1.0)
        elif histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0:
            signal_type = 'sell'
            strength = min(abs(histogram.iloc[-1]) / df['close'].iloc[-1] * 100, 1.0)
        elif histogram.iloc[-1] > 0:
            signal_type = 'buy'
            strength = min(abs(histogram.iloc[-1]) / df['close'].iloc[-1] * 100, 1.0) * 0.7
        elif histogram.iloc[-1] < 0:
            signal_type = 'sell'
            strength = min(abs(histogram.iloc[-1]) / df['close'].iloc[-1] * 100, 1.0) * 0.7
        else:
            signal_type = 'neutral'
            strength = 0.5

        return {
            'signal': signal_type,
            'strength': strength,
            'value': float(macd_line.iloc[-1]),
            'signal_line': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }

    def _calculate_bollinger_bands(self, df: pd.DataFrame, period=20, std_dev=2) -> dict:
        """Bollinger Bands計算"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        current_price = df['close'].iloc[-1]
        upper = upper_band.iloc[-1]
        middle = sma.iloc[-1]
        lower = lower_band.iloc[-1]

        # ポジション判定
        if current_price > upper:
            position = 'above_upper'
        elif current_price > middle:
            position = 'upper'
        elif current_price > lower:
            position = 'lower'
        else:
            position = 'below_lower'

        # バンド幅（ボラティリティ指標）
        bandwidth = (upper - lower) / middle * 100

        return {
            'position': position,
            'upper_band': float(upper),
            'middle_band': float(middle),
            'lower_band': float(lower),
            'bandwidth': float(bandwidth),
            'squeeze': bandwidth < 10  # バンド幅が狭い = スクイーズ
        }


def main():
    """テスト実行"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    from src.data.timeseries_storage import TimeSeriesStorage

    storage = TimeSeriesStorage()
    engine = MathematicalAnalysisEngine()

    # BTCの1日足データを読み込み
    df = storage.load_price_data('BTC', '1d')

    if df.empty:
        print("❌ BTCのデータがありません")
        return

    print("="*80)
    print("数学的分析エンジン テスト")
    print("="*80)
    print()

    # 分析実行
    result = engine.analyze('BTC', df)

    print("【総合スコア】")
    print(f"  基本スコア: {result['base_score']:.3f}")
    print()

    print("【スコア内訳】")
    print(f"  テクニカル分析: {result['technical_score']:.3f}")
    print(f"  予測分析:       {result['forecast_score']:.3f}")
    print(f"  リスク分析:     {result['volatility_score']:.3f}")
    print(f"  モメンタム分析: {result['momentum_score']:.3f}")
    print()

    print("【詳細データ】")
    details = result['details']

    print(f"\n■ テクニカル指標")
    print(f"  RSI(14): {details['rsi']:.2f}")
    print(f"  MACD: {details['macd']['signal'].upper()}シグナル (強度: {details['macd']['strength']:.2f})")
    print(f"  Bollinger Bands: {details['bollinger']['position']} (バンド幅: {details['bollinger']['bandwidth']:.2f}%)")

    print(f"\n■ 予測")
    if details['forecast_price_7d']:
        print(f"  現在価格: ${details['current_price']:,.2f}")
        print(f"  7日後予測: ${details['forecast_price_7d']:,.2f}")
        print(f"  予測リターン: {details['forecast_return_7d']*100:+.2f}%")
    else:
        print(f"  予測失敗: {details.get('error', 'Unknown')}")

    print(f"\n■ リスク")
    print(f"  ボラティリティ: {details['volatility']:.2f}%/日")
    print(f"  リスクレベル: {details['risk_level']}")

    print(f"\n■ モメンタム")
    print(f"  7日リターン:  {details['returns_7d']*100:+.2f}%")
    print(f"  30日リターン: {details['returns_30d']*100:+.2f}%")
    print(f"  90日リターン: {details['returns_90d']*100:+.2f}%")
    print(f"  加速トレンド: {'Yes' if details['is_accelerating'] else 'No'}")

    print()
    print("="*80)


if __name__ == '__main__':
    main()
