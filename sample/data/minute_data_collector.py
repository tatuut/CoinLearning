"""
1分足データ収集スクリプト

最も細かいチャート（1分足）を取得し、差分更新を行う。
初回: 全データ取得（指定期間分）
2回目以降: 最終取得時刻以降のデータのみ取得（差分更新）

使い方:
    # 初回実行（30日分取得）
    python sample/data/minute_data_collector.py --symbols BTC,ETH,SOL --days 30

    # 2回目以降（差分のみ）
    python sample/data/minute_data_collector.py --symbols BTC,ETH,SOL
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import argparse
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from pathlib import Path
from sample.data.timeseries_storage import TimeSeriesStorage


class MinuteDataCollector:
    """1分足データ収集システム"""

    def __init__(self, data_dir=None):
        self.storage = TimeSeriesStorage(data_dir)
        # Binance API（無料、認証不要）
        self.base_url = "https://api.binance.com/api/v3"

    def get_latest_timestamp(self, symbol: str) -> int:
        """
        既存データの最終タイムスタンプを取得

        Args:
            symbol: 通貨シンボル

        Returns:
            最終タイムスタンプ（ミリ秒）、なければNone
        """
        try:
            df = self.storage.load_price_data(symbol, '1m')
            if df.empty:
                return None
            # 最後のタイムスタンプをミリ秒に変換
            last_time = df.index[-1]
            return int(last_time.timestamp() * 1000)
        except:
            return None

    def fetch_klines(self, symbol: str, start_time: int = None, end_time: int = None, limit: int = 1000):
        """
        Binance APIから1分足データを取得

        Args:
            symbol: 通貨シンボル（例: BTCUSDT）
            start_time: 開始時刻（ミリ秒）
            end_time: 終了時刻（ミリ秒）
            limit: 取得件数（最大1000）

        Returns:
            価格データのリスト
        """
        endpoint = f"{self.base_url}/klines"

        params = {
            'symbol': f"{symbol}USDT",
            'interval': '1m',
            'limit': limit
        }

        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # データ変換
            result = []
            for kline in data:
                result.append({
                    'timestamp': kline[0],  # ミリ秒
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'quote_volume': float(kline[7])
                })

            return result

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] API fetch failed: {e}")
            return []

    def collect_initial_data(self, symbol: str, days: int = 30):
        """
        初回データ取得（指定日数分を全取得）

        Args:
            symbol: 通貨シンボル
            days: 取得日数

        Returns:
            取得件数
        """
        print(f"\n{'='*80}")
        print(f"[INITIAL] {symbol} - Fetching {days} days of data")
        print(f"{'='*80}")

        # 開始・終了時刻を計算
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        total_records = 0
        current_start = start_time

        # Binance APIは1回1000件まで
        while current_start < end_time:
            data = self.fetch_klines(symbol, start_time=current_start, end_time=end_time, limit=1000)

            if not data:
                break

            # 保存
            self.storage.save_price_data(symbol, '1m', data)
            total_records += len(data)

            # 次のバッチの開始時刻
            last_timestamp = data[-1]['timestamp']
            current_start = last_timestamp + 60000  # 1分後

            # 進捗表示
            progress = ((current_start - start_time) / (end_time - start_time)) * 100
            print(f"   Progress: {progress:.1f}% ({total_records} records)", end='\r')

            # API制限対策
            time.sleep(0.5)

            # 最新データに追いついたら終了
            if len(data) < 1000:
                break

        print(f"\n[OK] Completed: {total_records} records fetched")
        return total_records

    def collect_incremental_data(self, symbol: str):
        """
        差分データ取得（最終取得時刻以降のみ）

        Args:
            symbol: 通貨シンボル

        Returns:
            取得件数
        """
        print(f"\n{'='*80}")
        print(f"[UPDATE] {symbol} - Incremental update")
        print(f"{'='*80}")

        # 最終取得時刻を取得
        last_timestamp = self.get_latest_timestamp(symbol)

        if last_timestamp is None:
            print("[WARNING] No existing data. Please run initial fetch first.")
            return 0

        last_time_str = datetime.fromtimestamp(last_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Last fetch: {last_time_str}")

        # 最終取得時刻から現在まで
        start_time = last_timestamp + 60000  # 1分後
        end_time = int(datetime.now().timestamp() * 1000)

        # 時間差を計算
        time_diff = (end_time - start_time) / 1000 / 60  # 分
        print(f"Time delta: {time_diff:.0f} minutes")

        if time_diff <= 0:
            print("[OK] Already up-to-date.")
            return 0

        total_records = 0
        current_start = start_time

        while current_start < end_time:
            data = self.fetch_klines(symbol, start_time=current_start, end_time=end_time, limit=1000)

            if not data:
                break

            # 保存
            self.storage.save_price_data(symbol, '1m', data)
            total_records += len(data)

            # 次のバッチ
            last_timestamp = data[-1]['timestamp']
            current_start = last_timestamp + 60000

            # 進捗表示
            progress = ((current_start - start_time) / (end_time - start_time)) * 100
            print(f"   Progress: {progress:.1f}% ({total_records} records)", end='\r')

            # API制限対策
            time.sleep(0.5)

            # 最新データに追いついたら終了
            if len(data) < 1000:
                break

        print(f"\n[OK] Completed: {total_records} records fetched")
        return total_records

    def collect_data(self, symbol: str, days: int = None):
        """
        データ収集（自動判定: 初回 or 差分）

        Args:
            symbol: 通貨シンボル
            days: 初回取得日数（差分更新の場合は無視される）

        Returns:
            取得件数
        """
        last_timestamp = self.get_latest_timestamp(symbol)

        if last_timestamp is None:
            # 初回取得
            if days is None:
                days = 30  # デフォルト30日
            return self.collect_initial_data(symbol, days)
        else:
            # 差分取得
            return self.collect_incremental_data(symbol)

    def collect_multiple_symbols(self, symbols: list, days: int = None):
        """
        複数通貨の一括データ取得

        Args:
            symbols: 通貨シンボルリスト
            days: 初回取得日数

        Returns:
            dict: {symbol: count}
        """
        print(f"\n{'='*80}")
        print(f"Bulk Data Collection")
        print(f"{'='*80}")
        print(f"Symbols: {', '.join(symbols)}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")

        results = {}

        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] {symbol}")
            count = self.collect_data(symbol, days)
            results[symbol] = count

            # 次の通貨の前に少し待機
            if i < len(symbols):
                time.sleep(1)

        # サマリー
        print(f"\n{'='*80}")
        print(f"Summary")
        print(f"{'='*80}")
        for symbol, count in results.items():
            print(f"  {symbol}: {count:,} records")
        print(f"  Total: {sum(results.values()):,} records")
        print(f"{'='*80}\n")

        return results

    def get_data_summary(self, symbols: list = None):
        """
        保存済みデータのサマリーを表示

        Args:
            symbols: 確認する通貨リスト（Noneなら全て）
        """
        print(f"\n{'='*80}")
        print(f"Saved Data Summary")
        print(f"{'='*80}")

        if symbols is None:
            # データディレクトリから全ファイルを検索
            price_dir = self.storage.price_dir
            files = list(price_dir.glob("*_1m.parquet"))
            symbols = [f.stem.replace('_1m', '') for f in files]

        for symbol in symbols:
            try:
                df = self.storage.load_price_data(symbol, '1m')
                if df.empty:
                    print(f"  {symbol}: No data")
                    continue

                first_time = df.index[0].strftime('%Y-%m-%d %H:%M')
                last_time = df.index[-1].strftime('%Y-%m-%d %H:%M')
                count = len(df)
                days = (df.index[-1] - df.index[0]).days

                print(f"  {symbol}:")
                print(f"    Count: {count:,} records")
                print(f"    Period: {first_time} ~ {last_time} ({days} days)")

            except Exception as e:
                print(f"  {symbol}: Error ({e})")

        print(f"{'='*80}\n")


def main():
    """コマンドライン実行"""
    # Windows環境でUnicode出力を有効化
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description='1分足データ収集スクリプト')

    parser.add_argument('--symbols', type=str, default='BTC,ETH,SOL',
                       help='通貨シンボル（カンマ区切り）。例: BTC,ETH,SOL,AVAX')

    parser.add_argument('--days', type=int, default=None,
                       help='初回取得日数（デフォルト: 30日）。差分更新の場合は無視される')

    parser.add_argument('--summary', action='store_true',
                       help='保存済みデータのサマリーを表示')

    parser.add_argument('--data-dir', type=str, default=None,
                       help='データ保存先ディレクトリ（デフォルト: sample/data/timeseries）')

    args = parser.parse_args()

    # 収集システム初期化
    collector = MinuteDataCollector(data_dir=args.data_dir)

    # サマリー表示モード
    if args.summary:
        symbols = args.symbols.split(',')
        collector.get_data_summary(symbols)
        return

    # データ収集
    symbols = args.symbols.split(',')

    try:
        results = collector.collect_multiple_symbols(symbols, days=args.days)

        # データサマリーを表示
        collector.get_data_summary(symbols)

        print("[OK] All tasks completed!")

    except KeyboardInterrupt:
        print("\n\n[WARNING] Interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
