"""
高度な分析用データベース

銘柄情報、ニュース、RAG、分析履歴を管理
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os


class AdvancedDatabase:
    """高度な分析用データベース"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'advanced_trading.db')

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # 1. 銘柄基本情報テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                max_supply TEXT,
                circulating_supply TEXT,
                use_case TEXT,
                technology TEXT,
                blockchain_type TEXT,
                consensus_mechanism TEXT,
                created_date TEXT,
                founders TEXT,
                website_url TEXT,
                whitepaper_url TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. ニューステーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                title TEXT NOT NULL,
                content TEXT,
                source TEXT,
                url TEXT,
                published_date TIMESTAMP,
                collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sentiment TEXT,
                importance_score REAL DEFAULT 0.5,
                impact_score REAL DEFAULT 0.5,
                keywords TEXT,
                FOREIGN KEY (symbol) REFERENCES coin_info(symbol)
            )
        ''')

        # 3. ニュース埋め込みテーブル（RAG用）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER NOT NULL,
                embedding_vector TEXT,
                keywords TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (news_id) REFERENCES news(id)
            )
        ''')

        # 4. 分析履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price_at_analysis REAL,
                prediction TEXT,
                confidence_score REAL,
                factors_json TEXT,
                news_references TEXT,
                user_notes TEXT,
                FOREIGN KEY (symbol) REFERENCES coin_info(symbol)
            )
        ''')

        # 5. 銘柄分析結果テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_price REAL,
                market_cap REAL,
                volume_24h REAL,
                price_change_24h REAL,
                price_prediction_7d TEXT,
                price_prediction_30d TEXT,
                risk_level TEXT,
                opportunity_score REAL,
                pros TEXT,
                cons TEXT,
                recommendation TEXT,
                analyzed_news_count INTEGER DEFAULT 0,
                latest_news_date TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES coin_info(symbol)
            )
        ''')

        # 6. Coincheck取扱銘柄リスト
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coincheck_coins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                is_available BOOLEAN DEFAULT 1,
                min_purchase_amount REAL DEFAULT 500,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES coin_info(symbol)
            )
        ''')

        # 7. スコアリング履歴
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scoring_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                scoring_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevance_score REAL,
                importance_score REAL,
                impact_score REAL,
                time_decay_factor REAL,
                final_score REAL,
                news_count INTEGER,
                FOREIGN KEY (symbol) REFERENCES coin_info(symbol)
            )
        ''')

        # 8. 価格スナップショット（全銘柄の価格履歴）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                change_24h REAL,
                volume REAL,
                quote_volume REAL,
                high_24h REAL,
                low_24h REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES coin_info(symbol)
            )
        ''')

        # 価格スナップショットのインデックス
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_price_snapshots_symbol_timestamp
            ON price_snapshots(symbol, timestamp DESC)
        ''')

        self.conn.commit()

    # ========================================
    # 銘柄情報の操作
    # ========================================

    def add_coin_info(self, coin_data: Dict) -> int:
        """銘柄基本情報を追加"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO coin_info
            (symbol, name, description, max_supply, circulating_supply,
             use_case, technology, blockchain_type, consensus_mechanism,
             created_date, founders, website_url, whitepaper_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            coin_data.get('symbol'),
            coin_data.get('name'),
            coin_data.get('description'),
            coin_data.get('max_supply'),
            coin_data.get('circulating_supply'),
            coin_data.get('use_case'),
            coin_data.get('technology'),
            coin_data.get('blockchain_type'),
            coin_data.get('consensus_mechanism'),
            coin_data.get('created_date'),
            coin_data.get('founders'),
            coin_data.get('website_url'),
            coin_data.get('whitepaper_url'),
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_coin_info(self, symbol: str) -> Optional[Dict]:
        """銘柄基本情報を取得"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM coin_info WHERE symbol = ?', (symbol,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ========================================
    # ニュースの操作
    # ========================================

    def add_news(self, news_data: Dict) -> int:
        """ニュースを追加"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO news
            (symbol, title, content, source, url, published_date,
             sentiment, importance_score, impact_score, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            news_data.get('symbol'),
            news_data.get('title'),
            news_data.get('content'),
            news_data.get('source'),
            news_data.get('url'),
            news_data.get('published_date'),
            news_data.get('sentiment'),
            news_data.get('importance_score', 0.5),
            news_data.get('impact_score', 0.5),
            json.dumps(news_data.get('keywords', [])),
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_recent_news(self, symbol: str = None, limit: int = 10, days: int = 30) -> List[Dict]:
        """最近のニュースを取得"""
        cursor = self.conn.cursor()

        if symbol:
            cursor.execute('''
                SELECT * FROM news
                WHERE symbol = ?
                AND published_date >= datetime('now', '-' || ? || ' days')
                ORDER BY published_date DESC
                LIMIT ?
            ''', (symbol, days, limit))
        else:
            cursor.execute('''
                SELECT * FROM news
                WHERE published_date >= datetime('now', '-' || ? || ' days')
                ORDER BY published_date DESC
                LIMIT ?
            ''', (days, limit))

        return [dict(row) for row in cursor.fetchall()]

    # ========================================
    # RAG関連
    # ========================================

    def add_news_embedding(self, news_id: int, keywords: List[str]) -> int:
        """ニュースの埋め込み（キーワードベース）を追加"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO news_embeddings (news_id, keywords)
            VALUES (?, ?)
        ''', (news_id, json.dumps(keywords)))

        self.conn.commit()
        return cursor.lastrowid

    def search_relevant_news(self, symbol: str, keywords: List[str],
                            days_back: int = 30, limit: int = 10) -> List[Dict]:
        """関連ニュースを検索（キーワードベース + 時間重み付け）"""
        cursor = self.conn.cursor()

        # キーワードマッチングでスコアリング
        keyword_pattern = '%' + '%'.join(keywords) + '%'

        cursor.execute('''
            SELECT
                n.*,
                (julianday('now') - julianday(n.published_date)) as days_old,
                n.importance_score * n.impact_score as base_score
            FROM news n
            WHERE n.symbol = ?
            AND (n.title LIKE ? OR n.content LIKE ? OR n.keywords LIKE ?)
            AND n.published_date >= datetime('now', '-' || ? || ' days')
            ORDER BY base_score DESC, days_old ASC
            LIMIT ?
        ''', (symbol, keyword_pattern, keyword_pattern, keyword_pattern, days_back, limit))

        return [dict(row) for row in cursor.fetchall()]

    # ========================================
    # 分析履歴
    # ========================================

    def add_analysis(self, analysis_data: Dict) -> int:
        """分析結果を保存"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO analysis_history
            (symbol, analysis_type, price_at_analysis, prediction,
             confidence_score, factors_json, news_references, user_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_data.get('symbol'),
            analysis_data.get('analysis_type'),
            analysis_data.get('price_at_analysis'),
            analysis_data.get('prediction'),
            analysis_data.get('confidence_score'),
            json.dumps(analysis_data.get('factors', {})),
            json.dumps(analysis_data.get('news_references', [])),
            analysis_data.get('user_notes'),
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_analysis_history(self, symbol: str, limit: int = 10) -> List[Dict]:
        """分析履歴を取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM analysis_history
            WHERE symbol = ?
            ORDER BY analysis_date DESC
            LIMIT ?
        ''', (symbol, limit))

        return [dict(row) for row in cursor.fetchall()]

    # ========================================
    # Coincheck銘柄管理
    # ========================================

    def add_coincheck_coin(self, symbol: str, name: str) -> int:
        """Coincheck取扱銘柄を追加"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO coincheck_coins (symbol, name)
            VALUES (?, ?)
        ''', (symbol, name))
        self.conn.commit()
        return cursor.lastrowid

    def get_coincheck_coins(self) -> List[Dict]:
        """Coincheck取扱銘柄リストを取得"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM coincheck_coins WHERE is_available = 1')
        return [dict(row) for row in cursor.fetchall()]

    # ========================================
    # スコアリング
    # ========================================

    def add_scoring_result(self, scoring_data: Dict) -> int:
        """スコアリング結果を保存"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO scoring_history
            (symbol, relevance_score, importance_score, impact_score,
             time_decay_factor, final_score, news_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            scoring_data.get('symbol'),
            scoring_data.get('relevance_score'),
            scoring_data.get('importance_score'),
            scoring_data.get('impact_score'),
            scoring_data.get('time_decay_factor'),
            scoring_data.get('final_score'),
            scoring_data.get('news_count'),
        ))
        self.conn.commit()
        return cursor.lastrowid

    # ========================================
    # 価格スナップショット
    # ========================================

    def save_price_snapshot(self, symbol: str, price: float, change_24h: float = None,
                           volume: float = None, quote_volume: float = None,
                           high_24h: float = None, low_24h: float = None) -> int:
        """価格スナップショットを保存"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO price_snapshots
            (symbol, price, change_24h, volume, quote_volume, high_24h, low_24h)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, price, change_24h, volume, quote_volume, high_24h, low_24h))
        self.conn.commit()
        return cursor.lastrowid

    def get_latest_prices(self, limit: int = 50) -> List[Dict]:
        """最新の価格データを取得"""
        cursor = self.conn.cursor()
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
        return [dict(row) for row in cursor.fetchall()]

    def get_price_history(self, symbol: str, hours: int = 24) -> List[Dict]:
        """指定銘柄の価格履歴を取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM price_snapshots
            WHERE symbol = ?
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        ''', (symbol, hours))
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()


if __name__ == '__main__':
    # テスト
    print("[*] 高度な分析用データベーステスト")

    db = AdvancedDatabase()

    # テスト: 銘柄追加
    print("\n1. 銘柄情報追加テスト...")
    coin_data = {
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'description': 'デジタルゴールド、分散型デジタル通貨の元祖',
        'max_supply': '21000000',
        'use_case': '価値の保存、国際送金',
        'technology': 'ブロックチェーン',
        'blockchain_type': 'Bitcoin blockchain',
        'consensus_mechanism': 'Proof of Work',
    }
    db.add_coin_info(coin_data)
    print("  [OK] BTC情報追加完了")

    # テスト: ニュース追加
    print("\n2. ニュース追加テスト...")
    news_data = {
        'symbol': 'BTC',
        'title': 'ビットコインが最高値更新',
        'content': 'ビットコインが$100,000を突破し、史上最高値を更新しました。',
        'source': 'CoinPost',
        'published_date': datetime.now().isoformat(),
        'sentiment': 'positive',
        'importance_score': 0.9,
        'impact_score': 0.8,
        'keywords': ['bitcoin', '最高値', '100000'],
    }
    news_id = db.add_news(news_data)
    print(f"  [OK] ニュース追加完了 (ID: {news_id})")

    # テスト: 関連ニュース検索
    print("\n3. 関連ニュース検索テスト...")
    results = db.search_relevant_news('BTC', ['bitcoin', '最高値'])
    print(f"  [OK] {len(results)}件のニュースを取得")

    print("\n[OK] 全テスト完了！")
    db.close()
