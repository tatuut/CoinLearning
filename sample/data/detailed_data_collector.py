"""
詳細データ収集システム

WebSearchの全結果、価格の詳細履歴、オンチェーンデータなど
「最も詳細なデータ」を取得・保存する
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.advanced_database import AdvancedDatabase
from src.config.exchange_api import MEXCAPI
from datetime import datetime, timedelta
import json
import sqlite3


class DetailedDataCollector:
    """詳細データ収集システム"""

    def __init__(self):
        self.db = AdvancedDatabase()
        self.api = MEXCAPI()
        self._extend_tables()

    def _extend_tables(self):
        """より詳細なデータを保存するためのテーブル拡張"""
        cursor = self.db.conn.cursor()

        # 1. 詳細価格履歴テーブル（全期間の価格データ）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history_detailed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                interval TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                quote_volume REAL,
                trades_count INTEGER,
                taker_buy_volume REAL,
                taker_buy_quote_volume REAL,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp, interval)
            )
        ''')

        # 2. WebSearch生データテーブル（検索結果の完全保存）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS websearch_raw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query TEXT NOT NULL,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result_index INTEGER,
                title TEXT,
                url TEXT,
                snippet TEXT,
                full_content TEXT,
                metadata_json TEXT,
                relevance_score REAL,
                source_domain TEXT,
                published_date TEXT,
                author TEXT,
                image_urls TEXT,
                related_links TEXT
            )
        ''')

        # 3. 市場統計詳細テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_stats_detailed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price REAL,
                market_cap REAL,
                volume_24h REAL,
                volume_change_24h REAL,
                percent_change_1h REAL,
                percent_change_24h REAL,
                percent_change_7d REAL,
                percent_change_30d REAL,
                circulating_supply REAL,
                total_supply REAL,
                max_supply REAL,
                rank_by_marketcap INTEGER,
                dominance REAL,
                turnover_rate REAL,
                raw_data_json TEXT
            )
        ''')

        # 4. オーダーブック履歴（板情報）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orderbook_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bids_json TEXT,
                asks_json TEXT,
                bid_depth_1pct REAL,
                ask_depth_1pct REAL,
                spread REAL,
                mid_price REAL
            )
        ''')

        # 5. ニュース全文保存テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_full_text (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER,
                full_html TEXT,
                full_markdown TEXT,
                extracted_data TEXT,
                images_json TEXT,
                videos_json TEXT,
                related_articles_json TEXT,
                author_info TEXT,
                comment_count INTEGER,
                share_count INTEGER,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (news_id) REFERENCES news(id)
            )
        ''')

        self.db.conn.commit()

    def collect_price_history(self, symbol: str, interval: str = '1h',
                             days_back: int = 30, save_to_db: bool = True):
        """
        詳細な価格履歴を収集

        Args:
            symbol: 銘柄シンボル
            interval: 時間足（1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w）
            days_back: 何日分遡るか
            save_to_db: DBに保存するか

        Returns:
            価格データのリスト
        """
        print(f"📊 {symbol} の詳細価格履歴取得中...")
        print(f"   期間: {days_back}日分")
        print(f"   間隔: {interval}")

        # 1時間足の場合の必要なデータポイント数
        limit_map = {
            '1m': days_back * 24 * 60,
            '5m': days_back * 24 * 12,
            '15m': days_back * 24 * 4,
            '30m': days_back * 24 * 2,
            '1h': days_back * 24,
            '4h': days_back * 6,
            '1d': days_back,
            '1w': days_back // 7,
        }

        limit = min(limit_map.get(interval, 1000), 1000)  # MEXC APIの上限

        try:
            klines = self.api.get_klines(f"{symbol}USDT", interval=interval, limit=limit)
            print(f"   ✓ 取得件数: {len(klines)}件")

            if save_to_db:
                cursor = self.db.conn.cursor()
                saved_count = 0

                for kline in klines:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO price_history_detailed
                            (symbol, timestamp, interval, open, high, low, close, volume, quote_volume)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            symbol,
                            kline['timestamp'],
                            interval,
                            float(kline['open']),
                            float(kline['high']),
                            float(kline['low']),
                            float(kline['close']),
                            float(kline['volume']),
                            float(kline.get('quote_volume', 0))
                        ))
                        saved_count += 1
                    except Exception as e:
                        print(f"   ✗ 保存エラー: {e}")

                self.db.conn.commit()
                print(f"   ✓ DB保存: {saved_count}件")

            return klines

        except Exception as e:
            print(f"   ✗ 取得失敗: {e}")
            return []

    def save_websearch_result(self, query: str, results: list):
        """
        WebSearch結果を完全保存

        Args:
            query: 検索クエリ
            results: WebSearchの結果リスト

        使い方:
            Claude CodeでWebSearchを実行後、結果をこのメソッドに渡す
        """
        print(f"🔍 WebSearch結果を詳細保存中...")
        print(f"   クエリ: {query}")
        print(f"   結果数: {len(results)}件")

        cursor = self.db.conn.cursor()
        saved_count = 0

        for i, result in enumerate(results):
            try:
                cursor.execute('''
                    INSERT INTO websearch_raw
                    (search_query, result_index, title, url, snippet,
                     full_content, metadata_json, source_domain)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    query,
                    i,
                    result.get('title', ''),
                    result.get('url', ''),
                    result.get('snippet', ''),
                    result.get('content', ''),
                    json.dumps(result.get('metadata', {}), ensure_ascii=False),
                    result.get('domain', '')
                ))
                saved_count += 1
            except Exception as e:
                print(f"   ✗ 保存エラー: {e}")

        self.db.conn.commit()
        print(f"   ✓ 保存完了: {saved_count}件")

    def collect_market_stats(self, symbol: str, save_to_db: bool = True):
        """
        詳細な市場統計を収集

        現在価格だけでなく、時価総額、供給量、ランキングなども保存
        """
        print(f"📈 {symbol} の詳細市場統計取得中...")

        try:
            # 24h統計
            stats = self.api.get_24h_stats(f"{symbol}USDT")

            if save_to_db:
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    INSERT INTO market_stats_detailed
                    (symbol, price, volume_24h, percent_change_24h, raw_data_json)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    stats.get('price', 0),
                    stats.get('volume', 0),
                    stats.get('price_change_percent', 0),
                    json.dumps(stats, ensure_ascii=False)
                ))
                self.db.conn.commit()
                print(f"   ✓ 統計保存完了")

            return stats

        except Exception as e:
            print(f"   ✗ 取得失敗: {e}")
            return None

    def get_price_analysis(self, symbol: str, interval: str = '1h', limit: int = 100):
        """
        保存された詳細価格データから分析情報を取得

        Returns:
            分析結果の辞書
        """
        cursor = self.db.conn.cursor()

        cursor.execute('''
            SELECT timestamp, open, high, low, close, volume
            FROM price_history_detailed
            WHERE symbol = ? AND interval = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, interval, limit))

        rows = cursor.fetchall()

        if not rows:
            return None

        prices = [row[4] for row in rows]  # close price
        volumes = [row[5] for row in rows]

        analysis = {
            'data_points': len(rows),
            'current_price': prices[0],
            'average_price': sum(prices) / len(prices),
            'max_price': max(prices),
            'min_price': min(prices),
            'price_range': max(prices) - min(prices),
            'average_volume': sum(volumes) / len(volumes),
            'total_volume': sum(volumes),
            'volatility': (max(prices) - min(prices)) / min(prices) * 100,
            'trend': 'UP' if prices[0] > prices[-1] else 'DOWN',
            'period_change': ((prices[0] - prices[-1]) / prices[-1]) * 100,
        }

        return analysis

    def export_detailed_data(self, symbol: str, output_file: str = None):
        """
        銘柄の全詳細データをエクスポート

        Args:
            symbol: 銘柄シンボル
            output_file: 出力ファイル名（Noneの場合は自動生成）

        Returns:
            エクスポートされたデータの辞書
        """
        print(f"📦 {symbol} の全詳細データをエクスポート中...")

        cursor = self.db.conn.cursor()

        # 1. 価格履歴
        cursor.execute('''
            SELECT * FROM price_history_detailed
            WHERE symbol = ?
            ORDER BY timestamp DESC
        ''', (symbol,))
        price_data = [dict(row) for row in cursor.fetchall()]

        # 2. ニュース
        cursor.execute('''
            SELECT * FROM news
            WHERE symbol = ?
            ORDER BY published_date DESC
        ''', (symbol,))
        news_data = [dict(row) for row in cursor.fetchall()]

        # 3. 市場統計
        cursor.execute('''
            SELECT * FROM market_stats_detailed
            WHERE symbol = ?
            ORDER BY timestamp DESC
        ''', (symbol,))
        stats_data = [dict(row) for row in cursor.fetchall()]

        export_data = {
            'symbol': symbol,
            'export_date': datetime.now().isoformat(),
            'price_history': price_data,
            'news': news_data,
            'market_stats': stats_data,
            'summary': {
                'price_data_points': len(price_data),
                'news_count': len(news_data),
                'stats_snapshots': len(stats_data),
            }
        }

        # ファイルに保存
        if output_file is None:
            output_file = f"data_export_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        output_path = os.path.join(os.path.dirname(__file__), '..', 'exports', output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"   ✓ エクスポート完了: {output_path}")
        print(f"   価格データ: {len(price_data)}件")
        print(f"   ニュース: {len(news_data)}件")
        print(f"   市場統計: {len(stats_data)}件")

        return export_data

    def close(self):
        """リソースをクローズ"""
        self.db.close()


def main():
    """使用例"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    import argparse

    parser = argparse.ArgumentParser(
        description='詳細データ収集ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # BTCの1時間足データを30日分収集
  python detailed_data_collector.py BTC --interval 1h --days 30

  # BTCの詳細データをエクスポート
  python detailed_data_collector.py BTC --export

  # 複数の時間足を一括収集
  python detailed_data_collector.py BTC --all-intervals

収集されるデータ:
  - 価格履歴（1m, 5m, 15m, 30m, 1h, 4h, 1d）
  - 市場統計（時価総額、供給量、ランキング）
  - WebSearch結果の完全保存
  - オーダーブック履歴（実装予定）
        """
    )

    parser.add_argument('symbol', help='銘柄シンボル（例: BTC）')
    parser.add_argument('--interval', default='1h',
                       help='時間足（1m, 5m, 15m, 30m, 1h, 4h, 1d）')
    parser.add_argument('--days', type=int, default=30,
                       help='収集する日数（デフォルト: 30）')
    parser.add_argument('--all-intervals', action='store_true',
                       help='全ての時間足を収集')
    parser.add_argument('--export', action='store_true',
                       help='全データをエクスポート')
    parser.add_argument('--stats', action='store_true',
                       help='市場統計を収集')

    args = parser.parse_args()

    collector = DetailedDataCollector()

    try:
        symbol = args.symbol.upper()

        if args.export:
            # 全データエクスポート
            collector.export_detailed_data(symbol)

        elif args.all_intervals:
            # 全時間足を収集
            intervals = ['1h', '4h', '1d']
            for interval in intervals:
                print()
                collector.collect_price_history(symbol, interval=interval, days_back=args.days)

        else:
            # 指定された時間足を収集
            collector.collect_price_history(symbol, interval=args.interval, days_back=args.days)

        if args.stats:
            print()
            collector.collect_market_stats(symbol)

        # 分析結果表示
        print()
        print("="*80)
        print(f"📊 {symbol} - 保存データ分析")
        print("="*80)

        for interval in ['1h', '4h', '1d']:
            analysis = collector.get_price_analysis(symbol, interval=interval)
            if analysis:
                print(f"\n【{interval}足】")
                print(f"  データ数: {analysis['data_points']}件")
                print(f"  現在価格: ${analysis['current_price']:,.2f}")
                print(f"  平均価格: ${analysis['average_price']:,.2f}")
                print(f"  変動幅: ${analysis['price_range']:,.2f} ({analysis['volatility']:.2f}%)")
                print(f"  トレンド: {analysis['trend']} ({analysis['period_change']:+.2f}%)")

    finally:
        collector.close()


if __name__ == '__main__':
    main()
