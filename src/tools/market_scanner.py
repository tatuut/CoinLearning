"""
全銘柄市場スキャナー

全銘柄の価格を一括取得してDBに保存
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.exchange_api import MEXCAPI
from src.data.advanced_database import AdvancedDatabase
from datetime import datetime
import time
import argparse


class MarketScanner:
    """市場全体をスキャンして価格データを収集"""

    def __init__(self):
        self.api = MEXCAPI()
        self.db = AdvancedDatabase()

    def scan_all_markets(self, min_volume: float = 10000):
        """
        全銘柄をスキャンしてDBに保存

        Parameters:
        - min_volume: 最低出来高（USDT）
        """
        print("="*80)
        print("🔍 全銘柄市場スキャン開始")
        print("="*80)
        print()

        # 全銘柄の24h統計を取得
        print("📊 全銘柄データ取得中...")
        url = f'{self.api.BASE_URL}/api/v3/ticker/24hr'

        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()
            all_tickers = response.json()
        except Exception as e:
            print(f"❌ データ取得エラー: {e}")
            return

        # USDT建てのみフィルタ
        usdt_pairs = [
            item for item in all_tickers
            if item['symbol'].endswith('USDT') and float(item['quoteVolume']) >= min_volume
        ]

        print(f"✓ 取得完了: {len(usdt_pairs)}銘柄（出来高 >= ${min_volume:,.0f}）")
        print()

        # DBに保存
        print("💾 データベース保存中...")
        saved_count = 0
        skipped_count = 0

        for item in usdt_pairs:
            try:
                symbol = item['symbol'].replace('USDT', '')
                price = float(item['lastPrice'])
                change_24h = float(item['priceChangePercent'])
                volume = float(item['volume'])
                quote_volume = float(item['quoteVolume'])
                high_24h = float(item['highPrice'])
                low_24h = float(item['lowPrice'])

                self.db.save_price_snapshot(
                    symbol=symbol,
                    price=price,
                    change_24h=change_24h,
                    volume=volume,
                    quote_volume=quote_volume,
                    high_24h=high_24h,
                    low_24h=low_24h
                )
                saved_count += 1

                if saved_count % 50 == 0:
                    print(f"   処理中: {saved_count}/{len(usdt_pairs)}...")

            except Exception as e:
                skipped_count += 1
                # エラーは無視して続行

        print()
        print("="*80)
        print("✅ スキャン完了")
        print("="*80)
        print(f"保存: {saved_count}銘柄")
        print(f"スキップ: {skipped_count}銘柄")
        print()

    def show_top_movers(self, limit: int = 20):
        """変動率トップを表示"""
        print("="*80)
        print("📈 24時間変動率ランキング")
        print("="*80)
        print()

        # DBから最新データを取得
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT
                symbol,
                price,
                change_24h,
                quote_volume,
                timestamp
            FROM price_snapshots
            WHERE timestamp >= datetime('now', '-1 hour')
            ORDER BY change_24h DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()

        if not rows:
            print("⚠️ データがありません。先にスキャンを実行してください。")
            print("   python tools/market_scanner.py --scan")
            return

        print(f"{'順位':<4} {'銘柄':<8} {'価格':<15} {'24h変動':<10} {'出来高(USDT)':<15}")
        print("-"*80)

        for i, row in enumerate(rows, 1):
            symbol = row[0]
            price = row[1]
            change = row[2]
            volume = row[3]

            change_emoji = "🔥" if change >= 10 else "📈" if change >= 5 else "➡️"

            print(f"{i:<4} {symbol:<8} ${price:<14,.8f} {change_emoji} {change:>+7.2f}% ${volume:>13,.0f}")

        print()

    def show_top_volume(self, limit: int = 20):
        """出来高トップを表示"""
        print("="*80)
        print("💰 24時間出来高ランキング")
        print("="*80)
        print()

        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT
                symbol,
                price,
                change_24h,
                quote_volume,
                timestamp
            FROM price_snapshots
            WHERE timestamp >= datetime('now', '-1 hour')
            ORDER BY quote_volume DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()

        if not rows:
            print("⚠️ データがありません。先にスキャンを実行してください。")
            return

        print(f"{'順位':<4} {'銘柄':<8} {'価格':<15} {'24h変動':<10} {'出来高(USDT)':<15}")
        print("-"*80)

        for i, row in enumerate(rows, 1):
            symbol = row[0]
            price = row[1]
            change = row[2]
            volume = row[3]

            change_str = f"{change:+.2f}%"

            print(f"{i:<4} {symbol:<8} ${price:<14,.8f} {change_str:<10} ${volume:>13,.0f}")

        print()

    def search_symbol(self, query: str):
        """銘柄検索"""
        print("="*80)
        print(f"🔍 銘柄検索: {query}")
        print("="*80)
        print()

        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT
                symbol,
                price,
                change_24h,
                quote_volume,
                high_24h,
                low_24h,
                timestamp
            FROM price_snapshots
            WHERE symbol LIKE ? AND timestamp >= datetime('now', '-1 hour')
            ORDER BY quote_volume DESC
        ''', (f'%{query.upper()}%',))

        rows = cursor.fetchall()

        if not rows:
            print(f"⚠️ '{query}'に該当する銘柄が見つかりませんでした。")
            print()
            print("💡 ヒント:")
            print("   1. 先にスキャンを実行: python tools/market_scanner.py --scan")
            print("   2. 銘柄記号を確認: BTC, ETH, XRP, XLM など")
            return

        print(f"見つかった銘柄: {len(rows)}件")
        print()

        for row in rows:
            symbol = row[0]
            price = row[1]
            change = row[2]
            volume = row[3]
            high = row[4]
            low = row[5]
            timestamp = row[6]

            print(f"📊 {symbol}")
            print(f"   価格: ${price:,.8f}")
            print(f"   24h変動: {change:+.2f}%")
            print(f"   24h高値/安値: ${high:,.8f} / ${low:,.8f}")
            print(f"   24h出来高: ${volume:,.0f}")
            print(f"   更新: {timestamp}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='全銘柄市場スキャナー - 価格一覧をDBに保存',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python tools/market_scanner.py --scan              # 全銘柄スキャン
  python tools/market_scanner.py --top-movers        # 変動率ランキング
  python tools/market_scanner.py --top-volume        # 出来高ランキング
  python tools/market_scanner.py --search BTC        # 銘柄検索
  python tools/market_scanner.py --scan --show-all   # スキャン後に全て表示
        '''
    )

    parser.add_argument('--scan', action='store_true', help='全銘柄をスキャンしてDBに保存')
    parser.add_argument('--top-movers', action='store_true', help='変動率トップを表示')
    parser.add_argument('--top-volume', action='store_true', help='出来高トップを表示')
    parser.add_argument('--search', type=str, help='銘柄を検索')
    parser.add_argument('--min-volume', type=float, default=10000, help='最低出来高（USDT）')
    parser.add_argument('--limit', type=int, default=20, help='表示件数')
    parser.add_argument('--show-all', action='store_true', help='スキャン後に全ランキング表示')

    args = parser.parse_args()

    scanner = MarketScanner()

    # スキャン実行
    if args.scan:
        scanner.scan_all_markets(min_volume=args.min_volume)

        if args.show_all:
            print()
            scanner.show_top_movers(limit=args.limit)
            print()
            scanner.show_top_volume(limit=args.limit)

    # 変動率ランキング
    elif args.top_movers:
        scanner.show_top_movers(limit=args.limit)

    # 出来高ランキング
    elif args.top_volume:
        scanner.show_top_volume(limit=args.limit)

    # 銘柄検索
    elif args.search:
        scanner.search_symbol(args.search)

    # 引数なし：ヘルプ表示
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
