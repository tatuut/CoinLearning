"""
時系列データストレージ最適化

Parquet形式で軽量・高速・分析しやすいデータ保存
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json


class TimeSeriesStorage:
    """
    時系列データの最適化ストレージ

    - Parquet形式: 圧縮効率が高く、カラム単位で高速読み込み
    - 銘柄ごとにファイル分割: 必要な銘柄だけ読み込み可能
    - DatetimeIndex: 時間軸での操作が高速
    - 数値型最適化: float32で容量削減
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), 'timeseries')

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # 銘柄ごとのディレクトリ
        self.price_dir = self.data_dir / 'prices'
        self.news_dir = self.data_dir / 'news'
        self.stats_dir = self.data_dir / 'stats'

        for d in [self.price_dir, self.news_dir, self.stats_dir]:
            d.mkdir(exist_ok=True)

    def save_price_data(self, symbol: str, interval: str, data: list):
        """
        価格データをParquet形式で保存（高速化版）

        Args:
            symbol: 銘柄シンボル
            interval: 時間足（1h, 4h, 1d など）
            data: 価格データリスト [{'timestamp': ..., 'open': ..., }, ...]

        保存形式:
            data/timeseries/prices/BTC_1h.parquet
            data/timeseries/prices/BTC_1d.parquet
        """
        if not data:
            return

        # Parquetで保存（圧縮あり）
        filename = f"{symbol}_{interval}.parquet"
        filepath = self.price_dir / filename

        # 既存データがあれば最終タイムスタンプを取得
        last_timestamp = None
        existing_df = None
        if filepath.exists():
            try:
                existing_df = pd.read_parquet(filepath)
                if not existing_df.empty:
                    last_timestamp = existing_df.index[-1]
            except Exception as e:
                # 破損ファイルを検出（削除は後で）
                print(f"[WARNING] Corrupted file detected, will recreate: {filename}")
                existing_df = None
                # ファイルを新規作成モードにするため、filepathを一時的にリネーム
                import time
                backup_path = filepath.with_suffix(f'.corrupted.{int(time.time())}')
                try:
                    filepath.rename(backup_path)
                except:
                    pass  # リネーム失敗してもOK（新規データで上書きする）

        # DataFrameに変換
        df = pd.DataFrame(data)

        # タイムスタンプをdatetimeに変換（ミリ秒対応）
        if 'timestamp' in df.columns:
            if df['timestamp'].dtype == 'int64':
                # ミリ秒なら秒に変換
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            # DatetimeIndexに設定
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)

        # 新規データのみをフィルタ（既存データと重複を除外）
        if last_timestamp is not None:
            df = df[df.index > last_timestamp]

            # 新規データがなければスキップ
            if df.empty:
                return filepath

        # 数値型を最適化（float64 → float32で容量半分）
        for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
            if col in df.columns:
                df[col] = df[col].astype('float32')

        # 重複を削除
        df = df[~df.index.duplicated(keep='last')]

        # 既存データと結合
        if existing_df is not None:
            df = pd.concat([existing_df, df])
            df.sort_index(inplace=True)
            # existing_dfを明示的に削除（メモリ解放）
            del existing_df
            import gc
            gc.collect()

        # Atomic write: 一時ファイルに書き込み → 成功したらrename
        import time
        import gc
        temp_filename = f"{symbol}_{interval}.tmp.{int(time.time() * 1000)}.parquet"
        temp_filepath = self.price_dir / temp_filename

        try:
            # 一時ファイルに書き込み（compression無効化でテスト）
            df.to_parquet(temp_filepath, compression=None)

            # 書き込み成功を検証（読み込みテスト）
            test_df = pd.read_parquet(temp_filepath)
            if len(test_df) != len(df):
                raise ValueError(f"Verification failed: expected {len(df)} rows, got {len(test_df)}")

            # 検証用DataFrameを明示的に削除（ファイルハンドル解放）
            del test_df
            gc.collect()

            # 検証成功 → 本ファイルにrename（atomic操作）
            # Windowsでは既存ファイルがある場合は先に削除（retry付き）
            if filepath.exists():
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        filepath.unlink()
                        break
                    except PermissionError:
                        if attempt < max_retries - 1:
                            time.sleep(0.1)  # 100ms待機
                            gc.collect()  # 強制GC
                        else:
                            raise

            temp_filepath.rename(filepath)

            file_size = filepath.stat().st_size / 1024  # KB
            print(f"[OK] 保存: {filename} ({len(df)}行, {file_size:.1f}KB)")

        except Exception as e:
            # エラー時は一時ファイルを削除
            if temp_filepath.exists():
                temp_filepath.unlink()
            raise RuntimeError(f"Failed to save {filename}: {e}")

        return filepath

    def load_price_data(self, symbol: str, interval: str,
                       start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        価格データを読み込み

        Args:
            symbol: 銘柄シンボル
            interval: 時間足
            start_date: 開始日（例: '2025-10-01'）
            end_date: 終了日

        Returns:
            pandas DataFrame（DatetimeIndex付き）
        """
        filename = f"{symbol}_{interval}.parquet"
        filepath = self.price_dir / filename

        if not filepath.exists():
            print(f"[ERROR] ファイルなし: {filename}")
            return pd.DataFrame()

        df = pd.read_parquet(filepath)

        # 日付範囲でフィルタ
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        return df

    def get_storage_info(self):
        """
        ストレージ情報を取得

        Returns:
            各銘柄・時間足のファイルサイズと行数
        """
        info = {
            'prices': [],
            'total_size_kb': 0,
            'total_rows': 0
        }

        for filepath in self.price_dir.glob('*.parquet'):
            df = pd.read_parquet(filepath)
            size_kb = filepath.stat().st_size / 1024

            info['prices'].append({
                'file': filepath.name,
                'rows': len(df),
                'size_kb': round(size_kb, 1),
                'start_date': str(df.index.min()),
                'end_date': str(df.index.max())
            })

            info['total_size_kb'] += size_kb
            info['total_rows'] += len(df)

        return info

    def calculate_returns(self, df: pd.DataFrame, column: str = 'close') -> pd.Series:
        """
        リターン（収益率）を計算

        Returns:
            (価格t - 価格t-1) / 価格t-1
        """
        return df[column].pct_change()

    def calculate_log_returns(self, df: pd.DataFrame, column: str = 'close') -> pd.Series:
        """
        対数リターンを計算（連続複利）

        Returns:
            log(価格t / 価格t-1)
        """
        return np.log(df[column] / df[column].shift(1))

    def calculate_volatility(self, df: pd.DataFrame, window: int = 20,
                           column: str = 'close') -> pd.Series:
        """
        ボラティリティを計算（標準偏差）

        Args:
            window: 計算期間（デフォルト20期間）
        """
        returns = self.calculate_returns(df, column)
        return returns.rolling(window=window).std() * np.sqrt(window)

    def calculate_moving_average(self, df: pd.DataFrame, window: int,
                                column: str = 'close') -> pd.Series:
        """
        移動平均を計算
        """
        return df[column].rolling(window=window).mean()

    def calculate_ema(self, df: pd.DataFrame, span: int,
                     column: str = 'close') -> pd.Series:
        """
        指数移動平均（EMA）を計算
        """
        return df[column].ewm(span=span, adjust=False).mean()

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14,
                     column: str = 'close') -> pd.Series:
        """
        RSI（相対力指数）を計算
        """
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_bollinger_bands(self, df: pd.DataFrame, window: int = 20,
                                  num_std: float = 2, column: str = 'close'):
        """
        ボリンジャーバンドを計算

        Returns:
            (middle, upper, lower) のタプル
        """
        middle = self.calculate_moving_average(df, window, column)
        std = df[column].rolling(window=window).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)

        return middle, upper, lower

    def calculate_macd(self, df: pd.DataFrame,
                      fast: int = 12, slow: int = 26, signal: int = 9,
                      column: str = 'close'):
        """
        MACD（移動平均収束拡散法）を計算

        Returns:
            (macd, signal, histogram) のタプル
        """
        ema_fast = self.calculate_ema(df, fast, column)
        ema_slow = self.calculate_ema(df, slow, column)
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return macd, signal_line, histogram

    def resample_data(self, df: pd.DataFrame, rule: str):
        """
        時間足を変換（リサンプリング）

        Args:
            rule: '1H', '4H', '1D', '1W' など

        Example:
            # 1時間足を4時間足に変換
            df_4h = storage.resample_data(df_1h, '4H')
        """
        return df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })

    def get_price_at_time(self, df: pd.DataFrame, timestamp: str,
                         column: str = 'close'):
        """
        特定時刻の価格を取得（前方補完）

        Args:
            timestamp: '2025-10-15 14:30:00'
        """
        target_time = pd.to_datetime(timestamp)

        if target_time in df.index:
            return df.loc[target_time, column]
        else:
            # 前方補完（直前の値を使用）
            idx = df.index.searchsorted(target_time)
            if idx > 0:
                return df.iloc[idx - 1][column]
            return None

    def calculate_correlation(self, df1: pd.DataFrame, df2: pd.DataFrame,
                            column: str = 'close') -> float:
        """
        2つの銘柄の相関係数を計算
        """
        # 共通の時間軸に揃える
        common_index = df1.index.intersection(df2.index)

        if len(common_index) == 0:
            return None

        series1 = df1.loc[common_index, column]
        series2 = df2.loc[common_index, column]

        return series1.corr(series2)


def migrate_from_sqlite():
    """
    SQLiteからParquetへの移行ツール
    """
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    from data.advanced_database import AdvancedDatabase

    print("="*80)
    print("SQLite → Parquet 移行ツール")
    print("="*80)
    print()

    db = AdvancedDatabase()
    storage = TimeSeriesStorage()

    cursor = db.conn.cursor()

    # 銘柄と時間足の組み合わせを取得
    cursor.execute('''
        SELECT DISTINCT symbol, interval
        FROM price_history_detailed
        ORDER BY symbol, interval
    ''')

    combinations = cursor.fetchall()

    print(f"移行対象: {len(combinations)}件")
    print()

    for symbol, interval in combinations:
        print(f"処理中: {symbol} {interval}...")

        # データ取得
        cursor.execute('''
            SELECT timestamp, open, high, low, close, volume, quote_volume
            FROM price_history_detailed
            WHERE symbol = ? AND interval = ?
            ORDER BY timestamp
        ''', (symbol, interval))

        rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                'timestamp': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'volume': row[5],
                'quote_volume': row[6]
            })

        # Parquetで保存
        storage.save_price_data(symbol, interval, data)

    print()
    print("="*80)
    print("移行完了")
    print("="*80)
    print()

    # 統計情報
    info = storage.get_storage_info()
    print(f"総ファイル数: {len(info['prices'])}")
    print(f"総データ行数: {info['total_rows']}")
    print(f"総サイズ: {info['total_size_kb']:.1f}KB")
    print()

    print("ファイル一覧:")
    for item in info['prices']:
        print(f"  {item['file']}: {item['rows']}行, {item['size_kb']}KB")

    db.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='時系列データストレージ')
    parser.add_argument('--migrate', action='store_true',
                       help='SQLiteからParquetへ移行')
    parser.add_argument('--info', action='store_true',
                       help='ストレージ情報を表示')
    parser.add_argument('--test', metavar='SYMBOL',
                       help='指定銘柄でテスト分析')

    args = parser.parse_args()

    if args.migrate:
        migrate_from_sqlite()

    elif args.info:
        storage = TimeSeriesStorage()
        info = storage.get_storage_info()

        print("="*80)
        print("ストレージ情報")
        print("="*80)
        print(f"総ファイル数: {len(info['prices'])}")
        print(f"総データ行数: {info['total_rows']:,}")
        print(f"総サイズ: {info['total_size_kb']:.1f}KB")
        print()

        for item in info['prices']:
            print(f"{item['file']}")
            print(f"  行数: {item['rows']:,}")
            print(f"  サイズ: {item['size_kb']}KB")
            print(f"  期間: {item['start_date']} ～ {item['end_date']}")
            print()

    elif args.test:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

        storage = TimeSeriesStorage()
        symbol = args.test.upper()

        print(f"{'='*80}")
        print(f"{symbol} - 数学的分析テスト")
        print(f"{'='*80}")
        print()

        # 1日足データ読み込み
        df = storage.load_price_data(symbol, '1d')

        if df.empty:
            print(f"[ERROR] {symbol}のデータがありません")
            print("先にデータ収集してください:")
            print(f"  python data/detailed_data_collector.py {symbol} --all-intervals")
            exit(1)

        print(f"データ期間: {df.index.min()} ～ {df.index.max()}")
        print(f"データ数: {len(df)}行")
        print()

        # 各種指標を計算
        print("【計算中...】")
        df['returns'] = storage.calculate_returns(df)
        df['log_returns'] = storage.calculate_log_returns(df)
        df['volatility_20'] = storage.calculate_volatility(df, window=20)
        df['sma_20'] = storage.calculate_moving_average(df, window=20)
        df['ema_20'] = storage.calculate_ema(df, span=20)
        df['rsi'] = storage.calculate_rsi(df)

        bb_mid, bb_upper, bb_lower = storage.calculate_bollinger_bands(df)
        df['bb_mid'] = bb_mid
        df['bb_upper'] = bb_upper
        df['bb_lower'] = bb_lower

        macd, signal, hist = storage.calculate_macd(df)
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_hist'] = hist

        print("✓ 完了")
        print()

        # 最新のデータ表示
        print("【最新データ（直近5日）】")
        print(df[['close', 'returns', 'volatility_20', 'rsi', 'macd']].tail())
        print()

        # 統計情報
        print("【統計情報】")
        print(f"現在価格: ${df['close'].iloc[-1]:,.2f}")
        print(f"平均価格: ${df['close'].mean():,.2f}")
        print(f"最高価格: ${df['close'].max():,.2f}")
        print(f"最安価格: ${df['close'].min():,.2f}")
        print(f"平均リターン: {df['returns'].mean()*100:.2f}%")
        print(f"リターン標準偏差: {df['returns'].std()*100:.2f}%")
        print(f"現在のRSI: {df['rsi'].iloc[-1]:.2f}")
        print(f"現在のボラティリティ: {df['volatility_20'].iloc[-1]*100:.2f}%")
        print()

        # トレンド判定
        current_price = df['close'].iloc[-1]
        sma_20 = df['sma_20'].iloc[-1]
        rsi = df['rsi'].iloc[-1]

        print("【トレンド分析】")
        if current_price > sma_20:
            print("[OK] 価格は20日移動平均の上 → 上昇トレンド")
        else:
            print("[OK] 価格は20日移動平均の下 → 下降トレンド")

        if rsi > 70:
            print(f"[OK] RSI={rsi:.1f} → 買われすぎ")
        elif rsi < 30:
            print(f"[OK] RSI={rsi:.1f} → 売られすぎ")
        else:
            print(f"[OK] RSI={rsi:.1f} → 中立")

        print()
        print("="*80)

    else:
        parser.print_help()
