"""
ブレイクアウト戦略

価格がレンジ（ボリンジャーバンド）を突破した時に
大きな値動きを狙う戦略
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.exchange_api import BinanceAPI
import numpy as np


class BreakoutStrategy:
    """ブレイクアウト戦略"""

    def __init__(self, bb_period: int = 20, bb_std: float = 2.0):
        """
        Args:
            bb_period: ボリンジャーバンドの期間
            bb_std: 標準偏差の倍率
        """
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.api = BinanceAPI()

    def calculate_bollinger_bands(self, prices: list) -> dict:
        """
        ボリンジャーバンドを計算

        Returns:
            dict: {
                'upper': 上限バンド,
                'middle': 中央線（移動平均）,
                'lower': 下限バンド,
                'bandwidth': バンド幅
            }
        """
        if len(prices) < self.bb_period:
            return {
                'upper': 0,
                'middle': 0,
                'lower': 0,
                'bandwidth': 0
            }

        prices_array = np.array(prices[-self.bb_period:])

        # 移動平均（中央線）
        middle = np.mean(prices_array)

        # 標準偏差
        std = np.std(prices_array)

        # 上限・下限
        upper = middle + (self.bb_std * std)
        lower = middle - (self.bb_std * std)

        # バンド幅（ボラティリティの指標）
        bandwidth = ((upper - lower) / middle) * 100

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'bandwidth': bandwidth
        }

    def detect_squeeze(self, klines: list) -> dict:
        """
        スクイーズ（バンド幅が狭くなる）を検出

        スクイーズ後はブレイクアウトが起きやすい
        """
        if len(klines) < 30:
            return {'is_squeeze': False, 'bandwidth': 0}

        bandwidths = []
        for i in range(10):  # 直近10本分
            prices = [k['close'] for k in klines[:-(10-i)] if klines[:-(10-i)]]
            if len(prices) >= self.bb_period:
                bb = self.calculate_bollinger_bands(prices)
                bandwidths.append(bb['bandwidth'])

        if not bandwidths:
            return {'is_squeeze': False, 'bandwidth': 0}

        current_bandwidth = bandwidths[-1]
        avg_bandwidth = np.mean(bandwidths)

        # 現在のバンド幅が平均より小さい → スクイーズ
        is_squeeze = current_bandwidth < avg_bandwidth * 0.7

        return {
            'is_squeeze': is_squeeze,
            'current_bandwidth': current_bandwidth,
            'avg_bandwidth': avg_bandwidth
        }

    def check_breakout(self, prices: list, bb: dict) -> dict:
        """
        ブレイクアウトを検出

        - 上限突破 → 上昇ブレイクアウト（買い）
        - 下限突破 → 下降ブレイクアウト（見送り）
        """
        if not prices or not bb or bb['upper'] == 0:
            return {'breakout': False, 'direction': None}

        current_price = prices[-1]

        # 上限突破
        if current_price > bb['upper']:
            return {
                'breakout': True,
                'direction': 'up',
                'price': current_price,
                'upper': bb['upper']
            }

        # 下限突破
        if current_price < bb['lower']:
            return {
                'breakout': True,
                'direction': 'down',
                'price': current_price,
                'lower': bb['lower']
            }

        return {'breakout': False, 'direction': None}

    def calculate_rsi(self, prices: list, period: int = 14) -> float:
        """
        RSI (Relative Strength Index) を計算
        """
        if len(prices) < period + 1:
            return 50

        prices_array = np.array(prices)
        deltas = np.diff(prices_array)

        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def check_buy_signal(self, symbol: str) -> dict:
        """
        買いシグナルをチェック

        条件:
        1. ボリンジャーバンド上限を突破
        2. スクイーズ後のブレイクアウト（より強い）
        3. RSIが50以上（上昇の勢いあり）
        """
        # ローソク足データ取得
        klines = self.api.get_klines(symbol, interval='1h', limit=50)
        if not klines:
            return {'signal': False, 'reason': 'データ取得失敗'}

        prices = [k['close'] for k in klines]

        # ボリンジャーバンド計算
        bb = self.calculate_bollinger_bands(prices)

        # ブレイクアウト検出
        breakout = self.check_breakout(prices, bb)

        # スクイーズ検出
        squeeze = self.detect_squeeze(klines)

        # RSI計算
        rsi = self.calculate_rsi(prices)

        # 24時間統計
        stats = self.api.get_24h_stats(symbol)
        if not stats:
            return {'signal': False, 'reason': '統計取得失敗'}

        # 判定条件
        conditions = {
            'upward_breakout': breakout['breakout'] and breakout['direction'] == 'up',
            'rsi_bullish': rsi >= 50,
            'squeeze_detected': squeeze['is_squeeze'],  # オプション（より強い）
        }

        # 基本条件：上昇ブレイクアウト + RSI
        buy_signal = conditions['upward_breakout'] and conditions['rsi_bullish']

        # スクイーズ後のブレイクアウトは特に強い
        if conditions['squeeze_detected']:
            buy_signal = buy_signal and True  # すでにTrueなら変わらない

        return {
            'signal': buy_signal,
            'symbol': symbol,
            'price': stats['price'],
            'bb_upper': bb['upper'],
            'bb_middle': bb['middle'],
            'bb_lower': bb['lower'],
            'bandwidth': bb['bandwidth'],
            'rsi': rsi,
            'breakout_direction': breakout.get('direction'),
            'squeeze': squeeze['is_squeeze'],
            'conditions': conditions,
            'reason': '上昇ブレイクアウト' if buy_signal else '条件不足'
        }

    def check_sell_signal(self, symbol: str, buy_price: float) -> dict:
        """
        売りシグナルをチェック

        ブレイクアウト戦略は大きな利益を狙う：
        - +30-50%で利確
        - -10%で損切り
        - 価格がボリンジャーバンド中央線を下回ったら売り
        """
        # ローソク足データ取得
        klines = self.api.get_klines(symbol, interval='1h', limit=50)
        if not klines:
            return {'signal': False, 'reason': 'データ取得失敗'}

        prices = [k['close'] for k in klines]
        current_price = prices[-1]

        # 損益計算
        profit_loss_percent = ((current_price - buy_price) / buy_price) * 100

        # ボリンジャーバンド計算
        bb = self.calculate_bollinger_bands(prices)

        # RSI
        rsi = self.calculate_rsi(prices)

        # 売りシグナル判定
        conditions = {
            'take_profit': profit_loss_percent >= 30,  # +30%で利確
            'stop_loss': profit_loss_percent <= -10,  # -10%で損切り
            'below_middle': current_price < bb['middle'],  # 中央線を下回る
            'rsi_overbought': rsi > 75,  # 買われすぎ
        }

        sell_signal = any([
            conditions['take_profit'],
            conditions['stop_loss'],
            conditions['below_middle'] and profit_loss_percent > 15,  # 利益出てて中央線割れ
            conditions['rsi_overbought'] and profit_loss_percent > 20,  # 利益出てて過熱
        ])

        return {
            'signal': sell_signal,
            'symbol': symbol,
            'current_price': current_price,
            'buy_price': buy_price,
            'profit_loss_percent': profit_loss_percent,
            'bb_middle': bb['middle'],
            'rsi': rsi,
            'conditions': conditions,
            'reason': self._get_sell_reason(conditions, profit_loss_percent)
        }

    def _get_sell_reason(self, conditions: dict, profit_percent: float) -> str:
        """売却理由を返す"""
        if conditions['take_profit']:
            return '利確（+30%達成）'
        elif conditions['stop_loss']:
            return '損切り（-10%到達）'
        elif conditions['below_middle'] and profit_percent > 15:
            return '中央線割れ・利確'
        elif conditions['rsi_overbought'] and profit_percent > 20:
            return '買われすぎ・利確'
        else:
            return '保持継続'

    def scan_for_breakouts(self, min_volume_usdt: float = 100000) -> list:
        """
        市場をスキャンしてブレイクアウトを検知
        """
        print("🔍 ブレイクアウトをスキャン中...")

        trending = self.api.get_trending_coins(min_volume_usdt=min_volume_usdt)

        breakouts = []
        checked = 0

        for coin in trending[:30]:  # 上位30件をチェック
            symbol = coin['symbol']
            checked += 1

            if checked % 10 == 0:
                print(f"  チェック済み: {checked}件...")

            result = self.check_buy_signal(symbol)

            if result['signal']:
                breakouts.append(result)
                squeeze_mark = "🔥" if result['squeeze'] else ""
                print(f"  ✅ {symbol} {squeeze_mark}: RSI {result['rsi']:.1f}, "
                      f"バンド幅 {result['bandwidth']:.2f}%")

        return breakouts


def main():
    """テスト実行"""
    print("📈 ブレイクアウト戦略をテスト\n")

    strategy = BreakoutStrategy(bb_period=20, bb_std=2.0)

    # 特定のシンボルをチェック
    test_symbols = ['BTCUSDT', 'SHIBUSDT', 'PEPEUSDT']

    for symbol in test_symbols:
        print(f"\n{'='*50}")
        print(f"🔍 {symbol} を分析")
        print('='*50)

        result = strategy.check_buy_signal(symbol)

        print(f"価格: ${result.get('price', 'N/A')}")
        print(f"ボリンジャーバンド:")
        print(f"  上限: ${result.get('bb_upper', 0):.8f}")
        print(f"  中央: ${result.get('bb_middle', 0):.8f}")
        print(f"  下限: ${result.get('bb_lower', 0):.8f}")
        print(f"  バンド幅: {result.get('bandwidth', 0):.2f}%")
        print(f"RSI: {result.get('rsi', 0):.2f}")
        print(f"スクイーズ: {'✅ あり' if result.get('squeeze') else '❌ なし'}")
        print(f"\n買いシグナル: {'✅ あり' if result['signal'] else '❌ なし'}")
        print(f"理由: {result['reason']}")

    # 市場全体をスキャン
    print(f"\n{'='*50}")
    print("🌍 ブレイクアウトをスキャン")
    print('='*50)

    breakouts = strategy.scan_for_breakouts(min_volume_usdt=50000)

    if breakouts:
        print(f"\n✅ {len(breakouts)}個のブレイクアウトを発見！\n")
        for i, bo in enumerate(breakouts[:5], 1):
            squeeze_mark = "🔥 [スクイーズ後]" if bo['squeeze'] else ""
            print(f"{i}. {bo['symbol']} {squeeze_mark}")
            print(f"   RSI: {bo['rsi']:.1f}")
            print(f"   バンド幅: {bo['bandwidth']:.2f}%")
            print()
    else:
        print("\n❌ ブレイクアウトなし")


if __name__ == '__main__':
    main()
