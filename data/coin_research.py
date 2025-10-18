"""
銘柄リサーチシステム

Coincheck全銘柄の詳細情報を収集・保存
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.advanced_database import AdvancedDatabase
from datetime import datetime
import time


class CoinResearcher:
    """銘柄リサーチャー"""

    # Coincheck取扱銘柄リスト（2025年10月時点）
    COINCHECK_COINS = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('ETC', 'Ethereum Classic'),
        ('LSK', 'Lisk'),
        ('XRP', 'Ripple'),
        ('XEM', 'NEM'),
        ('LTC', 'Litecoin'),
        ('BCH', 'Bitcoin Cash'),
        ('MONA', 'Monacoin'),
        ('XLM', 'Stellar Lumens'),
        ('QTUM', 'Qtum'),
        ('BAT', 'Basic Attention Token'),
        ('IOST', 'IOST'),
        ('ENJ', 'Enjin Coin'),
        ('SAND', 'The Sandbox'),
        ('DOT', 'Polkadot'),
        ('FNCT', 'FiNANCiE Token'),
        ('CHZ', 'Chiliz'),
        ('LINK', 'Chainlink'),
        ('DAI', 'Dai'),
        ('MKR', 'Maker'),
        ('MATIC', 'Polygon'),
        ('APE', 'ApeCoin'),
        ('AXS', 'Axie Infinity'),
        ('IMX', 'Immutable X'),
        ('WBTC', 'Wrapped Bitcoin'),
        ('AVAX', 'Avalanche'),
        ('SHIB', 'Shiba Inu'),
        ('BRIL', 'Brilliantcrypto Token'),
        ('BC', 'Blood Crystal'),
        ('DOGE', 'Dogecoin'),
        ('PEPE', 'Pepe'),
        ('GRT', 'The Graph'),
        ('MANA', 'Decentraland'),
        ('MASK', 'Mask Network'),
    ]

    def __init__(self):
        self.db = AdvancedDatabase()

    def initialize_coincheck_list(self):
        """Coincheck銘柄リストをDBに登録"""
        print("[*] Coincheck取扱銘柄をデータベースに登録中...")

        for symbol, name in self.COINCHECK_COINS:
            self.db.add_coincheck_coin(symbol, name)
            print(f"  [OK] {symbol} ({name}) を登録")

        print(f"\n[OK] {len(self.COINCHECK_COINS)}銘柄の登録完了！")

    def research_coin(self, symbol: str, name: str, use_web_search: bool = False):
        """
        個別銘柄をリサーチ（WebSearchを使う場合はClaude Codeで実行）

        Args:
            symbol: 銘柄シンボル（例: BTC）
            name: 銘柄名（例: Bitcoin）
            use_web_search: WebSearchを使うかどうか
        """
        print(f"\n[*] {symbol} ({name}) のリサーチ開始...")

        # 基本情報のテンプレート
        coin_data = {
            'symbol': symbol,
            'name': name,
            'description': f'{name}の詳細情報',
            'max_supply': 'Unknown',
            'circulating_supply': 'Unknown',
            'use_case': 'To be researched',
            'technology': 'To be researched',
            'blockchain_type': 'To be researched',
            'consensus_mechanism': 'To be researched',
        }

        # データベースに保存
        self.db.add_coin_info(coin_data)
        print(f"  [OK] {symbol} の基本情報を保存")

        if use_web_search:
            print(f"  [*] WebSearchで詳細情報を収集してください:")
            print(f"      クエリ: {name} {symbol} 仮想通貨 特徴 将来性 2025")
            return False

        return True

    def bulk_research_all_coins(self):
        """全銘柄のリサーチを開始（手動WebSearch用のガイド）"""
        print("\n" + "="*60)
        print("全銘柄リサーチガイド")
        print("="*60)

        print("\n各銘柄について以下の情報を収集してください:\n")
        print("1. 基本情報")
        print("   - 発行上限")
        print("   - 用途・ユースケース")
        print("   - 技術的特徴")
        print("   - コンセンサスメカニズム")
        print("\n2. 最新ニュース（2025年）")
        print("   - 価格動向")
        print("   - 重要な提携・アップデート")
        print("   - 規制関連")
        print("\n3. 将来性評価")
        print("   - 価格予想")
        print("   - リスク評価")
        print("   - メリット・デメリット")

        print("\n" + "-"*60)
        print("銘柄リスト:")
        print("-"*60)

        for i, (symbol, name) in enumerate(self.COINCHECK_COINS, 1):
            print(f"{i:2d}. {symbol:6s} - {name}")

        print("\n[*] WebSearchを使って各銘柄を調査してください！")

    def get_research_status(self):
        """リサーチ状況を確認"""
        coins = self.db.get_coincheck_coins()
        print(f"\n登録済み銘柄: {len(coins)}件")

        # 詳細情報が入っているかチェック
        researched_count = 0
        for coin in coins:
            info = self.db.get_coin_info(coin['symbol'])
            if info and info.get('use_case') != 'To be researched':
                researched_count += 1

        print(f"リサーチ完了: {researched_count}件")
        print(f"リサーチ待ち: {len(coins) - researched_count}件")

    def close(self):
        """データベース接続を閉じる"""
        self.db.close()


if __name__ == '__main__':
    researcher = CoinResearcher()

    print("="*60)
    print("銘柄リサーチシステム")
    print("="*60)

    # Coincheck銘柄リストを初期化
    researcher.initialize_coincheck_list()

    # リサーチガイドを表示
    researcher.bulk_research_all_coins()

    # 状況確認
    researcher.get_research_status()

    researcher.close()
