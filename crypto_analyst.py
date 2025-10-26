"""
仮想通貨分析アシスタント

ワンコマンドで銘柄の全情報を取り寄せ、Claude Codeと一緒に分析できるツール
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.exchange_api import MEXCAPI
from src.data.advanced_database import AdvancedDatabase
from src.data.timeseries_storage import TimeSeriesStorage
from datetime import datetime, timedelta
from pathlib import Path
import argparse


class CryptoAnalyst:
    """仮想通貨分析アシスタント"""

    def __init__(self):
        self.api = MEXCAPI()
        self.db = AdvancedDatabase()
        self.storage = TimeSeriesStorage()

        # ニュース保存用ディレクトリ
        self.news_dir = Path('data/news')
        self.news_dir.mkdir(parents=True, exist_ok=True)

    def get_full_context(self, symbol: str):
        """
        銘柄の全コンテキストを取得

        価格、ニュース、スコアなど分析に必要な全情報を一括取得
        """
        print("="*80)
        print(f"📊 {symbol} - 分析コンテキスト取得中...")
        print("="*80)
        print()

        context = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
        }

        # 1. 現在の市場データ
        print("💰 [1/4] 市場データ取得中...")
        try:
            price = self.api.get_price(f"{symbol}USDT")
            stats = self.api.get_24h_stats(f"{symbol}USDT")

            context['price'] = {
                'current': price,
                'change_24h': stats.get('price_change_percent', 0),
                'high_24h': stats.get('high', 0),
                'low_24h': stats.get('low', 0),
                'volume': stats.get('volume', 0),
                'quote_volume': stats.get('quote_volume', 0),
            }
            print(f"   ✓ 現在価格: ${price:,.2f}")
            print(f"   ✓ 24h変動: {stats.get('price_change_percent', 0):+.2f}%")
        except Exception as e:
            print(f"   ✗ 価格データ取得失敗: {e}")
            context['price'] = None

        # 2. 最近のニュース
        print("\n📰 [2/4] ニュース取得中...")
        news_list = self.db.get_recent_news(symbol, limit=10, days=30)
        context['news'] = [dict(n) for n in news_list]
        print(f"   ✓ 取得件数: {len(news_list)}件")

        # ニュース原文をMarkdownで保存
        if news_list:
            print(f"   💾 ニュースをMarkdownで保存中...")
            for news in news_list:
                self.save_news_to_markdown(symbol, dict(news))
            print(f"   ✓ 保存完了")

        # 3. 影響力スコア
        print("\n📈 [3/4] スコアリング情報取得中...")
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT
                relevance_score,
                importance_score,
                impact_score,
                time_decay_factor,
                final_score,
                news_count,
                scoring_date
            FROM scoring_history
            WHERE symbol = ?
            ORDER BY scoring_date DESC
            LIMIT 1
        ''', (symbol,))

        row = cursor.fetchone()
        if row:
            context['score'] = {
                'relevance': row[0],
                'importance': row[1],
                'impact': row[2],
                'time_decay': row[3],
                'final': row[4],
                'news_count': row[5],
                'date': row[6],
            }
            print(f"   ✓ 最終スコア: {row[4]:.3f}")
        else:
            context['score'] = None
            print(f"   ✗ スコアデータなし")

        # 4. 価格履歴（チャート用）
        print("\n📉 [4/4] チャートデータ取得中...")
        try:
            klines = self.api.get_klines(f"{symbol}USDT", interval='1d', limit=30)
            context['chart'] = klines
            print(f"   ✓ 取得期間: 30日分")

            # Parquetに自動保存
            if klines:
                print(f"   💾 Parquetに保存中...")
                self.storage.save_price_data(symbol, '1d', klines)
        except Exception as e:
            print(f"   ✗ チャートデータ取得失敗: {e}")
            context['chart'] = []

        print()
        print("="*80)
        print("✅ コンテキスト取得完了")
        print("="*80)

        return context

    def display_context(self, context: dict):
        """コンテキストを見やすく表示"""
        symbol = context['symbol']

        print()
        print("="*80)
        print(f"💎 {symbol} - 分析ダッシュボード")
        print("="*80)
        print()

        # 価格情報
        if context['price']:
            p = context['price']
            print("📊 **現在の市場状況**")

            # 価格のフォーマット（小数点以下の桁数を動的に決定）
            price = p['current']
            if price >= 1:
                price_str = f"${price:,.2f}"
            elif price >= 0.01:
                price_str = f"${price:,.4f}"
            else:
                price_str = f"${price:,.8f}"

            high_24h = p['high_24h']
            if high_24h >= 1:
                high_str = f"${high_24h:,.2f}"
            elif high_24h >= 0.01:
                high_str = f"${high_24h:,.4f}"
            else:
                high_str = f"${high_24h:,.8f}"

            low_24h = p['low_24h']
            if low_24h >= 1:
                low_str = f"${low_24h:,.2f}"
            elif low_24h >= 0.01:
                low_str = f"${low_24h:,.4f}"
            else:
                low_str = f"${low_24h:,.8f}"

            print(f"   価格: {price_str}")
            print(f"   24h変動: {p['change_24h']:+.2f}%")
            print(f"   24h高値/安値: {high_str} / {low_str}")
            print(f"   24h出来高: {p['volume']:,.0f} {symbol}")
            print()

        # スコア情報
        if context['score']:
            s = context['score']
            print("🎯 **ニュース影響力スコア**")
            print(f"   最終スコア: {s['final']:.3f}")
            print(f"   ├─ 関連性: {s['relevance']:.3f}")
            print(f"   ├─ 重要性: {s['importance']:.3f}")
            print(f"   ├─ 影響力: {s['impact']:.3f}")
            print(f"   └─ 時間減衰: {s['time_decay']:.3f}")
            print(f"   分析ニュース数: {s['news_count']}件")
            print()

        # ニュース一覧
        if context['news']:
            print("📰 **最近のニュース（影響力順）**")
            print()

            # スコア付きでソート
            news_with_scores = []
            for news in context['news']:
                # 簡易スコア計算
                importance = news.get('importance_score', 0.5)
                impact = news.get('impact_score', 0.5)

                # 日付から時間減衰
                pub_date_str = news.get('published_date', datetime.now().isoformat())
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    days_old = (datetime.now() - pub_date).days
                    if days_old <= 3:
                        time_decay = 0.9
                    elif days_old <= 7:
                        time_decay = 0.7
                    elif days_old <= 14:
                        time_decay = 0.5
                    else:
                        time_decay = 0.3
                except:
                    time_decay = 0.5

                score = importance * impact * time_decay
                news_with_scores.append((score, news))

            news_with_scores.sort(reverse=True, key=lambda x: x[0])

            for i, (score, news) in enumerate(news_with_scores[:5], 1):
                pub_date = news.get('published_date', '')[:10]
                sentiment_icon = {
                    'very_positive': '📈',
                    'positive': '↗️',
                    'neutral': '➡️',
                    'negative': '↘️',
                    'very_negative': '📉',
                }.get(news.get('sentiment', 'neutral'), '➡️')

                print(f"{i}. {sentiment_icon} [{pub_date}] {news['title']}")
                print(f"   スコア: {score:.3f} | 重要度: {news.get('importance_score', 0):.2f} | "
                      f"影響: {news.get('impact_score', 0):.2f}")
                print(f"   出典: {news.get('source', 'Unknown')}")

                # 本文の最初の100文字
                content = news.get('content', '')[:100]
                if content:
                    print(f"   {content}...")
                print()

        # チャート概要
        if context['chart']:
            print("📉 **30日間の価格動向**")
            chart = context['chart']

            # 最初と最後の価格
            first_price = float(chart[0]['close'])
            last_price = float(chart[-1]['close'])
            change = ((last_price - first_price) / first_price) * 100

            # 最高値・最安値
            high = max(float(k['high']) for k in chart)
            low = min(float(k['low']) for k in chart)

            # 価格フォーマット関数
            def format_price(p):
                if p >= 1:
                    return f"${p:,.2f}"
                elif p >= 0.01:
                    return f"${p:,.4f}"
                else:
                    return f"${p:,.8f}"

            print(f"   30日前: {format_price(first_price)}")
            print(f"   現在: {format_price(last_price)}")
            print(f"   変動: {change:+.2f}%")
            print(f"   期間最高値: {format_price(high)}")
            print(f"   期間最安値: {format_price(low)}")
            print()

        print("="*80)
        print("💡 **次のアクション**")
        print("="*80)
        print()
        print("📌 このデータをもとに、Claude Codeと一緒に以下を分析できます：")
        print()
        print("1. 価格とニュースの相関分析")
        print("   「最近の価格上昇とニュースの関係を分析して」")
        print()
        print("2. 特定ニュースの詳細確認")
        print("   「1番目のニュースの詳細を見せて」")
        print()
        print("3. 技術的分析との組み合わせ")
        print("   「チャートパターンとニュースを照らし合わせて」")
        print()
        print("4. 他銘柄との比較")
        print("   「ETHと比較してどう？」")
        print()
        print("5. 投資判断の材料整理")
        print("   「今買うべきか、材料を整理して」")
        print()

    def get_news_detail(self, context: dict, index: int):
        """特定ニュースの詳細を表示（Markdown形式）"""
        if not context.get('news'):
            print("ニュースデータがありません")
            return

        if index < 1 or index > len(context['news']):
            print(f"ニュース番号は 1～{len(context['news'])} の範囲で指定してください")
            return

        news = context['news'][index - 1]

        print()
        print("="*80)
        print(f"📰 ニュース詳細 #{index}")
        print("="*80)
        print()

        # Markdown形式で表示
        print(f"# {news['title']}")
        print()
        print(f"**出典**: {news.get('source', 'Unknown')}")
        print(f"**公開日**: {news.get('published_date', 'Unknown')[:10]}")
        if news.get('url') and news.get('url') != 'N/A':
            print(f"**URL**: {news.get('url')}")
        print()

        # センチメント表示
        sentiment_map = {
            'very_positive': '📈 非常にポジティブ',
            'positive': '↗️ ポジティブ',
            'neutral': '➡️ 中立',
            'negative': '↘️ ネガティブ',
            'very_negative': '📉 非常にネガティブ',
        }
        sentiment = news.get('sentiment', 'neutral')
        print(f"**センチメント**: {sentiment_map.get(sentiment, '➡️ 中立')}")
        print(f"**重要度**: {news.get('importance_score', 0):.2f} / 1.00")
        print(f"**影響力**: {news.get('impact_score', 0):.2f} / 1.00")
        print()

        print("---")
        print()
        print("## 本文")
        print()

        # 本文を段落ごとに表示
        content = news.get('content', '')
        if content:
            # 段落に分割（改行2回以上で分割）
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for para in paragraphs:
                # 長い段落は適度に改行
                if len(para) > 80:
                    words = para.split()
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) + 1 > 80:
                            print(current_line)
                            current_line = word
                        else:
                            current_line = current_line + " " + word if current_line else word
                    if current_line:
                        print(current_line)
                else:
                    print(para)
                print()
        else:
            print("（本文なし）")

        print("="*80)

    def compare_with_chart(self, context: dict):
        """価格とニュースの時系列比較"""
        if not context.get('chart') or not context.get('news'):
            print("チャートまたはニュースデータがありません")
            return

        print()
        print("="*80)
        print("📊 価格 × ニュース 時系列分析")
        print("="*80)
        print()

        # チャートデータを日付でマッピング
        price_by_date = {}
        for k in context['chart']:
            # タイムスタンプを日付文字列に変換
            if isinstance(k['timestamp'], int):
                from datetime import datetime
                date = datetime.fromtimestamp(k['timestamp'] / 1000).strftime('%Y-%m-%d')
            else:
                date = str(k['timestamp'])[:10]

            price_by_date[date] = {
                'open': float(k['open']),
                'close': float(k['close']),
                'high': float(k['high']),
                'low': float(k['low']),
                'change': ((float(k['close']) - float(k['open'])) / float(k['open'])) * 100
            }

        # ニュースを日付順にソート
        news_by_date = {}
        for news in context['news']:
            date = news.get('published_date', '')[:10]
            if date not in news_by_date:
                news_by_date[date] = []
            news_by_date[date].append(news)

        # 統合表示
        all_dates = sorted(set(list(price_by_date.keys()) + list(news_by_date.keys())), reverse=True)

        for date in all_dates[:14]:  # 直近2週間
            print(f"📅 {date}")

            # 価格情報
            if date in price_by_date:
                p = price_by_date[date]
                change_icon = "📈" if p['change'] > 0 else "📉" if p['change'] < 0 else "➡️"
                print(f"   {change_icon} 価格: ${p['close']:,.4f} ({p['change']:+.2f}%)")

            # ニュース
            if date in news_by_date:
                for news in news_by_date[date]:
                    sentiment_icon = {
                        'very_positive': '📈',
                        'positive': '↗️',
                        'neutral': '➡️',
                        'negative': '↘️',
                        'very_negative': '📉',
                    }.get(news.get('sentiment', 'neutral'), '➡️')
                    print(f"   {sentiment_icon} {news['title'][:60]}...")

            print()

    def save_news_to_markdown(self, symbol: str, news: dict):
        """
        ニュース原文をMarkdown形式で保存

        保存先: data/news/{symbol}/YYYY-MM-DD_HH-MM-SS_{id}.md
        """
        # 銘柄ごとのディレクトリ作成
        symbol_dir = self.news_dir / symbol
        symbol_dir.mkdir(exist_ok=True)

        # ファイル名: 公開日時_ID.md
        pub_date = news.get('published_date', datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d_%H-%M-%S')
        except:
            date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        news_id = news.get('id', 'unknown')
        filename = f"{date_str}_{news_id}.md"
        filepath = symbol_dir / filename

        # 既に保存済みならスキップ
        if filepath.exists():
            return

        # センチメントマッピング
        sentiment_map = {
            'very_positive': '📈 非常にポジティブ',
            'positive': '↗️ ポジティブ',
            'neutral': '➡️ 中立',
            'negative': '↘️ ネガティブ',
            'very_negative': '📉 非常にネガティブ',
        }

        # Markdown作成
        md_content = f"""# {news.get('title', 'タイトルなし')}

**出典**: {news.get('source', 'Unknown')}
**公開日**: {pub_date[:19]}
**URL**: {news.get('url', 'N/A')}

---

## センチメント

{sentiment_map.get(news.get('sentiment', 'neutral'), '➡️ 中立')}

**スコア詳細**:
- 重要度: {news.get('importance_score', 0):.3f}
- 影響力: {news.get('impact_score', 0):.3f}

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
        self.db.close()


def main():
    parser = argparse.ArgumentParser(
        description='仮想通貨分析アシスタント - ワンコマンドで全情報取得',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python crypto_analyst.py BTC          # BTCの全情報を取得
  python crypto_analyst.py ETH          # ETHの全情報を取得
  python crypto_analyst.py SHIB         # SHIBの全情報を取得

取得される情報:
  - 現在価格と24h統計
  - 最近のニュース（影響力順）
  - ニュース影響力スコア
  - 30日間のチャートデータ
  - 価格とニュースの時系列比較

このツールで情報を集めた後、Claude Codeと一緒に詳細分析を行えます。
        """
    )

    parser.add_argument('symbol', help='銘柄シンボル（例: BTC, ETH, SHIB）')
    parser.add_argument('--timeline', action='store_true',
                       help='価格とニュースの時系列比較を表示')
    parser.add_argument('--news', type=int, metavar='N',
                       help='N番目のニュース詳細を表示')

    args = parser.parse_args()

    analyst = CryptoAnalyst()

    try:
        # 全コンテキスト取得
        context = analyst.get_full_context(args.symbol.upper())

        # 基本情報表示
        analyst.display_context(context)

        # オプション処理
        if args.timeline:
            analyst.compare_with_chart(context)

        if args.news:
            analyst.get_news_detail(context, args.news)

    finally:
        analyst.close()


if __name__ == '__main__':
    main()
