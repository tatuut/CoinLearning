"""
取引履歴を管理するデータベース
SQLiteを使用して全ての取引を記録・分析
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class TradeDatabase:
    def __init__(self, db_path: str = None):
        """データベース初期化"""
        if db_path is None:
            # デフォルトパス
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, 'trades.db')

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 辞書形式で取得
        self.setup_database()

    def setup_database(self):
        """テーブルを作成"""
        cursor = self.conn.cursor()

        # 取引履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                coin_symbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                trade_type TEXT NOT NULL,  -- 'BUY' or 'SELL'
                amount REAL NOT NULL,
                price REAL NOT NULL,
                total_cost REAL NOT NULL,
                fee REAL DEFAULT 0,
                strategy TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ポジションテーブル（現在保有中）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_symbol TEXT NOT NULL UNIQUE,
                amount REAL NOT NULL,
                avg_buy_price REAL NOT NULL,
                current_price REAL,
                profit_loss_percent REAL,
                stop_loss_price REAL,
                take_profit_price REAL,
                buy_trade_id INTEGER,
                opened_at TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buy_trade_id) REFERENCES trades(id)
            )
        ''')

        # 完了した取引ペア（買い→売り）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_symbol TEXT NOT NULL,
                buy_trade_id INTEGER NOT NULL,
                sell_trade_id INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                amount REAL NOT NULL,
                profit_loss REAL NOT NULL,
                profit_loss_percent REAL NOT NULL,
                strategy TEXT,
                duration_minutes INTEGER,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buy_trade_id) REFERENCES trades(id),
                FOREIGN KEY (sell_trade_id) REFERENCES trades(id)
            )
        ''')

        # 戦略パフォーマンステーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL UNIQUE,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                total_profit REAL DEFAULT 0,
                total_loss REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                avg_profit_percent REAL DEFAULT 0,
                avg_loss_percent REAL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # アカウント残高テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_balance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_balance REAL NOT NULL,
                available_balance REAL NOT NULL,
                in_positions REAL NOT NULL,
                total_profit_loss REAL NOT NULL,
                notes TEXT
            )
        ''')

        # 取引分析・メモテーブル（ユーザーとAIの協力分析用）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                coin_symbol TEXT,
                analysis_date TEXT NOT NULL,
                author TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        ''')

        self.conn.commit()

    def add_trade(self, coin_symbol: str, exchange: str, trade_type: str,
                  amount: float, price: float, total_cost: float,
                  fee: float = 0, strategy: str = None, notes: str = None) -> int:
        """取引を記録"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO trades (timestamp, coin_symbol, exchange, trade_type,
                                amount, price, total_cost, fee, strategy, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, coin_symbol, exchange, trade_type,
              amount, price, total_cost, fee, strategy, notes))

        self.conn.commit()
        return cursor.lastrowid

    def open_position(self, coin_symbol: str, amount: float, buy_price: float,
                     buy_trade_id: int, stop_loss_price: float = None,
                     take_profit_price: float = None):
        """ポジションを開く（買った時）"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()

        cursor.execute('''
            INSERT OR REPLACE INTO positions
            (coin_symbol, amount, avg_buy_price, current_price,
             stop_loss_price, take_profit_price, buy_trade_id, opened_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (coin_symbol, amount, buy_price, buy_price,
              stop_loss_price, take_profit_price, buy_trade_id, timestamp))

        self.conn.commit()

    def close_position(self, coin_symbol: str, sell_price: float, sell_trade_id: int):
        """ポジションを閉じる（売った時）"""
        cursor = self.conn.cursor()

        # ポジション情報を取得
        cursor.execute('SELECT * FROM positions WHERE coin_symbol = ?', (coin_symbol,))
        position = cursor.fetchone()

        if not position:
            raise ValueError(f"ポジションが見つかりません: {coin_symbol}")

        # 損益計算
        buy_price = position['avg_buy_price']
        amount = position['amount']
        profit_loss = (sell_price - buy_price) * amount
        profit_loss_percent = ((sell_price - buy_price) / buy_price) * 100

        # 時間計算
        opened_at = datetime.fromisoformat(position['opened_at'])
        duration = (datetime.now() - opened_at).total_seconds() / 60

        # 完了取引として記録
        cursor.execute('''
            INSERT INTO completed_trades
            (coin_symbol, buy_trade_id, sell_trade_id, buy_price, sell_price,
             amount, profit_loss, profit_loss_percent, strategy, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (coin_symbol, position['buy_trade_id'], sell_trade_id,
              buy_price, sell_price, amount, profit_loss, profit_loss_percent,
              None, duration))

        # ポジションを削除
        cursor.execute('DELETE FROM positions WHERE coin_symbol = ?', (coin_symbol,))

        self.conn.commit()
        return profit_loss, profit_loss_percent

    def update_position_price(self, coin_symbol: str, current_price: float):
        """ポジションの現在価格を更新"""
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE positions
            SET current_price = ?,
                profit_loss_percent = ((? - avg_buy_price) / avg_buy_price) * 100,
                updated_at = ?
            WHERE coin_symbol = ?
        ''', (current_price, current_price, datetime.now().isoformat(), coin_symbol))

        self.conn.commit()

    def get_all_positions(self) -> List[Dict]:
        """全てのポジションを取得"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM positions ORDER BY opened_at DESC')
        return [dict(row) for row in cursor.fetchall()]

    def get_completed_trades(self, limit: int = 50) -> List[Dict]:
        """完了した取引を取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM completed_trades
            ORDER BY completed_at DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        cursor = self.conn.cursor()

        # 完了取引の統計
        cursor.execute('''
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing_trades,
                AVG(CASE WHEN profit_loss > 0 THEN profit_loss_percent ELSE NULL END) as avg_win_percent,
                AVG(CASE WHEN profit_loss < 0 THEN profit_loss_percent ELSE NULL END) as avg_loss_percent,
                SUM(profit_loss) as total_profit_loss,
                SUM(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) as total_profit,
                SUM(CASE WHEN profit_loss < 0 THEN ABS(profit_loss) ELSE 0 END) as total_loss
            FROM completed_trades
        ''')

        result = cursor.fetchone()
        stats = dict(result)

        # 勝率計算
        if stats['total_trades'] > 0:
            stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100
        else:
            stats['win_rate'] = 0

        # プロフィットファクター計算
        if stats['total_loss'] and stats['total_loss'] > 0:
            stats['profit_factor'] = stats['total_profit'] / stats['total_loss']
        else:
            stats['profit_factor'] = 0 if stats['total_profit'] == 0 else float('inf')

        return stats

    def record_balance(self, total_balance: float, available_balance: float,
                      in_positions: float, total_profit_loss: float, notes: str = None):
        """残高を記録"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO account_balance
            (timestamp, total_balance, available_balance, in_positions, total_profit_loss, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, total_balance, available_balance, in_positions, total_profit_loss, notes))

        self.conn.commit()

    def get_balance_history(self, limit: int = 30) -> List[Dict]:
        """残高履歴を取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM account_balance
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def add_analysis(self, author: str, analysis_type: str, content: str,
                    trade_id: int = None, coin_symbol: str = None, tags: List[str] = None) -> int:
        """分析・メモを追加

        Args:
            author: 'user' または 'ai'
            analysis_type: 'pre_trade', 'during_trade', 'post_trade', 'memo', 'lesson'
            content: 分析内容
            trade_id: 関連する取引ID（オプション）
            coin_symbol: コインシンボル（オプション）
            tags: タグのリスト（オプション）
        """
        cursor = self.conn.cursor()
        analysis_date = datetime.now().isoformat()
        tags_json = json.dumps(tags) if tags else None

        cursor.execute('''
            INSERT INTO trade_analysis
            (trade_id, coin_symbol, analysis_date, author, analysis_type, content, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (trade_id, coin_symbol, analysis_date, author, analysis_type, content, tags_json))

        self.conn.commit()
        return cursor.lastrowid

    def get_trade_analysis(self, trade_id: int) -> List[Dict]:
        """特定の取引に関連する分析を取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trade_analysis
            WHERE trade_id = ?
            ORDER BY created_at ASC
        ''', (trade_id,))

        results = []
        for row in cursor.fetchall():
            analysis = dict(row)
            if analysis['tags']:
                analysis['tags'] = json.loads(analysis['tags'])
            results.append(analysis)

        return results

    def get_all_analysis(self, limit: int = 50, analysis_type: str = None) -> List[Dict]:
        """全ての分析を取得"""
        cursor = self.conn.cursor()

        if analysis_type:
            cursor.execute('''
                SELECT * FROM trade_analysis
                WHERE analysis_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (analysis_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM trade_analysis
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

        results = []
        for row in cursor.fetchall():
            analysis = dict(row)
            if analysis['tags']:
                analysis['tags'] = json.loads(analysis['tags'])
            results.append(analysis)

        return results

    def get_coin_analysis(self, coin_symbol: str) -> List[Dict]:
        """特定のコインに関する全ての分析を取得"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trade_analysis
            WHERE coin_symbol = ?
            ORDER BY created_at DESC
        ''', (coin_symbol,))

        results = []
        for row in cursor.fetchall():
            analysis = dict(row)
            if analysis['tags']:
                analysis['tags'] = json.loads(analysis['tags'])
            results.append(analysis)

        return results

    def search_analysis(self, keyword: str) -> List[Dict]:
        """キーワードで分析を検索"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trade_analysis
            WHERE content LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%',))

        results = []
        for row in cursor.fetchall():
            analysis = dict(row)
            if analysis['tags']:
                analysis['tags'] = json.loads(analysis['tags'])
            results.append(analysis)

        return results

    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()


if __name__ == '__main__':
    # テスト
    print("データベースをセットアップ中...")
    db = TradeDatabase()
    print("✅ データベース作成完了！")
    print(f"📁 保存場所: {db.db_path}")

    # サンプルデータを追加
    print("\nサンプル取引を追加...")
    trade_id = db.add_trade(
        coin_symbol='SHIB',
        exchange='Binance',
        trade_type='BUY',
        amount=1000000,
        price=0.00001,
        total_cost=10.0,
        strategy='RSI_Strategy',
        notes='RSI < 30で購入'
    )
    print(f"✅ 取引ID {trade_id} を記録")

    db.open_position('SHIB', 1000000, 0.00001, trade_id,
                     stop_loss_price=0.000009,
                     take_profit_price=0.000013)
    print("✅ ポジションをオープン")

    print("\n📊 現在のポジション:")
    positions = db.get_all_positions()
    for pos in positions:
        print(f"  {pos['coin_symbol']}: {pos['amount']} @ {pos['avg_buy_price']}")

    db.close()
    print("\n🎉 データベースのセットアップ完了！")
