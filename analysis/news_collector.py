"""
ニュース収集システム

WebSearchで各銘柄の最新ニュースを収集してDBに保存
※ WebSearchはClaude Codeが実行します
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.advanced_database import AdvancedDatabase
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional


class NewsCollector:
    """ニュース収集システム"""

    def __init__(self):
        self.db = AdvancedDatabase()

    def collect_news_for_coin(self, symbol: str, name: str, news_data_list: List[Dict]) -> int:
        """
        特定銘柄のニュースを収集してDBに保存

        Args:
            symbol: 銘柄シンボル（例: BTC）
            name: 銘柄名（例: Bitcoin）
            news_data_list: WebSearchで取得したニュースデータのリスト

        Returns:
            保存されたニュース件数
        """
        count = 0

        for news in news_data_list:
            try:
                news_entry = {
                    'symbol': symbol,
                    'title': news.get('title', ''),
                    'content': news.get('content', news.get('snippet', '')),
                    'source': news.get('source', 'Web'),
                    'url': news.get('url', ''),
                    'published_date': news.get('published_date', datetime.now().isoformat()),
                    'sentiment': news.get('sentiment', 'neutral'),
                    'importance_score': news.get('importance_score', 0.5),
                    'impact_score': news.get('impact_score', 0.5),
                    'keywords': news.get('keywords', [symbol, name]),
                }

                news_id = self.db.add_news(news_entry)

                # キーワード抽出してembeddingsテーブルに保存
                keywords = self._extract_keywords(news_entry['title'], news_entry['content'])
                self.db.add_news_embedding(news_id, keywords)

                count += 1
                print(f"  [OK] ニュース保存: {news_entry['title'][:50]}...")

            except Exception as e:
                print(f"  [NG] ニュース保存エラー: {e}")

        return count

    def _extract_keywords(self, title: str, content: str) -> List[str]:
        """
        タイトルと本文からキーワードを抽出

        Args:
            title: タイトル
            content: 本文

        Returns:
            キーワードリスト
        """
        # シンプルなキーワード抽出（重要な単語を抽出）
        important_terms = [
            '最高値', '急騰', '暴落', '規制', '承認', 'ETF', '提携',
            '上場', 'アップデート', 'ハードフォーク', 'ハッキング',
            '価格', '予想', '将来性', '投資', 'SEC', '金融庁',
        ]

        keywords = []
        text = f"{title} {content}".lower()

        for term in important_terms:
            if term.lower() in text or term in text:
                keywords.append(term)

        return keywords[:10]  # 最大10個

    def create_news_collection_guide(self, symbol: str, name: str) -> str:
        """
        Claude CodeでWebSearchを実行するためのガイドを生成

        Args:
            symbol: 銘柄シンボル
            name: 銘柄名

        Returns:
            検索クエリ
        """
        query = f"{name} {symbol} 仮想通貨 最新ニュース 2025 価格 将来性"
        return query

    def get_news_statistics(self) -> Dict:
        """ニュース収集統計を取得"""
        cursor = self.db.conn.cursor()

        # 総ニュース件数
        cursor.execute('SELECT COUNT(*) FROM news')
        total_news = cursor.fetchone()[0]

        # 銘柄別ニュース件数
        cursor.execute('''
            SELECT symbol, COUNT(*) as count
            FROM news
            GROUP BY symbol
            ORDER BY count DESC
            LIMIT 10
        ''')
        by_symbol = [{'symbol': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # 最新ニュースの日付
        cursor.execute('SELECT MAX(published_date) FROM news')
        latest_date = cursor.fetchone()[0]

        return {
            'total_news': total_news,
            'by_symbol': by_symbol,
            'latest_date': latest_date,
        }

    def close(self):
        """データベース接続を閉じる"""
        self.db.close()


class NewsCollectionTask:
    """
    ニュース収集タスク実行クラス

    Claude Codeが実行する際のエントリーポイント
    """

    def __init__(self):
        self.collector = NewsCollector()

    def collect_for_priority_coins(self, coin_list: List[tuple]) -> Dict:
        """
        優先銘柄のニュースを収集

        Args:
            coin_list: [(symbol, name), ...] のリスト

        Returns:
            収集結果の統計
        """
        print("\n" + "="*60)
        print("ニュース収集タスク開始")
        print("="*60)

        results = {
            'total_collected': 0,
            'by_coin': {},
            'queries': [],
        }

        for symbol, name in coin_list:
            print(f"\n[*] {symbol} ({name}) のニュース収集準備...")

            # 検索クエリを生成
            query = self.collector.create_news_collection_guide(symbol, name)
            results['queries'].append({
                'symbol': symbol,
                'query': query,
            })

            print(f"  検索クエリ: {query}")
            print(f"  ⚠️  Claude CodeでWebSearchを実行してください！")

        print("\n" + "="*60)
        print("次のステップ:")
        print("="*60)
        print("1. 上記の検索クエリでWebSearchを実行")
        print("2. 取得したニュースデータをこのシステムに渡す")
        print("3. collector.collect_news_for_coin() でDBに保存")

        return results

    def close(self):
        self.collector.close()


if __name__ == '__main__':
    # テスト実行
    print("="*60)
    print("ニュース収集システム - テスト")
    print("="*60)

    task = NewsCollectionTask()

    # 優先銘柄（Phase 1: 基軸通貨）
    priority_coins = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('XRP', 'Ripple'),
    ]

    # ニュース収集タスクを準備
    results = task.collect_for_priority_coins(priority_coins)

    print("\n[*] クエリリスト生成完了")
    print(f"    生成されたクエリ数: {len(results['queries'])}")

    # 統計表示
    stats = task.collector.get_news_statistics()
    print(f"\n[*] 現在のDB統計:")
    print(f"    総ニュース件数: {stats['total_news']}")

    task.close()
