"""
ニュース取得ヘルパー

Claude Codeと連携してWebSearchでニュースを取得し、DBに保存します
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.analysis.news_collector import NewsCollector
from src.data.advanced_database import AdvancedDatabase
from datetime import datetime
from pathlib import Path
import argparse


class NewsFetcher:
    """ニュース取得・保存システム"""

    def __init__(self):
        self.collector = NewsCollector()
        self.db = AdvancedDatabase()

    def request_news_search(self, symbol: str, coin_name: str = None):
        """
        Claude Codeに対してニュース検索をリクエスト

        このメソッドは、Claude Codeに検索クエリを提示します。
        Claude CodeがWebSearchを実行した後、結果をparse_and_save_news()に渡してください。
        """
        if not coin_name:
            coin_name = self._get_coin_name(symbol)

        query = f"{coin_name} {symbol} 仮想通貨 最新ニュース 2025"

        print("="*80)
        print("📰 ニュース取得リクエスト")
        print("="*80)
        print()
        print(f"**銘柄**: {symbol} ({coin_name})")
        print(f"**検索クエリ**: {query}")
        print()
        print("="*80)
        print("次のステップ:")
        print("="*80)
        print()
        print("Claude Codeにこのメッセージを伝えてください:")
        print()
        print(f'「{query}」でWebSearchを実行して、')
        print(f'結果を news_fetcher.parse_and_save_news() に渡してください')
        print()
        print("または、以下のコマンドを実行してください:")
        print()
        print(f'  python src/tools/news_fetcher.py {symbol} --interactive')
        print()
        print("="*80)

        return query

    def parse_and_save_news(self, symbol: str, search_results: list, coin_name: str = None):
        """
        WebSearchの結果を解析してDBに保存

        Args:
            symbol: 銘柄シンボル
            search_results: WebSearchの結果リスト
            coin_name: 銘柄名（オプション）

        Returns:
            保存件数
        """
        if not coin_name:
            coin_name = self._get_coin_name(symbol)

        print("="*80)
        print(f"📰 {symbol} ニュース保存中...")
        print("="*80)
        print()

        news_data = []
        for result in search_results:
            # WebSearchの結果を標準フォーマットに変換
            news_item = {
                'title': result.get('title', ''),
                'content': result.get('description', result.get('snippet', '')),
                'url': result.get('url', ''),
                'source': self._extract_domain(result.get('url', '')),
                'published_date': result.get('date', datetime.now().isoformat()),
                'sentiment': self._simple_sentiment_analysis(
                    result.get('title', '') + ' ' + result.get('description', '')
                ),
                'importance_score': 0.7,  # デフォルト
                'impact_score': 0.6,      # デフォルト
                'keywords': [symbol, coin_name],
            }
            news_data.append(news_item)

        # DBに保存
        saved_count = self.collector.collect_news_for_coin(symbol, coin_name, news_data)

        print()
        print(f"✅ {saved_count}件のニュースを保存しました")
        print()

        # Markdown形式でも保存
        self._save_as_markdown(symbol, news_data)

        return saved_count

    def save_manual_news(self, symbol: str, title: str, content: str, url: str = "", source: str = "Manual"):
        """
        手動でニュースを追加

        Args:
            symbol: 銘柄シンボル
            title: タイトル
            content: 本文
            url: URL（オプション）
            source: 出典（オプション）
        """
        coin_name = self._get_coin_name(symbol)

        news_data = [{
            'title': title,
            'content': content,
            'url': url,
            'source': source,
            'published_date': datetime.now().isoformat(),
            'sentiment': self._simple_sentiment_analysis(title + ' ' + content),
            'importance_score': 0.7,
            'impact_score': 0.6,
            'keywords': [symbol, coin_name],
        }]

        saved_count = self.collector.collect_news_for_coin(symbol, coin_name, news_data)

        if saved_count > 0:
            print(f"✅ ニュースを保存しました")
            self._save_as_markdown(symbol, news_data)
        else:
            print(f"❌ ニュースの保存に失敗しました")

        return saved_count

    def _get_coin_name(self, symbol: str) -> str:
        """銘柄シンボルから銘柄名を取得"""
        coin_names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'XRP': 'Ripple',
            'DOGE': 'Dogecoin',
            'SHIB': 'Shiba Inu',
            'ADA': 'Cardano',
            'SOL': 'Solana',
            'MATIC': 'Polygon',
        }
        return coin_names.get(symbol.upper(), symbol)

    def _extract_domain(self, url: str) -> str:
        """URLからドメイン名を抽出"""
        if not url:
            return "Unknown"
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return "Unknown"

    def _simple_sentiment_analysis(self, text: str) -> str:
        """簡易的なセンチメント分析"""
        text = text.lower()

        positive_words = ['上昇', '急騰', '高値', '好調', '期待', '成長', '成功', '承認', '提携', '採用']
        negative_words = ['下落', '暴落', '安値', '不調', '懸念', '規制', '失敗', 'ハッキング', '詐欺']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return 'positive' if positive_count - negative_count >= 2 else 'positive'
        elif negative_count > positive_count:
            return 'negative' if negative_count - positive_count >= 2 else 'negative'
        else:
            return 'neutral'

    def _save_as_markdown(self, symbol: str, news_data: list):
        """ニュースをMarkdown形式で保存"""
        news_dir = Path('data/news') / symbol
        news_dir.mkdir(parents=True, exist_ok=True)

        sentiment_map = {
            'positive': '↗️ ポジティブ',
            'negative': '↘️ ネガティブ',
            'neutral': '➡️ 中立',
        }

        for news in news_data:
            # ファイル名作成
            pub_date = news.get('published_date', datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d_%H-%M-%S')
            except:
                date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            # タイトルから安全なファイル名を作成
            safe_title = "".join(c for c in news.get('title', 'news')[:30] if c.isalnum() or c in (' ', '_')).strip()
            filename = f"{date_str}_{safe_title}.md"
            filepath = news_dir / filename

            # 既に存在する場合はスキップ
            if filepath.exists():
                continue

            # Markdown作成
            md_content = f"""# {news.get('title', 'タイトルなし')}

**出典**: {news.get('source', 'Unknown')}
**公開日**: {pub_date[:19]}
**URL**: {news.get('url', 'N/A')}

---

## センチメント

{sentiment_map.get(news.get('sentiment', 'neutral'), '➡️ 中立')}

**スコア詳細**:
- 重要度: {news.get('importance_score', 0.5):.3f}
- 影響力: {news.get('impact_score', 0.5):.3f}

---

## 本文

{news.get('content', '（本文なし）')}

---

**保存日時**: {datetime.now().isoformat()}
"""

            # ファイル保存
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

    def close(self):
        """リソースをクローズ"""
        self.collector.close()
        self.db.close()


def main():
    parser = argparse.ArgumentParser(
        description='ニュース取得ヘルパー',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # ニュース検索クエリを表示
  python src/tools/news_fetcher.py BTC

  # 手動でニュースを追加
  python src/tools/news_fetcher.py BTC --add-manual \\
    --title "ビットコインが最高値更新" \\
    --content "BTCが10万ドルを突破しました" \\
    --url "https://example.com/btc-news"
        """
    )

    parser.add_argument('symbol', help='銘柄シンボル（例: BTC, ETH）')
    parser.add_argument('--add-manual', action='store_true',
                       help='手動でニュースを追加')
    parser.add_argument('--title', help='ニュースタイトル')
    parser.add_argument('--content', help='ニュース本文')
    parser.add_argument('--url', default='', help='URL')
    parser.add_argument('--source', default='Manual', help='出典')

    args = parser.parse_args()

    fetcher = NewsFetcher()

    try:
        if args.add_manual:
            if not args.title or not args.content:
                print("❌ エラー: --title と --content は必須です")
                return

            fetcher.save_manual_news(
                args.symbol.upper(),
                args.title,
                args.content,
                args.url,
                args.source
            )
        else:
            # ニュース検索クエリを表示
            fetcher.request_news_search(args.symbol.upper())

    finally:
        fetcher.close()


if __name__ == '__main__':
    main()
