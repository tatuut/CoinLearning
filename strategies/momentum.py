"""
モメンタム戦略

価格が上昇トレンドにある時に買い、
勢いが衰えたら売る戦略
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.exchange_api import BinanceAPI
import numpy as np


class MomentumStrategy:
    """モメンタム戦略"""

    def __init__(self, lookback_period: int = 20):
        """
        Args:
            lookback_period: モメンタム計算に使う期間（ローソク足の本数）
        """
        self.lookback_period = lookback_period
        self.api = BinanceAPI()

    def calculate_momentum(self, prices: list) -> float:
        """
        モメンタムを計算

        モメンタム = 現在価格 - N期間前の価格
        """
        if len(prices) < self.lookback_period:
            return 0

        current = prices[-1]
        past = prices[-self.lookback_period]

        momentum = ((current - past) / past) * 100
        return momentum

    def calculate_roc(self, prices: list) -> float:
        """
        ROC (Rate of Change) を計算

        ROC = ((現在価格 - N期間前の価格) / N期間前の価格) * 100
        """
        if len(prices) < self.lookback_period:
            return 0

        current = prices[-1]
        past = prices[-self.lookback_period]

        roc = ((current - past) / past) * 100
        return roc

    def calculate_macd(self, prices: list) -> dict:
        """
        MACD (Moving Average Convergence Divergence) を計算

        MACD = EMA(12) - EMA(26)
        Signal = EMA(9) of MACD
        """
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}

        prices_array = np.array(prices)

        # EMA計算
        ema12 = self._calculate_ema(prices_array, 12)
        ema26 = self._calculate_ema(prices_array, 26)

        macd = ema12 - ema26

        # シグナルライン（MACDの9期間EMA）
        # 簡易計算のため、直近の値のみ返す
        signal = macd  # 本来はMACDの9期間EMAだが簡略化

        histogram = macd - signal

        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }

    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """EMA (Exponential Moving Average) を計算"""
        if len(prices) < period:
            return prices[-1]

        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])  # 最初はSMA

        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def check_buy_signal(self, symbol: str) -> dict:
        """
        買いシグナルをチェック

        条件:
        1. モメンタムがプラス（上昇トレンド）
        2. ROCが一定以上（勢いがある）
        3. 価格変動が24時間で+5%以上
        """
        # ローソク足データ取得
        klines = self.api.get_klines(symbol, interval='1h', limit=50)
        if not klines:
            return {'signal': False, 'reason': 'データ取得失敗'}

        prices = [k['close'] for k in klines]

        # 24時間統計取得
        stats = self.api.get_24h_stats(symbol)
        if not stats:
            return {'signal': False, 'reason': '統計取得失敗'}

        # モメンタム計算
        momentum = self.calculate_momentum(prices)
        roc = self.calculate_roc(prices)

        # 判定
        conditions = {
            'momentum_positive': momentum > 0,
            'strong_momentum': momentum > 5,  # 5%以上の上昇
            'roc_positive': roc > 3,  # 3%以上のROC
            'price_change': stats['price_change_percent'] > 5,  # 24時間で+5%
        }

        # 全ての条件を満たすか
        buy_signal = all(conditions.values())

        return {
            'signal': buy_signal,
            'symbol': symbol,
            'price': stats['price'],
            'momentum': momentum,
            'roc': roc,
            'price_change_24h': stats['price_change_percent'],
            'conditions': conditions,
            'reason': 'モメンタム上昇トレンド' if buy_signal else '条件不足'
        }

    def check_sell_signal(self, symbol: str, buy_price: float) -> dict:
        """
        売りシグナルをチェック

        条件:
        1. モメンタムがマイナス（下降トレンド）
        2. 利益が出ている場合は早めに利確
        3. 損失が一定以上なら損切り
        """
        # ローソク足データ取得
        klines = self.api.get_klines(symbol, interval='1h', limit=50)
        if not klines:
            return {'signal': False, 'reason': 'データ取得失敗'}

        prices = [k['close'] for k in klines]
        current_price = prices[-1]

        # 損益計算
        profit_loss_percent = ((current_price - buy_price) / buy_price) * 100

        # モメンタム計算
        momentum = self.calculate_momentum(prices)

        # 売りシグナル判定
        conditions = {
            'take_profit': profit_loss_percent >= 20,  # +20%で利確
            'stop_loss': profit_loss_percent <= -10,  # -10%で損切り
            'momentum_negative': momentum < -3,  # モメンタム下降
        }

        sell_signal = any([
            conditions['take_profit'],
            conditions['stop_loss'],
            conditions['momentum_negative']
        ])

        return {
            'signal': sell_signal,
            'symbol': symbol,
            'current_price': current_price,
            'buy_price': buy_price,
            'profit_loss_percent': profit_loss_percent,
            'momentum': momentum,
            'conditions': conditions,
            'reason': self._get_sell_reason(conditions)
        }

    def _get_sell_reason(self, conditions: dict) -> str:
        """売却理由を返す"""
        if conditions['take_profit']:
            return '利確（+20%達成）'
        elif conditions['stop_loss']:
            return '損切り（-10%到達）'
        elif conditions['momentum_negative']:
            return 'モメンタム低下'
        else:
            return '保持継続'

    def scan_market(self, min_volume_usdt: float = 100000) -> list:
        """
        市場をスキャンして買いシグナルのあるコインを探す
        """
        print("[*] 市場をスキャン中...")

        trending = self.api.get_trending_coins(min_volume_usdt=min_volume_usdt)

        signals = []
        for coin in trending[:20]:  # 上位20件をチェック
            symbol = coin['symbol']
            result = self.check_buy_signal(symbol)

            if result['signal']:
                signals.append(result)
                print(f"[OK] {symbol}: モメンタム {result['momentum']:.2f}%")

        return signals


def main():
    """テスト実行"""
    print("📈 モメンタム戦略をテスト\n")

    strategy = MomentumStrategy(lookback_period=20)

    # 特定のシンボルをチェック
    test_symbols = ['BTCUSDT', 'SHIBUSDT', 'PEPEUSDT']

    for symbol in test_symbols:
        print(f"\n{'='*50}")
        print(f"🔍 {symbol} を分析")
        print('='*50)

        result = strategy.check_buy_signal(symbol)

        print(f"価格: ${result.get('price', 'N/A')}")
        print(f"モメンタム: {result.get('momentum', 0):.2f}%")
        print(f"ROC: {result.get('roc', 0):.2f}%")
        print(f"24時間変動: {result.get('price_change_24h', 0):.2f}%")
        print(f"\n買いシグナル: {'✅ あり' if result['signal'] else '❌ なし'}")
        print(f"理由: {result['reason']}")

    # 市場全体をスキャン
    print(f"\n{'='*50}")
    print("🌍 市場全体をスキャン")
    print('='*50)

    signals = strategy.scan_market(min_volume_usdt=50000)

    if signals:
        print(f"\n✅ {len(signals)}個の買いシグナルを発見！\n")
        for sig in signals[:5]:
            print(f"  {sig['symbol']}: モメンタム {sig['momentum']:.2f}%, "
                  f"24h変動 {sig['price_change_24h']:.2f}%")
    else:
        print("\n❌ 買いシグナルなし")


if __name__ == '__main__':
    main()
