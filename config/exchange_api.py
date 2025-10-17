"""
取引所API連携
Binance, MEXCなどの主要取引所に対応
"""

import requests
import time
import hmac
import hashlib
from typing import Dict, List, Optional
from urllib.parse import urlencode
import json
import os


class ExchangeAPI:
    """取引所API基底クラス"""

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_price(self, symbol: str) -> float:
        """現在価格を取得"""
        raise NotImplementedError

    def get_24h_stats(self, symbol: str) -> Dict:
        """24時間統計を取得"""
        raise NotImplementedError

    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List:
        """ローソク足データを取得"""
        raise NotImplementedError

    def buy(self, symbol: str, quantity: float) -> Dict:
        """成行買い注文"""
        raise NotImplementedError

    def sell(self, symbol: str, quantity: float) -> Dict:
        """成行売り注文"""
        raise NotImplementedError


class BinanceAPI(ExchangeAPI):
    """Binance API"""

    BASE_URL = 'https://api.binance.com'

    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__(api_key, api_secret)

    def _sign_request(self, params: Dict) -> str:
        """リクエストに署名"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def get_price(self, symbol: str) -> float:
        """現在価格を取得（認証不要）"""
        url = f'{self.BASE_URL}/api/v3/ticker/price'
        params = {'symbol': symbol}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"❌ 価格取得エラー: {e}")
            return None

    def get_24h_stats(self, symbol: str) -> Dict:
        """24時間統計を取得（認証不要）"""
        url = f'{self.BASE_URL}/api/v3/ticker/24hr'
        params = {'symbol': symbol}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                'symbol': data['symbol'],
                'price': float(data['lastPrice']),
                'price_change_percent': float(data['priceChangePercent']),
                'high': float(data['highPrice']),
                'low': float(data['lowPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
            }
        except Exception as e:
            print(f"❌ 統計取得エラー: {e}")
            return None

    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List:
        """
        ローソク足データを取得（認証不要）

        interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        """
        url = f'{self.BASE_URL}/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            klines = response.json()

            # フォーマット変換
            formatted = []
            for k in klines:
                formatted.append({
                    'timestamp': k[0],
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5]),
                })

            return formatted
        except Exception as e:
            print(f"❌ ローソク足取得エラー: {e}")
            return None

    def get_trending_coins(self, min_volume_usdt: float = 100000) -> List[Dict]:
        """トレンドコインを取得（出来高が多い順）"""
        url = f'{self.BASE_URL}/api/v3/ticker/24hr'

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # USDT建てのみフィルタ & 出来高でソート
            usdt_pairs = [
                {
                    'symbol': item['symbol'],
                    'price': float(item['lastPrice']),
                    'change_percent': float(item['priceChangePercent']),
                    'volume_usdt': float(item['quoteVolume']),
                }
                for item in data
                if item['symbol'].endswith('USDT') and float(item['quoteVolume']) > min_volume_usdt
            ]

            # 出来高順にソート
            usdt_pairs.sort(key=lambda x: x['volume_usdt'], reverse=True)

            return usdt_pairs[:50]  # トップ50
        except Exception as e:
            print(f"❌ トレンドコイン取得エラー: {e}")
            return []

    def find_pumping_coins(self, min_change_percent: float = 10.0) -> List[Dict]:
        """急騰中のコインを探す"""
        url = f'{self.BASE_URL}/api/v3/ticker/24hr'

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            pumping = [
                {
                    'symbol': item['symbol'],
                    'price': float(item['lastPrice']),
                    'change_percent': float(item['priceChangePercent']),
                    'volume_usdt': float(item['quoteVolume']),
                }
                for item in data
                if item['symbol'].endswith('USDT') and
                float(item['priceChangePercent']) >= min_change_percent
            ]

            # 変動率順にソート
            pumping.sort(key=lambda x: x['change_percent'], reverse=True)

            return pumping
        except Exception as e:
            print(f"❌ 急騰コイン検索エラー: {e}")
            return []

    def buy(self, symbol: str, quantity: float) -> Dict:
        """成行買い注文（要認証）"""
        if not self.api_key or not self.api_secret:
            return {'error': 'API Key/Secretが設定されていません'}

        url = f'{self.BASE_URL}/api/v3/order'
        timestamp = int(time.time() * 1000)

        params = {
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': quantity,
            'timestamp': timestamp,
        }

        params['signature'] = self._sign_request(params)

        headers = {'X-MBX-APIKEY': self.api_key}

        try:
            response = requests.post(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def sell(self, symbol: str, quantity: float) -> Dict:
        """成行売り注文（要認証）"""
        if not self.api_key or not self.api_secret:
            return {'error': 'API Key/Secretが設定されていません'}

        url = f'{self.BASE_URL}/api/v3/order'
        timestamp = int(time.time() * 1000)

        params = {
            'symbol': symbol,
            'side': 'SELL',
            'type': 'MARKET',
            'quantity': quantity,
            'timestamp': timestamp,
        }

        params['signature'] = self._sign_request(params)

        headers = {'X-MBX-APIKEY': self.api_key}

        try:
            response = requests.post(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def get_account_balance(self) -> Dict:
        """アカウント残高を取得（要認証）"""
        if not self.api_key or not self.api_secret:
            return {'error': 'API Key/Secretが設定されていません'}

        url = f'{self.BASE_URL}/api/v3/account'
        timestamp = int(time.time() * 1000)

        params = {'timestamp': timestamp}
        params['signature'] = self._sign_request(params)

        headers = {'X-MBX-APIKEY': self.api_key}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            balances = {
                asset['asset']: {
                    'free': float(asset['free']),
                    'locked': float(asset['locked']),
                }
                for asset in data['balances']
                if float(asset['free']) > 0 or float(asset['locked']) > 0
            }

            return balances
        except Exception as e:
            return {'error': str(e)}


def load_api_credentials(exchange: str = 'binance') -> tuple:
    """
    設定ファイルからAPI認証情報を読み込む

    config/api_keys.json から読み込み
    """
    config_path = os.path.join(os.path.dirname(__file__), 'api_keys.json')

    if not os.path.exists(config_path):
        print("⚠️  API設定ファイルが見つかりません")
        print(f"📄 {config_path} を作成してください")
        return None, None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if exchange not in config:
            print(f"⚠️  {exchange}の設定が見つかりません")
            return None, None

        api_key = config[exchange].get('api_key')
        api_secret = config[exchange].get('api_secret')

        return api_key, api_secret
    except Exception as e:
        print(f"❌ 設定ファイル読み込みエラー: {e}")
        return None, None


if __name__ == '__main__':
    # テスト
    print("🔍 Binance APIをテスト中...\n")

    api = BinanceAPI()

    # 価格取得テスト
    print("1. BTC価格を取得:")
    btc_price = api.get_price('BTCUSDT')
    if btc_price:
        print(f"   BTC/USDT: ${btc_price:,.2f}\n")

    # 24時間統計テスト
    print("2. 24時間統計を取得:")
    stats = api.get_24h_stats('SHIBUSDT')
    if stats:
        print(f"   SHIB/USDT:")
        print(f"   価格: ${stats['price']:.8f}")
        print(f"   変動: {stats['price_change_percent']:+.2f}%")
        print(f"   出来高: ${stats['quote_volume']:,.0f}\n")

    # 急騰コイン検索
    print("3. 急騰中のコインを検索（+10%以上）:")
    pumping = api.find_pumping_coins(min_change_percent=10.0)
    if pumping:
        for i, coin in enumerate(pumping[:5], 1):
            print(f"   {i}. {coin['symbol']}: {coin['change_percent']:+.2f}%")
    else:
        print("   該当なし")

    print("\n✅ APIテスト完了!")
