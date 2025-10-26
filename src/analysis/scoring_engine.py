"""
スコアリングエンジン

ニュースの影響力を評価して総合スコアを算出
- 関連性（Relevance）
- 重要性（Importance）
- 影響力（Impact）
- 時間減衰（Time Decay）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.advanced_database import AdvancedDatabase
from datetime import datetime, timedelta
import math
from typing import List, Dict, Optional


class ScoringEngine:
    """ニューススコアリングエンジン"""

    def __init__(self):
        self.db = AdvancedDatabase()

        # 重要キーワードの重み付け
        self.high_impact_keywords = {
            'ETF': 1.0,
            'SEC': 0.9,
            '承認': 0.9,
            '規制': 0.8,
            '最高値': 0.8,
            '暴落': 0.9,
            '急騰': 0.8,
            'ハッキング': 1.0,
            '提携': 0.7,
            '上場': 0.7,
            'アップデート': 0.6,
            'ハードフォーク': 0.7,
        }

    def calculate_time_decay_factor(self, published_date: str) -> float:
        """
        時間減衰係数を計算

        Args:
            published_date: ニュース公開日（ISO形式）

        Returns:
            時間減衰係数（0.0～1.0）
        """
        try:
            pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
        except:
            # パースできない場合は現在時刻とする
            pub_date = datetime.now()

        now = datetime.now()
        days_old = (now - pub_date).days

        # 時間減衰曲線
        if days_old == 0:
            return 1.0  # 今日
        elif days_old <= 1:
            return 0.95  # 1日前
        elif days_old <= 3:
            return 0.9   # 3日前
        elif days_old <= 7:
            return 0.8   # 1週間前
        elif days_old <= 14:
            return 0.6   # 2週間前
        elif days_old <= 30:
            return 0.4   # 1ヶ月前
        elif days_old <= 90:
            return 0.2   # 3ヶ月前
        else:
            return 0.1   # それ以前

    def calculate_relevance_score(self, news: Dict, target_symbol: str) -> float:
        """
        関連性スコアを計算

        Args:
            news: ニュースデータ
            target_symbol: 対象銘柄シンボル

        Returns:
            関連性スコア（0.0～1.0）
        """
        score = 0.0

        # 銘柄が一致
        if news.get('symbol') == target_symbol:
            score += 0.5

        # タイトルに銘柄名が含まれる
        title = news.get('title', '').lower()
        if target_symbol.lower() in title:
            score += 0.3

        # 本文に銘柄名が含まれる
        content = news.get('content', '').lower()
        if target_symbol.lower() in content:
            score += 0.2

        return min(score, 1.0)

    def calculate_importance_score(self, news: Dict) -> float:
        """
        重要性スコアを計算（ニュース自体の重要度）

        Args:
            news: ニュースデータ

        Returns:
            重要性スコア（0.0～1.0）
        """
        # DBに保存されている重要性スコアを基準
        base_score = news.get('importance_score', 0.5)

        # キーワードによる補正
        keywords = news.get('keywords', '')
        if isinstance(keywords, str):
            import json
            try:
                keywords = json.loads(keywords)
            except:
                keywords = []

        keyword_bonus = 0.0
        for keyword in keywords:
            if keyword in self.high_impact_keywords:
                keyword_bonus += self.high_impact_keywords[keyword] * 0.1

        return min(base_score + keyword_bonus, 1.0)

    def calculate_impact_score(self, news: Dict) -> float:
        """
        影響力スコアを計算（市場への影響力）

        Args:
            news: ニュースデータ

        Returns:
            影響力スコア（0.0～1.0）
        """
        # DBに保存されている影響力スコアを基準
        base_score = news.get('impact_score', 0.5)

        # センチメントによる補正
        sentiment = news.get('sentiment', 'neutral')
        sentiment_multiplier = {
            'very_positive': 1.2,
            'positive': 1.1,
            'neutral': 1.0,
            'negative': 1.1,
            'very_negative': 1.2,
        }
        multiplier = sentiment_multiplier.get(sentiment, 1.0)

        return min(base_score * multiplier, 1.0)

    def calculate_final_score(self, news: Dict, target_symbol: str = None) -> Dict:
        """
        最終スコアを計算

        Args:
            news: ニュースデータ
            target_symbol: 対象銘柄シンボル（Noneの場合はnews内のsymbolを使用）

        Returns:
            スコア詳細の辞書
        """
        if target_symbol is None:
            target_symbol = news.get('symbol')

        # 各スコアを計算
        relevance = self.calculate_relevance_score(news, target_symbol)
        importance = self.calculate_importance_score(news)
        impact = self.calculate_impact_score(news)
        time_decay = self.calculate_time_decay_factor(news.get('published_date', datetime.now().isoformat()))

        # 最終スコア = 関連性 × 重要性 × 影響力 × 時間減衰
        final_score = relevance * importance * impact * time_decay

        return {
            'relevance_score': round(relevance, 3),
            'importance_score': round(importance, 3),
            'impact_score': round(impact, 3),
            'time_decay_factor': round(time_decay, 3),
            'final_score': round(final_score, 3),
        }

    def score_all_news_for_coin(self, symbol: str, days_back: int = 30) -> List[Dict]:
        """
        特定銘柄の全ニュースをスコアリング

        Args:
            symbol: 銘柄シンボル
            days_back: 何日前までのニュースを対象とするか

        Returns:
            スコア付きニュースのリスト（スコアの高い順）
        """
        # ニュースを取得
        news_list = self.db.get_recent_news(symbol, limit=100, days=days_back)

        scored_news = []
        for news in news_list:
            scores = self.calculate_final_score(dict(news), symbol)

            news_with_score = dict(news)
            news_with_score.update(scores)

            scored_news.append(news_with_score)

        # 最終スコアでソート（降順）
        scored_news.sort(key=lambda x: x['final_score'], reverse=True)

        return scored_news

    def save_scoring_results(self, symbol: str, scored_news: List[Dict]):
        """
        スコアリング結果をDBに保存

        Args:
            symbol: 銘柄シンボル
            scored_news: スコア付きニュースのリスト
        """
        if not scored_news:
            return

        # 平均スコアを計算
        avg_relevance = sum(n['relevance_score'] for n in scored_news) / len(scored_news)
        avg_importance = sum(n['importance_score'] for n in scored_news) / len(scored_news)
        avg_impact = sum(n['impact_score'] for n in scored_news) / len(scored_news)
        avg_time_decay = sum(n['time_decay_factor'] for n in scored_news) / len(scored_news)
        avg_final = sum(n['final_score'] for n in scored_news) / len(scored_news)

        scoring_data = {
            'symbol': symbol,
            'relevance_score': round(avg_relevance, 3),
            'importance_score': round(avg_importance, 3),
            'impact_score': round(avg_impact, 3),
            'time_decay_factor': round(avg_time_decay, 3),
            'final_score': round(avg_final, 3),
            'news_count': len(scored_news),
        }

        self.db.add_scoring_result(scoring_data)

    def get_top_influential_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """
        最も影響力の高いニュースを取得

        Args:
            symbol: 銘柄シンボル
            limit: 取得件数

        Returns:
            影響力の高いニュース（上位limit件）
        """
        scored_news = self.score_all_news_for_coin(symbol)
        return scored_news[:limit]

    def close(self):
        """データベース接続を閉じる"""
        self.db.close()


class ScoringAnalyzer:
    """
    スコアリング分析実行クラス

    Claude Codeが評価を実行する際のエントリーポイント
    """

    def __init__(self):
        self.engine = ScoringEngine()

    def analyze_news_impact(self, symbol: str, days_back: int = 365) -> Dict:
        """
        ニュースの影響力を分析

        Args:
            symbol: 銘柄シンボル
            days_back: 何日前までのニュースを対象とするか（デフォルト: 365日）

        Returns:
            分析結果
        """
        print(f"\n{'='*60}")
        print(f"{symbol} のニュース影響力分析")
        print('='*60)

        # 全ニュースをスコアリング
        scored_news = self.engine.score_all_news_for_coin(symbol, days_back=days_back)

        if not scored_news:
            print(f"  [!] {symbol} のニュースが見つかりません")
            return {'symbol': symbol, 'news_count': 0}

        print(f"\n[*] 分析対象ニュース件数: {len(scored_news)}")

        # トップ5を表示
        print(f"\n[*] 影響力トップ5:")
        for i, news in enumerate(scored_news[:5], 1):
            print(f"\n  {i}. {news['title'][:60]}...")
            print(f"     最終スコア: {news['final_score']:.3f}")
            print(f"     └ 関連性: {news['relevance_score']:.3f}")
            print(f"     └ 重要性: {news['importance_score']:.3f}")
            print(f"     └ 影響力: {news['impact_score']:.3f}")
            print(f"     └ 時間減衰: {news['time_decay_factor']:.3f}")

        # スコアリング結果をDBに保存
        self.engine.save_scoring_results(symbol, scored_news)

        # 統計計算
        avg_score = sum(n['final_score'] for n in scored_news) / len(scored_news)
        max_score = max(n['final_score'] for n in scored_news)

        result = {
            'symbol': symbol,
            'news_count': len(scored_news),
            'avg_final_score': round(avg_score, 3),
            'max_final_score': round(max_score, 3),
            'top_news': scored_news[:5],
        }

        print(f"\n[*] 統計:")
        print(f"    平均スコア: {result['avg_final_score']:.3f}")
        print(f"    最高スコア: {result['max_final_score']:.3f}")

        return result

    def close(self):
        self.engine.close()


if __name__ == '__main__':
    # テスト実行
    print("="*60)
    print("スコアリングエンジン - テスト")
    print("="*60)

    analyzer = ScoringAnalyzer()

    # テスト用ダミーニュース（実際にはDB内のニュースを使用）
    test_symbol = 'BTC'

    result = analyzer.analyze_news_impact(test_symbol)

    print(f"\n[OK] 分析完了")

    analyzer.close()
