"""
ATR（Average True Range）指標

ボラティリティ（価格変動の大きさ）を測定
"""

import pandas as pd
import numpy as np


def calculate(df, period=14, **kwargs):
    """
    ATR（Average True Range）を計算

    Args:
        df: pandas DataFrame（high, low, close が必要）
        period: ATRの期間（デフォルト: 14）

    Returns:
        Series: ATR値
    """
    # True Range の計算
    # TR = max(high - low, abs(high - 前日close), abs(low - 前日close))

    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # ATR = TRの移動平均
    atr = true_range.rolling(window=period).mean()

    return atr


# メタデータ
INDICATOR_NAME = "ATR（Average True Range）"
INDICATOR_DESCRIPTION = "ボラティリティを測定（値が大きいほど価格変動が激しい）"
DEFAULT_PARAMS = {
    "period": 14
}
