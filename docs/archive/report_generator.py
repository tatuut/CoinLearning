"""
分析レポート自動生成システム

ユーザーとAIが協力して取引を分析するためのMarkdownレポートを自動生成
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.exchange_api import MEXCAPI
from data.database import TradeDatabase
from strategies.momentum import MomentumStrategy
from strategies.volume_spike import VolumeSpikeStrategy
from strategies.breakout import BreakoutStrategy


class ReportGenerator:
    """分析レポート生成器"""

    def __init__(self):
        self.api = MEXCAPI()
        self.db = TradeDatabase()
        self.strategies = {
            'momentum': MomentumStrategy(),
            'volume_spike': VolumeSpikeStrategy(),
            'breakout': BreakoutStrategy(),
        }

        # レポート保存先
        self.reports_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'reports'
        )
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_trade_report(self, trade_id: int = None, coin_symbol: str = None) -> str:
        """
        取引分析レポートを生成

        Args:
            trade_id: 取引ID（オプション）
            coin_symbol: コインシンボル（オプション）

        Returns:
            生成されたレポートのファイルパス
        """
        if trade_id:
            # 特定の取引のレポート
            return self._generate_completed_trade_report(trade_id)
        elif coin_symbol:
            # 現在のポジションor市場分析レポート
            return self._generate_coin_analysis_report(coin_symbol)
        else:
            raise ValueError("trade_id または coin_symbol を指定してください")

    def _generate_completed_trade_report(self, trade_id: int) -> str:
        """完了した取引の分析レポートを生成"""
        # 取引情報を取得
        completed_trades = self.db.get_completed_trades(limit=100)
        trade = None
        for t in completed_trades:
            if t['buy_trade_id'] == trade_id or t['sell_trade_id'] == trade_id:
                trade = t
                break

        if not trade:
            raise ValueError(f"取引ID {trade_id} が見つかりません")

        symbol = trade['coin_symbol']

        # 市場データを収集
        print(f"\n[*] {symbol} のデータを収集中...")
        market_data = self._collect_market_data(symbol)

        # テクニカル分析
        print("[*] テクニカル分析を実行中...")
        technical = self._analyze_technical(symbol)

        # 類似コインの検索
        print("[*] 類似コインを検索中...")
        similar_coins = self._find_similar_coins(symbol)

        # レポート生成
        print("[*] レポートを生成中...")
        report_content = self._build_trade_report_markdown(
            trade, market_data, technical, similar_coins
        )

        # ファイルに保存
        filename = f"{datetime.now().strftime('%Y-%m-%d_%H%M')}_{symbol}_取引分析.md"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n[OK] レポート生成完了: {filepath}")
        return filepath

    def _generate_coin_analysis_report(self, symbol: str) -> str:
        """コインの市場分析レポートを生成"""
        print(f"\n[*] {symbol} の市場分析レポートを生成中...")

        # 市場データを収集
        market_data = self._collect_market_data(symbol)

        # テクニカル分析
        technical = self._analyze_technical(symbol)

        # 戦略分析
        strategy_signals = self._get_strategy_signals(symbol)

        # 類似コインの検索
        similar_coins = self._find_similar_coins(symbol)

        # レポート生成
        report_content = self._build_market_report_markdown(
            symbol, market_data, technical, strategy_signals, similar_coins
        )

        # ファイルに保存
        filename = f"{datetime.now().strftime('%Y-%m-%d_%H%M')}_{symbol}_市場分析.md"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n[OK] レポート生成完了: {filepath}")
        return filepath

    def _collect_market_data(self, symbol: str) -> Dict:
        """市場データを収集"""
        # 24時間統計
        stats = self.api.get_24h_stats(symbol)

        # ローソク足データ
        klines = self.api.get_klines(symbol, interval='1h', limit=24)

        return {
            'stats': stats,
            'klines': klines,
            'prices': [k['close'] for k in klines] if klines else [],
            'volumes': [k['volume'] for k in klines] if klines else []
        }

    def _analyze_technical(self, symbol: str) -> Dict:
        """テクニカル分析を実行"""
        results = {}

        # モメンタム戦略
        momentum_result = self.strategies['momentum'].check_buy_signal(symbol)
        results['momentum'] = momentum_result

        # 出来高急増戦略
        volume_result = self.strategies['volume_spike'].check_buy_signal(symbol)
        results['volume_spike'] = volume_result

        # ブレイクアウト戦略
        breakout_result = self.strategies['breakout'].check_buy_signal(symbol)
        results['breakout'] = breakout_result

        return results

    def _get_strategy_signals(self, symbol: str) -> Dict:
        """全戦略のシグナルを取得"""
        signals = {}

        for name, strategy in self.strategies.items():
            result = strategy.check_buy_signal(symbol)
            signals[name] = result

        return signals

    def _find_similar_coins(self, symbol: str) -> List[Dict]:
        """類似の動きをしているコインを検索"""
        # トレンドコインを取得
        trending = self.api.get_trending_coins(min_volume_usdt=50000)

        # 上位5件を返す
        return trending[:5]

    def _build_trade_report_markdown(self, trade: Dict, market_data: Dict,
                                     technical: Dict, similar_coins: List[Dict]) -> str:
        """取引分析レポートのMarkdownを生成"""
        symbol = trade['coin_symbol']

        md = f"""# {symbol} 取引分析レポート

**生成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

---

## 📊 取引概要

| 項目 | 値 |
|------|------|
| **コイン** | {symbol} |
| **購入価格** | ${trade['buy_price']:.8f} |
| **売却価格** | ${trade['sell_price']:.8f} |
| **数量** | {trade['amount']:,.0f} |
| **損益** | {trade['profit_loss_percent']:+.2f}% (${trade['profit_loss']:+.2f}) |
| **保有期間** | {trade['duration_minutes']:.0f}分 ({trade['duration_minutes']/60:.1f}時間) |
| **完了日時** | {trade['completed_at']} |

### 判定

"""
        # 損益による判定
        if trade['profit_loss_percent'] > 20:
            md += "✅ **素晴らしい取引！** 大きな利益を獲得しました。\n\n"
        elif trade['profit_loss_percent'] > 0:
            md += "✅ **成功！** 利益が出ました。\n\n"
        elif trade['profit_loss_percent'] > -10:
            md += "⚠️ **損失** 損切りルールで損失を限定できました。\n\n"
        else:
            md += "❌ **大きな損失** 改善が必要です。\n\n"

        md += f"""---

## 💹 現在の市場データ

### 24時間統計

| 指標 | 値 |
|------|------|
| **現在価格** | ${market_data['stats']['price'] if market_data['stats'] else 'N/A'} |
| **24h変動** | {market_data['stats']['price_change_percent'] if market_data['stats'] else 'N/A'}% |
| **24h高値** | ${market_data['stats']['high'] if market_data['stats'] else 'N/A'} |
| **24h安値** | ${market_data['stats']['low'] if market_data['stats'] else 'N/A'} |
| **24h出来高** | ${f"{market_data['stats']['quote_volume']:,.0f} USDT" if market_data['stats'] else 'N/A'} |

### 直近24時間の価格推移（簡易チャート）

```
"""
        # 簡易価格チャート
        if market_data['prices']:
            prices = market_data['prices']
            min_price = min(prices)
            max_price = max(prices)

            for i, price in enumerate(prices[-12:]):  # 直近12時間
                normalized = int((price - min_price) / (max_price - min_price) * 20) if max_price > min_price else 10
                bar = '█' * normalized
                md += f"{i+1:2d}h前: {bar} ${price:.8f}\n"

        md += "```\n\n"

        md += f"""---

## 📈 テクニカル分析

### モメンタム戦略

| 指標 | 値 |
|------|------|
| **シグナル** | {'✅ 買い' if technical['momentum']['signal'] else '❌ なし'} |
| **モメンタム** | {technical['momentum'].get('momentum', 0):.2f}% |
| **ROC** | {technical['momentum'].get('roc', 0):.2f}% |
| **理由** | {technical['momentum']['reason']} |

### 出来高急増戦略

| 指標 | 値 |
|------|------|
| **シグナル** | {'✅ 買い' if technical['volume_spike']['signal'] else '❌ なし'} |
| **出来高倍率** | {technical['volume_spike'].get('volume_spike_ratio', 0):.1f}x |
| **価格変動** | {technical['volume_spike'].get('price_change', 0):+.2f}% |
| **理由** | {technical['volume_spike']['reason']} |

### ブレイクアウト戦略

| 指標 | 値 |
|------|------|
| **シグナル** | {'✅ 買い' if technical['breakout']['signal'] else '❌ なし'} |
| **RSI** | {technical['breakout'].get('rsi', 0):.1f} |
| **バンド幅** | {technical['breakout'].get('bandwidth', 0):.2f}% |
| **理由** | {technical['breakout']['reason']} |

---

## 🔍 類似コインの動き

現在トレンドのコイン:

"""
        for i, coin in enumerate(similar_coins, 1):
            md += f"{i}. **{coin['symbol']}**: {coin['change_percent']:+.2f}% (24h)\n"

        md += f"""

---

## 💭 分析セクション - あなたとClaudeの対話

> **使い方**:
> 1. このセクションにあなたの分析・考察を自由に追記してください
> 2. 追記したら、Claude Codeにこのファイルを見せて対話してください
> 3. ClaudeがフィードバックをMarkdownに追記します

### 分析の観点

以下の観点で考えてみましょう：

1. **なぜこの取引をしたのか？**
   - どのシグナルに従った？
   - 判断の根拠は何だった？

2. **判断は正しかったか？**
   - 結果的に良い判断だったか
   - 予想外の出来事はあったか

3. **何を学んだか？**
   - この取引から得た教訓
   - 次回改善したいこと

4. **感情的な要因**
   - 焦りや恐怖はなかったか
   - ルールを守れたか

---

### [あなた] {datetime.now().strftime('%Y-%m-%d %H:%M')}

> ここにあなたの分析を追記してください

(例)
- 出来高が急増していたので購入した
- でも売却タイミングが早すぎた気がする
- 次回はもう少し我慢して利確ラインまで待つべき

---

### [Claude]

> あなたが分析を追記したら、このファイルをClaudeに見せてください
> Claudeがこのセクションにフィードバックを追記します

---

## 📝 追加メモ

- ここに自由にメモを追加できます
- 後で見返した時に役立つ情報を記録しましょう

---

**次のアクション**:
1. ✏️ 上の「分析セクション」にあなたの考えを書く
2. 💬 Claude Codeとこのファイルについて対話する
3. 📚 学んだことを次の取引に活かす

"""
        return md

    def _build_market_report_markdown(self, symbol: str, market_data: Dict,
                                     technical: Dict, strategy_signals: Dict,
                                     similar_coins: List[Dict]) -> str:
        """市場分析レポートのMarkdownを生成"""

        md = f"""# {symbol} 市場分析レポート

**生成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

---

## 📊 市場概要

### 24時間統計

| 指標 | 値 |
|------|------|
| **現在価格** | ${market_data['stats']['price'] if market_data['stats'] else 'N/A'} |
| **24h変動** | {market_data['stats']['price_change_percent'] if market_data['stats'] else 'N/A'}% |
| **24h高値** | ${market_data['stats']['high'] if market_data['stats'] else 'N/A'} |
| **24h安値** | ${market_data['stats']['low'] if market_data['stats'] else 'N/A'} |
| **24h出来高** | ${f"{market_data['stats']['quote_volume']:,.0f} USDT" if market_data['stats'] else 'N/A'} |

### 直近24時間の価格推移

```
"""
        # 簡易チャート
        if market_data['prices']:
            prices = market_data['prices']
            min_price = min(prices)
            max_price = max(prices)

            for i, price in enumerate(prices[-12:]):
                normalized = int((price - min_price) / (max_price - min_price) * 20) if max_price > min_price else 10
                bar = '█' * normalized
                md += f"{i+1:2d}h前: {bar} ${price:.8f}\n"

        md += "```\n\n"

        md += """---

## 📈 戦略分析

### 総合判定

"""
        # シグナル数をカウント
        signal_count = sum(1 for s in strategy_signals.values() if s['signal'])

        if signal_count >= 2:
            md += "✅ **強い買いシグナル！** 複数の戦略が一致しています。\n\n"
        elif signal_count == 1:
            md += "⚠️ **買いシグナルあり** 慎重に判断してください。\n\n"
        else:
            md += "❌ **買いシグナルなし** 現時点では見送りが賢明です。\n\n"

        md += f"""### 各戦略の詳細

#### 1. モメンタム戦略

| 指標 | 値 |
|------|------|
| **シグナル** | {'✅ 買い' if technical['momentum']['signal'] else '❌ なし'} |
| **モメンタム** | {technical['momentum'].get('momentum', 0):.2f}% |
| **ROC** | {technical['momentum'].get('roc', 0):.2f}% |
| **理由** | {technical['momentum']['reason']} |

#### 2. 出来高急増戦略

| 指標 | 値 |
|------|------|
| **シグナル** | {'✅ 買い' if technical['volume_spike']['signal'] else '❌ なし'} |
| **出来高倍率** | {technical['volume_spike'].get('volume_spike_ratio', 0):.1f}x |
| **価格変動** | {technical['volume_spike'].get('price_change', 0):+.2f}% |
| **理由** | {technical['volume_spike']['reason']} |

#### 3. ブレイクアウト戦略

| 指標 | 値 |
|------|------|
| **シグナル** | {'✅ 買い' if technical['breakout']['signal'] else '❌ なし'} |
| **RSI** | {technical['breakout'].get('rsi', 0):.1f} |
| **バンド幅** | {technical['breakout'].get('bandwidth', 0):.2f}% |
| **理由** | {technical['breakout']['reason']} |

---

## 🔍 類似コインの動き

現在トレンドのコイン:

"""
        for i, coin in enumerate(similar_coins, 1):
            md += f"{i}. **{coin['symbol']}**: {coin['change_percent']:+.2f}% (24h) - 出来高: ${coin['volume_usdt']:,.0f}\n"

        md += f"""

---

## 💭 取引判断セクション - あなたとClaudeの対話

> **このコインを買うべきか？**

### 検討ポイント

1. **シグナルの強さ**: {signal_count}/3 の戦略が買いシグナル
2. **リスク**:
3. **他の選択肢**:

---

### [あなた] {datetime.now().strftime('%Y-%m-%d %H:%M')}

> このコインについて、あなたの考えを書いてください

- このコインを買うべきだと思うか？
- 気になるポイントは？
- 他に調べるべきことは？

---

### [Claude]

> あなたの考えを読んで、Claudeがアドバイスを追記します

---

## 📝 メモ

---

**次のアクション**:
1. ✏️ 「取引判断セクション」にあなたの考えを書く
2. 💬 必要ならClaudeとこのファイルについて対話
3. 📊 他のコインも分析して比較検討
4. 🎯 最終的な取引判断を下す

"""
        return md


def main():
    """コマンドライン実行"""
    import argparse

    parser = argparse.ArgumentParser(description='取引分析レポート生成')
    parser.add_argument('--trade-id', type=int, help='取引ID')
    parser.add_argument('--symbol', type=str, help='コインシンボル (例: BTCUSDT)')

    args = parser.parse_args()

    generator = ReportGenerator()

    if args.trade_id:
        filepath = generator.generate_trade_report(trade_id=args.trade_id)
    elif args.symbol:
        filepath = generator.generate_trade_report(coin_symbol=args.symbol.upper())
    else:
        print("エラー: --trade-id または --symbol を指定してください")
        print("\n使い方:")
        print("  python report_generator.py --trade-id 1")
        print("  python report_generator.py --symbol PEPEUSDT")
        return

    print(f"\n[OK] レポートが生成されました: {filepath}")
    print("\n次のステップ:")
    print("1. レポートファイルを開く")
    print("2. 「分析セクション」にあなたの考えを追記")
    print("3. Claude Codeとレポートについて対話")


if __name__ == '__main__':
    main()
