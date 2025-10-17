"""
草コイントレーダー - メインプログラム

100円→1000円を目指す草コイン取引システム
"""

import os
import sys
from datetime import datetime

# 各モジュールをインポート
from config.exchange_api import BinanceAPI
from data.database import TradeDatabase
from strategies.momentum import MomentumStrategy
from strategies.volume_spike import VolumeSpikeStrategy
from strategies.breakout import BreakoutStrategy
from analysis.performance import PerformanceAnalyzer


class GrassCoinTrader:
    """草コイントレーダー"""

    def __init__(self):
        self.api = BinanceAPI()
        self.db = TradeDatabase()
        self.analyzer = PerformanceAnalyzer()

        # 戦略
        self.strategies = {
            'momentum': MomentumStrategy(),
            'volume_spike': VolumeSpikeStrategy(),
            'breakout': BreakoutStrategy(),
        }

    def show_menu(self):
        """メニューを表示"""
        print("\n" + "="*60)
        print("🌿 草コイントレーダー - 100円→1000円への道")
        print("="*60)
        print("\n【メインメニュー】")
        print("  1. 市場スキャン（買いシグナル検索）")
        print("  2. 特定コインを分析")
        print("  3. 現在のポジション確認")
        print("  4. パフォーマンス分析")
        print("  5. 学習カリキュラムを表示")
        print("  6. 取引を手動記録")
        print("  0. 終了")
        print("="*60)

    def scan_market(self):
        """市場をスキャン"""
        print("\n" + "="*60)
        print("🔍 市場スキャン")
        print("="*60)
        print("\n【どの戦略でスキャンしますか？】")
        print("  1. モメンタム戦略（上昇トレンド）")
        print("  2. 出来高急増戦略（Volume Spike）")
        print("  3. ブレイクアウト戦略")
        print("  4. 全部スキャン")
        print("  0. 戻る")

        choice = input("\n選択: ").strip()

        if choice == '1':
            print("\n📈 モメンタム戦略でスキャン中...")
            signals = self.strategies['momentum'].scan_market(min_volume_usdt=50000)
            self._display_signals(signals, "モメンタム")

        elif choice == '2':
            print("\n📊 出来高急増戦略でスキャン中...")
            signals = self.strategies['volume_spike'].get_hot_coins()
            self._display_hot_coins(signals)

        elif choice == '3':
            print("\n📈 ブレイクアウト戦略でスキャン中...")
            signals = self.strategies['breakout'].scan_for_breakouts(min_volume_usdt=50000)
            self._display_signals(signals, "ブレイクアウト")

        elif choice == '4':
            print("\n🌐 全戦略でスキャン中...\n")

            print("【1. モメンタム戦略】")
            momentum_signals = self.strategies['momentum'].scan_market(min_volume_usdt=50000)
            self._display_signals(momentum_signals, "モメンタム", limit=3)

            print("\n【2. 出来高急増戦略】")
            volume_signals = self.strategies['volume_spike'].get_hot_coins()
            self._display_hot_coins(volume_signals, limit=3)

            print("\n【3. ブレイクアウト戦略】")
            breakout_signals = self.strategies['breakout'].scan_for_breakouts(min_volume_usdt=50000)
            self._display_signals(breakout_signals, "ブレイクアウト", limit=3)

    def _display_signals(self, signals, strategy_name, limit=None):
        """シグナルを表示"""
        if not signals:
            print(f"\n❌ {strategy_name}の買いシグナルなし")
            return

        print(f"\n✅ {len(signals)}個の買いシグナルを発見！\n")

        display_count = min(len(signals), limit) if limit else len(signals)

        for i, sig in enumerate(signals[:display_count], 1):
            print(f"{i}. {sig['symbol']}")
            print(f"   価格: ${sig.get('price', 'N/A')}")
            if 'momentum' in sig:
                print(f"   モメンタム: {sig['momentum']:.2f}%")
            if 'volume_spike_ratio' in sig:
                print(f"   出来高: {sig['volume_spike_ratio']:.1f}x")
            if 'rsi' in sig:
                print(f"   RSI: {sig['rsi']:.1f}")
            print(f"   理由: {sig['reason']}")
            print()

    def _display_hot_coins(self, hot_coins, limit=None):
        """激アツコインを表示"""
        if not hot_coins:
            print("\n❌ 激アツコインなし")
            return

        print(f"\n🔥 {len(hot_coins)}個の激アツコインを発見！\n")

        display_count = min(len(hot_coins), limit) if limit else len(hot_coins)

        for i, coin in enumerate(hot_coins[:display_count], 1):
            print(f"{i}. {coin['symbol']}")
            print(f"   価格変動: {coin['price_change_24h']:+.2f}%")
            print(f"   出来高: {coin['volume_spike_ratio']:.1f}x")
            print(f"   スコア: {coin['score']:.1f}")
            print()

    def analyze_coin(self):
        """特定コインを分析"""
        print("\n" + "="*60)
        print("🔍 コイン分析")
        print("="*60)

        symbol = input("\nシンボルを入力（例: SHIBUSDT）: ").strip().upper()

        if not symbol:
            print("❌ シンボルが入力されていません")
            return

        # 全戦略で分析
        print(f"\n🔍 {symbol} を全戦略で分析中...\n")

        print("【モメンタム戦略】")
        momentum_result = self.strategies['momentum'].check_buy_signal(symbol)
        self._display_analysis_result(momentum_result)

        print("\n【出来高急増戦略】")
        volume_result = self.strategies['volume_spike'].check_buy_signal(symbol)
        self._display_analysis_result(volume_result)

        print("\n【ブレイクアウト戦略】")
        breakout_result = self.strategies['breakout'].check_buy_signal(symbol)
        self._display_analysis_result(breakout_result)

        # 総合判定
        signals_count = sum([
            momentum_result['signal'],
            volume_result['signal'],
            breakout_result['signal']
        ])

        print("\n" + "-"*60)
        print("【総合判定】")
        if signals_count >= 2:
            print("✅✅ 強い買いシグナル！複数の戦略が一致しています。")
        elif signals_count == 1:
            print("✅ 買いシグナルあり。慎重に判断してください。")
        else:
            print("❌ 買いシグナルなし。別のコインを探しましょう。")

    def _display_analysis_result(self, result):
        """分析結果を表示"""
        signal_mark = "✅" if result['signal'] else "❌"
        print(f"  {signal_mark} {result['reason']}")

        if 'price' in result:
            print(f"  価格: ${result['price']}")
        if 'momentum' in result:
            print(f"  モメンタム: {result['momentum']:.2f}%")
        if 'volume_spike_ratio' in result:
            print(f"  出来高: {result['volume_spike_ratio']:.1f}x")
        if 'rsi' in result:
            print(f"  RSI: {result['rsi']:.1f}")

    def show_positions(self):
        """現在のポジション表示"""
        print("\n" + "="*60)
        print("📊 現在のポジション")
        print("="*60)

        positions = self.db.get_all_positions()

        if not positions:
            print("\n現在ポジションはありません。")
            return

        print(f"\n保有中: {len(positions)}件\n")

        for pos in positions:
            symbol = pos['coin_symbol']
            amount = pos['amount']
            buy_price = pos['avg_buy_price']
            current_price = pos['current_price'] or buy_price
            pl_percent = pos['profit_loss_percent'] or 0

            pl_mark = "📈" if pl_percent > 0 else "📉"

            print(f"{pl_mark} {symbol}")
            print(f"  保有量: {amount}")
            print(f"  購入価格: ${buy_price:.8f}")
            print(f"  現在価格: ${current_price:.8f}")
            print(f"  損益: {pl_percent:+.2f}%")

            # 損切り・利確ライン
            if pos['stop_loss_price']:
                print(f"  損切り: ${pos['stop_loss_price']:.8f}")
            if pos['take_profit_price']:
                print(f"  利確: ${pos['take_profit_price']:.8f}")

            print()

    def show_performance(self):
        """パフォーマンス分析表示"""
        self.analyzer.generate_full_report(starting_balance=100.0)

    def show_curriculum(self):
        """学習カリキュラムを表示"""
        print("\n" + "="*60)
        print("📚 学習カリキュラム")
        print("="*60)
        print("\n【週次カリキュラム】")
        print("  1. Week 1: 基礎知識と最初の取引")
        print("  2. Week 2: テクニカル分析の基礎")
        print("  3. Week 3: 戦略構築とリスク管理")
        print("  4. Week 4: 実践と改善サイクル")
        print("  0. 戻る")

        choice = input("\n表示するWeek（1-4）: ").strip()

        curriculum_dir = os.path.join(os.path.dirname(__file__), 'curriculum')

        files = {
            '1': 'week1_basics.md',
            '2': 'week2_technicals.md',
            '3': 'week3_strategy.md',
            '4': 'week4_advanced.md',
        }

        if choice in files:
            file_path = os.path.join(curriculum_dir, files[choice])
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print("\n" + content)
            else:
                print(f"❌ ファイルが見つかりません: {file_path}")

    def record_trade_manually(self):
        """手動で取引を記録"""
        print("\n" + "="*60)
        print("✏️  取引を手動記録")
        print("="*60)

        try:
            symbol = input("\nシンボル（例: SHIBUSDT）: ").strip().upper()
            trade_type = input("取引種類（BUY/SELL）: ").strip().upper()

            if trade_type not in ['BUY', 'SELL']:
                print("❌ BUYまたはSELLを入力してください")
                return

            amount = float(input("数量: "))
            price = float(input("価格: "))
            total_cost = amount * price

            strategy = input("使用戦略（任意）: ").strip()
            notes = input("メモ（任意）: ").strip()

            # データベースに記録
            trade_id = self.db.add_trade(
                coin_symbol=symbol,
                exchange='Manual',
                trade_type=trade_type,
                amount=amount,
                price=price,
                total_cost=total_cost,
                strategy=strategy if strategy else None,
                notes=notes if notes else None
            )

            print(f"\n✅ 取引を記録しました（ID: {trade_id}）")

            # 買いの場合はポジションを開く
            if trade_type == 'BUY':
                stop_loss = float(input("損切りライン（任意、0でスキップ）: ") or 0)
                take_profit = float(input("利確ライン（任意、0でスキップ）: ") or 0)

                self.db.open_position(
                    coin_symbol=symbol,
                    amount=amount,
                    buy_price=price,
                    buy_trade_id=trade_id,
                    stop_loss_price=stop_loss if stop_loss > 0 else None,
                    take_profit_price=take_profit if take_profit > 0 else None
                )
                print("✅ ポジションを開きました")

            # 売りの場合はポジションを閉じる
            elif trade_type == 'SELL':
                try:
                    profit_loss, pl_percent = self.db.close_position(symbol, price, trade_id)
                    print(f"✅ ポジションを閉じました")
                    print(f"   損益: ${profit_loss:+.2f} ({pl_percent:+.2f}%)")
                except ValueError as e:
                    print(f"⚠️  {e}")

        except ValueError:
            print("❌ 入力エラー。数値を正しく入力してください。")
        except Exception as e:
            print(f"❌ エラー: {e}")

    def run(self):
        """メインループ"""
        print("\n" + "🌿"*30)
        print("草コイントレーダー起動！")
        print("100円→1000円への道を始めましょう！")
        print("🌿"*30)

        while True:
            self.show_menu()
            choice = input("\n選択: ").strip()

            if choice == '1':
                self.scan_market()
            elif choice == '2':
                self.analyze_coin()
            elif choice == '3':
                self.show_positions()
            elif choice == '4':
                self.show_performance()
            elif choice == '5':
                self.show_curriculum()
            elif choice == '6':
                self.record_trade_manually()
            elif choice == '0':
                print("\n👋 お疲れ様でした！また次回！")
                break
            else:
                print("\n❌ 無効な選択です")

            input("\nEnterキーで続行...")


def main():
    """エントリーポイント"""
    trader = GrassCoinTrader()
    trader.run()


if __name__ == '__main__':
    main()
