# 🪙 草コイントレーダー - 100円→1000円への道

**Claude Codeと一緒に分析する、仮想通貨インテリジェンスシステム**

---

## 🎯 このシステムの特徴

**「答えを出すツール」ではなく、「分析材料を揃えるアシスタント」**

- ✅ ワンコマンドで銘柄の全情報を取得
- ✅ 価格、ニュース、スコアを統合表示
- ✅ 軽量なParquet形式で時系列データ保存
- ✅ 複数銘柄の相関分析・ベータ分析
- ✅ Claude Codeと対話しながら分析

---

## 🚀 クイックスタート

### 必要なパッケージ

```bash
pip install requests numpy pandas pyarrow
```

### 基本的な使い方

```bash
# 1. 銘柄の全情報を取得
python crypto_analyst.py BTC

# 2. 詳細な技術分析
python data/timeseries_storage.py --test BTC

# 3. 複数銘柄の相関分析
python analysis/correlation_analyzer.py --market BTC ETH XRP DOGE SHIB
```

---

## 📊 主要機能

### 1. 統合分析ダッシュボード（crypto_analyst.py）

ワンコマンドで以下を取得：

- 💰 現在価格・24h統計
- 🎯 ニュース影響力スコア（大雑把な目安）
- 📰 最近のニュース（影響力順）
- 📉 30日間の価格動向

```bash
python crypto_analyst.py BTC
python crypto_analyst.py ETH --timeline
python crypto_analyst.py SHIB --news 1
```

### 2. 時系列データストレージ（timeseries_storage.py）

**Parquet形式で軽量・高速分析**

- 89%のデータ圧縮（144KB SQLite → 15.8KB Parquet）
- DatetimeIndexによる高速時系列操作
- 組み込み数学分析関数（RSI, MACD, ボリンジャーバンド等）

```bash
# SQLiteからParquetへ変換
python data/timeseries_storage.py --migrate

# データ確認
python data/timeseries_storage.py --info

# 詳細分析実行
python data/timeseries_storage.py --test BTC
```

**分析機能**：
- リターン・対数リターン計算
- ボラティリティ分析
- 移動平均（SMA・EMA）
- RSI（相対力指数）
- MACD
- ボリンジャーバンド
- 時間軸リサンプリング

### 3. 複数銘柄の相関分析（correlation_analyzer.py）

**市場の連動性とリスク分散を分析**

```bash
# 市場連動性分析
python analysis/correlation_analyzer.py --market BTC ETH XRP DOGE SHIB

# ベータ分析（市場感応度）
python analysis/correlation_analyzer.py --beta DOGE --benchmark BTC

# 分散投資ペア推奨
python analysis/correlation_analyzer.py --diversify BTC ETH XRP DOGE SHIB
```

**分析結果の例**：
- 主要5銘柄の平均相関: 0.927（非常に高い連動性）
- DOGEのベータ値: 2.409（BTCの2.4倍動く）
- 仮想通貨内での分散投資効果は限定的

### 4. 詳細データ収集（detailed_data_collector.py）

**複数の時間足で詳細データを収集**

```bash
# BTCの全時間足データを収集
python data/detailed_data_collector.py BTC --all-intervals

# 特定の時間足を収集
python data/detailed_data_collector.py ETH --interval 4h --days 30

# 市場統計も収集
python data/detailed_data_collector.py XRP --all-intervals --stats

# データをエクスポート
python data/detailed_data_collector.py BTC --export
```

**対応時間足**: 1m, 5m, 15m, 30m, 1h, 4h, 1d

---

## 🔄 実践的ワークフロー

### シナリオ1: 朝のマーケットチェック

```bash
# 保有銘柄を確認
python crypto_analyst.py BTC
python crypto_analyst.py ETH

# Claude Codeに質問
「この2つ、今日何か動きそう？」
```

### シナリオ2: 新規購入を検討

```bash
# 候補銘柄の情報収集
python crypto_analyst.py SHIB --timeline

# 技術的指標を確認
python data/timeseries_storage.py --test SHIB

# 市場感応度を確認
python analysis/correlation_analyzer.py --beta SHIB

# Claude Codeと一緒に判断
「このRSI値と価格トレンド、どう見る？」
「今買うべき？それとも待つべき？」
```

### シナリオ3: ポートフォリオのリスク分析

```bash
# 保有銘柄の相関を確認
python analysis/correlation_analyzer.py --market BTC ETH DOGE

# 結果を見ながらClaude Codeと対話
「平均相関0.92って、かなり連動してるよね？」
「これだと分散投資の意味があまりないのでは？」
```

詳細は **[docs/analysis_workflow.md](docs/analysis_workflow.md)** を参照

---

## 📚 教材構成（100円→1000円チャレンジ）

### 二軸学習アプローチ

**実践（Week形式）** × **理解（Chapter形式）**

```
📖 Week形式                📚 Chapter形式
curriculum/                curriculum/stories/

Week 1: 100円開始      ←→  Chapter 1: 投資戦略
                       ←→  Chapter 2: RSI発明
Week 2: テクニカル      ←→  Chapter 3: MACD誕生
                       ←→  Chapter 4: Bollinger Bands
Week 3: ニュース分析    ←→  Chapter 5: ARIMA/GARCH
                       ←→  Chapter 6: 統合分析

  ↓ 実際に手を動かす        ↓ なぜ動くか理解する
```

### Week形式（実践教材）

**対象**: 実際に100円→1000円を達成したい実践者

**内容**: ツールの使い方、具体的な手順、失敗→改善のストーリー

| Week | 目標 | 主な内容 | 状態 |
|------|------|---------|------|
| [Week 1](curriculum/week1_basics.md) | 100円→110円 | 取引所登録、初取引 | ✅ 完成 |
| Week 2 | 110円→150円 | RSI, MACD, BB実践 | 📝 予定 |
| Week 3 | 150円→300円 | 感情分析、統合判断 | 📝 予定 |
| Week 4 | 300円→1000円 | システム化、振り返り | 📝 予定 |

詳細: **[curriculum/README.md](curriculum/README.md)**

---

### Chapter形式（技術ストーリー）

**対象**: 技術の「なぜ」「どうやって」を深く理解したい学習者

**内容**: 発明者の物語、数式の意味、実装方法

| Chapter | タイトル | 発明者/技術 | 状態 |
|---------|---------|------------|------|
| [1. 投資戦略](curriculum/stories/01_investment_strategy.md) | ユウタ式スイングトレード | 戦略確立 | ✅ 完成 |
| [2. RSI](curriculum/stories/02_rsi_invention.md) | 過熱を数値化した男 | J.W. Wilder (1978) | ✅ 完成 |
| [3. MACD](curriculum/stories/03_macd_invention.md) | トレンドを見える化 | G. Appel (1970s) | ✅ 完成 |
| [4. Bollinger Bands](curriculum/stories/04_bollinger_bands_invention.md) | リスクを可視化 | J. Bollinger (1980s) | ✅ 完成 |
| [5. ARIMA/GARCH](curriculum/stories/05_arima_garch_discovery.md) | 未来を予測 | Box/Engle | ✅ 完成 |
| [6. 統合分析](curriculum/stories/06_integrated_analysis.md) | 全てを統合 | - | ✅ 完成 |

詳細: **[curriculum/stories/README.md](curriculum/stories/README.md)**

---

### 学習パターン

**パターン1: 実践優先型（初心者向け）**
1. Week 1 → 実践で100円→104円を体験
2. Chapter 1-2 → なぜ成功/失敗したか理解
3. Week 2 → 学んだ技術を使って実践

**パターン2: 理解優先型（中級者向け）**
1. Chapter 1-6 → 技術を一通り学ぶ
2. Week 1-4 → 実践で技術を使いこなす

**パターン3: ハイブリッド型（推奨）**
- Week（実践）→ Chapter（理解）→ Week（実践）...と交互に

---

## 📁 プロジェクト構成

```
grass-coin-trader/
├── crypto_analyst.py               # 統合分析ダッシュボード
├── main.py                          # 旧メインシステム
│
├── curriculum/                      # 📚 学習者向け教材
│   ├── README.md                    # 教材全体ガイド
│   ├── week1_basics.md              # Week 1: 100円チャレンジ開始
│   │
│   └── stories/                     # 📖 Chapter形式（技術ストーリー）
│       ├── README.md                # Chapter形式ガイド
│       ├── 01_investment_strategy.md
│       ├── 02_rsi_invention.md
│       ├── 03_macd_invention.md
│       ├── 04_bollinger_bands_invention.md
│       ├── 05_arima_garch_discovery.md
│       └── 06_integrated_analysis.md
│
├── docs/                            # 🔧 システム開発・保守ドキュメント
│   ├── analysis_workflow.md         # システムの使い方
│   ├── data_collection_guide.md     # データ収集方法
│   ├── parquet_explained.md         # Parquet技術説明
│   ├── system_redesign_proposal.md  # システム設計書
│   │
│   └── meta/                        # 📝 メタドキュメント（教材作成者向け）
│       ├── curriculum_creation_guide.md # 教材作成ガイド
│       └── samples/                 # 詳細サンプル
│           ├── chapter_format_detailed_example.md
│           └── week_format_detailed_example.md
│
├── config/
│   └── exchange_api.py              # MEXC API連携
│
├── data/
│   ├── advanced_database.py         # SQLiteデータベース
│   ├── detailed_data_collector.py   # 詳細データ収集
│   ├── timeseries_storage.py        # Parquet時系列ストレージ
│   └── timeseries/
│       └── prices/                  # Parquetファイル保存場所
│           ├── BTC_1d.parquet
│           ├── BTC_4h.parquet
│           └── ...
│
└── analysis/
    ├── intelligence_system.py       # インテリジェンスシステム
    ├── scoring_engine.py            # スコアリングエンジン
    ├── correlation_analyzer.py      # 相関分析ツール
    └── news_collector.py            # ニュース収集
```

---

## 📚 ドキュメント

### 学習者向け教材
- **[curriculum/README.md](curriculum/README.md)** - 教材全体ガイド（Week + Chapter）
- **[curriculum/stories/README.md](curriculum/stories/README.md)** - Chapter形式（技術ストーリー）ガイド

### システム開発・保守
- **[README_ANALYST.md](README_ANALYST.md)** - 分析アシスタントの概要
- **[docs/analysis_workflow.md](docs/analysis_workflow.md)** - 実践的な分析ワークフロー
- **[docs/data_collection_guide.md](docs/data_collection_guide.md)** - 詳細データ収集ガイド

---

## 💾 データ構造

### SQLite（詳細データの永続化）

- `price_history_detailed` - 複数時間足の価格データ
- `news` - ニュース情報
- `websearch_raw` - WebSearch結果の完全保存
- `market_stats_detailed` - 市場統計
- `scoring_history` - スコアリング履歴

### Parquet（軽量・高速分析用）

```
data/timeseries/prices/
├── BTC_1d.parquet    # 30行, 5.3KB
├── BTC_4h.parquet    # 180行, 10.4KB
├── ETH_1d.parquet
├── ETH_4h.parquet
└── ...
```

**メリット**:
- 89%のサイズ削減
- カラム指向で高速読み取り
- pandas/NumPy直接対応
- 数学的分析に最適

---

## 🎨 分析結果の読み方

### RSI（相対力指数）

```
RSI > 70  → 買われすぎ（調整の可能性）
RSI < 30  → 売られすぎ（反発の可能性）
RSI 30-70 → 中立
```

### ベータ値

```
ベータ > 1.5 → 市場より大きく動く（ハイリスク・ハイリターン）
ベータ 1.0  → 市場と同じ
ベータ < 0.5 → 市場より小さく動く（ローリスク・ローリターン）
```

### 相関係数

```
相関 > 0.7  → 強く連動（分散効果は低い）
相関 0.3-0.7 → 中程度の連動
相関 < 0.3  → 独立した動き（分散効果あり）
```

---

## ⚠️ 重要な注意事項

1. **投資助言ではありません**
   - このツールは分析材料を提供するだけです
   - 最終判断は自己責任で行ってください

2. **スコアは目安です**
   - 機械的に計算した参考値
   - 実際の内容を必ず確認してください

3. **Claude Codeとの対話が本質**
   - ツールは材料を揃えるだけ
   - 分析は一緒に考えましょう

4. **リスク管理を忘れずに**
   - 分散投資
   - 余剰資金の範囲内
   - 損切りラインの設定

---

## 🚀 今後の拡張

- [ ] オンチェーンデータ分析
- [ ] ソーシャルメディアセンチメント分析
- [ ] バックテスト機能
- [ ] アラート機能
- [ ] ポートフォリオ最適化

---

## 🛠️ 技術スタック

- **Python 3.8+**
- **MEXC API** - 価格データ取得
- **SQLite** - 詳細データの永続化
- **Parquet** - 高速分析用データストレージ
- **pandas** - データ分析
- **NumPy** - 数値計算

---

## 📊 実績

- ✅ 5銘柄のデータ収集・保存（BTC, ETH, XRP, DOGE, SHIB）
- ✅ 1050データポイント、77.9KB（Parquet形式）
- ✅ 相関分析で市場の連動性を実証（平均相関0.927）
- ✅ ベータ分析でリスク特性を定量化

---

**Powered by Claude Code**

データを見て、一緒に考える。それが賢い投資の第一歩。
