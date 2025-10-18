"""
出来高急増戦略

通常の10倍以上の出来高を検知して、
大きな値動きの前兆を捉える戦略
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.exchange_api import MEXCAPI
import numpy as np


class VolumeSpikeStrategy:
    """出来高急増戦略"""

    def __init__(self, spike_threshold: float = 3.0):
        """
        Args:
            spike_threshold: 出来高急増と判定する倍率（平均の何倍か）
        """
        self.spike_threshold = spike_threshold
        self.api = MEXCAPI()

    def calculate_volume_spike(self, volumes: list) -> dict:
        """
        出来高急増を計算

        Returns:
            dict: {
                'current_volume': 現在の出来高,
                'avg_volume': 平均出来高,
                'spike_ratio': 倍率,
                'is_spike': 急増判定
            }
        """
        if len(volumes) < 20:
            return {
                'current_volume': volumes[-1] if volumes else 0,
                'avg_volume': 0,
                'spike_ratio': 0,
                'is_spike': False
            }

        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[:-1])  # 直近を除く平均

        spike_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        is_spike = spike_ratio >= self.spike_threshold

        return {
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'spike_ratio': spike_ratio,
            'is_spike': is_spike
        }

    def check_price_action(self, klines: list) -> dict:
        """
        価格の動きをチェック

        出来高急増と同時に：
        - 価格が上昇している → 買いシグナル
        - 価格が下降している → 見送り
        """
        if len(klines) < 2:
            return {'bullish': False, 'bearish': False}

        latest = klines[-1]
        previous = klines[-2]

        # 価格変動
        price_change = ((latest['close'] - previous['close']) / previous['close']) * 100

        # 大陽線・大陰線の判定
        body = abs(latest['close'] - latest['open'])
        range_size = latest['high'] - latest['low']
        body_ratio = (body / range_size) if range_size > 0 else 0

        bullish = price_change > 2 and body_ratio > 0.6  # 大陽線
        bearish = price_change < -2 and body_ratio > 0.6  # 大陰線

        return {
            'price_change': price_change,
            'body_ratio': body_ratio,
            'bullish': bullish,
            'bearish': bearish
        }

    def check_buy_signal(self, symbol: str) -> dict:
        """
        買いシグナルをチェック

        条件:
        1. 出来高が平均の3倍以上
        2. 価格が上昇中（+2%以上）
        3. 大陽線が出ている
        """
        # ローソク足データ取得
        klines = self.api.get_klines(symbol, interval='1h', limit=50)
        if not klines:
            return {'signal': False, 'reason': 'データ取得失敗'}

        volumes = [k['volume'] for k in klines]
        prices = [k['close'] for k in klines]

        # 出来高急増チェック
        volume_data = self.calculate_volume_spike(volumes)

        # 価格の動きチェック
        price_action = self.check_price_action(klines)

        # 24時間統計
        stats = self.api.get_24h_stats(symbol)
        if not stats:
            return {'signal': False, 'reason': '統計取得失敗'}

        # 判定条件
        conditions = {
            'volume_spike': volume_data['is_spike'],
            'price_rising': price_action['bullish'],
            'positive_24h': stats['price_change_percent'] > 0,
        }

        buy_signal = all(conditions.values())

        return {
            'signal': buy_signal,
            'symbol': symbol,
            'price': stats['price'],
            'volume_spike_ratio': volume_data['spike_ratio'],
            'price_change': price_action['price_change'],
            'price_change_24h': stats['price_change_percent'],
            'conditions': conditions,
            'reason': '出来高急増＋上昇' if buy_signal else '条件不足'
        }

    def check_sell_signal(self, symbol: str, buy_price: float) -> dict:
        """
        売りシグナルをチェック

        出来高急増戦略は短期取引向け：
        - +20-30%で利確
        - -10%で損切り
        - 出来高が減って勢いがなくなったら売り
        """
        # ローソク足データ取得
        klines = self.api.get_klines(symbol, interval='1h', limit=50)
        if not klines:
            return {'signal': False, 'reason': 'データ取得失敗'}

        volumes = [k['volume'] for k in klines]
        current_price = klines[-1]['close']

        # 損益計算
        profit_loss_percent = ((current_price - buy_price) / buy_price) * 100

        # 出来高の勢いチェック
        volume_data = self.calculate_volume_spike(volumes)

        # 売りシグナル判定
        conditions = {
            'take_profit': profit_loss_percent >= 25,  # +25%で利確
            'stop_loss': profit_loss_percent <= -10,  # -10%で損切り
            'volume_decline': volume_data['spike_ratio'] < 1.0,  # 出来高減少
        }

        sell_signal = any([
            conditions['take_profit'],
            conditions['stop_loss'],
            conditions['volume_decline'] and profit_loss_percent > 10  # 利益出てて出来高減少
        ])

        return {
            'signal': sell_signal,
            'symbol': symbol,
            'current_price': current_price,
            'buy_price': buy_price,
            'profit_loss_percent': profit_loss_percent,
            'volume_spike_ratio': volume_data['spike_ratio'],
            'conditions': conditions,
            'reason': self._get_sell_reason(conditions, profit_loss_percent)
        }

    def _get_sell_reason(self, conditions: dict, profit_percent: float) -> str:
        """売却理由を返す"""
        if conditions['take_profit']:
            return '利確（+25%達成）'
        elif conditions['stop_loss']:
            return '損切り（-10%到達）'
        elif conditions['volume_decline'] and profit_percent > 10:
            return '出来高減少・利確'
        else:
            return '保持継続'

    def scan_for_volume_spikes(self, min_volume_usdt: float = 100000) -> list:
        """
        市場をスキャンして出来高急増を検知
        """
        print("[*] 出来高急増をスキャン中...")

        trending = self.api.get_trending_coins(min_volume_usdt=min_volume_usdt)

        spikes = []
        checked = 0

        for coin in trending[:30]:  # 上位30件をチェック
            symbol = coin['symbol']
            checked += 1

            if checked % 10 == 0:
                print(f"  チェック済み: {checked}件...")

            result = self.check_buy_signal(symbol)

            if result['signal']:
                spikes.append(result)
                print(f"  [OK] {symbol}: 出来高 {result['volume_spike_ratio']:.1f}x, "
                      f"価格変動 {result['price_change_24h']:.2f}%")

        return spikes

    def get_hot_coins(self) -> list:
        """
        急騰＋出来高急増のコインを探す（最も狙い目）
        """
        print("[*] 激アツコインを検索中...")

        # 急騰コインを取得
        pumping = self.api.find_pumping_coins(min_change_percent=10.0)

        hot_coins = []

        for coin in pumping[:20]:
            symbol = coin['symbol']

            # 出来高急増もチェック
            klines = self.api.get_klines(symbol, interval='1h', limit=50)
            if not klines:
                continue

            volumes = [k['volume'] for k in klines]
            volume_data = self.calculate_volume_spike(volumes)

            if volume_data['is_spike']:
                hot_coins.append({
                    'symbol': symbol,
                    'price': coin['price'],
                    'price_change_24h': coin['change_percent'],
                    'volume_spike_ratio': volume_data['spike_ratio'],
                    'score': coin['change_percent'] * volume_data['spike_ratio']
                })

        # スコア順にソート
        hot_coins.sort(key=lambda x: x['score'], reverse=True)

        return hot_coins


def main():
    """テスト実行"""
    print("📊 出来高急増戦略をテスト\n")

    strategy = VolumeSpikeStrategy(spike_threshold=3.0)

    # 特定のシンボルをチェック
    test_symbols = ['BTCUSDT', 'SHIBUSDT', 'PEPEUSDT']

    for symbol in test_symbols:
        print(f"\n{'='*50}")
        print(f"🔍 {symbol} を分析")
        print('='*50)

        result = strategy.check_buy_signal(symbol)

        print(f"価格: ${result.get('price', 'N/A')}")
        print(f"出来高急増倍率: {result.get('volume_spike_ratio', 0):.2f}x")
        print(f"価格変動(直近): {result.get('price_change', 0):.2f}%")
        print(f"24時間変動: {result.get('price_change_24h', 0):.2f}%")
        print(f"\n買いシグナル: {'✅ あり' if result['signal'] else '❌ なし'}")
        print(f"理由: {result['reason']}")

    # 激アツコインを検索
    print(f"\n{'='*50}")
    print("🔥 激アツコイン（急騰＋出来高急増）")
    print('='*50)

    hot_coins = strategy.get_hot_coins()

    if hot_coins:
        print(f"\n✅ {len(hot_coins)}個発見！\n")
        for i, coin in enumerate(hot_coins[:5], 1):
            print(f"{i}. {coin['symbol']}")
            print(f"   価格変動: {coin['price_change_24h']:+.2f}%")
            print(f"   出来高: {coin['volume_spike_ratio']:.1f}x")
            print(f"   スコア: {coin['score']:.1f}")
            print()
    else:
        print("\n❌ 該当なし")


if __name__ == '__main__':
    main()
