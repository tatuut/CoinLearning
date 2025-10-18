"""
OBV（On Balance Volume）指標

出来高を使って価格トレンドの強さを測定
"""

import pandas as pd


def calculate(df, **kwargs):
    """
    OBV（On Balance Volume）を計算

    価格が上昇した日は出来高を加算、
    下落した日は出来高を減算

    Args:
        df: pandas DataFrame（close, volume が必要）

    Returns:
        Series: OBV値
    """
    # 価格変化
    price_change = df['close'].diff()

    # 出来高の方向付け
    # 上昇 → +volume
    # 下落 → -volume
    # 変化なし → 0
    signed_volume = df['volume'].copy()
    signed_volume[price_change < 0] = -signed_volume[price_change < 0]
    signed_volume[price_change == 0] = 0

    # 累積出来高
    obv = signed_volume.cumsum()

    return obv


# メタデータ
INDICATOR_NAME = "OBV（On Balance Volume）"
INDICATOR_DESCRIPTION = "出来高でトレンドの強さを測定（上昇トレンド時はOBVも上昇）"
DEFAULT_PARAMS = {}
