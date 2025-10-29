"""
ストキャスティクス指標

買われすぎ・売られすぎを判定する指標
"""

import pandas as pd


def calculate(df, k_period=14, d_period=3, **kwargs):
    """
    ストキャスティクス（%K, %D）を計算

    Args:
        df: pandas DataFrame（high, low, close が必要）
        k_period: %K の期間（デフォルト: 14）
        d_period: %D の期間（デフォルト: 3）

    Returns:
        DataFrame: %K と %D の列を含む
    """
    # 最高値・最安値
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()

    # %K = (現在価格 - n日間の最安値) / (n日間の最高値 - n日間の最安値) * 100
    k = 100 * (df['close'] - low_min) / (high_max - low_min)

    # %D = %Kのn日移動平均
    d = k.rolling(window=d_period).mean()

    result = pd.DataFrame({
        'stoch_k': k,
        'stoch_d': d
    }, index=df.index)

    return result


# メタデータ
INDICATOR_NAME = "ストキャスティクス"
INDICATOR_DESCRIPTION = "買われすぎ・売られすぎを判定（%K > 80: 買われすぎ、%K < 20: 売られすぎ）"
DEFAULT_PARAMS = {
    "k_period": 14,
    "d_period": 3
}
