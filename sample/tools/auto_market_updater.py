"""
定期自動市場データ更新

定期的に全銘柄の価格をスキャンしてDBに保存
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.market_scanner import MarketScanner
import time
import argparse
from datetime import datetime


class AutoMarketUpdater:
    """自動市場データ更新"""

    def __init__(self, interval_minutes: int = 60, min_volume: float = 10000):
        """
        Parameters:
        - interval_minutes: 更新間隔（分）
        - min_volume: 最低出来高（USDT）
        """
        self.scanner = MarketScanner()
        self.interval_minutes = interval_minutes
        self.min_volume = min_volume
        self.run_count = 0

    def run_once(self):
        """1回だけスキャンを実行"""
        self.run_count += 1
        print()
        print("="*80)
        print(f"🔄 自動更新 #{self.run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        self.scanner.scan_all_markets(min_volume=self.min_volume)

        print(f"✅ 更新完了 - 次回: {self.interval_minutes}分後")

    def run_continuous(self):
        """定期的にスキャンを実行"""
        print("="*80)
        print("🤖 自動市場データ更新を開始")
        print("="*80)
        print(f"更新間隔: {self.interval_minutes}分")
        print(f"最低出来高: ${self.min_volume:,.0f}")
        print()
        print("💡 停止するには Ctrl+C を押してください")
        print()

        try:
            while True:
                self.run_once()

                # 次回まで待機
                print(f"⏸️  {self.interval_minutes}分間待機中...")
                time.sleep(self.interval_minutes * 60)

        except KeyboardInterrupt:
            print()
            print("="*80)
            print("⏹️  自動更新を停止しました")
            print("="*80)
            print(f"総実行回数: {self.run_count}回")


def main():
    parser = argparse.ArgumentParser(
        description='定期自動市場データ更新 - 指定間隔で全銘柄をスキャン',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  # 1回だけ実行
  python tools/auto_market_updater.py --once

  # 60分ごとに自動更新（デフォルト）
  python tools/auto_market_updater.py --continuous

  # 30分ごとに自動更新
  python tools/auto_market_updater.py --continuous --interval 30

  # 10分ごと、出来高5万以上
  python tools/auto_market_updater.py --continuous --interval 10 --min-volume 50000

推奨設定:
  - 開発中: --interval 10（10分ごと）
  - 通常運用: --interval 60（1時間ごと）
  - 高頻度トレード: --interval 5（5分ごと）
        '''
    )

    parser.add_argument('--once', action='store_true', help='1回だけ実行')
    parser.add_argument('--continuous', action='store_true', help='定期的に実行')
    parser.add_argument('--interval', type=int, default=60, help='更新間隔（分）')
    parser.add_argument('--min-volume', type=float, default=10000, help='最低出来高（USDT）')

    args = parser.parse_args()

    updater = AutoMarketUpdater(
        interval_minutes=args.interval,
        min_volume=args.min_volume
    )

    if args.once:
        # 1回だけ実行
        updater.run_once()

    elif args.continuous:
        # 定期的に実行
        updater.run_continuous()

    else:
        # 引数なし：ヘルプ表示
        parser.print_help()


if __name__ == '__main__':
    main()
