"""
指標プラグインシステムのデモ

新しい指標を追加する流れを実演
"""

import sys
import os
import io

# UTF-8出力設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.indicators import load_all_indicators, calculate_indicator
from data.timeseries_storage import TimeSeriesStorage


def main():
    print()
    print("=" * 80)
    print("🎯 指標プラグインシステム デモ")
    print("=" * 80)
    print()

    # 1. 利用可能な指標を確認
    print("【ステップ1】利用可能な指標を確認")
    print()

    indicators = load_all_indicators()

    print(f"✓ ロードされた指標数: {len(indicators)}")
    print()

    for indicator_id, info in indicators.items():
        print(f"📊 {info['name']} ({indicator_id})")
        print(f"   {info['description']}")
        print(f"   デフォルトパラメータ: {info['default_params']}")
        print()

    # 2. データを読み込み
    print()
    print("=" * 80)
    print("【ステップ2】BTCデータを読み込み")
    print("=" * 80)
    print()

    storage = TimeSeriesStorage()
    df = storage.load_price_data('BTC', '1d')

    if df is None or df.empty:
        print("⚠️ データが見つかりません")
        print("まずデータを収集してください:")
        print("  python data/detailed_data_collector.py BTC --all-intervals")
        print("  python data/timeseries_storage.py --migrate")
        return

    print(f"✓ データ読み込み成功")
    print(f"  期間: {df.index[0]} ～ {df.index[-1]}")
    print(f"  データ数: {len(df)}行")
    print()

    # 3. 各指標を計算
    print()
    print("=" * 80)
    print("【ステップ3】各指標を計算")
    print("=" * 80)
    print()

    # ストキャスティクス
    print("📈 ストキャスティクス")
    stoch = calculate_indicator('stochastic', df, k_period=14, d_period=3)
    print(stoch.tail(5))
    print()
    print(f"  現在の%K: {stoch['stoch_k'].iloc[-1]:.2f}")
    print(f"  現在の%D: {stoch['stoch_d'].iloc[-1]:.2f}")
    if stoch['stoch_k'].iloc[-1] > 80:
        print("  → 買われすぎ")
    elif stoch['stoch_k'].iloc[-1] < 20:
        print("  → 売られすぎ")
    else:
        print("  → 中立")
    print()

    # ATR
    print("📊 ATR（Average True Range）")
    atr = calculate_indicator('atr', df, period=14)
    print(atr.tail(5))
    print()
    print(f"  現在のATR: ${atr.iloc[-1]:,.2f}")
    print(f"  → ボラティリティ: {'高' if atr.iloc[-1] > atr.mean() else '低'}")
    print()

    # OBV
    print("📉 OBV（On Balance Volume）")
    obv = calculate_indicator('obv', df)
    print(obv.tail(5))
    print()

    # OBVのトレンド判定
    obv_trend = "上昇" if obv.iloc[-1] > obv.iloc[-5] else "下降"
    print(f"  現在のOBV: {obv.iloc[-1]:,.0f}")
    print(f"  5日前と比較: {obv_trend}トレンド")
    print()

    # 4. まとめ
    print()
    print("=" * 80)
    print("【まとめ】新しい指標の追加方法")
    print("=" * 80)
    print()
    print("1. analysis/indicators/my_indicator.py を作成")
    print("2. calculate() 関数を定義")
    print("3. メタデータを設定（INDICATOR_NAME, INDICATOR_DESCRIPTION, DEFAULT_PARAMS）")
    print("4. 自動的に使える！")
    print()
    print("詳細は analysis/indicators/README.md を参照")
    print()


if __name__ == '__main__':
    main()
