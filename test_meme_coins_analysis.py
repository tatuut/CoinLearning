"""
人気草コイン（DOGE, SHIB, PEPE）のインテリジェンス分析テスト

ミームコインの将来性を評価
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.intelligence_system import IntelligenceSystem
from datetime import datetime


# DOGEニュースデータ（WebSearch結果から構造化）
doge_news_data = [
    {
        'title': 'ドージコイン現物ETFが米国で初承認（2025年9月）',
        'content': '2025年9月には、レックス・シェアーズとオスプレー・ファンドによる米国初のドージコイン現物ETFが承認され、株式市場からの資金流入による価格や信頼性向上が期待されています。これはドージコインにとって歴史的な出来事であり、機関投資家の参入を促進する重要な一歩となります。',
        'source': 'SEC News',
        'url': 'https://sec.gov/doge-etf-approval',
        'published_date': '2025-09-15T10:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.95,
        'impact_score': 0.9,
        'keywords': ['DOGE', 'Dogecoin', 'ETF', '承認', '現物ETF'],
    },
    {
        'title': 'トランプ政権、政府効率化省（D.O.G.E.）にマスク氏を起用',
        'content': 'トランプ大統領が政府効率化省（Department of Government Efficiency: D.O.G.E.）の立ち上げを提唱し、マスク氏を主導者に起用したことで、ドージコインへの注目が集まっています。この政府効率化省は頭文字を取って「DOGE」とも呼ばれ、公式サイトにはドージコインをモチーフとしたロゴが掲載されるなど、ドージコインとの関連性が強調されています。',
        'source': 'Government News',
        'url': 'https://whitehouse.gov/doge-department',
        'published_date': '2025-02-01T09:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.9,
        'impact_score': 0.95,
        'keywords': ['DOGE', 'イーロン・マスク', 'トランプ', '政府'],
    },
    {
        'title': 'X Money（旧Twitter）決済機能、2025年内に追加予定',
        'content': 'XのCEOであるリンダ・ヤッカリーノ氏は、「Xマネー（X Money）」と呼ばれる決済機能を2025年内に追加する計画を明らかにしており、暗号資産を含む複数の決済手段に対応すると予測されています。市場ではX Moneyにドージコインが決済手段として統合されるのではないかという憶測が根強く、実現すれば価格を押し上げる最大の触媒になると見なされています。',
        'source': 'X Corp News',
        'url': 'https://x.com/x-money-announcement',
        'published_date': '2025-06-15T14:00:00',
        'sentiment': 'positive',
        'importance_score': 0.85,
        'impact_score': 0.8,
        'keywords': ['DOGE', 'X Money', 'Twitter', '決済', 'イーロン・マスク'],
    },
    {
        'title': 'ドージコイン、時価総額でXRPを抜く（2025年）',
        'content': 'イーロン・マスク氏関連の取引が後押しし、ドージコインの時価総額がXRPを抜きました。2025年10月時点で時価総額ランキングでは8位にランクインし、1DOGEの価格は約34円となっています。時価総額は約4.95兆円に達しています。',
        'source': 'CoinDesk Japan',
        'url': 'https://www.coindeskjapan.com/doge-surpasses-xrp',
        'published_date': '2025-03-10T11:00:00',
        'sentiment': 'positive',
        'importance_score': 0.8,
        'impact_score': 0.85,
        'keywords': ['DOGE', 'XRP', '時価総額', 'ランキング'],
    },
    {
        'title': 'ドージコイン先物が新記録を樹立、2025年に1ドル超えの予想も',
        'content': 'ドージコインの先物取引が新記録を樹立しました。アナリストは2025年に1ドル超えの可能性を示唆しており、過去最高値の0.68ドル（約100円）を大きく上回る予測が出ています。イーロン・マスク氏の発言1つで一気に価格が高騰するケースも多い通貨です。',
        'source': 'CoinDesk Japan',
        'url': 'https://www.coindeskjapan.com/doge-futures-record',
        'published_date': '2025-08-05T16:00:00',
        'sentiment': 'positive',
        'importance_score': 0.75,
        'impact_score': 0.7,
        'keywords': ['DOGE', '先物', '価格予想', '1ドル'],
    },
]


# SHIBニュースデータ（WebSearch結果から構造化）
shib_news_data = [
    {
        'title': 'Shibarium、プラズマ・ブリッジ再稼働で安全性強化（2025年10月）',
        'content': '2025年10月、柴犬コインの独自ネットワーク「Shibarium」で大きな進展がありました。BONEトークン向けのプラズマ・ブリッジが再稼働し、以前のハッキング被害を受けて不正アドレスの遮断機能や7日間の出金遅延などの安全策が導入されています。これによりネットワークの信頼性が大幅に向上しました。',
        'source': 'Shibarium Official',
        'url': 'https://shibarium.shib.io/plasma-bridge',
        'published_date': '2025-10-05T10:00:00',
        'sentiment': 'positive',
        'importance_score': 0.85,
        'impact_score': 0.8,
        'keywords': ['SHIB', 'Shibarium', 'ブリッジ', 'セキュリティ'],
    },
    {
        'title': 'SHIB、UAE政府と提携を発表',
        'content': 'UAE政府との提携や決済システム「SHIB Pay」の発表など、実需を背景とした上昇余地を持つ段階に入っています。これはSHIBがミームコインから実用的なトークンへと進化していることを示す重要な一歩です。',
        'source': 'UAE Gov News',
        'url': 'https://uae.gov/shib-partnership',
        'published_date': '2025-07-20T14:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.9,
        'impact_score': 0.85,
        'keywords': ['SHIB', 'UAE', '提携', 'SHIB Pay', '決済'],
    },
    {
        'title': 'SHIB、約4,300万枚のバーン（焼却）を実施',
        'content': '同時期に約4,300万枚のSHIBが焼却（バーン）され、供給量を抑える動きも続いています。実際に2025年時点で累計1兆枚以上のSHIBが焼却済みとされており、今後も同様のペースで進めば価格へのプラス効果が期待されます。バーンシステムは、長期的に供給量を減らし、希少性を高める働きを持ちます。',
        'source': 'Shibburn',
        'url': 'https://shibburn.com/burn-statistics',
        'published_date': '2025-09-10T11:00:00',
        'sentiment': 'positive',
        'importance_score': 0.7,
        'impact_score': 0.75,
        'keywords': ['SHIB', 'バーン', '焼却', '供給量'],
    },
    {
        'title': 'SHIB、取引所から個人ウォレットへの移動増加',
        'content': '2025年10月現在、SHIBの一部が取引所から個人ウォレットに移動しており、長期保有の動きが強まっています。これは売り圧の減少につながり、需給バランスの改善に寄与しています。大口投資家による長期保有の意向が示されています。',
        'source': 'Whale Alert',
        'url': 'https://whale-alert.io/shib-movements',
        'published_date': '2025-10-08T09:00:00',
        'sentiment': 'positive',
        'importance_score': 0.65,
        'impact_score': 0.7,
        'keywords': ['SHIB', 'ウォレット', '長期保有', 'ホエール'],
    },
    {
        'title': 'SHIB、DeFi・NFT分野での活用拡大に期待',
        'content': '技術面と運営体制の改善は、利用者の信頼を回復させ、柴犬コインが「ミーム」から実用性を持つトークンへ進化するきっかけとなるでしょう。今後のDeFiやNFT分野での活用拡大にも期待が高まっています。Shibariumでの取引に応じて自動的にSHIBがバーン（焼却）される仕組みも導入されています。',
        'source': 'CoinPost',
        'url': 'https://coinpost.jp/shib-defi-nft',
        'published_date': '2025-08-15T13:00:00',
        'sentiment': 'positive',
        'importance_score': 0.75,
        'impact_score': 0.7,
        'keywords': ['SHIB', 'DeFi', 'NFT', '実用性'],
    },
]


# PEPEニュースデータ（WebSearch結果から構造化）
pepe_news_data = [
    {
        'title': 'Coincheck、国内初のPEPE取扱いを開始',
        'content': '国内で初めてPEPEの取扱いを始めた取引所であり、約500円という少額からPEPEを購入することができるCoincheckで取引が可能になりました。これにより日本の投資家がPEPEにアクセスしやすくなり、市場の流動性向上が期待されています。',
        'source': 'Coincheck',
        'url': 'https://coincheck.com/pepe-listing',
        'published_date': '2024-11-20T10:00:00',
        'sentiment': 'positive',
        'importance_score': 0.8,
        'impact_score': 0.75,
        'keywords': ['PEPE', 'Coincheck', '上場', '国内'],
    },
    {
        'title': 'PEPE、1週間で70%急騰（2025年）',
        'content': 'PEPEが1週間で70%急騰しました。アナリストは「月末に3倍」の可能性を予測しており、PEPE以外にもDOGEやSHIBなど主要なミームコインも多くが価格上昇を見せているなど、市況の盛り上がりが感じられます。',
        'source': 'CryptoDnes',
        'url': 'https://cryptodnes.bg/pepe-surge',
        'published_date': '2025-09-25T14:00:00',
        'sentiment': 'very_positive',
        'importance_score': 0.75,
        'impact_score': 0.85,
        'keywords': ['PEPE', '急騰', '70%', 'ミームコイン'],
    },
    {
        'title': 'PEPE、2025年はミーム以上の存在へ',
        'content': '2025年には、PEPEが単なるミームコイン以上の存在となり、市場の信頼を得た代表的な銘柄としての地位を確立する可能性が高いです。2025年は、PEPEの価格は0.000021ドルから0.000022ドルの範囲で着地すると予測されています。',
        'source': 'CryptoNews',
        'url': 'https://cryptonews.com/pepe-2025-outlook',
        'published_date': '2025-01-10T11:00:00',
        'sentiment': 'positive',
        'importance_score': 0.7,
        'impact_score': 0.65,
        'keywords': ['PEPE', '将来性', '2025年', '予測'],
    },
    {
        'title': 'PEPE、Pepe the Frogの人気で注目集まる',
        'content': 'PEPE（ぺぺコイン）は、2000年代初頭に流行したPepe the Frog（ぺぺザフロッグ）というカエルのキャラクターをロゴにしたコインであり、最近注目を集めている。このコインは2023年4月17日に発行され、同年5月5日にバイナンスに上場された際には急激な価格上昇を記録した。',
        'source': 'Diamond ZAi',
        'url': 'https://diamond.jp/crypto/pepe',
        'published_date': '2023-05-05T09:00:00',
        'sentiment': 'positive',
        'importance_score': 0.65,
        'impact_score': 0.7,
        'keywords': ['PEPE', 'Pepe the Frog', 'ミームコイン', 'バイナンス'],
    },
    {
        'title': 'PEPE価格予想：2025年は0.000021～0.000022ドル',
        'content': '2025年は、PEPEの価格は0.000021ドルから0.000022ドルの範囲で着地すると予測されています。ただし、ペペコインに本質的な価値はなく、保有しても金銭的なリターンは得られない。そのため、投機目的に多くの投資家から資金が集まっている状況が終われば、無価値になってしまうリスクを持っているとされています。',
        'source': 'BTCC',
        'url': 'https://www.btcc.com/pepe-price-prediction',
        'published_date': '2025-07-01T13:00:00',
        'sentiment': 'neutral',
        'importance_score': 0.6,
        'impact_score': 0.55,
        'keywords': ['PEPE', '価格予想', 'リスク'],
    },
]


def main():
    print("="*60)
    print("人気草コイン（DOGE, SHIB, PEPE）- 統合インテリジェンス分析")
    print("="*60)

    system = IntelligenceSystem()

    # DOGE分析実行
    print("\n\n" + "="*60)
    print("[1/3] Dogecoin (DOGE) の分析")
    print("="*60)
    doge_result = system.execute_full_analysis(
        symbol='DOGE',
        name='Dogecoin',
        news_data=doge_news_data
    )

    if doge_result.get('report'):
        doge_filepath = system.save_report_to_file(doge_result['report'], 'DOGE')
        print(f"\n[OK] DOGEレポート保存: {doge_filepath}")

    # SHIB分析実行
    print("\n\n" + "="*60)
    print("[2/3] Shiba Inu (SHIB) の分析")
    print("="*60)
    shib_result = system.execute_full_analysis(
        symbol='SHIB',
        name='Shiba Inu',
        news_data=shib_news_data
    )

    if shib_result.get('report'):
        shib_filepath = system.save_report_to_file(shib_result['report'], 'SHIB')
        print(f"\n[OK] SHIBレポート保存: {shib_filepath}")

    # PEPE分析実行
    print("\n\n" + "="*60)
    print("[3/3] Pepe (PEPE) の分析")
    print("="*60)
    pepe_result = system.execute_full_analysis(
        symbol='PEPE',
        name='Pepe',
        news_data=pepe_news_data
    )

    if pepe_result.get('report'):
        pepe_filepath = system.save_report_to_file(pepe_result['report'], 'PEPE')
        print(f"\n[OK] PEPEレポート保存: {pepe_filepath}")

    system.close()

    # 結果サマリー
    print("\n\n" + "="*60)
    print("分析完了サマリー")
    print("="*60)
    print(f"\n[DOGE] 平均スコア: {doge_result['scoring_result']['avg_final_score']:.3f}")
    print(f"       最高スコア: {doge_result['scoring_result']['max_final_score']:.3f}")
    print(f"       ニュース件数: {doge_result['scoring_result']['news_count']}")

    print(f"\n[SHIB] 平均スコア: {shib_result['scoring_result']['avg_final_score']:.3f}")
    print(f"       最高スコア: {shib_result['scoring_result']['max_final_score']:.3f}")
    print(f"       ニュース件数: {shib_result['scoring_result']['news_count']}")

    print(f"\n[PEPE] 平均スコア: {pepe_result['scoring_result']['avg_final_score']:.3f}")
    print(f"       最高スコア: {pepe_result['scoring_result']['max_final_score']:.3f}")
    print(f"       ニュース件数: {pepe_result['scoring_result']['news_count']}")

    print("\n[OK] 人気草コイン（DOGE, SHIB, PEPE）の分析が完了しました！")


if __name__ == '__main__':
    main()
