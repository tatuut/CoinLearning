# 📊 技術指標プラグインシステム

## 🎯 概要

このディレクトリに新しい指標ファイルを追加するだけで、
自動的に分析システムに統合されます。

**プログラミング知識がある人なら、誰でも簡単に指標を追加できます！**

---

## 🚀 使い方

### 1. 既存の指標を使う

```python
from analysis.indicators import calculate_indicator, get_indicator_list
from data.timeseries_storage import TimeSeriesStorage

# 利用可能な指標を確認
indicators = get_indicator_list()
for id, name, desc in indicators:
    print(f"{name} ({id}): {desc}")

# データを読み込み
storage = TimeSeriesStorage()
df = storage.load_price_data('BTC', '1d')

# 指標を計算
result = calculate_indicator('stochastic', df, k_period=14, d_period=3)
print(result.tail())
```

### 2. 新しい指標を追加する

#### ステップ1: ファイルを作成

`analysis/indicators/my_indicator.py` を作成：

```python
"""
あなたの指標の説明
"""

import pandas as pd
import numpy as np


def calculate(df, param1=10, param2=20, **kwargs):
    """
    指標を計算する関数

    Args:
        df: pandas DataFrame（OHLCV データ）
        param1: パラメータ1の説明
        param2: パラメータ2の説明

    Returns:
        計算結果（Series または DataFrame）
    """
    # ここに計算ロジックを書く
    result = df['close'].rolling(window=param1).mean()

    return result


# メタデータ（必須）
INDICATOR_NAME = "あなたの指標名"
INDICATOR_DESCRIPTION = "指標の簡単な説明"
DEFAULT_PARAMS = {
    "param1": 10,
    "param2": 20
}
```

#### ステップ2: 自動的に使える！

```python
from analysis.indicators import calculate_indicator

# すぐに使える！
result = calculate_indicator('my_indicator', df)
```

**それだけ！** コードの変更やインポートの追加は不要です。

---

## 📚 既存の指標

### 1. ストキャスティクス（stochastic）

**説明**: 買われすぎ・売られすぎを判定

**パラメータ**:
- `k_period`: %Kの期間（デフォルト: 14）
- `d_period`: %Dの期間（デフォルト: 3）

**使い方**:
```python
result = calculate_indicator('stochastic', df, k_period=14, d_period=3)
# result は DataFrame で、'stoch_k' と 'stoch_d' 列を含む
```

**解釈**:
- %K > 80: 買われすぎ
- %K < 20: 売られすぎ
- %Kが%Dを上抜け: 買いシグナル
- %Kが%Dを下抜け: 売りシグナル

---

### 2. ATR（atr）

**説明**: Average True Range - ボラティリティを測定

**パラメータ**:
- `period`: ATRの期間（デフォルト: 14）

**使い方**:
```python
atr = calculate_indicator('atr', df, period=14)
# atr は Series
```

**解釈**:
- 値が大きい → 価格変動が激しい（ボラティリティ高）
- 値が小さい → 価格変動が穏やか（ボラティリティ低）

---

### 3. OBV（obv）

**説明**: On Balance Volume - 出来高でトレンドの強さを測定

**パラメータ**: なし

**使い方**:
```python
obv = calculate_indicator('obv', df)
# obv は Series
```

**解釈**:
- OBVが上昇 → 上昇トレンドが強い
- OBVが下降 → 下降トレンドが強い
- OBVと価格のダイバージェンス → トレンド転換の兆候

---

## 🔧 必須要件

### calculate関数

- **引数**: 第1引数は必ず `df`（pandas DataFrame）
- **返り値**: pandas Series または DataFrame
- **パラメータ**: `**kwargs` で追加パラメータを受け取る

### メタデータ

必ず以下を定義：

```python
INDICATOR_NAME = "指標名"
INDICATOR_DESCRIPTION = "説明"
DEFAULT_PARAMS = {"param1": value1, "param2": value2}
```

---

## 📊 データフレームの構造

渡される `df` には以下の列が含まれます：

```python
df.columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
df.index = DatetimeIndex  # 時系列データ
```

---

## 💡 指標追加の例

### 例1: シンプルな移動平均

```python
"""Simple Moving Average"""

def calculate(df, period=20, **kwargs):
    return df['close'].rolling(window=period).mean()

INDICATOR_NAME = "単純移動平均"
INDICATOR_DESCRIPTION = "指定期間の平均価格"
DEFAULT_PARAMS = {"period": 20}
```

### 例2: 複数の値を返す指標

```python
"""Bollinger Bands"""

import pandas as pd

def calculate(df, period=20, std_dev=2, **kwargs):
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()

    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)

    return pd.DataFrame({
        'bb_middle': sma,
        'bb_upper': upper,
        'bb_lower': lower
    }, index=df.index)

INDICATOR_NAME = "ボリンジャーバンド"
INDICATOR_DESCRIPTION = "価格のバンド（中央、上限、下限）"
DEFAULT_PARAMS = {"period": 20, "std_dev": 2}
```

### 例3: 複雑な計算

```python
"""MACD"""

import pandas as pd

def calculate(df, fast=12, slow=26, signal=9, **kwargs):
    ema_fast = df['close'].ewm(span=fast).mean()
    ema_slow = df['close'].ewm(span=slow).mean()

    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line

    return pd.DataFrame({
        'macd': macd,
        'macd_signal': signal_line,
        'macd_hist': histogram
    }, index=df.index)

INDICATOR_NAME = "MACD"
INDICATOR_DESCRIPTION = "移動平均収束拡散法"
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}
```

---

## 🧪 テスト方法

### 方法1: システムテストで確認

```bash
python tests/test_all.py
```

「指標プラグイン」セクションで新しい指標が表示されます。

### 方法2: 直接テスト

```python
from analysis.indicators import calculate_indicator
from data.timeseries_storage import TimeSeriesStorage

storage = TimeSeriesStorage()
df = storage.load_price_data('BTC', '1d')

# あなたの指標をテスト
result = calculate_indicator('your_indicator', df)
print(result.tail())
```

---

## 📖 参考リソース

### 一般的な技術指標

- **トレンド系**: SMA, EMA, MACD, ADX, Parabolic SAR
- **オシレーター系**: RSI, Stochastic, CCI, Williams %R
- **ボラティリティ系**: Bollinger Bands, ATR, Keltner Channel
- **出来高系**: OBV, CMF, VWAP, A/D Line

### 実装のヒント

1. **pandas操作**: `rolling()`, `ewm()`, `shift()`, `diff()` を活用
2. **欠損値処理**: 計算結果の最初の数行は NaN になることが多い
3. **型変換**: 必要に応じて `astype()` で型を変換
4. **パフォーマンス**: 大量データの場合は NumPy を使う

---

## 🚀 今後の拡張

このプラグインシステムにより、以下が可能になります：

- [ ] カスタム指標のライブラリ構築
- [ ] コミュニティによる指標の共有
- [ ] バックテストシステムとの統合
- [ ] リアルタイム分析での利用

---

**Powered by Claude Code**

あなたのアイデアを、すぐに形にできます。
