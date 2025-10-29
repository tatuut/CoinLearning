# 🗺️ Grass Coin Trader プロジェクトロードマップ

**最終更新**: 2025-10-29

このプロジェクトは4段階で完成を目指します。

---

## 🎯 全体の流れ

```
⑴ Claude Code統合
   ↓
⑵ 数学的分析機能 + 教材
   ↓
⑶ ポートフォリオ理論教材
   ↓
⑷ 全機能テスト・完成
```

---

## ⑴ Claude Code統合【優先度：最高】

### 目標
**Streamlit UIから別のClaude Codeインスタンスと対話できるようにする**

### なぜ必要？
- ニュース分析を自動化したい
- WebSearchで最新情報を取得したい
- 対話的に分析を進めたい
- API料金を気にせず使いたい（Max 20x Plan利用）

### 実装内容

```
┌─────────────────────────────────────────────────────────┐
│                    ユーザー（あなた）                      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│              Streamlit UI (claude_chat.py)              │
│              - チャット形式の対話                          │
│              - 履歴表示・保存                             │
└─────────────────┬───────────────────────────────────────┘
                  │ WebSocket接続
                  ↓
┌─────────────────────────────────────────────────────────┐
│         Node.js サーバー (server-cli.js)                 │
│         - WebSocket受付                                  │
│         - Claude CLIプロセス起動・管理                    │
└─────────────────┬───────────────────────────────────────┘
                  │ spawn('claude')
                  ↓
┌─────────────────────────────────────────────────────────┐
│              Claude Code CLI (別プロセス)                 │
│              - セッション管理（--session-id）             │
│              - WebSearch機能（--allowed-tools WebSearch）│
│              - ファイル操作（Read, Write, Edit, Bash等）  │
└─────────────────────────────────────────────────────────┘
```

### タスク
- [x] ~~`server-interactive.js`で実装試み~~（失敗）
- [ ] `server-cli.js`をgit履歴から復元
- [ ] `--session-id`でセッション管理を実装
- [ ] `--allowed-tools WebSearch`でWebSearch有効化
- [ ] Streamlit UIから動作確認

### 成果物
- ✅ 動作する`backend/server-cli.js`
- ✅ WebSocket経由で対話可能
- ✅ セッション履歴保持
- ✅ StreamlitからClaude Codeと対話できるUI

---

## ⑵ 数学的分析機能の実装 + 教材作成【優先度：高】

### 目標
**高度な分析機能を実装し、使い方を教材にまとめる**

### 現状
✅ 基本的な技術指標は実装済み
- RSI, MACD, Bollinger Bands
- 移動平均、ATR, OBV, Stochastic
- 相関分析、ベータ分析

❌ 予測・機械学習は未実装

### 実装する機能

#### A. ARIMA/GARCHモデル（時系列予測）

```
過去の価格データ
    ↓
┌────────────────────┐
│   ARIMAモデル       │  価格のトレンド・季節性を予測
└────────────────────┘
    ↓
┌────────────────────┐
│   GARCHモデル       │  ボラティリティ（変動性）を予測
└────────────────────┘
    ↓
将来の価格レンジ予測
```

**実装先**: `sample/analysis/forecasting.py` を拡張

#### B. 高度な統計分析

- 共分散行列の計算
- VaR（バリュー・アット・リスク）計算
- CVaR（条件付きVaR）
- ドローダウン分析

**実装先**: `sample/analysis/risk_metrics.py`（新規）

#### C. 機械学習モデル

```
特徴量エンジニアリング
    ↓ (価格、RSI、MACD、出来高、ニュースセンチメント等)
┌────────────────────┐
│   LSTMモデル        │  時系列パターン学習
│   または            │
│   XGBoostモデル     │  非線形パターン学習
└────────────────────┘
    ↓
価格方向性の予測
```

**実装先**: `sample/analysis/ml_predictor.py`（新規）

### 作成する教材

| ファイル名 | 内容 | 対象読者 |
|-----------|------|----------|
| `docs/guides/arima_garch_guide.md` | ARIMA/GARCHの理論と実装 | 中級者 |
| `docs/guides/statistics_advanced.md` | 高度な統計分析（VaR等） | 中級者 |
| `docs/guides/machine_learning_crypto.md` | 機械学習による予測 | 中級者 |
| `curriculum/stories/07_forecasting_story.md` | 予測の歴史と実装（Chapter形式） | 初心者〜中級者 |

### 成果物
- ✅ 予測機能付き分析ツール
- ✅ 各機能の使い方がわかる教材

---

## ⑶ ポートフォリオ理論の教材作成【優先度：中】

### 目標
**ポートフォリオ管理の知識を教材にまとめる**

### なぜ必要？
- 複数銘柄をどう組み合わせるか
- リスク分散の数学的理解
- 効率的な資産配分

### 作成する教材

#### Chapter形式（ストーリー教材）

**`curriculum/stories/07_portfolio_theory.md`**

構成案：
```
Scene 1: マーコウィッツの悩み（1952年）
         → 分散投資の数学的定式化

Scene 2: 効率的フロンティアの発見
         → リスク・リターンの最適バランス

Scene 3: シャープレシオの誕生
         → リスク調整後リターンの測定

Scene 4-12: 実装・応用・実践
```

#### 実装ガイド

**`docs/guides/portfolio_optimization.md`**

内容：
- 共分散行列の計算
- 効率的フロンティアの描画
- ポートフォリオ最適化の実装（Python）
- 実践的なアセットアロケーション

### コード実装

**`sample/analysis/portfolio_optimizer.py`**（新規作成）

機能：
- 複数銘柄の最適配分計算
- リスク・リターンのシミュレーション
- 効率的フロンティアの可視化

### 成果物
- ✅ ポートフォリオ理論の教材（Chapter形式）
- ✅ 実践的な最適化ガイド
- ✅ 実装コード

---

## ⑷ 全機能の単体テスト・動作確認【優先度：最高】

### 目標
**各機能が単体で正しく動作することを確認**

### テスト項目一覧

```
✅ = 動作確認済み
❌ = 未確認
```

#### コア機能
- ✅ データ収集・保存（Parquet形式）
  - `python crypto_analyst.py BTC`

- ✅ 技術指標計算
  - `python data/timeseries_storage.py --test BTC`

- ✅ 相関分析・ベータ分析
  - `python analysis/correlation_analyzer.py --market BTC ETH`

- ✅ Streamlitダッシュボード
  - `streamlit run src/tools/parquet_dashboard.py`

#### 新機能（⑴⑵⑶で実装）
- ❌ Claude Code統合
  - `streamlit run ui/claude_chat.py`

- ❌ ARIMA/GARCH予測
  - `python sample/analysis/forecasting.py BTC --forecast 7`

- ❌ 機械学習モデル
  - `python sample/analysis/ml_predictor.py BTC --train`

- ❌ ポートフォリオ最適化
  - `python sample/analysis/portfolio_optimizer.py --symbols BTC ETH XRP`

### テストドキュメント作成

**`docs/tests/integration_tests.md`**

内容：
- 各機能のテスト手順
- 期待される結果
- トラブルシューティング

### 成果物
- ✅ テストスクリプト集
- ✅ テスト手順書
- ✅ 各機能の動作確認レポート
- ✅ すべての機能が単体で動作することの保証

---

## 📊 進捗管理

| フェーズ | 状態 | 完了予定 |
|---------|------|----------|
| ⑴ Claude Code統合 | 🔄 作業中 | 最優先 |
| ⑵ 数学的分析 + 教材 | 📝 未着手 | ⑴完了後 |
| ⑶ ポートフォリオ教材 | 📝 未着手 | ⑵完了後 |
| ⑷ 全機能テスト | 📝 未着手 | ⑶完了後 |

---

## 🎯 最終ゴール

### システムとして
- ✅ データ収集から分析、予測まで一貫したシステム
- ✅ Claude Codeとの対話で深い洞察を得られる
- ✅ すべての機能が単体でテスト済み

### 教材として
- ✅ Week 1-4：実践ガイド（100円→1000円）
- ✅ Chapter 1-7：技術ストーリー（発明の物語）
- ✅ 実装ガイド：各機能の詳細解説

### ユーザー体験
```
朝：streamlit run src/tools/parquet_dashboard.py
    → 保有銘柄の状況確認

昼：python crypto_analyst.py SHIB --timeline
    → 新規購入候補の調査

夕：streamlit run ui/claude_chat.py
    → Claude Codeと対話しながら判断
    「このRSI値をどう見る？」
    「ニュースの影響は？」

夜：python sample/analysis/portfolio_optimizer.py
    → ポートフォリオの最適化
```

---

## 🔗 関連ドキュメント

- [DOCS_INDEX.md](docs/DOCS_INDEX.md) - 全ドキュメント索引
- [README.md](README.md) - プロジェクト概要
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - ディレクトリ構造

---

**最終更新**: 2025-10-29
**作成者**: Claude Code（with tatut）
