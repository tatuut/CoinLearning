"""
時系列データ管理システム (PyStore版)

1分足データを全取得してParquetに保存
差分更新で通信量削減
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pystore
import pandas as pd
from datetime import datetime, timedelta
from src.config.exchange_api import MEXCAPI
from typing import Optional, List
import time


class TimeSeriesManager:
    """時系列データ管理（PyStore使用）"""

    def __init__(self, store_path: str = './data/pystore_data'):
        """
        初期化

        Args:
            store_path: PyStoreのデータ保存先
        """
        # PyStoreの初期化
        pystore.set_path(store_path)
        self.store = pystore.store('crypto_timeseries')

        # コレクション作成（なければ）
        if 'prices_1m' not in self.store.list_collections():
            self.store.collection('prices_1m')

        self.collection = self.store.collection('prices_1m')
        self.api = MEXCAPI()

    def fetch_all_history(self, symbol: str, start_date: str = '2020-01-01') -> pd.DataFrame:
        """
        全履歴を取得（1分足）

        Args:
            symbol: 銘柄シンボル（例: BTC, ETH）
            start_date: 開始日（YYYY-MM-DD）

        Returns:
            DataFrame（timestamp, open, high, low, close, volume）
        """
        print(f"📥 {symbol}: 全履歴取得中（1分足）...")
        print(f"   開始日: {start_date}")

        pair = f"{symbol}USDT"

        # 開始日時
        start = datetime.strptime(start_date, '%Y-%m-%d')
        now = datetime.now()

        all_data = []
        current = start

        # 1000本ずつ取得（MEXC APIの制限）
        while current < now:
            print(f"   取得中: {current.strftime('%Y-%m-%d %H:%M')}...", end='\r')

            try:
                # 1分足を1000本取得
                klines = self.api.get_klines(pair, interval='1m', limit=1000)

                if not klines:
                    break

                # DataFrame変換
                df = pd.DataFrame(klines)
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df.set_index('timestamp')

                all_data.append(df)

                # 次の開始時刻
                current = df.index[-1] + timedelta(minutes=1)

                # API制限対策（1秒待機）
                time.sleep(1)

            except Exception as e:
                print(f"\n   ⚠️ エラー: {e}")
                break

        if all_data:
            # 全データを結合
            full_df = pd.concat(all_data)
            full_df = full_df[~full_df.index.duplicated(keep='first')]  # 重複削除
            full_df = full_df.sort_index()

            print(f"\n   ✅ 取得完了: {len(full_df):,}行")
            print(f"   期間: {full_df.index[0]} ～ {full_df.index[-1]}")

            return full_df
        else:
            print(f"\n   ❌ データ取得失敗")
            return pd.DataFrame()

    def save_data(self, symbol: str, df: pd.DataFrame):
        """
        データをParquetに保存

        Args:
            symbol: 銘柄シンボル
            df: DataFrame
        """
        print(f"💾 {symbol}: Parquetに保存中...")

        metadata = {
            'symbol': symbol,
            'interval': '1m',
            'start_date': df.index[0].isoformat(),
            'end_date': df.index[-1].isoformat(),
            'row_count': len(df),
            'last_updated': datetime.now().isoformat()
        }

        self.collection.write(symbol, df, metadata=metadata)
        print(f"   ✅ 保存完了")

    def update_data(self, symbol: str) -> pd.DataFrame:
        """
        差分更新（新しいデータだけ取得）

        Args:
            symbol: 銘柄シンボル

        Returns:
            更新後のDataFrame
        """
        print(f"🔄 {symbol}: 差分更新中...")

        # 既存データ確認
        if symbol not in self.collection.list_items():
            print(f"   ⚠️ 既存データなし。全取得を実行してください。")
            return None

        # 最新のタイムスタンプ取得
        item = self.collection.item(symbol)
        existing_df = item.to_pandas()
        latest_timestamp = existing_df.index[-1]

        print(f"   最終データ: {latest_timestamp}")
        print(f"   新規データ取得中...")

        pair = f"{symbol}USDT"

        try:
            # 最新データを取得
            klines = self.api.get_klines(pair, interval='1m', limit=1000)

            if not klines:
                print(f"   ℹ️ 新規データなし")
                return existing_df

            # DataFrame変換
            new_df = pd.DataFrame(klines)
            new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')
            new_df = new_df.set_index('timestamp')

            # 最新タイムスタンプより後のデータのみ
            new_df = new_df[new_df.index > latest_timestamp]

            if len(new_df) == 0:
                print(f"   ℹ️ 新規データなし")
                return existing_df

            print(f"   ✅ 新規データ: {len(new_df)}行")

            # 追記
            self.collection.append(symbol, new_df)

            # 更新後のデータ取得
            updated_df = self.collection.item(symbol).to_pandas()

            print(f"   ✅ 更新完了: 総行数 {len(updated_df):,}行")

            return updated_df

        except Exception as e:
            print(f"   ❌ エラー: {e}")
            return existing_df

    def get_data(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """
        データ取得

        Args:
            symbol: 銘柄シンボル
            start: 開始日時（YYYY-MM-DD HH:MM:SS）
            end: 終了日時（YYYY-MM-DD HH:MM:SS）

        Returns:
            DataFrame
        """
        if symbol not in self.collection.list_items():
            print(f"❌ {symbol}: データが存在しません")
            return pd.DataFrame()

        item = self.collection.item(symbol)
        df = item.to_pandas()

        # 期間でフィルタ
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]

        return df

    def resample(self, df: pd.DataFrame, interval: str) -> pd.DataFrame:
        """
        任意の粒度にリサンプリング

        Args:
            df: 1分足DataFrame
            interval: '5m', '15m', '1h', '4h', '1d' など

        Returns:
            リサンプリング後のDataFrame
        """
        interval_map = {
            '5m': '5min',
            '15m': '15min',
            '30m': '30min',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1w',
        }

        pandas_interval = interval_map.get(interval, interval)

        resampled = df.resample(pandas_interval).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

        return resampled

    def get_metadata(self, symbol: str) -> dict:
        """
        メタデータ取得

        Args:
            symbol: 銘柄シンボル

        Returns:
            メタデータ
        """
        if symbol not in self.collection.list_items():
            return {}

        item = self.collection.item(symbol)
        return item.metadata

    def list_symbols(self) -> List[str]:
        """保存されている銘柄一覧"""
        return self.collection.list_items()


def main():
    """テスト実行"""
    import argparse

    parser = argparse.ArgumentParser(description='時系列データ管理')
    parser.add_argument('symbol', help='銘柄シンボル（例: BTC, ETH, SHIB）')
    parser.add_argument('--init', action='store_true', help='全履歴取得（初回）')
    parser.add_argument('--update', action='store_true', help='差分更新')
    parser.add_argument('--show', action='store_true', help='データ表示')
    parser.add_argument('--resample', choices=['5m', '15m', '1h', '4h', '1d'], help='リサンプリング')
    parser.add_argument('--start-date', default='2023-01-01', help='開始日（初回取得時）')

    args = parser.parse_args()

    manager = TimeSeriesManager()

    if args.init:
        # 初回: 全取得
        df = manager.fetch_all_history(args.symbol, start_date=args.start_date)
        if not df.empty:
            manager.save_data(args.symbol, df)

    elif args.update:
        # 差分更新
        df = manager.update_data(args.symbol)

    elif args.show:
        # データ表示
        df = manager.get_data(args.symbol)

        if not df.empty:
            print(f"\n📊 {args.symbol} データ")
            print(f"   期間: {df.index[0]} ～ {df.index[-1]}")
            print(f"   行数: {len(df):,}行")
            print(f"\n   直近10行:")
            print(df.tail(10))

            # リサンプリング
            if args.resample:
                resampled = manager.resample(df, args.resample)
                print(f"\n   リサンプリング（{args.resample}）:")
                print(resampled.tail(10))

            # メタデータ
            metadata = manager.get_metadata(args.symbol)
            print(f"\n   メタデータ:")
            for key, value in metadata.items():
                print(f"     {key}: {value}")
    else:
        # 銘柄一覧
        symbols = manager.list_symbols()
        print(f"📂 保存済み銘柄: {len(symbols)}件")
        for sym in symbols:
            meta = manager.get_metadata(sym)
            print(f"   {sym}: {meta.get('row_count', 0):,}行 | 最終更新: {meta.get('last_updated', 'N/A')[:19]}")


if __name__ == '__main__':
    main()
