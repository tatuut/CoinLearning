"""
複数銘柄の相関分析ツール

保存された時系列データから、銘柄間の価格相関を分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.timeseries_storage import TimeSeriesStorage
import pandas as pd
import numpy as np


class CorrelationAnalyzer:
    """銘柄間相関分析"""

    def __init__(self):
        self.storage = TimeSeriesStorage()

    def get_multi_symbol_data(self, symbols: list, interval: str = '1d'):
        """
        複数銘柄のデータを取得

        Args:
            symbols: 銘柄リスト（例: ['BTC', 'ETH', 'XRP']）
            interval: 時間足

        Returns:
            各銘柄の終値を含むDataFrame
        """
        data_dict = {}

        for symbol in symbols:
            try:
                df = self.storage.load_price_data(symbol, interval)
                if df is not None and not df.empty:
                    # 終値だけを取得
                    data_dict[symbol] = df['close']
                else:
                    print(f"⚠️ {symbol}: データが見つかりません")
            except Exception as e:
                print(f"✗ {symbol}: エラー {e}")

        if not data_dict:
            return None

        # 全銘柄のデータを統合（時間軸で結合）
        combined_df = pd.DataFrame(data_dict)

        # 欠損値を前の値で埋める
        combined_df = combined_df.fillna(method='ffill')

        return combined_df

    def calculate_correlation_matrix(self, symbols: list, interval: str = '1d'):
        """
        相関係数行列を計算

        Returns:
            相関係数行列DataFrame
        """
        df = self.get_multi_symbol_data(symbols, interval)

        if df is None:
            return None

        # リターンの相関を計算（価格そのものではなく変化率の相関）
        returns = df.pct_change().dropna()

        correlation = returns.corr()

        return correlation

    def analyze_market_cohesion(self, symbols: list, interval: str = '1d'):
        """
        市場の連動性を分析

        相関が高い → マーケット全体が同じ方向に動いている
        相関が低い → 個別要因が強い
        """
        print("=" * 80)
        print("📊 市場連動性分析")
        print("=" * 80)
        print()
        print(f"分析対象: {', '.join(symbols)}")
        print(f"時間足: {interval}")
        print()

        corr = self.calculate_correlation_matrix(symbols, interval)

        if corr is None:
            print("データ不足のため分析できません")
            return

        print("【相関係数行列】")
        print(corr.round(3))
        print()

        # 平均相関を計算（対角成分を除く）
        n = len(corr)
        total_corr = 0
        count = 0

        for i in range(n):
            for j in range(i+1, n):
                total_corr += corr.iloc[i, j]
                count += 1

        avg_corr = total_corr / count if count > 0 else 0

        print(f"【平均相関係数】: {avg_corr:.3f}")
        print()

        # 解釈
        if avg_corr > 0.7:
            print("✓ 非常に高い連動性 → マーケット全体が同じ方向に動いています")
            print("  → 分散投資の効果は限定的")
        elif avg_corr > 0.5:
            print("✓ 高い連動性 → マーケットトレンドが支配的です")
            print("  → ある程度の分散効果あり")
        elif avg_corr > 0.3:
            print("✓ 中程度の連動性 → マーケット要因と個別要因が混在")
            print("  → 分散投資が有効")
        else:
            print("✓ 低い連動性 → 個別要因が強いです")
            print("  → 分散投資が非常に有効")

        print()

        # 最も相関が高いペア
        print("【最も連動している銘柄ペア】")
        max_corr = 0
        max_pair = None

        for i in range(n):
            for j in range(i+1, n):
                if corr.iloc[i, j] > max_corr:
                    max_corr = corr.iloc[i, j]
                    max_pair = (corr.index[i], corr.columns[j])

        if max_pair:
            print(f"  {max_pair[0]} - {max_pair[1]}: {max_corr:.3f}")

        # 最も相関が低いペア
        print()
        print("【最も独立している銘柄ペア】")
        min_corr = 1.0
        min_pair = None

        for i in range(n):
            for j in range(i+1, n):
                if corr.iloc[i, j] < min_corr:
                    min_corr = corr.iloc[i, j]
                    min_pair = (corr.index[i], corr.columns[j])

        if min_pair:
            print(f"  {min_pair[0]} - {min_pair[1]}: {min_corr:.3f}")

        print()

    def analyze_beta(self, target_symbol: str, benchmark_symbol: str = 'BTC',
                    interval: str = '1d'):
        """
        ベータ値を計算（市場感応度）

        ベータ > 1: 市場より大きく動く（ハイリスク・ハイリターン）
        ベータ = 1: 市場と同じ動き
        ベータ < 1: 市場より小さく動く（ローリスク・ローリターン）
        """
        print("=" * 80)
        print(f"📈 ベータ分析: {target_symbol} vs {benchmark_symbol}")
        print("=" * 80)
        print()

        df = self.get_multi_symbol_data([target_symbol, benchmark_symbol], interval)

        if df is None or target_symbol not in df or benchmark_symbol not in df:
            print("データ不足のため分析できません")
            return

        # リターンを計算
        returns = df.pct_change().dropna()

        # ベータ = Cov(対象, ベンチマーク) / Var(ベンチマーク)
        covariance = returns[target_symbol].cov(returns[benchmark_symbol])
        benchmark_variance = returns[benchmark_symbol].var()

        beta = covariance / benchmark_variance

        print(f"ベータ値: {beta:.3f}")
        print()

        # 解釈
        if beta > 1.5:
            print("✓ 非常に高ベータ → 市場の1.5倍以上動く")
            print(f"  → {benchmark_symbol}が10%上昇すると、{target_symbol}は約{beta*10:.1f}%上昇する傾向")
            print("  → ハイリスク・ハイリターン")
        elif beta > 1.0:
            print("✓ 高ベータ → 市場より大きく動く")
            print(f"  → {benchmark_symbol}が10%上昇すると、{target_symbol}は約{beta*10:.1f}%上昇する傾向")
            print("  → リスク高め")
        elif beta > 0.5:
            print("✓ 中程度のベータ → 市場と同程度に動く")
            print(f"  → {benchmark_symbol}が10%上昇すると、{target_symbol}は約{beta*10:.1f}%上昇する傾向")
            print("  → 標準的なリスク")
        else:
            print("✓ 低ベータ → 市場より小さく動く")
            print(f"  → {benchmark_symbol}が10%上昇すると、{target_symbol}は約{beta*10:.1f}%上昇する傾向")
            print("  → ローリスク（または市場との連動性が低い）")

        print()

        # 相関係数も表示
        correlation = returns[target_symbol].corr(returns[benchmark_symbol])
        print(f"相関係数: {correlation:.3f}")
        print()

        if correlation > 0.7:
            print(f"✓ {benchmark_symbol}と強く連動しています")
        elif correlation > 0.5:
            print(f"✓ {benchmark_symbol}とある程度連動しています")
        else:
            print(f"✓ {benchmark_symbol}との連動性は低いです（独自の動き）")

        print()

    def find_diversification_pairs(self, symbols: list, interval: str = '1d',
                                   threshold: float = 0.5):
        """
        分散投資に適したペアを探す

        相関が低いペアほど分散効果が高い
        """
        print("=" * 80)
        print("🎯 分散投資ペア推奨")
        print("=" * 80)
        print()
        print(f"分析対象: {', '.join(symbols)}")
        print(f"相関閾値: {threshold:.2f}（これ以下を推奨）")
        print()

        corr = self.calculate_correlation_matrix(symbols, interval)

        if corr is None:
            print("データ不足のため分析できません")
            return

        # 相関が低いペアを抽出
        low_corr_pairs = []

        n = len(corr)
        for i in range(n):
            for j in range(i+1, n):
                corr_value = corr.iloc[i, j]
                if corr_value < threshold:
                    low_corr_pairs.append((
                        corr.index[i],
                        corr.columns[j],
                        corr_value
                    ))

        # 相関が低い順にソート
        low_corr_pairs.sort(key=lambda x: x[2])

        if low_corr_pairs:
            print("【推奨ペア】（相関が低い順）")
            for i, (sym1, sym2, corr_val) in enumerate(low_corr_pairs, 1):
                print(f"{i}. {sym1} - {sym2}: {corr_val:.3f}")
                if corr_val < 0:
                    print(f"   → 負の相関！片方が上がると片方が下がる傾向")
                else:
                    print(f"   → 独立した動きをする傾向")
            print()
            print("✓ これらのペアを組み合わせることで、リスク分散効果が期待できます")
        else:
            print(f"相関が{threshold:.2f}以下のペアは見つかりませんでした")
            print("→ すべての銘柄が連動している可能性があります")

        print()


def main():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    import argparse

    parser = argparse.ArgumentParser(
        description='複数銘柄の相関分析ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 主要銘柄の市場連動性分析
  python correlation_analyzer.py --market BTC ETH XRP DOGE SHIB

  # ETHのベータ値（対BTC）を計算
  python correlation_analyzer.py --beta ETH --benchmark BTC

  # 分散投資に適したペアを探す
  python correlation_analyzer.py --diversify BTC ETH XRP DOGE SHIB
        """
    )

    parser.add_argument('--market', nargs='+', metavar='SYMBOL',
                       help='市場連動性分析を実行（銘柄リスト）')
    parser.add_argument('--beta', metavar='SYMBOL',
                       help='ベータ分析を実行（対象銘柄）')
    parser.add_argument('--benchmark', default='BTC',
                       help='ベンチマーク銘柄（デフォルト: BTC）')
    parser.add_argument('--diversify', nargs='+', metavar='SYMBOL',
                       help='分散投資ペア推奨（銘柄リスト）')
    parser.add_argument('--interval', default='1d',
                       help='時間足（デフォルト: 1d）')

    args = parser.parse_args()

    analyzer = CorrelationAnalyzer()

    if args.market:
        analyzer.analyze_market_cohesion(args.market, args.interval)

    if args.beta:
        analyzer.analyze_beta(args.beta, args.benchmark, args.interval)

    if args.diversify:
        analyzer.find_diversification_pairs(args.diversify, args.interval)

    if not any([args.market, args.beta, args.diversify]):
        parser.print_help()


if __name__ == '__main__':
    main()
