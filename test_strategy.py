"""
戦略テスト（絵文字なし版）
"""
import sys
sys.path.append('.')

from strategies.momentum import MomentumStrategy

print("モメンタム戦略をテスト中...\n")

strategy = MomentumStrategy()

# BTCをチェック
print("="*50)
print("BTCUSDTを分析")
print("="*50)

result = strategy.check_buy_signal('BTCUSDT')
print(f"価格: ${result.get('price', 'N/A')}")
print(f"モメンタム: {result.get('momentum', 0):.2f}%")
print(f"ROC: {result.get('roc', 0):.2f}%")
print(f"24時間変動: {result.get('price_change_24h', 0):.2f}%")
print(f"\n買いシグナル: {'あり' if result['signal'] else 'なし'}")
print(f"理由: {result['reason']}\n")

# 市場スキャン
print("="*50)
print("市場全体をスキャン（min_volume=50000）")
print("="*50)

signals = strategy.scan_market(min_volume_usdt=50000)

if signals:
    print(f"\n{len(signals)}個の買いシグナルを発見！\n")
    for i, sig in enumerate(signals[:5], 1):
        print(f"{i}. {sig['symbol']}: モメンタム {sig['momentum']:.2f}%, "
              f"24h変動 {sig['price_change_24h']:.2f}%")
else:
    print("\n買いシグナルなし")
    print("※条件が厳しい可能性があります")

print("\n完了")
