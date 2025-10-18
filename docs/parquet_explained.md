# 📦 Parquetとは？なぜ使うの？

## 🎯 簡単に言うと

**Parquet（パーケット）** = 数値データを超効率的に保存できるファイル形式

時系列データ（価格、出来高など）の保存・分析に最適です。

---

## 📊 JSONとの比較

### JSONの場合（行指向）

```json
[
  {"timestamp": "2025-01-01", "open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000},
  {"timestamp": "2025-01-02", "open": 103, "high": 108, "low": 102, "close": 107, "volume": 1500},
  {"timestamp": "2025-01-03", "open": 107, "high": 110, "low": 105, "close": 109, "volume": 1200}
]
```

**問題点**:
- ❌ ファイルサイズが大きい（テキスト形式）
- ❌ 全データを読む必要がある
- ❌ 特定の列だけ読めない
- ❌ 圧縮率が低い

### Parquetの場合（列指向）

```
内部構造（バイナリ形式）:
timestamp列: [2025-01-01, 2025-01-02, 2025-01-03]
open列:      [100, 103, 107]
high列:      [105, 108, 110]
low列:       [99, 102, 105]
close列:     [103, 107, 109]
volume列:    [1000, 1500, 1200]
```

**メリット**:
- ✅ ファイルサイズが小さい（バイナリ + 圧縮）
- ✅ 必要な列だけ読める（超高速）
- ✅ 数値計算に最適
- ✅ pandas/NumPy直接対応

---

## 🔍 具体例：このプロジェクトでの効果

### 実測データ

```
SQLite（JSON的な保存）:
- BTC 30日分 + 180件4h足
- サイズ: 144KB

Parquet:
- 同じデータ
- サイズ: 15.8KB

削減率: 89%！
```

### 複数銘柄の場合

```
5銘柄（BTC, ETH, XRP, DOGE, SHIB）:
- 各銘柄: 1d × 30行 + 4h × 180行 = 210行
- 総データ: 1050行

SQLite相当: 約720KB
Parquet実測: 77.9KB

削減率: 89%
```

---

## ⚡ 速度の違い

### シナリオ: 「closeカラムだけ読んで平均を計算」

**JSON/CSV**:
```python
# 全データを読み込む必要がある
data = json.load(file)  # 全列を読む
prices = [row['close'] for row in data]
avg = sum(prices) / len(prices)
```

**Parquet**:
```python
# closeカラムだけ読む
df = pd.read_parquet(file, columns=['close'])
avg = df['close'].mean()
```

**結果**: Parquetは必要な列だけ読むので、**10倍〜100倍速い**ことも

---

## 🎨 使い分け

### JSONを使うべき場合

- 🔹 少量のデータ（数十件）
- 🔹 人間が読む必要がある
- 🔹 Web APIのレスポンス
- 🔹 設定ファイル

### Parquetを使うべき場合

- 🔹 大量の数値データ
- 🔹 時系列データ
- 🔹 数学的分析が必要
- 🔹 列ごとに読みたい
- 🔹 ディスク容量を節約したい

---

## 💻 このプロジェクトでの使い方

### 1. データを保存

```python
from data.timeseries_storage import TimeSeriesStorage

storage = TimeSeriesStorage()

# SQLiteから自動的にParquetへ変換
storage.migrate_from_sqlite()

# または直接保存
price_data = [
    {'timestamp': 1234567890000, 'open': 100, 'high': 105, ...},
    ...
]
storage.save_price_data('BTC', '1d', price_data)
```

**保存先**: `data/timeseries/prices/BTC_1d.parquet`

### 2. データを読み込み

```python
# 全データを読み込み
df = storage.load_price_data('BTC', '1d')

# 特定の列だけ読み込み（超高速）
df = pd.read_parquet('data/timeseries/prices/BTC_1d.parquet',
                     columns=['close', 'volume'])
```

### 3. 分析

```python
# リターン計算
returns = df['close'].pct_change()

# ボラティリティ
volatility = returns.rolling(20).std()

# 移動平均
sma = df['close'].rolling(20).mean()
```

---

## 🧮 技術的詳細

### カラム指向ストレージとは？

**行指向（JSON, CSV, SQLite）**:
```
行1: [timestamp1, open1, high1, low1, close1, volume1]
行2: [timestamp2, open2, high2, low2, close2, volume2]
行3: [timestamp3, open3, high3, low3, close3, volume3]
```

**列指向（Parquet）**:
```
timestamp列: [timestamp1, timestamp2, timestamp3, ...]
open列:      [open1, open2, open3, ...]
high列:      [high1, high2, high3, ...]
...
```

### なぜ列指向が速い？

1. **必要な列だけアクセス**
   - 「closeだけ読む」が可能
   - 不要な列はディスクから読まない

2. **圧縮率が高い**
   - 同じ型のデータが連続
   - 似た値が続く（時系列の特性）
   - 効率的に圧縮できる

3. **CPU キャッシュに優しい**
   - データが連続配置
   - SIMDで並列処理可能

### このプロジェクトの最適化

```python
# float32を使用（float64の半分のサイズ）
df[col] = df[col].astype('float32')

# Snappy圧縮（高速で適度な圧縮率）
df.to_parquet(filepath, compression='snappy')

# DatetimeIndex（時系列操作に最適）
df.set_index('timestamp', inplace=True)
```

---

## 📈 拡張性

### 現在のデータ量

```
5銘柄 × 210行 = 1050行
サイズ: 77.9KB
```

### 将来のデータ量（想定）

```
20銘柄 × 1年分（1分足） × 365日 = 約1000万行
JSON/SQLite: 数GB
Parquet: 数百MB

→ Parquetなら管理可能！
```

---

## 🛠️ ツールとの互換性

### 読み書きできるツール

- ✅ **Python**: pandas, pyarrow, fastparquet
- ✅ **R**: arrow パッケージ
- ✅ **Spark**: ネイティブサポート
- ✅ **Dask**: 大規模データ処理
- ✅ **DuckDB**: SQL で直接クエリ可能

### 例: DuckDBでSQL

```sql
SELECT
    symbol,
    AVG(close) as avg_price,
    MAX(high) as max_price
FROM 'data/timeseries/prices/*.parquet'
GROUP BY symbol;
```

---

## 🎓 まとめ

### Parquetを使う理由

1. **軽量**: 89%削減（144KB → 15.8KB）
2. **高速**: 必要な列だけ読める
3. **数学的分析に最適**: pandas/NumPy と直接連携
4. **スケーラブル**: 大量データでも高速
5. **標準的**: 多くのツールでサポート

### このプロジェクトでの効果

- ✅ 5銘柄で77.9KB（SQLiteなら約720KB）
- ✅ 数学的分析（RSI, MACD等）が超高速
- ✅ 将来的に数十銘柄に拡張可能
- ✅ Claude Codeとの対話的分析に最適

---

## 📚 参考リンク

- [Apache Parquet公式](https://parquet.apache.org/)
- [pandas.to_parquet ドキュメント](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html)
- [PyArrow ドキュメント](https://arrow.apache.org/docs/python/)

---

**Powered by Claude Code**

効率的なデータ保存で、快適な分析を。
