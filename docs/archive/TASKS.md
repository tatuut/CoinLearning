# 📋 Grass Coin Trader - タスク管理

**最終更新**: 2025-11-01

このファイルは、プロジェクトの全タスクを一元管理します。

---

## 🚨 現在進行中のタスク

### Phase 1: データ収集完了

- [x] 数学的分析手段の概括ファイル作成（docs/ANALYSIS_METHODS.md）
- [x] dashboard自動検出機能の実装
- [x] ドキュメント整理（README, ROADMAP, GETTING_STARTED）
- [x] ADA破損問題の調査と修正（Snappy圧縮問題を特定・解決）
- [ ] **データ収集完了とシステム検証**（🔥 進行中）
  - [ ] 40銘柄すべての取得完了
  - [ ] データ完全性チェック
  - [ ] データ収集のGitコミット

**解決済み**: Snappy圧縮が大きなファイルで破損。無圧縮に変更し安定化。後から圧縮可能。

---

### Phase 2: カリキュラム＆ポートフォリオシステム（🆕 NEW）

**目標**: 動的カリキュラム＋リアルタイム保有資産管理

- [ ] **カリキュラム再構成計画の策定**
  - [ ] Week 0追加（基礎知識：買う前に学ぶ）
  - [ ] 既存Week 1-7の見直し
  - [ ] 動的カリキュラムの設計

- [ ] **MEXC API連携**
  - [ ] API Key設定ガイド作成
  - [ ] ポートフォリオトラッキング機能実装
  - [ ] 保有資産の自動取得・保存

- [ ] **インタラクティブUI強化**
  - [ ] Streamlitにポートフォリオ表示追加
  - [ ] リアルタイム損益グラフ
  - [ ] RSI/MACDスライダー操作

- [ ] **Claude統合: リアルタイム解説生成**
  - [ ] 保有データ見ながら分析解説
  - [ ] 状況に応じたmarkdown生成
  - [ ] インタラクティブ学習支援

---

## 📊 Phase別タスク

### ✅ Phase 1: データ収集基盤構築【完了 100%】

**実装済み**:
- [x] 1分足データ収集システム
  - [x] Binance API連携（認証不要）
  - [x] 差分更新機能（既存データスキップ）
  - [x] 3000日分の履歴取得
- [x] symbols.txt銘柄管理（40銘柄）
- [x] Parquetストレージ（89%圧縮）
- [x] リアルタイム出力とprogress表示
- [x] Windows対応（ライン・バッファリング）
- [x] パフォーマンス最適化（30-50x高速化）
- [x] 破損ファイルの自動検出・リネーム機能

**成果物**:
- `src/data/minute_data_collector.py`
- `src/data/timeseries_storage.py`
- `symbols.txt`

---

### ✅ Phase 2: ダッシュボード統合【完了 100%】

**実装済み**:
- [x] Streamlit Webダッシュボード
  - [x] ローソク足チャート（Plotly）
  - [x] テクニカル指標表示（RSI, MACD, Bollinger Bands）
  - [x] 移動平均線（SMA20, SMA50, EMA20）
- [x] 時間足の自動変換
  - [x] 1分足→任意時間足resample
  - [x] 1m, 5m, 15m, 1h, 4h, 1d対応
- [x] 分析ツール自動検出
  - [x] src/analysis/配下のモジュール自動検出
  - [x] カテゴリ別表示（予測/統計/ニュース/指標）
  - [x] 動的importlib使用
- [x] データ一括取得UI
  - [x] ダッシュボードから全銘柄取得
  - [x] プログレスバー表示

**成果物**:
- `dashboard/main.py`
- `docs/ANALYSIS_METHODS.md`
- `docs/GETTING_STARTED.md`

---

### 🔄 Phase 3: Claude Code統合【進行中 50%】

**目標**: Streamlit UIから別のClaude Codeインスタンスと対話できるようにする

**実装済み**:
- [x] WebSocketサーバー実装（Node.js）
  - [x] `claude-chat/backend/server-cli.js`
- [x] Streamlit Chat UI
  - [x] `claude-chat/streamlit/claude_chat.py`

**未実装**:
- [ ] セッション管理の実装（⏸️ 一時停止中）
  - [ ] セッション履歴の保存
  - [ ] 複数セッションの管理
  - [ ] セッションの再開機能
- [ ] WebSearch有効化
  - [ ] Claude CLIからWebSearchを実行
  - [ ] 検索結果の整形
- [ ] ニュース分析の自動化
  - [ ] ニュース取得の自動トリガー
  - [ ] センチメント分析の統合

**アーキテクチャ**:
```
Streamlit UI (claude_chat.py)
    ↓ WebSocket
Node.js サーバー (server-cli.js)
    ↓ spawn('claude')
Claude Code CLI
    ↓ WebSearch, Read, Write, Edit
```

---

### 📝 Phase 4: 高度な分析機能【未着手 0%】

#### A. ARIMA/GARCH予測の改善

**現状**: 基本実装済み（`src/analysis/forecasting.py`）

**改善タスク**:
- [ ] モデル自動選択（AIC/BIC基準）
- [ ] 複数モデルのアンサンブル
- [ ] 予測精度の可視化
- [ ] パラメータチューニングの自動化

#### B. GRU深層学習予測の改善

**現状**: 実装済み（`src/analysis/gru_forecaster.py`）

**改善タスク**:
- [ ] 学習データ拡張
- [ ] ハイパーパラメータ調整
- [ ] リアルタイム予測API
- [ ] モデルの保存・読み込み機能

#### C. 高度な統計分析（新規実装）

**実装タスク**:
- [ ] VaR（バリュー・アット・リスク）計算
- [ ] CVaR（条件付きVaR）
- [ ] ドローダウン分析
- [ ] 共分散行列の可視化
- [ ] シャープレシオ計算

**実装先**: `src/analysis/risk_metrics.py`（新規）

#### D. ポートフォリオ最適化（新規実装）

**実装タスク**:
- [ ] 複数銘柄の最適配分計算
- [ ] 効率的フロンティアの描画
- [ ] シャープレシオ最大化
- [ ] リスク制約下の最適化

**実装先**: `src/analysis/portfolio_optimizer.py`（新規）

**成果物（予定）**:
- `src/analysis/risk_metrics.py`
- `src/analysis/portfolio_optimizer.py`
- `docs/guides/advanced_analysis.md`

---

### 📝 Phase 5: 実践・教材完成【未着手 0%】

**目標**: 実践と教材の両立で100円→1000円を達成できるシステムに

#### A. 実践機能

**実装タスク**:
- [ ] バックテスト機能
  - [ ] 過去データでの戦略検証
  - [ ] リターン・リスクの可視化
  - [ ] 複数戦略の比較
  - [ ] レポート生成
- [ ] アラート機能
  - [ ] RSI閾値超え通知
  - [ ] 価格変動アラート
  - [ ] カスタムアラート設定UI
  - [ ] 通知方法の選択（メール、Slack等）

#### B. 教材作成

| 教材 | タイトル | 内容 | 状態 |
|------|---------|------|------|
| Week 1 | 100円→110円（基礎） | 取引所登録、初取引 | ✅ 完成 |
| 02 | RSIの基礎 | 相対力指数の理解と実践 | ✅ 完成 |
| 03 | MACDの基礎 | トレンド判定の実践 | ✅ 完成 |
| 04 | Bollinger Bands | ボラティリティ分析 | ✅ 完成 |
| 05 | ARIMA/GARCH | 統計的時系列予測 | ✅ 完成 |
| 06 | 統合分析 | 全指標の統合 | ✅ 完成 |
| 07 | GRU予測 | 深層学習予測 | ✅ 完成 |
| Week 2 | 110円→150円（テクニカル） | 高度なテクニカル分析 | 📝 未作成 |
| Week 3 | 150円→300円（統合分析） | 複合的な分析手法 | 📝 未作成 |
| Week 4 | 300円→1000円（システム化） | 自動化とリスク管理 | 📝 未作成 |

**成果物（予定）**:
- バックテスト機能
- アラート機能
- `curriculum/week2_advanced_technical.md`
- `curriculum/week3_integrated_analysis.md`
- `curriculum/week4_automation.md`

---

## 🎯 優先順位

### 最優先（今すぐ）

1. **データ収集完了の確認**
   - 40銘柄すべて取得完了しているか
   - データの完全性チェック
   - ADA破損問題の解決

2. **カリキュラム学習**（優先順位未定）
   - 実装済み機能の学習
   - 数学的分析手法の理解
   - 既存教材（Week 1, 02-07）の習得

### 優先度: 高

3. **Claude Code統合の完成**（Phase 3）
   - セッション管理の実装
   - WebSearch有効化
   - ニュース分析の自動化

### 優先度: 中

4. **高度な分析機能の追加**（Phase 4）
   - リスク指標（VaR, CVaR）
   - ポートフォリオ最適化
   - ARIMA/GARCH予測の改善
   - GRU深層学習予測の改善

### 優先度: 低

5. **実践機能の追加**（Phase 5）
   - バックテスト機能
   - アラート機能
   - Week 2-4教材作成

---

## 📊 進捗サマリー

| フェーズ | 状態 | 完了率 | 備考 |
|---------|------|--------|------|
| Phase 1: データ収集基盤 | ✅ 完了 | 100% | 40銘柄・3000日分、パフォーマンス最適化済み |
| Phase 2: ダッシュボード | ✅ 完了 | 100% | 自動検出機能実装済み |
| Phase 3: Claude統合 | 🔄 進行中 | 50% | UI完成、セッション管理保留 |
| Phase 4: 高度分析 | 📝 未着手 | 0% | Phase 3完了後 |
| Phase 5: 実践・教材 | 📝 未着手 | 0% | Phase 4完了後 |

---

## 🐛 既知の問題

### 重要度: 高

1. **ADA Parquetファイルの繰り返し破損**（🔥 対応中）
   - 症状: 保存中に `Unexpected end of stream` エラー
   - 影響: データ収集が中断される
   - 対応: 破損ファイルの自動リネームは実装済み、根本原因は調査中

### 重要度: 中

2. **並列データ収集時の衝突**
   - 症状: 同じファイルに複数プロセスが書き込もうとする
   - 対応: ユーザーが手動で管理（1プロセスのみ実行）

---

## 🔗 関連ドキュメント

- [ROADMAP.md](ROADMAP.md) - 開発ロードマップ（Phase別の詳細）
- [README.md](README.md) - プロジェクト概要
- [docs/ANALYSIS_METHODS.md](docs/ANALYSIS_METHODS.md) - 分析手法ガイド
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) - セットアップ・使い方
- [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md) - 全ドキュメント索引
- [curriculum/README.md](curriculum/README.md) - カリキュラム全体ガイド

---

## 📝 メモ・備考

### 2025-11-01

- dashboard自動検出機能を実装（importlib/inspect使用）
- パフォーマンス最適化実施（30-50x高速化）
- 破損ファイル対策実装（自動リネーム）
- ドキュメント整理完了（README, ROADMAP, GETTING_STARTED）
- データ収集中にADA破損問題が発生、調査中

---

**最終更新**: 2025-11-01
**作成者**: Claude Code（with tatut）
