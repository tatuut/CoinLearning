"""
パフォーマンス分析ツール

取引履歴を分析して統計を表示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import TradeDatabase
from datetime import datetime, timedelta
from typing import Dict, List


class PerformanceAnalyzer:
    """パフォーマンス分析"""

    def __init__(self, db_path: str = None):
        self.db = TradeDatabase(db_path)

    def get_overall_stats(self) -> Dict:
        """全体統計を取得"""
        return self.db.get_statistics()

    def print_summary(self):
        """サマリーを表示"""
        stats = self.get_overall_stats()

        print("\n" + "="*60)
        print("📊 トレード成績サマリー")
        print("="*60)

        print(f"\n【基本統計】")
        print(f"  総取引数:     {stats['total_trades']} 回")
        print(f"  勝ちトレード: {stats['winning_trades']} 回")
        print(f"  負けトレード: {stats['losing_trades']} 回")
        print(f"  勝率:         {stats['win_rate']:.1f}%")

        print(f"\n【損益】")
        print(f"  総損益:       ${stats['total_profit_loss']:.2f}")
        print(f"  総利益:       ${stats['total_profit']:.2f}")
        print(f"  総損失:       ${stats['total_loss']:.2f}")
        print(f"  プロフィットファクター: {stats['profit_factor']:.2f}")

        print(f"\n【平均】")
        avg_win = stats['avg_win_percent'] or 0
        avg_loss = stats['avg_loss_percent'] or 0
        print(f"  平均利益率:   {avg_win:+.2f}%")
        print(f"  平均損失率:   {avg_loss:.2f}%")

        # 評価
        print(f"\n【評価】")
        if stats['total_trades'] == 0:
            print("  まだ取引がありません。")
        elif stats['win_rate'] >= 60 and stats['profit_factor'] >= 2.0:
            print("  🌟 優秀！この調子で続けましょう！")
        elif stats['win_rate'] >= 50 and stats['profit_factor'] >= 1.5:
            print("  ✅ 良好！安定した成績です。")
        elif stats['total_profit_loss'] > 0:
            print("  💡 利益は出ています。改善の余地あり。")
        else:
            print("  ⚠️  損失が出ています。戦略を見直しましょう。")

        print("="*60 + "\n")

    def get_recent_trades(self, days: int = 7) -> List[Dict]:
        """最近の取引を取得"""
        trades = self.db.get_completed_trades(limit=100)

        cutoff = datetime.now() - timedelta(days=days)

        recent = [
            t for t in trades
            if datetime.fromisoformat(t['completed_at']) > cutoff
        ]

        return recent

    def print_recent_trades(self, days: int = 7):
        """最近の取引を表示"""
        trades = self.get_recent_trades(days)

        print(f"\n📅 直近{days}日間の取引履歴")
        print("="*80)

        if not trades:
            print("取引履歴がありません。")
            return

        for trade in trades[:10]:  # 最新10件
            symbol = trade['coin_symbol']
            profit = trade['profit_loss_percent']
            amount = trade['profit_loss']
            time = datetime.fromisoformat(trade['completed_at']).strftime('%m/%d %H:%M')

            profit_mark = "📈" if profit > 0 else "📉"
            print(f"{profit_mark} {time} | {symbol:10s} | "
                  f"{profit:+7.2f}% | ${amount:+8.2f}")

        print("="*80 + "\n")

    def get_best_worst_trades(self) -> Dict:
        """最高・最悪の取引を取得"""
        trades = self.db.get_completed_trades(limit=1000)

        if not trades:
            return {'best': None, 'worst': None}

        best = max(trades, key=lambda x: x['profit_loss_percent'])
        worst = min(trades, key=lambda x: x['profit_loss_percent'])

        return {'best': best, 'worst': worst}

    def print_best_worst(self):
        """最高・最悪の取引を表示"""
        bw = self.get_best_worst_trades()

        print("\n🏆 ベスト & ワースト")
        print("="*60)

        if bw['best']:
            best = bw['best']
            print(f"最高利益: {best['coin_symbol']}")
            print(f"  利益率: {best['profit_loss_percent']:+.2f}%")
            print(f"  利益額: ${best['profit_loss']:+.2f}")
            print(f"  日時:   {best['completed_at'][:16]}")

        if bw['worst']:
            worst = bw['worst']
            print(f"\n最大損失: {worst['coin_symbol']}")
            print(f"  損失率: {worst['profit_loss_percent']:.2f}%")
            print(f"  損失額: ${worst['profit_loss']:.2f}")
            print(f"  日時:   {worst['completed_at'][:16]}")

        print("="*60 + "\n")

    def get_coin_performance(self) -> Dict:
        """コイン別のパフォーマンス"""
        trades = self.db.get_completed_trades(limit=1000)

        coin_stats = {}

        for trade in trades:
            symbol = trade['coin_symbol']

            if symbol not in coin_stats:
                coin_stats[symbol] = {
                    'total_trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_profit_loss': 0,
                }

            coin_stats[symbol]['total_trades'] += 1
            coin_stats[symbol]['total_profit_loss'] += trade['profit_loss']

            if trade['profit_loss'] > 0:
                coin_stats[symbol]['wins'] += 1
            else:
                coin_stats[symbol]['losses'] += 1

        # 勝率計算
        for symbol, stats in coin_stats.items():
            stats['win_rate'] = (stats['wins'] / stats['total_trades']) * 100

        return coin_stats

    def print_coin_performance(self):
        """コイン別パフォーマンスを表示"""
        coin_perf = self.get_coin_performance()

        if not coin_perf:
            print("取引履歴がありません。")
            return

        print("\n💰 コイン別パフォーマンス")
        print("="*80)
        print(f"{'コイン':<12} | {'取引数':>6} | {'勝率':>6} | {'損益':>12}")
        print("-"*80)

        # 損益順にソート
        sorted_coins = sorted(coin_perf.items(),
                              key=lambda x: x[1]['total_profit_loss'],
                              reverse=True)

        for symbol, stats in sorted_coins[:10]:  # トップ10
            print(f"{symbol:<12} | {stats['total_trades']:>6} | "
                  f"{stats['win_rate']:>5.1f}% | ${stats['total_profit_loss']:>10.2f}")

        print("="*80 + "\n")

    def get_balance_trend(self) -> List[Dict]:
        """残高の推移を取得"""
        return self.db.get_balance_history(limit=30)

    def print_balance_trend(self):
        """残高推移を表示"""
        history = self.get_balance_trend()

        if not history:
            print("残高履歴がありません。")
            return

        print("\n📈 残高推移（直近10件）")
        print("="*70)
        print(f"{'日時':<18} | {'総資産':>12} | {'利用可能':>12} | {'総損益':>12}")
        print("-"*70)

        for record in history[:10]:
            time = record['timestamp'][:16]
            total = record['total_balance']
            available = record['available_balance']
            pl = record['total_profit_loss']

            print(f"{time:<18} | ${total:>10.2f} | ${available:>10.2f} | ${pl:>10.2f}")

        print("="*70 + "\n")

    def get_100_to_1000_progress(self, starting_balance: float = 100.0) -> Dict:
        """100円→1000円への進捗"""
        balance_history = self.get_balance_trend()

        if not balance_history:
            current_balance = starting_balance
        else:
            current_balance = balance_history[0]['total_balance']

        progress = (current_balance / 1000.0) * 100
        remaining = 1000.0 - current_balance
        multiplier = current_balance / starting_balance

        return {
            'starting': starting_balance,
            'current': current_balance,
            'target': 1000.0,
            'progress_percent': progress,
            'remaining': remaining,
            'multiplier': multiplier
        }

    def print_goal_progress(self, starting_balance: float = 100.0):
        """目標達成進捗を表示"""
        progress = self.get_100_to_1000_progress(starting_balance)

        print("\n🎯 100円→1000円への道")
        print("="*60)
        print(f"スタート: ${progress['starting']:.2f}")
        print(f"現在:     ${progress['current']:.2f} ({progress['multiplier']:.1f}倍)")
        print(f"目標:     ${progress['target']:.2f}")
        print(f"残り:     ${progress['remaining']:.2f}")
        print(f"\n進捗: {progress['progress_percent']:.1f}%")

        # プログレスバー
        bar_length = 40
        filled = int(bar_length * progress['progress_percent'] / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"[{bar}]")

        if progress['current'] >= 1000:
            print("\n🎉 目標達成！おめでとうございます！")
        elif progress['progress_percent'] >= 50:
            print("\n💪 折り返し地点突破！この調子で！")
        else:
            print("\n📊 順調に進んでいます！")

        print("="*60 + "\n")

    def generate_full_report(self, starting_balance: float = 100.0):
        """完全なレポートを生成"""
        print("\n" + "🎯" * 30)
        print(" " * 20 + "トレード分析レポート")
        print("🎯" * 30)

        self.print_goal_progress(starting_balance)
        self.print_summary()
        self.print_recent_trades(days=7)
        self.print_best_worst()
        self.print_coin_performance()
        self.print_balance_trend()

        print("\n✅ レポート生成完了\n")


def main():
    """メイン実行"""
    analyzer = PerformanceAnalyzer()

    analyzer.generate_full_report(starting_balance=100.0)


if __name__ == '__main__':
    main()
