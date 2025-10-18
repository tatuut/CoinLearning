"""
投資優先度分析ツール

全10銘柄の分析結果を比較して、投資優先度をランク付け
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.advanced_database import AdvancedDatabase
from datetime import datetime


def main():
    print("="*80)
    print("投資優先度分析レポート - 全10銘柄比較")
    print("="*80)
    print(f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    print()

    db = AdvancedDatabase()

    # 分析対象銘柄
    target_coins = [
        # 基軸通貨
        ('BTC', 'Bitcoin', '基軸通貨'),
        ('ETH', 'Ethereum', '基軸通貨'),
        ('XRP', 'Ripple', '基軸通貨'),
        # ミームコイン
        ('DOGE', 'Dogecoin', 'ミームコイン'),
        ('SHIB', 'Shiba Inu', 'ミームコイン'),
        ('PEPE', 'Pepe', 'ミームコイン'),
        # 将来性銘柄
        ('MATIC', 'Polygon', '将来性'),
        ('DOT', 'Polkadot', '将来性'),
        ('LINK', 'Chainlink', '将来性'),
        ('AVAX', 'Avalanche', '将来性'),
    ]

    # 各銘柄のスコアを取得
    results = []
    for symbol, name, category in target_coins:
        # 最新のスコアリング結果を取得
        cursor = db.conn.cursor()
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
            results.append({
                'symbol': symbol,
                'name': name,
                'category': category,
                'relevance': row[0],
                'importance': row[1],
                'impact': row[2],
                'time_decay': row[3],
                'final_score': row[4],
                'news_count': row[5],
                'timestamp': row[6],
            })
        else:
            results.append({
                'symbol': symbol,
                'name': name,
                'category': category,
                'relevance': 0,
                'importance': 0,
                'impact': 0,
                'time_decay': 0,
                'final_score': 0,
                'news_count': 0,
                'timestamp': None,
            })

    # スコアでソート（降順）
    results.sort(key=lambda x: x['final_score'], reverse=True)

    # カテゴリ別の最高スコア
    category_best = {}
    for result in results:
        cat = result['category']
        if cat not in category_best or result['final_score'] > category_best[cat]['final_score']:
            category_best[cat] = result

    print("\n" + "="*80)
    print("📊 総合ランキング（影響力スコア順）")
    print("="*80)
    print()
    print(f"{'順位':<4} {'銘柄':<10} {'名称':<15} {'カテゴリ':<12} {'最終スコア':<10} {'ニュース件数':<10}")
    print("-"*80)

    for i, result in enumerate(results, 1):
        rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{rank_icon}{i:<3} {result['symbol']:<10} {result['name']:<15} {result['category']:<12} "
              f"{result['final_score']:<10.3f} {result['news_count']:<10}")

    print()
    print("="*80)
    print("📈 カテゴリ別ベスト銘柄")
    print("="*80)
    print()

    for category in ['基軸通貨', 'ミームコイン', '将来性']:
        if category in category_best:
            best = category_best[category]
            print(f"【{category}】")
            print(f"  🏆 {best['name']} ({best['symbol']})")
            print(f"     最終スコア: {best['final_score']:.3f}")
            print(f"     関連性: {best['relevance']:.3f} | 重要性: {best['importance']:.3f} | "
                  f"影響力: {best['impact']:.3f} | 時間減衰: {best['time_decay']:.3f}")
            print()

    print("="*80)
    print("💡 投資推奨アドバイス")
    print("="*80)
    print()

    # トップ3銘柄
    top3 = results[:3]

    print("【最優先投資候補】")
    for i, coin in enumerate(top3, 1):
        print(f"{i}. {coin['name']} ({coin['symbol']}) - スコア {coin['final_score']:.3f}")
    print()

    # カテゴリ別推奨
    print("【カテゴリ別推奨】")

    # 基軸通貨
    base_coins = [r for r in results if r['category'] == '基軸通貨']
    if base_coins:
        print(f"• 基軸通貨: {base_coins[0]['name']} ({base_coins[0]['symbol']})")
        print(f"  → 安定性重視の投資に最適")

    # ミームコイン
    meme_coins = [r for r in results if r['category'] == 'ミームコイン']
    if meme_coins:
        print(f"• ミームコイン: {meme_coins[0]['name']} ({meme_coins[0]['symbol']})")
        print(f"  → 高リスク・高リターン志向の投資に適合")

    # 将来性銘柄
    future_coins = [r for r in results if r['category'] == '将来性']
    if future_coins:
        print(f"• 将来性銘柄: {future_coins[0]['name']} ({future_coins[0]['symbol']})")
        print(f"  → 技術力と成長性を重視した中長期投資に推奨")

    print()

    print("="*80)
    print("⚠️  投資上の注意事項")
    print("="*80)
    print()
    print("1. このレポートはニュース影響力スコアに基づく分析であり、")
    print("   投資助言ではありません。")
    print("2. 仮想通貨投資は高いリスクを伴います。")
    print("3. 投資判断は自己責任で行い、余剰資金の範囲内で行ってください。")
    print("4. 複数銘柄への分散投資を推奨します。")
    print()

    print("="*80)
    print("📝 詳細な個別銘柄レポート")
    print("="*80)
    print()
    print("各銘柄の詳細なインテリジェンスレポートは以下に保存されています：")
    print("analysis/intelligence_reports/")
    print()
    print("最新レポート一覧：")

    import os
    reports_dir = os.path.join(os.path.dirname(__file__), 'analysis', 'intelligence_reports')
    if os.path.exists(reports_dir):
        reports = sorted([f for f in os.listdir(reports_dir) if f.endswith('.md')], reverse=True)
        for report in reports[:10]:  # 最新10件
            print(f"  - {report}")

    print()
    print("="*80)
    print("分析完了")
    print("="*80)

    db.close()


if __name__ == '__main__':
    main()
