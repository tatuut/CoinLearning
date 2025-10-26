"""
ETHとXRPのインテリジェンス分析テスト

基軸通貨の残り2つの分析を実行
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.intelligence_system import IntelligenceSystem
from datetime import datetime


# ETHニュースデータ（WebSearch結果から構造化）
eth_news_data = [
    {
        'title': 'イーサリアム、Pectraアップグレード実装で機能強化（2025年5月）',
        'content': '2025年5月に実装された「ペクトラ」アップグレードにより、32ETHの閾値撤廃やバリデータ上限の拡大が実現し、ステーキングの効率が向上しました。このアップグレードはアカウント抽象化によるUX向上やL2手数料の削減など、ネットワークの機能強化に大きく貢献しています。',
        'source': 'CoinPost',
        'url': 'https://coinpost.jp/ethereum-pectra-upgrade',
        'published_date': '2025-05-15T10:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.9,
        'impact_score': 0.85,
        'keywords': ['ETH', 'Ethereum', 'Pectra', 'アップグレード', 'ステーキング'],
    },
    {
        'title': 'イーサリアムを財務資産として保有する企業が世界的に急増',
        'content': '2025年、イーサリアム（ETH）を財務資産として保有する企業が世界的に急増しており、企業の中長期戦略において「インフラ資産」として位置づけられ始めています。これは機関投資家によるイーサリアムへの信頼が高まっていることを示しています。',
        'source': 'CoinDesk Japan',
        'url': 'https://www.coindeskjapan.com/eth-corporate-adoption',
        'published_date': '2025-09-20T14:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.85,
        'impact_score': 0.9,
        'keywords': ['ETH', '企業', '財務資産', '機関投資家', '採用'],
    },
    {
        'title': 'アーサー・ヘイズ氏「イーサリアムは年末までに1万ドルに到達」',
        'content': '海外仮想通貨取引所BitMEXの共同創業者であるアーサー・ヘイズ氏は、2025年7月23日に「イーサリアムは年末までに1万ドルに到達する」との予想を投稿しました。現在の価格は約4,185ドル（約618,000円）で推移しています。',
        'source': 'BitMEX',
        'url': 'https://bitmex.com/eth-prediction-10k',
        'published_date': '2025-07-23T16:00:00',
        'sentiment': 'positive',
        'importance_score': 0.75,
        'impact_score': 0.7,
        'keywords': ['ETH', '価格予想', '1万ドル', 'アーサー・ヘイズ'],
    },
    {
        'title': 'ブラックロック、利回り付きETH ETFについてSECと協議中',
        'content': 'ブラックロックなどがSECと協議中で、利回り付きETFの誕生が現実味を帯びています。これが実現すれば、イーサリアムへの機関投資家の資金流入がさらに加速すると期待されています。',
        'source': 'BlackRock News',
        'url': 'https://blackrock.com/eth-yield-etf',
        'published_date': '2025-08-10T11:00:00',
        'sentiment': 'positive',
        'importance_score': 0.9,
        'impact_score': 0.85,
        'keywords': ['ETH', 'ETF', '利回り', 'ブラックロック', 'SEC'],
    },
    {
        'title': 'イーサリアムの現物ETFが米SECに承認（2024年5月）',
        'content': '2024年5月24日には米SECが現物ETFの承認をしており高値を更新し、仮想通貨に友好的なドナルドトランプ氏が米大統領に返り咲いた影響もあり、60万円台で取引されていました。',
        'source': 'SEC News',
        'url': 'https://sec.gov/eth-etf-approval',
        'published_date': '2024-05-24T09:00:00',
        'sentiment': 'very_positive',
        'importance_score': 1.0,
        'impact_score': 0.95,
        'keywords': ['ETH', 'ETF', '承認', 'SEC'],
    },
]


# XRPニュースデータ（WebSearch結果から構造化）
xrp_news_data = [
    {
        'title': 'リップル対SEC、5年の法廷闘争に終止符（2025年8月）',
        'content': 'リップル社と米証券取引委員会（SEC）との間で約5年間に及んだ法廷闘争が終結しました。現在はSECとの裁判も終結されたとの見方が多く、過去高値を更新しています。規制面での不透明感が解消されたことで、今後の事業展開や機関投資家からの資金流入が期待されています。',
        'source': '日本経済新聞',
        'url': 'https://www.nikkei.com/ripple-sec-settlement',
        'published_date': '2025-08-08T10:00:00',
        'sentiment': 'very_positive',
        'importance_score': 1.0,
        'impact_score': 0.95,
        'keywords': ['XRP', 'Ripple', 'SEC', '裁判', '終結'],
    },
    {
        'title': 'XRP、7年ぶりに3ドル突破（2025年1月）',
        'content': '2025年はポジティブなニュースが続き、7年ぶりに最高値を更新するなど話題性のある通貨です。2025年1月16日に2018年以来初めて3ドルを突破しました。',
        'source': 'CoinPost',
        'url': 'https://coinpost.jp/xrp-3dollar-breakthrough',
        'published_date': '2025-01-16T14:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.85,
        'impact_score': 0.9,
        'keywords': ['XRP', '3ドル', '最高値', '突破'],
    },
    {
        'title': 'リップルCTO デヴィッド・シュワルツ氏、年末で日常業務から退任',
        'content': '2025年10月1日、リップルのCTO（最高技術責任者）でありXRP Ledger（XRPL）の中心的人物でもあったデヴィッド・シュワルツ氏が、年末をもって日常業務から退くと発表しました。ただし、彼は名誉的役職として取締役会に残る予定です。',
        'source': 'Ripple Official',
        'url': 'https://ripple.com/cto-retirement-announcement',
        'published_date': '2025-10-01T09:00:00',
        'sentiment': 'neutral',
        'importance_score': 0.7,
        'impact_score': 0.6,
        'keywords': ['XRP', 'Ripple', 'CTO', 'デヴィッド・シュワルツ', '退任'],
    },
    {
        'title': 'XRP先物ETFがナスダックに上場（2025年8月）',
        'content': '2025年8月、ETF運用会社「VolatilityShares」が、XRPを対象とした先物ETFをナスダックに上場しました。これは機関投資家がXRPにアクセスしやすくなることを意味し、今後の資金流入が期待されています。',
        'source': 'NASDAQ News',
        'url': 'https://nasdaq.com/xrp-futures-etf',
        'published_date': '2025-08-20T11:00:00',
        'sentiment': 'positive',
        'importance_score': 0.9,
        'impact_score': 0.85,
        'keywords': ['XRP', 'ETF', '先物', 'ナスダック', '上場'],
    },
    {
        'title': 'リップル、国際送金での実用化を推進',
        'content': 'リップルは国際送金での利用に長けた仮想通貨（暗号資産）であり、さまざまな金融機関や企業と提携して、送金手段としての実用化を進めています。規制面での不透明感が解消されたことで、今後の事業展開が加速すると期待されています。',
        'source': 'Ripple News',
        'url': 'https://ripple.com/international-payment-adoption',
        'published_date': '2025-09-15T13:00:00',
        'sentiment': 'positive',
        'importance_score': 0.8,
        'impact_score': 0.75,
        'keywords': ['XRP', 'Ripple', '国際送金', '実用化', '金融機関'],
    },
]


def main():
    print("="*60)
    print("ETH & XRP - 統合インテリジェンス分析")
    print("="*60)

    system = IntelligenceSystem()

    # ETH分析実行
    print("\n\n" + "="*60)
    print("[1/2] Ethereum (ETH) の分析")
    print("="*60)
    eth_result = system.execute_full_analysis(
        symbol='ETH',
        name='Ethereum',
        news_data=eth_news_data
    )

    if eth_result.get('report'):
        eth_filepath = system.save_report_to_file(eth_result['report'], 'ETH')
        print(f"\n[OK] ETHレポート保存: {eth_filepath}")

    # XRP分析実行
    print("\n\n" + "="*60)
    print("[2/2] XRP (Ripple) の分析")
    print("="*60)
    xrp_result = system.execute_full_analysis(
        symbol='XRP',
        name='Ripple',
        news_data=xrp_news_data
    )

    if xrp_result.get('report'):
        xrp_filepath = system.save_report_to_file(xrp_result['report'], 'XRP')
        print(f"\n[OK] XRPレポート保存: {xrp_filepath}")

    system.close()

    # 結果サマリー
    print("\n\n" + "="*60)
    print("分析完了サマリー")
    print("="*60)
    print(f"\n[ETH] 平均スコア: {eth_result['scoring_result']['avg_final_score']:.3f}")
    print(f"      最高スコア: {eth_result['scoring_result']['max_final_score']:.3f}")
    print(f"      ニュース件数: {eth_result['scoring_result']['news_count']}")

    print(f"\n[XRP] 平均スコア: {xrp_result['scoring_result']['avg_final_score']:.3f}")
    print(f"      最高スコア: {xrp_result['scoring_result']['max_final_score']:.3f}")
    print(f"      ニュース件数: {xrp_result['scoring_result']['news_count']}")

    print("\n[OK] 基軸通貨（BTC, ETH, XRP）の分析が完了しました！")


if __name__ == '__main__':
    main()
