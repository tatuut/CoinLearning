"""
ニュース全文保存システム

銘柄ごとにフォルダ分けし、Markdown形式で保存
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.advanced_database import AdvancedDatabase
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class NewsManager:
    """ニュース全文保存・管理"""

    def __init__(self, base_path: str = './data/news'):
        """
        初期化

        Args:
            base_path: ニュース保存先ベースディレクトリ
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db = AdvancedDatabase()

    def save_news_markdown(self, news: dict) -> str:
        """
        ニュースをMarkdown形式で保存

        Args:
            news: ニュースデータ（dict）

        Returns:
            保存したファイルパス
        """
        symbol = news.get('symbol', 'UNKNOWN')

        # 銘柄ごとのディレクトリ作成
        symbol_dir = self.base_path / symbol
        symbol_dir.mkdir(parents=True, exist_ok=True)

        # ファイル名: 公開日時
        pub_date_str = news.get('published_date', datetime.now().isoformat())
        try:
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
            filename = pub_date.strftime('%Y-%m-%d_%H-%M-%S') + '.md'
        except:
            filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.md'

        filepath = symbol_dir / filename

        # Markdown生成
        markdown_content = self._generate_markdown(news)

        # ファイル保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return str(filepath)

    def _generate_markdown(self, news: dict) -> str:
        """
        ニュースからMarkdownを生成

        Args:
            news: ニュースデータ

        Returns:
            Markdown文字列
        """
        title = news.get('title', 'タイトルなし')
        source = news.get('source', 'Unknown')
        pub_date = news.get('published_date', 'Unknown')
        url = news.get('url', 'N/A')
        symbol = news.get('symbol', 'N/A')

        # スコア情報
        relevance = news.get('relevance_score', 0)
        importance = news.get('importance_score', 0)
        impact = news.get('impact_score', 0)
        time_decay = news.get('time_decay_factor', 0)
        final_score = news.get('final_score', 0)

        # センチメント
        sentiment = news.get('sentiment', 'neutral')
        sentiment_map = {
            'very_positive': '📈 非常にポジティブ',
            'positive': '↗️ ポジティブ',
            'neutral': '➡️ 中立',
            'negative': '↘️ ネガティブ',
            'very_negative': '📉 非常にネガティブ',
        }
        sentiment_text = sentiment_map.get(sentiment, '➡️ 中立')

        # 本文
        content = news.get('content', '（本文なし）')

        # Markdown生成
        md = f"""# {title}

**銘柄**: {symbol}
**出典**: {source}
**公開日**: {pub_date[:10] if len(pub_date) > 10 else pub_date}
**URL**: {url if url != 'N/A' else '（URLなし）'}

---

## 📊 スコア分析

**センチメント**: {sentiment_text}

### スコア詳細

| 項目 | 値 |
|------|-----|
| 関連性 | {relevance:.3f} |
| 重要性 | {importance:.3f} |
| 影響力 | {impact:.3f} |
| 時間減衰 | {time_decay:.3f} |
| **最終スコア** | **{final_score:.3f}** |

---

## 📝 本文

{content}

---

**保存日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**データソース**: Advanced Database
"""
        return md

    def export_all_news(self, symbol: str = None, days: int = 30):
        """
        全ニュースをMarkdownエクスポート

        Args:
            symbol: 銘柄（Noneなら全銘柄）
            days: 過去何日分
        """
        if symbol:
            news_list = self.db.get_recent_news(symbol, limit=1000, days=days)
            print(f"📰 {symbol}: {len(news_list)}件のニュースをエクスポート中...")
        else:
            # 全銘柄
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT DISTINCT symbol FROM news
                WHERE published_date >= date('now', ?)
            ''', (f'-{days} days',))
            symbols = [row[0] for row in cursor.fetchall()]

            print(f"📰 全{len(symbols)}銘柄のニュースをエクスポート中...")
            news_list = []
            for sym in symbols:
                news_list.extend(self.db.get_recent_news(sym, limit=1000, days=days))

        # エクスポート
        count = 0
        for news in news_list:
            news_dict = dict(news)
            filepath = self.save_news_markdown(news_dict)
            count += 1
            if count % 10 == 0:
                print(f"   {count}件完了...", end='\r')

        print(f"\n✅ 完了: {count}件のニュースを保存")

    def list_news(self, symbol: str) -> List[Path]:
        """
        銘柄のニュースファイル一覧

        Args:
            symbol: 銘柄シンボル

        Returns:
            ファイルパスのリスト
        """
        symbol_dir = self.base_path / symbol

        if not symbol_dir.exists():
            return []

        files = list(symbol_dir.glob('*.md'))
        files.sort(reverse=True)  # 新しい順
        return files

    def get_latest_news(self, symbol: str, limit: int = 5) -> List[str]:
        """
        最新ニュースを取得

        Args:
            symbol: 銘柄シンボル
            limit: 取得件数

        Returns:
            ファイルパスのリスト
        """
        files = self.list_news(symbol)
        return [str(f) for f in files[:limit]]

    def read_news(self, filepath: str) -> str:
        """
        ニュースファイルを読み込み

        Args:
            filepath: ファイルパス

        Returns:
            Markdown内容
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def search_news(self, keyword: str, symbol: str = None) -> List[Path]:
        """
        キーワードでニュースを検索

        Args:
            keyword: 検索キーワード
            symbol: 銘柄（Noneなら全銘柄）

        Returns:
            マッチしたファイルのリスト
        """
        if symbol:
            files = self.list_news(symbol)
        else:
            files = list(self.base_path.rglob('*.md'))

        matched = []
        for file in files:
            content = file.read_text(encoding='utf-8')
            if keyword.lower() in content.lower():
                matched.append(file)

        return matched

    def get_statistics(self) -> dict:
        """
        ニュース統計情報

        Returns:
            統計情報
        """
        symbols = [d.name for d in self.base_path.iterdir() if d.is_dir()]

        stats = {
            'total_symbols': len(symbols),
            'total_news': 0,
            'by_symbol': {}
        }

        for symbol in symbols:
            news_files = self.list_news(symbol)
            count = len(news_files)
            stats['total_news'] += count
            stats['by_symbol'][symbol] = count

        return stats


def main():
    """テスト実行"""
    import argparse

    parser = argparse.ArgumentParser(description='ニュース管理システム')
    parser.add_argument('--export', action='store_true', help='全ニュースをエクスポート')
    parser.add_argument('--symbol', help='銘柄シンボル（エクスポート対象）')
    parser.add_argument('--days', type=int, default=30, help='過去何日分（デフォルト30）')
    parser.add_argument('--list', action='store_true', help='ニュース一覧表示')
    parser.add_argument('--search', help='キーワード検索')
    parser.add_argument('--stats', action='store_true', help='統計情報表示')

    args = parser.parse_args()

    manager = NewsManager()

    if args.export:
        manager.export_all_news(symbol=args.symbol, days=args.days)

    elif args.list:
        if not args.symbol:
            print("❌ --symbol を指定してください")
            return

        files = manager.list_news(args.symbol)
        print(f"📂 {args.symbol} のニュース: {len(files)}件")
        for i, file in enumerate(files[:10], 1):
            print(f"   {i}. {file.name}")

    elif args.search:
        files = manager.search_news(args.search, symbol=args.symbol)
        print(f"🔍 検索結果: {len(files)}件")
        for i, file in enumerate(files[:20], 1):
            print(f"   {i}. {file.parent.name}/{file.name}")

    elif args.stats:
        stats = manager.get_statistics()
        print(f"📊 ニュース統計")
        print(f"   総銘柄数: {stats['total_symbols']}")
        print(f"   総ニュース数: {stats['total_news']}")
        print(f"\n   銘柄別:")
        for symbol, count in sorted(stats['by_symbol'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"     {symbol}: {count}件")

    else:
        print("使用例:")
        print("  python news_manager.py --export --symbol BTC")
        print("  python news_manager.py --list --symbol BTC")
        print("  python news_manager.py --search ETF --symbol BTC")
        print("  python news_manager.py --stats")


if __name__ == '__main__':
    main()
