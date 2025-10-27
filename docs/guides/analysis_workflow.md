# 📊 実践的分析ワークフロー

## 🎯 このシステムの使い方

**「答えを出すツール」ではなく、「あなたが分析するための材料を一瞬で揃えるアシスタント」**

Claude Codeと一緒に、データを見ながら対話的に分析を進めます。

---

## 📋 基本ワークフロー

### 1️⃣ 材料を集める

```bash
# 銘柄の全コンテキストを取得
python crypto_analyst.py BTC

# 出力内容:
# - 💰 現在価格・24h統計
# - 🎯 ニュース影響力スコア（大雑把な目安）
# - 📰 最近のニュース（影響力順）
# - 📉 30日間の価格動向
```

### 2️⃣ Claude Codeと対話分析

材料を見ながら、以下のような質問を投げかける：

```
「10月15日のニュースと価格変動、どう読む？」
「現在のRSIと価格トレンド、どう解釈すべき？」
「ETHと比較して、どちらが今買い時？」
```

### 3️⃣ 詳細な数学的分析

```bash
# 時系列データで詳細分析
python data/timeseries_storage.py --test BTC

# 出力内容:
# - リターン計算
# - ボラティリティ
# - RSI（相対力指数）
# - MACD
# - ボリンジャーバンド
# - トレンド判定
```

### 4️⃣ 複数銘柄の相関分析

```bash
# 市場全体の連動性を分析
python analysis/correlation_analyzer.py --market BTC ETH XRP DOGE SHIB

# 出力内容:
# - 相関係数行列
# - 平均相関（市場の連動度）
# - 最も連動している/独立しているペア
# - 分散投資の有効性判断
```

```bash
# ベータ値分析（市場感応度）
python analysis/correlation_analyzer.py --beta DOGE --benchmark BTC

# 出力内容:
# - ベータ値（BTCに対する感応度）
# - 相関係数
# - リスク・リターン特性の解釈
```

---

## 🔄 実践的シナリオ

### シナリオ1: 朝のマーケットチェック

```bash
# 1. 保有銘柄の現在状況を確認
python crypto_analyst.py BTC
python crypto_analyst.py ETH

# 2. Claude Codeに質問
「この2つ、今日何か動きそう？」
「ニュースから見て、注意すべきリスクは？」

# 3. 必要に応じて詳細分析
python data/timeseries_storage.py --test BTC
```

### シナリオ2: 新規購入を検討

```bash
# 1. 候補銘柄の情報収集
python crypto_analyst.py SHIB --timeline

# 2. 技術的指標を確認
python data/timeseries_storage.py --test SHIB

# 3. 市場感応度を確認
python analysis/correlation_analyzer.py --beta SHIB

# 4. Claude Codeと一緒に判断
「このRSI値と価格トレンド、どう見る？」
「ベータ2.4ってことは、かなりボラティリティ高いよね？」
「今買うべき？それとも待つべき？」
```

### シナリオ3: ポートフォリオのリスク分析

```bash
# 1. 保有銘柄の相関を確認
python analysis/correlation_analyzer.py --market BTC ETH DOGE

# 2. 結果を見ながらClaude Codeと対話
「平均相関0.92って、かなり連動してるよね？」
「これだと分散投資の意味があまりないのでは？」
「他にどんな銘柄を追加すればリスク分散できる？」
```

### シナリオ4: ニュース影響の分析

```bash
# 1. 最新情報を取得
python crypto_analyst.py BTC

# 2. 特定ニュースの詳細を確認
python crypto_analyst.py BTC --news 1

# 3. 価格とニュースの時系列比較
python crypto_analyst.py BTC --timeline

# 4. Claude Codeと一緒に考察
「このETF流入のニュース、実際に価格に影響してる？」
「過去のパターンから、今後どう動きそう？」
```

---

## 📊 データの階層構造

### レベル1: 概要把握（スコアと要約）

```bash
python crypto_analyst.py BTC
```

**用途**: 大雑把な状況把握、スコアは目安として使用

**出力**:
- 現在価格
- スコア（参考値）
- ニュース一覧
- 価格概要

### レベル2: 詳細な技術分析

```bash
python data/timeseries_storage.py --test BTC
```

**用途**: 数学的・技術的な深掘り分析

**出力**:
- リターン、ボラティリティ
- RSI, MACD, ボリンジャーバンド
- トレンド判定
- 統計情報

### レベル3: 複数銘柄の比較分析

```bash
python analysis/correlation_analyzer.py --market BTC ETH XRP
```

**用途**: ポートフォリオ全体のリスク分析

**出力**:
- 相関係数
- ベータ値
- 分散投資の有効性
- リスク・リターン特性

---

## 🛠️ データ収集の流れ

### 初回セットアップ

```bash
# 1. 詳細データを収集（SQLiteに保存）
python data/detailed_data_collector.py BTC --all-intervals
python data/detailed_data_collector.py ETH --all-intervals
python data/detailed_data_collector.py XRP --all-intervals

# 2. Parquet形式に変換（軽量・高速分析用）
python data/timeseries_storage.py --migrate

# 3. データの確認
python data/timeseries_storage.py --info
```

**結果**:
- SQLite: 詳細データの永続化
- Parquet: 軽量で高速な分析用データ
- 5銘柄で約78KB（非常にコンパクト）

### 定期的なデータ更新

```bash
# 1. 最新データを取得
python data/detailed_data_collector.py BTC --all-intervals --stats

# 2. Parquetに追加
python data/timeseries_storage.py --migrate

# 3. 更新内容を確認
python data/timeseries_storage.py --info
```

---

## 💡 分析のコツ

### 1. スコアは「目安」として使う

❌ **間違い**: スコアが高いから買う
✅ **正しい**: スコアで候補を絞り、実際のニュース内容と価格データを見て判断

### 2. 複数の指標を組み合わせる

```
価格トレンド ＋ RSI ＋ ニュースセンチメント ＋ 出来高
→ 総合的な判断
```

### 3. Claude Codeとの対話を活用

```
× 「買うべきですか？」
○ 「このデータから、どんなリスクが読み取れる？」
○ 「過去のパターンと比較すると、今回はどう？」
○ 「他の銘柄と比べて、何が違う？」
```

### 4. 相関を理解してリスク管理

```bash
# まず相関を確認
python analysis/correlation_analyzer.py --market BTC ETH DOGE

# 相関が高い（>0.7） → 分散投資の効果は限定的
# 相関が低い（<0.5） → 分散投資が有効
```

---

## 📈 分析結果の読み方

### RSI（相対力指数）

```
RSI > 70  → 買われすぎ（調整の可能性）
RSI < 30  → 売られすぎ（反発の可能性）
RSI 30-70 → 中立
```

**注意**: RSIだけで判断せず、他の指標と組み合わせる

### ボラティリティ

```
高ボラティリティ → ハイリスク・ハイリターン
低ボラティリティ → ローリスク・ローリターン
```

### ベータ値

```
ベータ > 1.5 → 市場より大きく動く（攻撃的）
ベータ 1.0  → 市場と同じ
ベータ < 0.5 → 市場より小さく動く（守備的）
```

### 相関係数

```
相関 > 0.7  → 強く連動（分散効果は低い）
相関 0.3-0.7 → 中程度の連動
相関 < 0.3  → 独立した動き（分散効果あり）
相関 < 0    → 負の相関（片方↑でもう片方↓）
```

---

## ⚠️ 重要な注意事項

1. **投資助言ではありません**
   - このツールは分析材料を提供するだけ
   - 最終判断は自己責任で

2. **スコアを過信しない**
   - 機械的に計算した参考値
   - 実際の内容を必ず確認する

3. **複数の視点で分析**
   - 技術的分析（RSI, MACD等）
   - ファンダメンタル分析（ニュース）
   - センチメント分析（市場の雰囲気）

4. **リスク管理を徹底**
   - 分散投資
   - 損切りラインの設定
   - 余剰資金の範囲内で

5. **仮想通貨の特性を理解**
   - 高ボラティリティ
   - 24時間取引
   - 主要銘柄は高い相関

---

## 🚀 次のステップ

### さらなる分析機能の追加

- [ ] オンチェーンデータ分析（トランザクション数、アクティブアドレス）
- [ ] ソーシャルメディアセンチメント分析
- [ ] バックテスト機能（過去データでの戦略検証）
- [ ] アラート機能（特定条件で通知）
- [ ] ポートフォリオ最適化

### データの拡充

- [ ] より多くの銘柄（アルトコイン、DeFiトークン）
- [ ] 1分足、5分足の短期データ
- [ ] より長期のデータ（1年、2年分）
- [ ] オーダーブック履歴

---

## 📚 関連ドキュメント

- [README_ANALYST.md](../README_ANALYST.md) - 分析アシスタントの概要
- [data_collection_guide.md](./data_collection_guide.md) - 詳細データ収集ガイド
- [crypto_analyst.py](../crypto_analyst.py) - メインツール
- [timeseries_storage.py](../data/timeseries_storage.py) - 時系列ストレージ
- [correlation_analyzer.py](../analysis/correlation_analyzer.py) - 相関分析

---

**Powered by Claude Code**
データを見て、一緒に考える。それが賢い投資の第一歩。
