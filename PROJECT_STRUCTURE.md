# 📁 プロジェクト構造

**草コイントレーダー** のディレクトリ構成と各ファイルの役割を説明します。

---

## 🎯 プロジェクト概要

**目的**: 100円→1000円を目指す仮想通貨取引の学習システム

**特徴**:
- ✅ 実践教材（Week形式）+ 技術理解（Chapter形式）
- ✅ 分析材料を揃えるアシスタント（自動判断しない）
- ✅ Claude Codeと対話しながら学習

---

## 📂 ディレクトリ構成

```
grass-coin-trader/
│
├── crypto_analyst.py           # メインツール（頻繁に使うのでルートに）
├── requirements.txt            # 必要パッケージ
│
├── 🔧 src/                     # 全システムコード
│   ├── analysis/              # 分析エンジン
│   │   ├── intelligence_system.py
│   │   ├── scoring_engine.py
│   │   ├── correlation_analyzer.py
│   │   ├── news_collector.py
│   │   └── indicators/
│   │       ├── atr.py
│   │       ├── obv.py
│   │       └── stochastic.py
│   │
│   ├── data/                  # データ管理
│   │   ├── advanced_database.py
│   │   ├── timeseries_manager.py
│   │   ├── detailed_data_collector.py
│   │   ├── news_manager.py
│   │   ├── coin_research.py
│   │   └── timeseries/
│   │       └── prices/
│   │
│   ├── config/                # 設定
│   │   └── exchange_api.py
│   │
│   └── tools/                 # ユーティリティ
│       ├── market_scanner.py
│       └── auto_market_updater.py
│
├── 📚 curriculum/             # 学習教材
│   ├── README.md
│   ├── week1_basics.md        # Week 1: 100円チャレンジ開始
│   └── stories/               # Chapter形式（技術ストーリー）
│       ├── README.md
│       ├── 01_investment_strategy.md
│       ├── 02_rsi_invention.md
│       ├── 03_macd_invention.md
│       ├── 04_bollinger_bands_invention.md
│       ├── 05_arima_garch_discovery.md
│       └── 06_integrated_analysis.md
│
└── 📖 docs/                   # ドキュメント + 参照系
    ├── analysis_workflow.md
    ├── data_collection_guide.md
    ├── parquet_explained.md
    ├── system_redesign_proposal.md
    │
    ├── meta/                  # 教材作成者向け
    │   ├── curriculum_creation_guide.md
    │   └── samples/
    │       ├── chapter_format_detailed_example.md
    │       └── week_format_detailed_example.md
    │
    ├── tests/                 # テストコード
    │   └── test_*.py
    │
    └── archive/               # 旧システム（参考）
        ├── main.py
        ├── strategies/
        ├── database.py
        ├── performance.py
        └── report_generator.py
```

---

## 🎨 設計思想

### 1. **3層構造**
- **src/** - 実行するもの（システムコード）
- **curriculum/** - 学ぶもの（教材）
- **docs/** - 参照するもの（ドキュメント、テスト、アーカイブ）

### 2. **関連するものを近くに**
- システムコードの全部品（analysis, data, config, tools）→ `src/` 配下
- 参照系（docs, tests, archive）→ `docs/` 配下

### 3. **一目で分かる構造**
- ルートを見れば、プロジェクトの全体像が即座に理解できる
- **ルート直下ディレクトリ：3個のみ**（src, curriculum, docs）

---

## 🔧 src/ - システムコード

### analysis/ - 分析エンジン

**主要ツール**:
1. **intelligence_system.py**: インテリジェンス分析
2. **scoring_engine.py**: ニュース影響力スコアリング
3. **correlation_analyzer.py**: 複数銘柄の相関分析
4. **news_collector.py**: ニュース収集

```bash
# 市場連動性分析
python src/analysis/correlation_analyzer.py --market BTC ETH XRP DOGE SHIB

# ベータ分析（市場感応度）
python src/analysis/correlation_analyzer.py --beta DOGE --benchmark BTC
```

**indicators/** - テクニカル指標:
- ATR (Average True Range)
- OBV (On-Balance Volume)
- Stochastic Oscillator

---

### data/ - データ管理

**2層構造**:

1. **SQLite** (`advanced_database.py`): 詳細データの永続化
   - `price_history_detailed`: 複数時間足の価格データ
   - `news`: ニュース情報
   - `websearch_raw`: WebSearch結果の完全保存
   - `market_stats_detailed`: 市場統計

2. **Parquet** (`timeseries/`): 軽量・高速分析用
   - 89%のサイズ削減
   - pandas/NumPy直接対応
   - 数学的分析に最適

```bash
# SQLiteからParquetへ変換
python src/data/timeseries_manager.py --migrate

# データ確認
python src/data/timeseries_manager.py --info

# 詳細分析実行
python src/data/timeseries_manager.py --test BTC
```

---

### config/ - 設定

- `exchange_api.py`: MEXC API連携

---

### tools/ - ユーティリティ

- `market_scanner.py`: 全銘柄スキャン
- `auto_market_updater.py`: 自動マーケット更新

```bash
# 全銘柄をスキャン
python src/tools/market_scanner.py
```

---

## 📚 curriculum/ - 学習教材

### 対象
実際に手を動かして100円→1000円を達成したい実践者

### 構成

**Week形式**: 実践手順、ツールの使い方、失敗→改善のストーリー
- `week1_basics.md`: 100円→110円（✅ 完成）
- Week 2-4: 予定

**Chapter形式** (`stories/`): 技術の発明背景、数式の意味、実装方法
- Chapter 1-6: 全て完成 ✅

### 学習パターン

1. **実践優先型**: Week → Chapter → Week ...（初心者向け）
2. **理解優先型**: Chapter 1-6 → Week 1-4（中級者向け）
3. **ハイブリッド型**: Week と Chapter を交互に（推奨）

詳細: **[curriculum/README.md](curriculum/README.md)**

---

## 📖 docs/ - ドキュメント + 参照系

### システムドキュメント

**主要ドキュメント**:
- `analysis_workflow.md`: 実践的な分析ワークフロー
- `data_collection_guide.md`: データ収集方法
- `parquet_explained.md`: Parquet技術説明

### meta/ - 教材作成者向け

- `curriculum_creation_guide.md`: 教材作成ガイド
- `samples/`: Week/Chapter形式の詳細サンプル

### tests/ - テストコード

- `test_*.py`: 各種テスト
- `investment_priority_analysis.py`: 投資優先度分析

### archive/ - 旧システム

参考として残してあります：
- `main.py`: 旧メインシステム
- `strategies/`: 戦略ファイル
- `database.py`, `performance.py`, `report_generator.py`

---

## 🚀 クイックスタート

### 1. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

### 2. 学習者の場合

```bash
# Week 1を読む
cat curriculum/week1_basics.md

# Chapter 1-6を読む
cat curriculum/stories/01_investment_strategy.md
```

### 3. 分析を試す

```bash
# BTCを分析
python crypto_analyst.py BTC

# 詳細な技術分析
python src/data/timeseries_manager.py --test BTC

# 複数銘柄の相関分析
python src/analysis/correlation_analyzer.py --market BTC ETH XRP DOGE SHIB
```

---

## 🛠️ メインツール - crypto_analyst.py

統合分析ダッシュボード（ルートに配置）

```bash
# BTCの全情報を取得
python crypto_analyst.py BTC

# ETHの詳細タイムラインを表示
python crypto_analyst.py ETH --timeline

# SHIBのニュース1日分を取得
python crypto_analyst.py SHIB --news 1
```

**出力内容**:
- 💰 現在価格・24h統計
- 🎯 ニュース影響力スコア（大雑把な目安）
- 📰 最近のニュース（影響力順）
- 📉 30日間の価格動向

---

## 📝 ファイルの役割

### ルート直下のファイル

| ファイル | 役割 | 状態 |
|---------|------|------|
| `README.md` | プロジェクト全体の説明 | ✅ メイン |
| `PROJECT_STRUCTURE.md` | このファイル（構造説明） | ✅ 必須 |
| `crypto_analyst.py` | 統合分析ダッシュボード | ✅ メインツール |
| `requirements.txt` | 必要パッケージ | ✅ 必須 |
| `.gitignore` | Git除外設定 | ✅ 必須 |

---

## 💡 なぜこの構造？

### Before（旧構造）
```
grass-coin-trader/
├── analysis/       ← システムコード
├── config/         ← システムコード
├── data/           ← システムコード
├── tools/          ← システムコード
├── curriculum/     ← 学習コンテンツ
├── docs/           ← ドキュメント
├── tests/          ← テスト
└── old/            ← アーカイブ
```
**ルート直下：8個のディレクトリ** → 混乱しやすい

### After（新構造）
```
grass-coin-trader/
├── src/            ← システムコード（4つを統合）
├── curriculum/     ← 学習コンテンツ
└── docs/           ← ドキュメント + tests + archive（参照系を統合）
```
**ルート直下：3個のディレクトリ** → 一目で理解できる

---

## 📊 プロジェクトの実績

- ✅ 5銘柄のデータ収集・保存（BTC, ETH, XRP, DOGE, SHIB）
- ✅ 1050データポイント、77.9KB（Parquet形式）
- ✅ 相関分析で市場の連動性を実証（平均相関0.927）
- ✅ ベータ分析でリスク特性を定量化
- ✅ Week 1 + Chapter 1-6 完成

---

**Powered by Claude Code**

データを見て、一緒に考える。それが賢い投資の第一歩。
