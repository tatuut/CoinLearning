# 🗺️ Grass Coin Trader プロジェクトロードマップ

**最終更新**: 2025-11-01

このプロジェクトの開発フェーズと進捗状況を記載します。

---

## 🎯 全体の流れ

```
✅ Phase 1: データ収集基盤構築
   ↓
✅ Phase 2: ダッシュボード統合
   ↓
🔄 Phase 3: Claude Code統合（進行中）
   ↓
📝 Phase 4: 高度な分析機能
   ↓
📝 Phase 5: 実践・教材完成
```

---

## ✅ Phase 1: データ収集基盤構築【完了】

### 実装内容

- ✅ 1分足データ収集システム
  - Binance API連携（認証不要）
  - 差分更新機能（既存データスキップ）
  - 3000日分の履歴取得

- ✅ symbols.txt銘柄管理
  - 40銘柄を一元管理
  - コメント行対応

- ✅ Parquetストレージ
  - 軽量データ保存（89%圧縮）
  - pandas直接対応
  - DatetimeIndex対応

- ✅ リアルタイム出力
  - Windowsでのライン・バッファリング
  - 進捗表示機能

### 成果物

- `src/data/minute_data_collector.py` - データ収集スクリプト
- `src/data/timeseries_storage.py` - Parquetストレージ
- `symbols.txt` - 40銘柄リスト

---

## ✅ Phase 2: ダッシュボード統合【完了】

### 実装内容

- ✅ Streamlit Webダッシュボード
  - ローソク足チャート（Plotly）
  - テクニカル指標表示（RSI, MACD, Bollinger Bands）
  - 移動平均線（SMA20, SMA50, EMA20）

- ✅ 時間足の自動変換
  - 1分足→任意時間足resample
  - 1m, 5m, 15m, 1h, 4h, 1d対応

- ✅ 分析ツール自動検出
  - src/analysis/配下のモジュール自動検出
  - カテゴリ別表示（予測/統計/ニュース/指標）
  - 動的importlib使用

- ✅ データ一括取得UI
  - ダッシュボードから全銘柄取得
  - プログレスバー表示

### 成果物

- `dashboard/main.py` - 統合ダッシュボード
- `docs/ANALYSIS_METHODS.md` - 分析手法ガイド

---

## 🔄 Phase 3: Claude Code統合【進行中】

### 目標

**Streamlit UIから別のClaude Codeインスタンスと対話できるようにする**

### 現状

- ✅ WebSocketサーバー実装（Node.js）
- ✅ Streamlit Chat UI
- ⏸️ セッション管理（一時停止中）

### 実装予定

```
┌─────────────────────────────────────────┐
│     Streamlit UI (claude_chat.py)       │
│     - チャット形式の対話                   │
└─────────────┬───────────────────────────┘
              │ WebSocket接続
              ↓
┌─────────────────────────────────────────┐
│   Node.js サーバー (server-cli.js)       │
│   - WebSocket受付                        │
│   - Claude CLIプロセス起動・管理          │
└─────────────┬───────────────────────────┘
              │ spawn('claude')
              ↓
┌─────────────────────────────────────────┐
│     Claude Code CLI (別プロセス)         │
│     - WebSearch機能                      │
│     - ファイル操作（Read, Write, Edit）  │
└─────────────────────────────────────────┘
```

### タスク

- [ ] セッション管理の実装
- [ ] WebSearch有効化
- [ ] ニュース分析の自動化

### 成果物（予定）

- ✅ `claude-chat/backend/server-cli.js`
- ✅ `claude-chat/streamlit/claude_chat.py`
- ⏸️ セッション履歴管理

---

## 📝 Phase 4: 高度な分析機能【未着手】

### 実装予定

#### A. ARIMA/GARCH予測の改善

**現状**: 基本実装済み（forecasting.py）

**改善内容**:
- モデル自動選択（AIC/BIC基準）
- 複数モデルのアンサンブル
- 予測精度の可視化

#### B. GRU深層学習予測の実装

**現状**: gru_forecaster.py実装済み

**改善内容**:
- 学習データ拡張
- ハイパーパラメータ調整
- リアルタイム予測API

#### C. 高度な統計分析

**新規実装**:
- VaR（バリュー・アット・リスク）計算
- CVaR（条件付きVaR）
- ドローダウン分析
- 共分散行列の可視化

**実装先**: `src/analysis/risk_metrics.py`（新規）

#### D. ポートフォリオ最適化

**新規実装**:
- 複数銘柄の最適配分計算
- 効率的フロンティアの描画
- シャープレシオ最大化

**実装先**: `src/analysis/portfolio_optimizer.py`（新規）

### 成果物（予定）

- `src/analysis/risk_metrics.py`
- `src/analysis/portfolio_optimizer.py`
- `docs/guides/advanced_analysis.md`

---

## 📝 Phase 5: 実践・教材完成【未着手】

### 目標

**実践と教材の両立で100円→1000円を達成できるシステムに**

### 実装予定

#### A. 実践機能

- [ ] バックテスト機能
  - 過去データでの戦略検証
  - リターン・リスクの可視化

- [ ] アラート機能
  - RSI閾値超え通知
  - 価格変動アラート

#### B. 教材作成

| 教材 | タイトル | 状態 |
|------|---------|------|
| Week 2 | 110円→150円（テクニカル） | 📝 未作成 |
| Week 3 | 150円→300円（統合分析） | 📝 未作成 |
| Week 4 | 300円→1000円（システム化） | 📝 未作成 |

### 成果物（予定）

- バックテスト機能
- アラート機能
- Week 2-4教材

---

## 📊 進捗管理

| フェーズ | 状態 | 完了率 | 備考 |
|---------|------|--------|------|
| Phase 1: データ収集基盤 | ✅ 完了 | 100% | 40銘柄・3000日分 |
| Phase 2: ダッシュボード | ✅ 完了 | 100% | 自動検出機能実装済み |
| Phase 3: Claude統合 | 🔄 進行中 | 50% | UI完成、セッション管理保留 |
| Phase 4: 高度分析 | 📝 未着手 | 0% | Phase 3完了後 |
| Phase 5: 実践・教材 | 📝 未着手 | 0% | Phase 4完了後 |

---

## 🎯 現在の優先順位

### 最優先

1. **データ収集完了の確認**
   - 40銘柄すべて取得完了しているか
   - データの完全性チェック

2. **カリキュラム学習**
   - 実装済み機能の学習
   - 数学的分析手法の理解

### 優先度: 高

3. **Claude Code統合の完成**
   - セッション管理の実装
   - ニュース分析の自動化

### 優先度: 中

4. **高度な分析機能の追加**
   - リスク指標（VaR, CVaR）
   - ポートフォリオ最適化

### 優先度: 低

5. **実践機能の追加**
   - バックテスト
   - アラート

---

## 🔗 関連ドキュメント

- [README.md](README.md) - プロジェクト概要
- [docs/ANALYSIS_METHODS.md](docs/ANALYSIS_METHODS.md) - 分析手法ガイド
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) - セットアップ・使い方
- [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md) - 全ドキュメント索引

---

**最終更新**: 2025-11-01
**作成者**: Claude Code（with tatut）
