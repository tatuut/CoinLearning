"""
Parquet閲覧CLIツール

保存されているparquetファイルを見やすく表示
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# ルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from pathlib import Path
import argparse
from datetime import datetime
from src.data.timeseries_storage import TimeSeriesStorage


class ParquetViewer:
    """Parquetデータビューア"""

    def __init__(self):
        self.storage = TimeSeriesStorage()

    def list_all(self):
        """全parquetファイル一覧"""
        print("="*80)
        print("📊 保存されているParquetファイル一覧")
        print("="*80)
        print()

        info = self.storage.get_storage_info()

        if not info['prices']:
            print("❌ Parquetファイルが見つかりません")
            print()
            print("データを収集してください:")
            print("  python crypto_analyst.py BTC")
            return

        print(f"総ファイル数: {len(info['prices'])}")
        print(f"総データ行数: {info['total_rows']:,}行")
        print(f"総サイズ: {info['total_size_kb']:.1f}KB")
        print()
        print("-"*80)
        print()

        # テーブル形式で表示
        print(f"{'ファイル名':<20} {'行数':>10} {'サイズ':>10} {'期間':<40}")
        print("-"*80)

        for item in sorted(info['prices'], key=lambda x: x['file']):
            file_name = item['file']
            rows = f"{item['rows']:,}行"
            size = f"{item['size_kb']}KB"
            period = f"{item['start_date'][:10]} ～ {item['end_date'][:10]}"
            print(f"{file_name:<20} {rows:>10} {size:>10} {period:<40}")

        print()

    def show_data(self, symbol: str, interval: str, limit: int = 10):
        """データの内容を表示"""
        print("="*80)
        print(f"📈 {symbol} - {interval} データ")
        print("="*80)
        print()

        df = self.storage.load_price_data(symbol, interval)

        if df.empty:
            print(f"❌ {symbol}_{interval}.parquet が見つかりません")
            return

        print(f"期間: {df.index.min()} ～ {df.index.max()}")
        print(f"総行数: {len(df):,}行")
        print()

        # 直近N件を表示
        print(f"【直近{limit}件】")
        print()

        # pandas表示オプション設定
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.float_format', '{:.2f}'.format)

        print(df.tail(limit))
        print()

    def show_stats(self, symbol: str, interval: str):
        """統計情報を表示"""
        print("="*80)
        print(f"📊 {symbol} - {interval} 統計情報")
        print("="*80)
        print()

        df = self.storage.load_price_data(symbol, interval)

        if df.empty:
            print(f"❌ {symbol}_{interval}.parquet が見つかりません")
            return

        print(f"【基本情報】")
        print(f"  期間: {df.index.min()} ～ {df.index.max()}")
        print(f"  データ数: {len(df):,}行")
        print()

        print(f"【価格統計】")
        print(f"  現在価格: ${df['close'].iloc[-1]:,.2f}")
        print(f"  期間最高: ${df['high'].max():,.2f}")
        print(f"  期間最安: ${df['low'].min():,.2f}")
        print(f"  平均価格: ${df['close'].mean():,.2f}")
        print(f"  中央値: ${df['close'].median():,.2f}")
        print()

        # リターン計算
        returns = df['close'].pct_change()
        print(f"【リターン統計】")
        print(f"  平均リターン: {returns.mean()*100:.2f}%")
        print(f"  標準偏差: {returns.std()*100:.2f}%")
        print(f"  最大上昇: {returns.max()*100:.2f}%")
        print(f"  最大下落: {returns.min()*100:.2f}%")
        print()

        # RSI計算
        rsi = self.storage.calculate_rsi(df)
        print(f"【テクニカル指標】")
        print(f"  現在のRSI(14): {rsi.iloc[-1]:.2f}")
        if rsi.iloc[-1] > 70:
            print(f"    → 買われすぎ")
        elif rsi.iloc[-1] < 30:
            print(f"    → 売られすぎ")
        else:
            print(f"    → 中立")
        print()

        # ボラティリティ
        volatility = self.storage.calculate_volatility(df, window=20)
        print(f"  ボラティリティ(20期間): {volatility.iloc[-1]*100:.2f}%")
        print()

    def show_chart(self, symbol: str, interval: str, limit: int = 20):
        """簡易チャート表示（ASCIIアート）"""
        print("="*80)
        print(f"📈 {symbol} - {interval} チャート（直近{limit}件）")
        print("="*80)
        print()

        df = self.storage.load_price_data(symbol, interval)

        if df.empty:
            print(f"❌ {symbol}_{interval}.parquet が見つかりません")
            return

        # 直近N件
        df = df.tail(limit)

        # 価格の正規化（0-20の範囲にマッピング）
        close_prices = df['close'].values
        min_price = close_prices.min()
        max_price = close_prices.max()

        chart_height = 20

        def normalize(price):
            if max_price == min_price:
                return chart_height // 2
            return int((price - min_price) / (max_price - min_price) * chart_height)

        # チャート描画
        for i in range(chart_height, -1, -1):
            # Y軸ラベル
            price_at_level = min_price + (max_price - min_price) * (i / chart_height)
            y_label = f"${price_at_level:8,.2f} │"
            line = y_label

            # プロット
            for price in close_prices:
                level = normalize(price)
                if level == i:
                    line += "●"
                elif level > i:
                    line += " "
                else:
                    line += " "

            print(line)

        # X軸
        print("           └" + "─" * len(close_prices))

        # 日付表示（最初と最後）
        first_date = df.index[0].strftime('%m/%d')
        last_date = df.index[-1].strftime('%m/%d')
        print(f"            {first_date}" + " " * (len(close_prices) - 10) + f"{last_date}")
        print()

        # 価格変動
        first_price = close_prices[0]
        last_price = close_prices[-1]
        change_pct = ((last_price - first_price) / first_price) * 100

        if change_pct > 0:
            print(f"  📈 期間変動: +{change_pct:.2f}% (${first_price:,.2f} → ${last_price:,.2f})")
        else:
            print(f"  📉 期間変動: {change_pct:.2f}% (${first_price:,.2f} → ${last_price:,.2f})")
        print()

    def compare_symbols(self, symbols: list, interval: str):
        """複数銘柄の比較"""
        print("="*80)
        print(f"📊 複数銘柄比較 ({interval})")
        print("="*80)
        print()

        data = {}
        for symbol in symbols:
            df = self.storage.load_price_data(symbol, interval)
            if not df.empty:
                data[symbol] = df

        if not data:
            print("❌ データがありません")
            return

        # テーブル形式で比較
        print(f"{'銘柄':<8} {'現在価格':>12} {'期間高値':>12} {'期間安値':>12} {'変動率':>10} {'データ数':>10}")
        print("-"*80)

        for symbol, df in data.items():
            current = df['close'].iloc[-1]
            high = df['high'].max()
            low = df['low'].min()
            change = ((current - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
            count = len(df)

            print(f"{symbol:<8} ${current:>11,.2f} ${high:>11,.2f} ${low:>11,.2f} {change:>9.2f}% {count:>9,}行")

        print()

        # 相関係数計算
        if len(data) >= 2:
            print("【相関係数】")
            symbols_list = list(data.keys())
            for i in range(len(symbols_list)):
                for j in range(i + 1, len(symbols_list)):
                    sym1, sym2 = symbols_list[i], symbols_list[j]
                    corr = self.storage.calculate_correlation(data[sym1], data[sym2])
                    if corr is not None:
                        print(f"  {sym1} ⟷ {sym2}: {corr:.3f}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Parquet閲覧CLIツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 全ファイル一覧
  python src/tools/parquet_viewer.py --list

  # BTCの1日足データを表示
  python src/tools/parquet_viewer.py --show BTC 1d

  # BTCの統計情報
  python src/tools/parquet_viewer.py --stats BTC 1d

  # BTCのチャート表示
  python src/tools/parquet_viewer.py --chart BTC 1d

  # 複数銘柄の比較
  python src/tools/parquet_viewer.py --compare BTC ETH DOGE --interval 1d
        """
    )

    parser.add_argument('--list', action='store_true',
                       help='全parquetファイル一覧')
    parser.add_argument('--show', nargs=2, metavar=('SYMBOL', 'INTERVAL'),
                       help='データ表示（例: BTC 1d）')
    parser.add_argument('--stats', nargs=2, metavar=('SYMBOL', 'INTERVAL'),
                       help='統計情報表示（例: BTC 1d）')
    parser.add_argument('--chart', nargs=2, metavar=('SYMBOL', 'INTERVAL'),
                       help='チャート表示（例: BTC 1d）')
    parser.add_argument('--compare', nargs='+', metavar='SYMBOL',
                       help='複数銘柄比較（例: BTC ETH DOGE）')
    parser.add_argument('--interval', default='1d',
                       help='時間足（compareモード用、デフォルト: 1d）')
    parser.add_argument('--limit', type=int, default=10,
                       help='表示件数（デフォルト: 10）')

    args = parser.parse_args()

    viewer = ParquetViewer()

    if args.list:
        viewer.list_all()

    elif args.show:
        symbol, interval = args.show
        viewer.show_data(symbol.upper(), interval, limit=args.limit)

    elif args.stats:
        symbol, interval = args.stats
        viewer.show_stats(symbol.upper(), interval)

    elif args.chart:
        symbol, interval = args.chart
        viewer.show_chart(symbol.upper(), interval, limit=args.limit)

    elif args.compare:
        symbols = [s.upper() for s in args.compare]
        viewer.compare_symbols(symbols, args.interval)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
