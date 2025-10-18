"""
MEXC API動作テスト
"""

from config.exchange_api import MEXCAPI
import traceback

print("="*60)
print("MEXC API テスト開始")
print("="*60)

try:
    api = MEXCAPI()

    # テスト1: BTC価格取得
    print("\n[TEST 1] BTC価格を取得...")
    price = api.get_price('BTCUSDT')
    if price:
        print(f"  [OK] BTC Price: ${price:,.2f}")
    else:
        print("  [NG] Price is None")

    # テスト2: 24時間統計取得
    print("\n[TEST 2] SHIB 24時間統計を取得...")
    stats = api.get_24h_stats('SHIBUSDT')
    if stats:
        print(f"  [OK] SHIB/USDT:")
        print(f"       Price: ${stats['price']:.8f}")
        print(f"       Change: {stats['price_change_percent']:+.2f}%")
        print(f"       Volume: ${stats['quote_volume']:,.0f}")
    else:
        print("  [NG] Stats is None")

    # テスト3: トレンドコイン取得
    print("\n[TEST 3] トレンドコインを取得（トップ5）...")
    trending = api.get_trending_coins(min_volume_usdt=1000000)
    if trending:
        print(f"  [OK] Found {len(trending)} coins")
        for i, coin in enumerate(trending[:5], 1):
            print(f"       {i}. {coin['symbol']}: ${coin['price']:.8f} ({coin['change_percent']:+.2f}%)")
    else:
        print("  [NG] Trending is empty")

    print("\n" + "="*60)
    print("[OK] 全てのテスト完了！")
    print("="*60)

except Exception as e:
    print(f"\n[NG] Exception: {e}")
    traceback.print_exc()
