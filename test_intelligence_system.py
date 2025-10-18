"""
統合インテリジェンスシステムのテスト

BTC, ETH, XRPのニュースを収集してスコアリング
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.intelligence_system import IntelligenceSystem
from datetime import datetime


# BTCニュースデータ（WebSearch結果から構造化）
btc_news_data = [
    {
        'title': 'ビットコインが史上最高値$126,286を記録（2025年10月）',
        'content': '2025年10月、連邦準備制度理事会の初めての利下げに続き、BTCは126,286ドルの新しい史上最高値を記録しました。10月1日時点で、ビットコインは$111,900前後で推移しており、世界の暗号資産時価総額は3.96兆ドル、ビットコインドミナンスは約58.5%を記録しています。',
        'source': 'CryptoMarket News',
        'url': 'https://example.com/btc-ath-2025',
        'published_date': '2025-10-15T10:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.9,
        'impact_score': 0.95,
        'keywords': ['BTC', 'bitcoin', '最高値', '史上最高値', 'ATH', '126286'],
    },
    {
        'title': 'ビットコインETFに過去最大の35.5億ドル流入',
        'content': '2025年10月7日までの週次データによると、世界の仮想通貨関連ETFには過去最大の59.5億ドルが流入し、そのうちビットコインETFへの流入は35.5億ドルに達しました。これは機関投資家の参入が加速していることを示しています。',
        'source': 'ETF Tracker',
        'url': 'https://example.com/btc-etf-inflow',
        'published_date': '2025-10-08T14:30:00',
        'sentiment': 'positive',
        'importance_score': 0.85,
        'impact_score': 0.9,
        'keywords': ['BTC', 'ETF', '流入', '機関投資家', '35.5億ドル'],
    },
    {
        'title': 'CryptoQuant: ビットコイン2025年目標価格は$145,000～$249,000',
        'content': 'CryptoQuantは、2025年のビットコイン（BTC）の目標価格は14万5,000ドル（約2,268万円）から24万9,000ドル（約3,894万円）との見方を示した。2025年末までに、ビットコインは約150,000ドルの新記録を達成すると予想されています。',
        'source': 'CryptoQuant',
        'url': 'https://example.com/btc-price-prediction',
        'published_date': '2025-10-05T09:00:00',
        'sentiment': 'positive',
        'importance_score': 0.8,
        'impact_score': 0.75,
        'keywords': ['BTC', '価格予想', '145000', '249000', 'CryptoQuant'],
    },
    {
        'title': 'ビットコイン、10年で100倍成長の可能性',
        'content': '2025年10月、IQ276とされる投資家のYoungHoon Kim氏が、ビットコインは今後10年で100倍に成長すると大胆に予測しました。10年後の2034年の高価格の予想はPricePredictionが円換算で1BTCが約7.7億円と分析しています。',
        'source': 'Investment Analysis',
        'url': 'https://example.com/btc-10year-prediction',
        'published_date': '2025-10-12T16:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.7,
        'impact_score': 0.6,
        'keywords': ['BTC', '長期予想', '100倍', '10年'],
    },
    {
        'title': 'ビットコイン、日足レベルで上昇トレンド形成',
        'content': '2025年10月6日現在、ビットコインは日足レベルで上昇トレンドを形成しており、価格は1864万3000円付近で推移している状況です。10月と11月は歴史的に強い月として、非常に期待がされています。',
        'source': 'Technical Analysis',
        'url': 'https://example.com/btc-trend-analysis',
        'published_date': '2025-10-06T11:00:00',
        'sentiment': 'positive',
        'importance_score': 0.6,
        'impact_score': 0.65,
        'keywords': ['BTC', '上昇トレンド', 'テクニカル分析'],
    },
]


def main():
    # Windows環境でのUnicodeエラーを回避
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("="*60)
    print("統合インテリジェンスシステム - 実戦テスト")
    print("="*60)

    system = IntelligenceSystem()

    # BTC分析実行
    print("\n[*] Bitcoin (BTC) の完全分析を実行...")
    result = system.execute_full_analysis(
        symbol='BTC',
        name='Bitcoin',
        news_data=btc_news_data
    )

    # レポート保存
    if result.get('report'):
        filepath = system.save_report_to_file(result['report'], 'BTC')
        print(f"\n[OK] レポート保存完了: {filepath}")

        # レポート内容を表示
        print("\n" + "="*60)
        print("生成されたレポート:")
        print("="*60)
        print(result['report'])

    system.close()

    print("\n[OK] テスト完了！")


if __name__ == '__main__':
    main()
