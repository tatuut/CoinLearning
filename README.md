# 🪙 草コイントレーダー - 100円→1000円への道

**Claude Codeと一緒に分析する、仮想通貨インテリジェンスシステム**

---

## 🎯 このシステムの特徴

**「答えを出すツール」ではなく、「分析材料を揃えるアシスタント」**

- ✅ 40銘柄の1分足データを自動収集（3000日分 ≈ 8年）
- ✅ 1分足→任意時間足への自動変換（5m, 15m, 1h, 4h, 1d）
- ✅ **自動検出**: src/analysis/配下の分析ツールを自動認識
- ✅ **高度な分析**: RSI, MACD, Bollinger Bands, ARIMA, GRU予測
- ✅ **軽量保存**: Parquet形式で時系列データ圧縮（89%削減）
- ✅ **インタラクティブUI**: Streamlit WebダッシュボードX
- ✅ Claude Codeと対話しながら分析

---

## 🚀 クイックスタート

### 必要なパッケージ

```bash
pip install -r requirements.txt
```

または個別に:

```bash
pip install requests numpy pandas pyarrow streamlit plotly torch scikit-learn statsmodels
```

### 基本的な使い方

```bash
# 1. 全銘柄のデータを一括取得（初回は3000日分、2回目以降は差分のみ）
python src/data/minute_data_collector.py

# 2. ダッシュボードを起動
streamlit run dashboard/main.py

# 3. ブラウザで http://localhost:8501 にアクセス
#    → 銘柄選択、時間足選択、チャート表示、分析ツール実行
```

---

## 📊 主要機能

### 1. 1分足データ収集システム

**symbols.txtで銘柄を一元管理（40銘柄）**

- 初回: 3000日分の全データを取得
- 2回目以降: 差分のみ取得（効率的）
- リアルタイム出力でprogress確認

```bash
# 全銘柄取得（symbols.txtから自動読み込み）
python src/data/minute_data_collector.py

# 特定銘柄のみ取得
python src/data/minute_data_collector.py --symbols BTC,ETH

# データサマリー表示
python src/data/minute_data_collector.py --summary
```

**保存先**: `src/data/timeseries/prices/{SYMBOL}_1m.parquet`

### 2. 時間足の自動変換

**1分足データから任意の時間足を生成**

ダッシュボードで時間足を選択すると、自動的にresampleして表示：

- 1m（1分足）- そのまま表示
- 5m, 15m（短期トレード）
- 1h, 4h（デイトレード）
- 1d（スイングトレード）

メリット：
- ストレージ節約（1分足のみ保存）
- 柔軟な分析（いつでも好きな時間足に変換）
- データ整合性保証（変換ロジックが一元化）

### 3. 統合ダッシュボード（Streamlit UI）

```bash
streamlit run dashboard/main.py
```

**機能**:
- ✅ ローソク足チャート（Plotly）
- ✅ テクニカル指標（RSI, MACD, Bollinger Bands, 移動平均）
- ✅ 統計情報ダッシュボード
- ✅ ARIMA/GARCH価格予測
- ✅ 保存されたニュース一覧
- ✅ **分析ツール自動検出** - src/analysis/配下のツールを自動表示

**ブラウザで http://localhost:8501 にアクセス**

### 4. 分析ツール自動検出

**src/analysis/配下の分析ツールを自動認識**

ダッシュボードが以下を自動で検出してカテゴリ別に表示：

- **予測**: ARIMA/GARCH予測, GRU深層学習予測
- **統計分析**: 複数銘柄の相関分析, ベータ分析
- **テクニカル指標**: ATR, OBV, ストキャスティクス
- **ニュース分析**: センチメント分析, スコアリング

新しい分析ツールを追加すると、自動的にダッシュボードに反映されます。

詳細は **[docs/ANALYSIS_METHODS.md](docs/ANALYSIS_METHODS.md)** を参照

### 5. 高精度価格予測

**2つの予測モデル**

#### ARIMA/GARCH（伝統的統計モデル）
- 時系列データの自己相関を利用
- 7日間の価格予測
- 95%信頼区間付き

#### GRU（深層学習モデル）
- **ARIMAの24倍の精度**（MAPE 0.09% vs 2.15%）
- Research: "High-Frequency Cryptocurrency Price Forecasting" (MDPI, 2024)
- リアルタイム予測

詳細は **[curriculum/07_advanced_mathematical_methods.md](curriculum/07_advanced_mathematical_methods.md)** を参照

---

## 📁 プロジェクト構成

```
grass-coin-trader/
├── dashboard/                       # 📊 メインダッシュボード
│   └── main.py                      # Streamlit UI
│
├── src/                             # 🔧 システムコア
│   ├── analysis/                   # 分析エンジン
│   │   ├── forecasting.py          # ARIMA/GARCH予測
│   │   ├── gru_forecaster.py       # GRU深層学習予測
│   │   ├── correlation_analyzer.py # 相関分析
│   │   ├── news_collector.py       # ニュース収集
│   │   ├── scoring_engine.py       # スコアリング
│   │   └── indicators/             # テクニカル指標
│   │       ├── atr.py              # ATR（ボラティリティ）
│   │       ├── obv.py              # OBV（出来高）
│   │       └── stochastic.py       # ストキャスティクス
│   │
│   ├── data/                       # データ管理
│   │   ├── minute_data_collector.py # 1分足データ収集
│   │   ├── timeseries_storage.py    # Parquetストレージ
│   │   └── timeseries/
│   │       └── prices/              # Parquetファイル
│   │
│   ├── config/                     # 設定
│   │   └── exchange_api.py
│   │
│   └── tools/                      # ユーティリティ
│
├── claude-chat/                     # 🤖 Claude Code統合
│   ├── backend/                    # WebSocketサーバー
│   ├── cli/                        # CLIクライアント
│   └── streamlit/                  # Streamlit Chat UI
│
├── symbols.txt                      # 対象銘柄リスト（40銘柄）
│
├── curriculum/                      # 📚 カリキュラム（学習教材）
│   ├── README.md                    # ← カリキュラム全体のマスターファイル
│   ├── LEARNING_PATH.md             # 学習パス（3階層構造）
│   ├── CONCEPT_TREE.md              # 概念チェックリスト
│   ├── ROADMAP_TO_REALITY.md        # 現実的な100円→10000円ロードマップ
│   └── textbook/                    # 教材本体
│       ├── README.md                # 教材一覧
│       ├── 00_foundations.md        # Week 0: 基礎知識
│       └── 01_first_purchase/       # Week 1: 初めての購入
│
└── docs/                            # 📖 プロジェクトドキュメント
    ├── README.md                    # ← ドキュメント全体のマスターファイル
    ├── GETTING_STARTED.md           # セットアップ・使い方
    ├── ROADMAP.md                   # 開発ロードマップ
    ├── ANALYSIS_METHODS.md          # 分析手法ガイド
    ├── MEXC_API_SETUP.md            # MEXC API設定
    ├── curriculum/                  # 教材作成マニュアル
    ├── archive/                     # 古いドキュメント
    └── userimported/                # ユーザー提供資料
```

---

## 🔄 実践的ワークフロー

### シナリオ1: 朝のマーケットチェック

```bash
# ダッシュボード起動
streamlit run dashboard/main.py

# → BTC, ETHを確認
# → RSI, MACDの値を見る
# → 高度な分析ツールで相関を確認
```

### シナリオ2: 新規購入を検討

```bash
# 1. 最新データ取得
python src/data/minute_data_collector.py --symbols SHIB

# 2. ダッシュボードで分析
#    - 1日足でトレンド確認
#    - RSI > 70 → 買われすぎ？
#    - MACD確認

# 3. GRU予測を実行
#    - 7日間の価格予測を確認
#    - 信頼区間内か？

# 4. Claude Codeと一緒に判断
「このRSI値と価格トレンド、どう見る？」
「今買うべき？それとも待つべき？」
```

### シナリオ3: ポートフォリオのリスク分析

```bash
# ダッシュボードで相関分析ツールを実行
# → BTC, ETH, DOGEの相関係数を確認
# → 相関 > 0.7 → 分散投資効果は限定的
```

---

## 📚 カリキュラム - 100円から始める仮想通貨トレーディング

**→ [curriculum/README.md](curriculum/README.md) を参照（カリキュラム全体のマスターファイル）**

### 📖 学習の進め方

1. **[curriculum/README.md](curriculum/README.md)** - カリキュラム全体の説明
   - カリキュラムの特徴、現実的な期待値、限界

2. **[curriculum/ROADMAP_TO_REALITY.md](curriculum/ROADMAP_TO_REALITY.md)** - 100円→10000円への現実的なロードマップ
   - フェーズ1（100円→1000円）: テクニカル分析の基礎
   - フェーズ2（1000円→5000円）: ファンダメンタルズ・センチメント分析
   - フェーズ3（5000円→10000円）: 草コインへの挑戦

3. **[curriculum/LEARNING_PATH.md](curriculum/LEARNING_PATH.md)** - 学習パス（3階層構造）
   - Level 0: 抽象的大目標
   - Level 1: 具体的目標（3フェーズ）
   - Level 2: 概念チェックリスト & Week形式

4. **[curriculum/CONCEPT_TREE.md](curriculum/CONCEPT_TREE.md)** - 概念チェックリスト
   - Tree構造で習得状況を管理
   - 順不同（必要なものから学ぶ）

5. **[curriculum/textbook/](curriculum/textbook/)** - 教材本体
   - Week 0: 基礎知識（RSI, MACD, BOLL） ✅ 完了
   - Week 1: 初めての購入（100円チャレンジ） ✅ 完了
   - Week 1.5以降: 実践で必要になった内容を動的に追加

### 現在の進捗

- ✅ **Week 0-1**: 完了（フェーズ1の基礎）
- 📝 **Week 1.5以降**: あなた自身の実践（動的に作成）
- **習得率**: 24%（11/46 概念）

---

## 📚 ドキュメント

**→ [docs/README.md](docs/README.md) を参照（ドキュメント全体のマスターファイル）**

### 🎯 まず読むべきファイル

#### 初めての方
1. **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - セットアップ・使い方ガイド
2. **[curriculum/README.md](curriculum/README.md)** - カリキュラム全体の説明
3. **[curriculum/LEARNING_PATH.md](curriculum/LEARNING_PATH.md)** - 学習の進め方

#### 開発者・貢献者
1. **[docs/ROADMAP.md](docs/ROADMAP.md)** - プロジェクト開発ロードマップ
2. **[docs/curriculum/CURRICULUM_CREATION_MANUAL.md](docs/curriculum/CURRICULUM_CREATION_MANUAL.md)** - 教材作成マニュアル

### 📖 ドキュメントカテゴリ

- **プロジェクト全体ガイド**
  - [GETTING_STARTED.md](docs/GETTING_STARTED.md) - セットアップ・使い方
  - [ROADMAP.md](docs/ROADMAP.md) - 開発ロードマップ
  - [ANALYSIS_METHODS.md](docs/ANALYSIS_METHODS.md) - 分析手法一覧

- **API・設定ガイド**
  - [MEXC_API_SETUP.md](docs/MEXC_API_SETUP.md) - MEXC API設定

- **教材作成関連**
  - [docs/curriculum/](docs/curriculum/) - 教材作成マニュアル

- **カリキュラム（学習教材）**
  - [curriculum/](curriculum/) - 学習者向け教材

詳細は **[docs/README.md](docs/README.md)** を参照

---

## 💾 データ構造

### Parquet（軽量・高速分析用）

```
src/data/timeseries/prices/
├── BTC_1m.parquet    # BTCの1分足（全期間）
├── ETH_1m.parquet    # ETHの1分足（全期間）
├── ...               # 40銘柄分
```

**メリット**:
- 89%のサイズ削減
- カラム指向で高速読み取り
- pandas/NumPy直接対応
- 数学的分析に最適

**時間足変換**:
- 1分足データのみ保存
- 表示時に必要な時間足へresample
- ストレージ効率とデータ整合性を両立

---

## 🎨 分析結果の読み方

### RSI（相対力指数）

```
RSI > 70  → 買われすぎ（調整の可能性）
RSI < 30  → 売られすぎ（反発の可能性）
RSI 30-70 → 中立
```

### MACD

```
MACD > Signal    → 買いシグナル
MACD < Signal    → 売りシグナル
Histogram拡大    → トレンド強化
Histogram縮小    → トレンド弱化
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

## 🛠️ 技術スタック

- **Python 3.8+**
- **Binance API** - 価格データ取得（認証不要）
- **Parquet** - 高速分析用データストレージ
- **pandas** - データ分析
- **NumPy** - 数値計算
- **PyTorch** - 深層学習（GRU予測）
- **Streamlit** - WebダッシュボードUI
- **Plotly** - インタラクティブチャート

---

## 📊 実績

- ✅ 40銘柄の1分足データ管理（symbols.txt）
- ✅ 3000日分の履歴データ収集
- ✅ dashboard自動検出機能（分析ツールの自動認識）
- ✅ 1分足→任意時間足の自動変換
- ✅ GRU予測モデル実装（ARIMA比24倍精度）
- ✅ 7つのカリキュラム教材完成

---

**Powered by Claude Code**

データを見て、一緒に考える。それが賢い投資の第一歩。
