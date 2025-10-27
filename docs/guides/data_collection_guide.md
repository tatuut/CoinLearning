# 📊 詳細データ取得・保存ガイド

## 🎯 データの種類と保存場所

### 現在保存されているデータ

| データ種類 | 保存テーブル | 詳細度 | 更新頻度 |
|-----------|-------------|--------|---------|
| **価格履歴（詳細）** | `price_history_detailed` | 1分足～1日足 | 手動収集 |
| **ニュース** | `news` | タイトル・本文・スコア | 手動追加 |
| **WebSearch生データ** | `websearch_raw` | 完全な検索結果 | 手動保存 |
| **市場統計** | `market_stats_detailed` | 時価総額・供給量・ランキング | 手動収集 |
| **スコアリング結果** | `scoring_history` | 影響力スコア | 自動計算 |

---

## 📥 データの取得方法

### 1. 価格履歴の詳細データ

**取得元:** MEXC API
**保存データ:**
- タイムスタンプ
- 始値・高値・安値・終値（OHLC）
- 出来高・Quote出来高
- 時間足の種類（1m, 5m, 15m, 30m, 1h, 4h, 1d）

**取得コマンド:**
```bash
# 1日足を30日分
python data/detailed_data_collector.py BTC --interval 1d --days 30

# 1時間足を30日分
python data/detailed_data_collector.py BTC --interval 1h --days 30

# 全時間足を一括収集
python data/detailed_data_collector.py BTC --all-intervals
```

**保存例:**
```sql
sqlite> SELECT * FROM price_history_detailed WHERE symbol='BTC' LIMIT 1;

id: 1
symbol: BTC
timestamp: 1760745600000
interval: 1d
open: 106428.7
high: 107495.52
low: 106320.25
close: 107279.15
volume: 2792.82714634
quote_volume: 0
collected_at: 2025-10-18 20:43:15
```

**実際に保存されている情報:**
- ✅ 全てのOHLCデータ
- ✅ タイムスタンプ（ミリ秒精度）
- ✅ 出来高（取引量）
- ✅ 複数の時間足

---

### 2. ニュースの詳細データ

**現在の保存内容:**
```sql
SELECT * FROM news WHERE id=1;

id: 1
symbol: BTC
title: ビットコインが最高値更新
content: ビットコインが$100,000を突破し、史上最高値を更新しました。
source: CoinPost
url: (空)
published_date: 2025-10-18T20:10:31
sentiment: positive
importance_score: 0.9
impact_score: 0.8
keywords: ["bitcoin", "最高値", "100000"]
```

**拡張可能な情報（実装済み）:**

`news_full_text` テーブルに以下を保存可能：
- 完全なHTML
- Markdown形式の本文
- 画像URL一覧
- 動画URL一覧
- 関連記事リンク
- 著者情報
- コメント数・シェア数

**WebSearch生データの保存:**

`websearch_raw` テーブルに以下を保存可能：
- 検索クエリ
- 検索結果の完全なタイトル
- URL
- スニペット
- 完全な本文（フェッチした場合）
- メタデータ（JSON形式）
- 関連性スコア

**使い方（Pythonコード内）:**
```python
from data.detailed_data_collector import DetailedDataCollector

collector = DetailedDataCollector()

# WebSearchの結果を保存
websearch_results = [
    {
        'title': 'ビットコインが史上最高値',
        'url': 'https://example.com/btc-ath',
        'snippet': '2025年10月、BTCは...',
        'content': '完全な本文がここに入る',
        'metadata': {'author': '山田太郎', 'date': '2025-10-18'},
        'domain': 'example.com'
    },
    # ... more results
]

collector.save_websearch_result(
    query="Bitcoin 最新ニュース 2025",
    results=websearch_results
)
```

---

### 3. 市場統計の詳細データ

**保存内容:**
```sql
SELECT * FROM market_stats_detailed WHERE symbol='BTC' LIMIT 1;

id: 1
symbol: BTC
timestamp: 2025-10-18 20:43:16
price: 107190.06
volume_24h: 8671
percent_change_24h: 0.01
raw_data_json: {"price": 107190.06, "symbol": "BTCUSDT", ...}
```

**保存される情報:**
- ✅ 現在価格
- ✅ 24時間出来高
- ✅ 24時間変動率
- ✅ **生のJSON（全てのAPIレスポンス）**

**拡張可能な情報（カラムあり）:**
- 時価総額
- 循環供給量・総供給量・最大供給量
- ランキング
- ドミナンス率
- 回転率

---

### 4. オーダーブック履歴（板情報）

**テーブル:** `orderbook_history`

**保存可能な情報:**
- 買い板（Bids）の完全なデータ（JSON）
- 売り板（Asks）の完全なデータ（JSON）
- 1%深さの板厚
- スプレッド
- 中間価格

**実装状態:** テーブル作成済み、収集機能は未実装

---

## 💾 データの保存フロー

### 完全な流れ

```
1. データソース
   ├─ MEXC API（価格・市場統計）
   ├─ WebSearch（ニュース・情報）
   └─ オンチェーンデータ（実装予定）
         ↓
2. 収集スクリプト
   ├─ detailed_data_collector.py（価格・統計）
   ├─ news_collector.py（ニュース）
   └─ 手動でWebSearch実行
         ↓
3. データ変換・構造化
   ├─ タイムスタンプ正規化
   ├─ JSON形式での保存
   └─ スコア計算
         ↓
4. SQLiteデータベースに保存
   ├─ price_history_detailed
   ├─ news / news_full_text
   ├─ websearch_raw
   ├─ market_stats_detailed
   └─ orderbook_history
         ↓
5. 分析ツールで活用
   ├─ crypto_analyst.py（対話分析）
   ├─ scoring_engine.py（スコアリング）
   └─ カスタム分析（SQL直接）
```

---

## 🔍 データの確認方法

### SQLiteで直接確認

```bash
# データベースに接続
sqlite3 data/advanced_trading.db

# テーブル一覧
.tables

# 価格データ確認
SELECT * FROM price_history_detailed
WHERE symbol='BTC' AND interval='1d'
ORDER BY timestamp DESC
LIMIT 10;

# ニュース確認
SELECT title, published_date, importance_score
FROM news
WHERE symbol='BTC'
ORDER BY published_date DESC;

# データ件数確認
SELECT
    (SELECT COUNT(*) FROM price_history_detailed WHERE symbol='BTC') as price_count,
    (SELECT COUNT(*) FROM news WHERE symbol='BTC') as news_count,
    (SELECT COUNT(*) FROM market_stats_detailed WHERE symbol='BTC') as stats_count;
```

### Pythonで確認

```python
from data.detailed_data_collector import DetailedDataCollector

collector = DetailedDataCollector()

# 分析結果を取得
analysis = collector.get_price_analysis('BTC', interval='1h', limit=100)
print(f"データ数: {analysis['data_points']}")
print(f"現在価格: ${analysis['current_price']}")
print(f"ボラティリティ: {analysis['volatility']:.2f}%")

# 全データをエクスポート
collector.export_detailed_data('BTC')
# → exports/data_export_BTC_20251018_HHMMSS.json に保存
```

---

## 📤 データのエクスポート

### JSON形式でエクスポート

```bash
# BTCの全データをエクスポート
python data/detailed_data_collector.py BTC --export
```

**出力ファイル:** `exports/data_export_BTC_20251018_204315.json`

**含まれる内容:**
```json
{
  "symbol": "BTC",
  "export_date": "2025-10-18T20:43:15",
  "price_history": [
    {
      "timestamp": 1760745600000,
      "interval": "1d",
      "open": 106428.7,
      "high": 107495.52,
      "low": 106320.25,
      "close": 107279.15,
      "volume": 2792.82714634
    },
    // ... more data
  ],
  "news": [
    {
      "title": "ビットコインが最高値更新",
      "content": "...",
      "sentiment": "positive",
      "importance_score": 0.9
    },
    // ... more news
  ],
  "market_stats": [
    // ... stats
  ],
  "summary": {
    "price_data_points": 210,
    "news_count": 6,
    "stats_snapshots": 1
  }
}
```

---

## 🎨 データの可視化・分析

### Claude Codeとの対話分析

```bash
# 材料を取得
python crypto_analyst.py BTC

# Claude Codeに質問
「データベースから1時間足の直近100件を取って、
 ボリンジャーバンドを計算してくれる？」

「10月15日のニュースと価格変動を比較したい。
 データベースから該当データを抽出して」
```

### SQL直接クエリ

```sql
-- 1. 価格とニュースの時系列相関
SELECT
    DATE(p.timestamp/1000, 'unixepoch') as date,
    AVG(p.close) as avg_price,
    COUNT(n.id) as news_count,
    AVG(n.importance_score) as avg_importance
FROM price_history_detailed p
LEFT JOIN news n ON DATE(n.published_date) = DATE(p.timestamp/1000, 'unixepoch')
WHERE p.symbol = 'BTC' AND p.interval = '1d'
GROUP BY date
ORDER BY date DESC
LIMIT 30;

-- 2. ボラティリティ分析
SELECT
    interval,
    COUNT(*) as data_points,
    MIN(low) as period_low,
    MAX(high) as period_high,
    (MAX(high) - MIN(low)) / MIN(low) * 100 as volatility_pct
FROM price_history_detailed
WHERE symbol = 'BTC'
GROUP BY interval;

-- 3. ニュースセンチメント推移
SELECT
    DATE(published_date) as date,
    sentiment,
    COUNT(*) as count,
    AVG(importance_score) as avg_score
FROM news
WHERE symbol = 'BTC'
GROUP BY date, sentiment
ORDER BY date DESC;
```

---

## 🔄 自動収集の設定（今後の拡張）

### cron/タスクスケジューラで定期実行

**Linux/Mac:**
```bash
# 毎日0時に価格データ収集
0 0 * * * cd /path/to/project && python data/detailed_data_collector.py BTC --all-intervals --stats
```

**Windows:**
```powershell
# タスクスケジューラで設定
schtasks /create /tn "CryptoDataCollection" /tr "python detailed_data_collector.py BTC --all-intervals" /sc daily /st 00:00
```

---

## 📊 データの活用例

### 1. バックテスト

```python
# 過去のデータで戦略をテスト
cursor = db.conn.cursor()
cursor.execute('''
    SELECT timestamp, close, volume
    FROM price_history_detailed
    WHERE symbol = 'BTC' AND interval = '1h'
    ORDER BY timestamp
''')
# → 移動平均戦略のシミュレーション
```

### 2. 機械学習の特徴量

```python
# 価格・出来高・ニューススコアを特徴量として使用
features = []
for row in price_data:
    news_score = get_news_score_for_date(row['timestamp'])
    features.append([
        row['close'],
        row['volume'],
        row['high'] - row['low'],  # レンジ
        news_score
    ])
```

### 3. アラート生成

```python
# 特定条件でアラート
latest_price = get_latest_price('BTC')
latest_news_score = get_latest_news_score('BTC')

if latest_price > 110000 and latest_news_score > 0.5:
    send_alert("BTC高値 + ポジティブニュース多数")
```

---

## 🛠️ 拡張可能性

### 今後実装可能な機能

1. **リアルタイム価格ストリーム**
   - WebSocketで1秒ごとの価格更新
   - 板情報のリアルタイム記録

2. **ニュースの自動収集**
   - RSS/APIからの自動取得
   - 自然言語処理でセンチメント分析

3. **オンチェーンデータ**
   - トランザクション数
   - アクティブアドレス数
   - ウォレット残高推移

4. **ソーシャルメディア分析**
   - Twitter/Redditのセンチメント
   - インフルエンサーの発言追跡

---

## 📝 まとめ

### 「最も詳細なデータ」= 以下の組み合わせ

1. **価格データ**
   - ✅ 複数時間足（1m～1d）
   - ✅ OHLCV完全保存
   - ✅ 長期履歴（最大1000件）

2. **ニュースデータ**
   - ✅ タイトル・本文
   - ✅ 出典・URL
   - ✅ スコアリング結果
   - ⏳ 完全HTML（拡張可能）

3. **市場データ**
   - ✅ 24h統計
   - ✅ 生JSONの完全保存
   - ⏳ 時価総額・供給量（拡張可能）

4. **WebSearchデータ**
   - ✅ 検索結果の完全保存
   - ✅ メタデータ保存
   - ⏳ 完全本文フェッチ（拡張可能）

**重要:** データは「取得」→「保存」→「分析」の3ステップ。
Claude Codeと一緒に、必要なデータを必要なときに取り寄せて分析！
