"""
草コイントレーダー - メインプログラム

100円→1000円を目指す草コイン取引システム
"""

import os
import sys
from datetime import datetime

# 各モジュールをインポート
from config.exchange_api import MEXCAPI
from data.database import TradeDatabase
from strategies.momentum import MomentumStrategy
from strategies.volume_spike import VolumeSpikeStrategy
from strategies.breakout import BreakoutStrategy
from analysis.performance import PerformanceAnalyzer
from analysis.report_generator import ReportGenerator


class GrassCoinTrader:
    """草コイントレーダー"""

    def __init__(self):
        self.api = MEXCAPI()
        self.db = TradeDatabase()
        self.analyzer = PerformanceAnalyzer()
        self.report_gen = ReportGenerator()

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
        print("  7. 取引分析・メモ（システム内で記録）")
        print("  8. 分析レポート生成（Markdownで対話）★NEW")
        print("  0. 終了")
        print("="*60)

    def scan_market(self):
        """市場をスキャン"""
        print("\n" + "="*60)
        print("[*] 市場スキャン")
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
            print("\n[CHART] 出来高急増戦略でスキャン中...")
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
            print(f"\n[NG] {strategy_name}の買いシグナルなし")
            return

        print(f"\n[OK] {len(signals)}個の買いシグナルを発見！\n")

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
            print("\n[NG] 激アツコインなし")
            return

        print(f"\n[HOT] {len(hot_coins)}個の激アツコインを発見！\n")

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
        print("[*] コイン分析")
        print("="*60)

        symbol = input("\nシンボルを入力（例: SHIBUSDT）: ").strip().upper()

        if not symbol:
            print("[NG] シンボルが入力されていません")
            return

        # 全戦略で分析
        print(f"\n[*] {symbol} を全戦略で分析中...\n")

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
            print("[STRONG] 強い買いシグナル！複数の戦略が一致しています。")
        elif signals_count == 1:
            print("[OK] 買いシグナルあり。慎重に判断してください。")
        else:
            print("[NG] 買いシグナルなし。別のコインを探しましょう。")

    def _display_analysis_result(self, result):
        """分析結果を表示"""
        signal_mark = "[OK]" if result['signal'] else "[NG]"
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
        print("[CHART] 現在のポジション")
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
                print(f"[NG] ファイルが見つかりません: {file_path}")

    def record_trade_manually(self):
        """手動で取引を記録"""
        print("\n" + "="*60)
        print("✏️  取引を手動記録")
        print("="*60)

        try:
            symbol = input("\nシンボル（例: SHIBUSDT）: ").strip().upper()
            trade_type = input("取引種類（BUY/SELL）: ").strip().upper()

            if trade_type not in ['BUY', 'SELL']:
                print("[NG] BUYまたはSELLを入力してください")
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

            print(f"\n[OK] 取引を記録しました（ID: {trade_id}）")

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
                print("[OK] ポジションを開きました")

            # 売りの場合はポジションを閉じる
            elif trade_type == 'SELL':
                try:
                    profit_loss, pl_percent = self.db.close_position(symbol, price, trade_id)
                    print(f"[OK] ポジションを閉じました")
                    print(f"   損益: ${profit_loss:+.2f} ({pl_percent:+.2f}%)")
                except ValueError as e:
                    print(f"⚠️  {e}")

        except ValueError:
            print("[NG] 入力エラー。数値を正しく入力してください。")
        except Exception as e:
            print(f"[NG] エラー: {e}")

    def analyze_trades(self):
        """取引分析・メモ機能（AIとユーザーの協力分析）"""
        print("\n" + "="*60)
        print("[*] 取引分析・メモ")
        print("="*60)
        print("\n【メニュー】")
        print("  1. 最近の取引を分析")
        print("  2. 特定のコインの分析履歴を見る")
        print("  3. 学んだことを記録")
        print("  4. 全ての分析を表示")
        print("  0. 戻る")

        choice = input("\n選択: ").strip()

        if choice == '1':
            self._analyze_recent_trades()
        elif choice == '2':
            self._view_coin_analysis_history()
        elif choice == '3':
            self._record_lesson()
        elif choice == '4':
            self._view_all_analysis()

    def _analyze_recent_trades(self):
        """最近の取引を分析"""
        print("\n" + "-"*60)
        print("[*] 最近の取引")
        print("-"*60)

        # 完了した取引を取得
        completed = self.db.get_completed_trades(limit=10)

        if not completed:
            print("\n取引履歴がありません。")
            return

        print(f"\n最近の{len(completed)}件の取引:\n")
        for i, trade in enumerate(completed, 1):
            pl_mark = "[OK]" if trade['profit_loss'] > 0 else "[NG]"
            print(f"{i}. {trade['coin_symbol']} - {pl_mark} {trade['profit_loss_percent']:+.2f}%")
            print(f"   購入: ${trade['buy_price']:.8f} → 売却: ${trade['sell_price']:.8f}")
            print(f"   完了: {trade['completed_at'][:10]}")
            print()

        # 取引を選択
        try:
            selection = int(input("分析する取引番号を選択（0で戻る）: ").strip())
            if selection == 0:
                return
            if selection < 1 or selection > len(completed):
                print("[NG] 無効な番号です")
                return

            selected_trade = completed[selection - 1]
            self._interactive_analysis(selected_trade)

        except ValueError:
            print("[NG] 数値を入力してください")

    def _interactive_analysis(self, trade):
        """対話的な取引分析"""
        print("\n" + "="*60)
        print(f"[*] {trade['coin_symbol']} の分析")
        print("="*60)

        # 取引詳細を表示
        print(f"\n【取引詳細】")
        print(f"コイン: {trade['coin_symbol']}")
        print(f"購入価格: ${trade['buy_price']:.8f}")
        print(f"売却価格: ${trade['sell_price']:.8f}")
        print(f"数量: {trade['amount']}")
        print(f"損益: {trade['profit_loss_percent']:+.2f}% (${trade['profit_loss']:+.2f})")
        print(f"保有期間: {trade['duration_minutes']:.0f}分")

        # 既存の分析を表示
        analyses = self.db.get_trade_analysis(trade['buy_trade_id'])
        if analyses:
            print(f"\n【既存の分析】（{len(analyses)}件）")
            for i, analysis in enumerate(analyses, 1):
                author_mark = "[You]" if analysis['author'] == 'user' else "[AI]"
                print(f"\n{i}. {author_mark} [{analysis['analysis_type']}]")
                print(f"   {analysis['content']}")

        # ユーザーの分析を追加
        print("\n" + "-"*60)
        print("【あなたの分析】")
        print("この取引について、あなたの考えを記録してください。")
        print("例: なぜ買ったのか、判断は正しかったか、次に改善することは？")
        print("（何も入力せずEnterでスキップ）")
        print("-"*60)

        user_analysis = input("\nあなたの分析: ").strip()

        if user_analysis:
            self.db.add_analysis(
                author='user',
                analysis_type='post_trade',
                content=user_analysis,
                trade_id=trade['buy_trade_id'],
                coin_symbol=trade['coin_symbol']
            )
            print("\n[OK] あなたの分析を記録しました")

            # AIの分析を提供
            print("\n" + "-"*60)
            print("[AI] あなたの分析を踏まえて、いくつか観点を追加します：")
            print("-"*60)

            ai_insights = self._generate_ai_insights(trade, user_analysis)
            print(f"\n{ai_insights}")

            # AIの分析を保存するか確認
            save_ai = input("\n[AI]の分析も保存しますか？ (y/n): ").strip().lower()
            if save_ai == 'y':
                self.db.add_analysis(
                    author='ai',
                    analysis_type='post_trade',
                    content=ai_insights,
                    trade_id=trade['buy_trade_id'],
                    coin_symbol=trade['coin_symbol']
                )
                print("[OK] AIの分析も記録しました")

    def _generate_ai_insights(self, trade, user_analysis):
        """AIの分析を生成"""
        pl = trade['profit_loss_percent']
        duration = trade['duration_minutes']

        insights = []

        # 結果に基づく分析
        if pl > 20:
            insights.append(f"[GREAT] {pl:+.2f}%の利益、素晴らしい取引です！")
            insights.append("この取引で成功した要因を他の取引でも再現できるか考えてみましょう。")
        elif pl > 0:
            insights.append(f"[OK] {pl:+.2f}%の利益。堅実な取引です。")
            insights.append("利益が出たのは良いですが、さらに伸ばせる余地はなかったか振り返りましょう。")
        elif pl > -10:
            insights.append(f"[CAUTION] {pl:+.2f}%の損失。")
            insights.append("損切りルールが機能しました。損失を限定できたのは良い判断です。")
        else:
            insights.append(f"[WARNING] {pl:+.2f}%の損失。")
            insights.append("損切りが遅れた可能性があります。次回はより早い判断を心がけましょう。")

        # 保有期間に基づく分析
        if duration < 60:
            insights.append(f"\n保有期間: {duration:.0f}分（短期）")
            insights.append("短期取引は素早い判断が重要です。シグナルは明確でしたか？")
        elif duration < 1440:  # 24時間
            insights.append(f"\n保有期間: {duration/60:.1f}時間（中期）")
            insights.append("この期間で価格がどう動いたか、チャートで確認しましょう。")
        else:
            insights.append(f"\n保有期間: {duration/1440:.1f}日（長期）")
            insights.append("長期保有は忍耐が必要です。途中で不安になりませんでしたか？")

        # ユーザー分析に基づくフィードバック
        if user_analysis:
            if "失敗" in user_analysis or "ミス" in user_analysis:
                insights.append("\n失敗を認識できるのは成長の第一歩です。")
                insights.append("具体的な改善策を考えましょう。")
            if "感情" in user_analysis or "焦" in user_analysis:
                insights.append("\n感情的な判断に気づけたのは素晴らしいです。")
                insights.append("次回はルールを厳守して、感情に流されないようにしましょう。")

        return "\n".join(insights)

    def _view_coin_analysis_history(self):
        """特定のコインの分析履歴を表示"""
        symbol = input("\nコインシンボルを入力（例: SHIBUSDT）: ").strip().upper()

        if not symbol:
            return

        analyses = self.db.get_coin_analysis(symbol)

        if not analyses:
            print(f"\n{symbol}の分析履歴がありません。")
            return

        print(f"\n{'='*60}")
        print(f"[*] {symbol} の分析履歴（{len(analyses)}件）")
        print('='*60)

        for i, analysis in enumerate(analyses, 1):
            author_mark = "[You]" if analysis['author'] == 'user' else "[AI]"
            print(f"\n{i}. {author_mark} [{analysis['analysis_type']}] - {analysis['created_at'][:10]}")
            print(f"   {analysis['content'][:100]}...")

    def _record_lesson(self):
        """学んだことを記録"""
        print("\n" + "="*60)
        print("[*] 学んだことを記録")
        print("="*60)
        print("\n取引から学んだこと、気づいたことを自由に記録してください。")
        print("特定の取引に関係なくても構いません。")
        print("-"*60)

        lesson = input("\n学んだこと: ").strip()

        if not lesson:
            return

        # タグを追加するか確認
        add_tags = input("タグを追加しますか？（カンマ区切り、例: RSI,損切り）: ").strip()
        tags = [tag.strip() for tag in add_tags.split(',')] if add_tags else None

        self.db.add_analysis(
            author='user',
            analysis_type='lesson',
            content=lesson,
            tags=tags
        )

        print("\n[OK] 学びを記録しました！")
        print("記録を積み重ねることで、あなただけのトレーディングノートが完成します。")

    def _view_all_analysis(self):
        """全ての分析を表示"""
        print("\n" + "="*60)
        print("[*] 分析履歴")
        print("="*60)

        analyses = self.db.get_all_analysis(limit=20)

        if not analyses:
            print("\n分析記録がありません。")
            return

        print(f"\n最近の{len(analyses)}件の分析:\n")

        for i, analysis in enumerate(analyses, 1):
            author_mark = "[You]" if analysis['author'] == 'user' else "[AI]"
            type_label = {
                'pre_trade': '取引前',
                'during_trade': '保有中',
                'post_trade': '取引後',
                'memo': 'メモ',
                'lesson': '学び'
            }.get(analysis['analysis_type'], analysis['analysis_type'])

            print(f"{i}. {author_mark} [{type_label}] - {analysis['created_at'][:10]}")
            if analysis['coin_symbol']:
                print(f"   コイン: {analysis['coin_symbol']}")
            print(f"   {analysis['content'][:150]}...")
            if analysis.get('tags'):
                print(f"   タグ: {', '.join(analysis['tags'])}")
            print()

    def generate_analysis_report(self):
        """分析レポート生成（Markdownで対話）"""
        print("\n" + "="*60)
        print("[*] 分析レポート生成")
        print("="*60)
        print("\n【何のレポートを作成しますか？】")
        print("  1. 完了した取引の分析レポート")
        print("  2. 特定コインの市場分析レポート")
        print("  0. 戻る")

        choice = input("\n選択: ").strip()

        try:
            if choice == '1':
                self._generate_trade_report()
            elif choice == '2':
                self._generate_market_report()
        except Exception as e:
            print(f"\n[NG] エラー: {e}")

    def _generate_trade_report(self):
        """完了した取引のレポート生成"""
        print("\n" + "-"*60)
        print("[*] 取引分析レポート生成")
        print("-"*60)

        # 完了した取引を表示
        completed = self.db.get_completed_trades(limit=10)

        if not completed:
            print("\n完了した取引がありません。")
            return

        print(f"\n最近の{len(completed)}件の取引:\n")
        for i, trade in enumerate(completed, 1):
            pl_mark = "[OK]" if trade['profit_loss'] > 0 else "[NG]"
            print(f"{i}. {trade['coin_symbol']} - {pl_mark} {trade['profit_loss_percent']:+.2f}%")
            print(f"   {trade['completed_at'][:10]}")

        # 取引を選択
        try:
            selection = int(input("\n分析する取引番号（0で戻る）: ").strip())
            if selection == 0:
                return
            if selection < 1 or selection > len(completed):
                print("[NG] 無効な番号です")
                return

            selected_trade = completed[selection - 1]
            trade_id = selected_trade['buy_trade_id']

            # レポート生成
            filepath = self.report_gen.generate_trade_report(trade_id=trade_id)

            print("\n" + "="*60)
            print("✅ レポート生成完了！")
            print("="*60)
            print(f"\nファイル: {filepath}")
            print("\n【次のステップ】")
            print("1. レポートファイルを開く")
            print("2. 「分析セクション」にあなたの考えを追記")
            print("3. Claude Codeにファイルを見せて対話")
            print("\n例: ")
            print("  「analysis/reports/xxx.md を読んで、私の分析にフィードバックをください」")

        except ValueError:
            print("[NG] 数値を入力してください")

    def _generate_market_report(self):
        """市場分析レポート生成"""
        print("\n" + "-"*60)
        print("[*] 市場分析レポート生成")
        print("-"*60)

        symbol = input("\nコインシンボルを入力（例: PEPEUSDT）: ").strip().upper()

        if not symbol:
            return

        # レポート生成
        filepath = self.report_gen.generate_trade_report(coin_symbol=symbol)

        print("\n" + "="*60)
        print("✅ レポート生成完了！")
        print("="*60)
        print(f"\nファイル: {filepath}")
        print("\n【次のステップ】")
        print("1. レポートファイルを開く")
        print("2. 「取引判断セクション」にあなたの考えを追記")
        print("3. Claude Codeにファイルを見せて対話")
        print("4. 最終的に取引するか判断")
        print("\n例: ")
        print("  「analysis/reports/xxx.md を読んで、私の判断にフィードバックをください」")

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
            elif choice == '7':
                self.analyze_trades()
            elif choice == '8':
                self.generate_analysis_report()
            elif choice == '0':
                print("\n👋 お疲れ様でした！また次回！")
                break
            else:
                print("\n[NG] 無効な選択です")

            input("\nEnterキーで続行...")


def main():
    """エントリーポイント"""
    trader = GrassCoinTrader()
    trader.run()


if __name__ == '__main__':
    main()
