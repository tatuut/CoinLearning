"""
ARIMA/GARCH予測エンジン

価格予測とボラティリティ予測を行います
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')


class ForecastingEngine:
    """ARIMA/GARCH予測エンジン"""

    def __init__(self):
        pass

    def forecast_price_arima(self, df: pd.DataFrame, periods: int = 7, order=(1, 1, 1)):
        """
        ARIMAモデルで価格予測

        Args:
            df: 価格データ（DatetimeIndex付きDataFrame）
            periods: 予測期間（日数）
            order: ARIMA(p,d,q)のパラメータ

        Returns:
            dict: 予測結果
                - forecast: 予測値のリスト
                - conf_int: 信頼区間（上限・下限）
                - model_summary: モデル情報
        """
        try:
            # 終値を使用
            prices = df['close'].dropna()

            if len(prices) < 30:
                return {
                    'success': False,
                    'error': 'データ不足（最低30日分必要）',
                    'forecast': [],
                    'conf_int': None
                }

            # ARIMAモデル構築
            model = ARIMA(prices, order=order)
            fitted_model = model.fit()

            # 予測
            forecast_result = fitted_model.forecast(steps=periods)
            forecast_values = forecast_result.values if hasattr(forecast_result, 'values') else forecast_result

            # 予測区間を取得（statsmodelsのバージョンによって異なる）
            try:
                pred = fitted_model.get_forecast(steps=periods)
                conf_int = pred.conf_int()
            except:
                # 簡易的な信頼区間（±5%）
                conf_int = pd.DataFrame({
                    'lower': forecast_values * 0.95,
                    'upper': forecast_values * 1.05
                })

            return {
                'success': True,
                'forecast': forecast_values.tolist() if hasattr(forecast_values, 'tolist') else list(forecast_values),
                'conf_int_lower': conf_int.iloc[:, 0].tolist(),
                'conf_int_upper': conf_int.iloc[:, 1].tolist(),
                'model_order': order,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'forecast': [],
                'conf_int': None
            }

    def forecast_volatility_garch(self, df: pd.DataFrame, periods: int = 7, p=1, q=1):
        """
        GARCHモデルでボラティリティ予測

        Args:
            df: 価格データ（DatetimeIndex付きDataFrame）
            periods: 予測期間（日数）
            p: GARCHのpパラメータ
            q: GARCHのqパラメータ

        Returns:
            dict: 予測結果
                - volatility_forecast: ボラティリティ予測値（標準偏差%）
                - returns_forecast: リターン予測の標準偏差
        """
        try:
            # リターンを計算
            returns = df['close'].pct_change().dropna() * 100  # パーセント表示

            if len(returns) < 100:
                return {
                    'success': False,
                    'error': 'データ不足（最低100日分必要）',
                    'volatility_forecast': []
                }

            # GARCHモデル構築
            model = arch_model(returns, vol='Garch', p=p, q=q)
            fitted_model = model.fit(disp='off')

            # 予測
            forecast = fitted_model.forecast(horizon=periods)

            # ボラティリティ予測値（標準偏差）
            volatility = np.sqrt(forecast.variance.values[-1, :])

            return {
                'success': True,
                'volatility_forecast': volatility.tolist(),
                'mean_volatility': float(volatility.mean()),
                'current_volatility': float(returns.std()),
                'model': f'GARCH({p},{q})',
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'volatility_forecast': []
            }

    def auto_select_arima_order(self, df: pd.DataFrame, max_p=5, max_d=2, max_q=5):
        """
        AICを最小化するARIMAパラメータを自動選択

        Args:
            df: 価格データ
            max_p: pの最大値
            max_d: dの最大値
            max_q: qの最大値

        Returns:
            tuple: 最適な(p, d, q)
        """
        prices = df['close'].dropna()

        if len(prices) < 30:
            return (1, 1, 1)  # デフォルト

        best_aic = np.inf
        best_order = (1, 1, 1)

        # グリッドサーチ（計算時間を考慮して範囲を制限）
        for p in range(0, min(3, max_p)):
            for d in range(0, min(2, max_d)):
                for q in range(0, min(3, max_q)):
                    try:
                        model = ARIMA(prices, order=(p, d, q))
                        fitted = model.fit()
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                    except:
                        continue

        return best_order

    def combined_forecast(self, df: pd.DataFrame, periods: int = 7):
        """
        ARIMA価格予測 + GARCHボラティリティ予測の統合

        Args:
            df: 価格データ
            periods: 予測期間

        Returns:
            dict: 統合予測結果
        """
        # 最適なARIMAパラメータを選択
        best_order = self.auto_select_arima_order(df)

        # ARIMA予測
        price_forecast = self.forecast_price_arima(df, periods=periods, order=best_order)

        # GARCHボラティリティ予測
        volatility_forecast = self.forecast_volatility_garch(df, periods=periods)

        # 統合結果
        result = {
            'price_forecast': price_forecast,
            'volatility_forecast': volatility_forecast,
            'periods': periods,
            'current_price': float(df['close'].iloc[-1]),
        }

        # 予測成功時に簡易サマリーを追加
        if price_forecast['success'] and volatility_forecast['success']:
            forecasts = price_forecast['forecast']
            volatilities = volatility_forecast['volatility_forecast']

            result['summary'] = {
                'predicted_price_7d': forecasts[-1] if len(forecasts) >= 7 else forecasts[-1],
                'expected_return_7d': ((forecasts[-1] - result['current_price']) / result['current_price'] * 100) if len(forecasts) > 0 else 0,
                'mean_volatility': volatility_forecast['mean_volatility'],
                'risk_level': self._classify_risk(volatility_forecast['mean_volatility']),
            }

        return result

    def _classify_risk(self, volatility: float) -> str:
        """
        ボラティリティからリスクレベルを分類

        Args:
            volatility: ボラティリティ（%）

        Returns:
            str: リスクレベル
        """
        if volatility < 1.5:
            return "非常に低い"
        elif volatility < 3.0:
            return "低い"
        elif volatility < 5.0:
            return "中程度"
        elif volatility < 10.0:
            return "高い"
        else:
            return "非常に高い"

    def explain_forecast(self, forecast_result: dict) -> str:
        """
        予測結果をわかりやすく説明

        Args:
            forecast_result: combined_forecast()の結果

        Returns:
            str: 説明文（Markdown形式）
        """
        if not forecast_result['price_forecast']['success']:
            return f"❌ 価格予測に失敗しました: {forecast_result['price_forecast']['error']}"

        if not forecast_result['volatility_forecast']['success']:
            return f"⚠️ ボラティリティ予測に失敗しました: {forecast_result['volatility_forecast']['error']}"

        summary = forecast_result.get('summary', {})
        current_price = forecast_result['current_price']
        predicted_price = summary.get('predicted_price_7d', 0)
        expected_return = summary.get('expected_return_7d', 0)
        volatility = summary.get('mean_volatility', 0)
        risk_level = summary.get('risk_level', '不明')

        explanation = f"""
## 📊 予測結果サマリー

### 価格予測（7日後）
- **現在価格**: ${current_price:,.2f}
- **予測価格**: ${predicted_price:,.2f}
- **期待リターン**: {expected_return:+.2f}%

### リスク評価
- **平均ボラティリティ**: {volatility:.2f}%/日
- **リスクレベル**: {risk_level}

### 解説

"""

        if expected_return > 5:
            explanation += "✅ モデルは**大きな上昇**を予測しています。ただし、過去データに基づく予測なので、実際の価格は異なる可能性があります。\n\n"
        elif expected_return > 0:
            explanation += "↗️ モデルは**緩やかな上昇**を予測しています。\n\n"
        elif expected_return > -5:
            explanation += "↘️ モデルは**緩やかな下落**を予測しています。\n\n"
        else:
            explanation += "❌ モデルは**大きな下落**を予測しています。注意が必要です。\n\n"

        if volatility > 5:
            explanation += "⚠️ ボラティリティが**非常に高い**です。価格が大きく変動する可能性があるため、リスク管理が重要です。\n\n"
        elif volatility > 3:
            explanation += "ℹ️ ボラティリティは**中程度**です。通常の変動範囲内です。\n\n"
        else:
            explanation += "✅ ボラティリティは**低い**です。比較的安定した値動きが期待できます。\n\n"

        explanation += """
**注意**: この予測は過去のデータに基づく統計モデルです。実際の価格は、ニュース、規制、市場心理など様々な要因で変動します。投資判断は慎重に行ってください。
"""

        return explanation


def main():
    """テスト実行"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    from sample.data.timeseries_storage import TimeSeriesStorage

    storage = TimeSeriesStorage()
    engine = ForecastingEngine()

    # BTCの1日足データを読み込み
    df = storage.load_price_data('BTC', '1d')

    if df.empty:
        print("❌ BTCのデータがありません")
        return

    print("="*80)
    print("ARIMA/GARCH 予測テスト")
    print("="*80)
    print()

    # 統合予測
    result = engine.combined_forecast(df, periods=7)

    # 結果表示
    print(engine.explain_forecast(result))

    print("="*80)
    print("詳細データ")
    print("="*80)

    if result['price_forecast']['success']:
        print("\n【価格予測（1-7日後）】")
        for i, price in enumerate(result['price_forecast']['forecast'], 1):
            print(f"  {i}日後: ${price:,.2f}")

    if result['volatility_forecast']['success']:
        print("\n【ボラティリティ予測（1-7日後）】")
        for i, vol in enumerate(result['volatility_forecast']['volatility_forecast'], 1):
            print(f"  {i}日後: {vol:.2f}%/日")


if __name__ == '__main__':
    main()
