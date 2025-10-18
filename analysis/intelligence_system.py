"""
統合インテリジェンスシステム

ニュース収集 → スコアリング → 分析 を自動実行
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.advanced_database import AdvancedDatabase
from analysis.news_collector import NewsCollector
from analysis.scoring_engine import ScoringAnalyzer
from datetime import datetime
from typing import List, Dict


class IntelligenceSystem:
    """統合インテリジェンスシステム"""

    def __init__(self):
        self.db = AdvancedDatabase()
        self.news_collector = NewsCollector()
        self.scoring_analyzer = ScoringAnalyzer()

    def execute_full_analysis(self, symbol: str, name: str, news_data: List[Dict] = None) -> Dict:
        """
        完全分析を実行

        Args:
            symbol: 銘柄シンボル
            name: 銘柄名
            news_data: WebSearchで収集したニュースデータ（オプション）

        Returns:
            分析結果
        """
        print("\n" + "="*60)
        print(f"統合分析実行: {symbol} ({name})")
        print("="*60)

        result = {
            'symbol': symbol,
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'news_collected': 0,
            'scoring_result': None,
        }

        # ステップ1: ニュース収集
        if news_data:
            print(f"\n[STEP 1] ニュース収集...")
            count = self.news_collector.collect_news_for_coin(symbol, name, news_data)
            result['news_collected'] = count
            print(f"  [OK] {count}件のニュースを保存")
        else:
            print(f"\n[STEP 1] ニュース収集スキップ（データなし）")

        # ステップ2: スコアリング
        print(f"\n[STEP 2] スコアリング分析...")
        scoring_result = self.scoring_analyzer.analyze_news_impact(symbol)
        result['scoring_result'] = scoring_result

        # ステップ3: レポート生成
        print(f"\n[STEP 3] レポート生成...")
        report = self._generate_report(result)
        result['report'] = report

        print(f"\n{'='*60}")
        print(f"[OK] 統合分析完了")
        print(f"{'='*60}")

        return result

    def _generate_report(self, analysis_result: Dict) -> str:
        """
        分析レポートを生成

        Args:
            analysis_result: 分析結果

        Returns:
            Markdown形式のレポート
        """
        symbol = analysis_result['symbol']
        name = analysis_result['name']
        scoring = analysis_result.get('scoring_result', {})

        report = f"""
# {name} ({symbol}) - インテリジェンスレポート

**生成日時**: {analysis_result['timestamp']}

## 📊 ニュース収集結果

- 新規収集件数: {analysis_result['news_collected']}件
- 分析対象件数: {scoring.get('news_count', 0)}件

## 🎯 影響力スコア分析

- 平均影響力スコア: {scoring.get('avg_final_score', 0):.3f}
- 最大影響力スコア: {scoring.get('max_final_score', 0):.3f}

## 🔥 影響力トップニュース

"""
        top_news = scoring.get('top_news', [])
        for i, news in enumerate(top_news[:5], 1):
            report += f"""
### {i}. {news.get('title', 'No title')}

- **最終スコア**: {news.get('final_score', 0):.3f}
- **関連性**: {news.get('relevance_score', 0):.3f}
- **重要性**: {news.get('importance_score', 0):.3f}
- **影響力**: {news.get('impact_score', 0):.3f}
- **時間減衰**: {news.get('time_decay_factor', 0):.3f}
- **公開日**: {news.get('published_date', 'Unknown')}
- **ソース**: {news.get('source', 'Unknown')}

{news.get('content', '')[:200]}...

---
"""

        report += f"""
## 💡 総合評価

スコア分析に基づき、{name}の市場への影響力は**{'高い' if scoring.get('avg_final_score', 0) > 0.5 else '中程度' if scoring.get('avg_final_score', 0) > 0.3 else '低い'}**と評価されます。

---

_このレポートは自動生成されました_
"""

        return report

    def batch_analyze_coins(self, coin_list: List[tuple]) -> List[Dict]:
        """
        複数銘柄を一括分析

        Args:
            coin_list: [(symbol, name), ...] のリスト

        Returns:
            各銘柄の分析結果リスト
        """
        results = []

        for symbol, name in coin_list:
            result = self.execute_full_analysis(symbol, name)
            results.append(result)

        return results

    def save_report_to_file(self, report: str, symbol: str):
        """
        レポートをファイルに保存

        Args:
            report: レポート内容
            symbol: 銘柄シンボル
        """
        reports_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'analysis', 'intelligence_reports'
        )
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filename = f"{timestamp}_{symbol}_intelligence.md"
        filepath = os.path.join(reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"[OK] レポート保存: {filepath}")
        return filepath

    def close(self):
        """データベース接続を閉じる"""
        self.db.close()
        self.news_collector.close()
        self.scoring_analyzer.close()


if __name__ == '__main__':
    # テスト実行
    print("="*60)
    print("統合インテリジェンスシステム - テスト")
    print("="*60)

    system = IntelligenceSystem()

    # テスト: BTCの分析
    result = system.execute_full_analysis('BTC', 'Bitcoin')

    # レポート保存
    if result.get('report'):
        system.save_report_to_file(result['report'], 'BTC')

    system.close()
