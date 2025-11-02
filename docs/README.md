# 📚 ドキュメント インデックス

**Grass Coin Trader プロジェクトの全ドキュメント一覧**

このREADMEは、`docs/`ディレクトリ内のすべてのファイルとサブディレクトリへのリンクを提供します。

---

## 📖 目次

1. [プロジェクト全体ガイド](#プロジェクト全体ガイド)
2. [カリキュラム関連](#カリキュラム関連)
3. [API・設定関連](#api設定関連)
4. [分析手法関連](#分析手法関連)
5. [アーカイブ・参考資料](#アーカイブ参考資料)
6. [ユーザーインポート](#ユーザーインポート)

---

## 📘 プロジェクト全体ガイド

### [GETTING_STARTED.md](./GETTING_STARTED.md)
セットアップから基本的な使い方まで、初めての方向けの完全ガイド。

**内容:**
- 環境準備とインストール手順
- データ収集の実行方法
- Streamlitダッシュボードの起動方法
- トラブルシューティング

**対象:** プロジェクト初心者、セットアップする方

---

### [ANALYSIS_METHODS.md](./ANALYSIS_METHODS.md)
利用可能な分析手法の全体像を網羅的に解説。

**内容:**
- テクニカル指標（RSI, MACD, Bollinger Bands, ATR, OBV, Stochastic）
- 統計分析（相関分析、ボラティリティ）
- 時系列予測（ARIMA, GRU）
- ニュース分析
- ダッシュボードからの使い方

**対象:** 分析手法を理解したい方

---

### [ROADMAP.md](./ROADMAP.md)
プロジェクトの開発フェーズと進捗状況を記録。

**内容:**
- Phase 1: データ収集基盤構築（完了）
- Phase 2: ダッシュボード統合（完了）
- Phase 3: Claude Code統合（進行中）
- Phase 4: 高度な分析機能（未着手）
- Phase 5: 実践・教材完成（未着手）

**対象:** プロジェクトの全体像を把握したい方

---

### [TASKS.md](./TASKS.md)
プロジェクトの全タスクを一元管理するファイル。

**内容:**
- 現在進行中のタスク
- Phase別タスク
- 優先順位
- 既知の問題

**対象:** プロジェクトの現在地と次のステップを確認したい方

---

### [DOCS_INDEX.md](./DOCS_INDEX.md)
旧インデックスファイル。より詳細な分類でドキュメントを整理。

**内容:**
- 教材作成ガイド（meta/）
- 設計書（design/）
- 実装ガイド（implementation/）
- 使い方ガイド（guides/）

**対象:** より詳細なドキュメント分類を見たい方

---

## 📚 カリキュラム関連

### [CURRICULUM_REDESIGN.md](./CURRICULUM_REDESIGN.md)
カリキュラム再構成計画。Week 0追加に伴う変更点を解説。

**内容:**
- 現状の問題点（知識ゼロでいきなり購入）
- 改善の方向性（基礎知識 → デモ体験 → 少額実践 → 動的学習）
- Week 0: 基礎知識の追加
- ポートフォリオトラッキング実装
- MEXC API連携

**対象:** カリキュラムの全体構成を理解したい方

---

### [CURRICULUM_RESTRUCTURE_PLAN.md](./CURRICULUM_RESTRUCTURE_PLAN.md)
Week 0追加後の既存カリキュラム整合性確保計画。

**内容:**
- 現状分析（Week 0-7の内容重複・矛盾）
- 新カリキュラム構成（Phase 1-4）
- 各Weekの再構成内容
- 実装タスク

**対象:** カリキュラム修正作業をする方

---

### curriculum/

カリキュラムファイルが格納されたディレクトリ。

#### [curriculum/CURRICULUM_CREATION_MANUAL.md](./curriculum/CURRICULUM_CREATION_MANUAL.md)
カリキュラム作成の品質基準とフィードバック改善プロセス。

**内容:**
- 骨子ファーストアプローチ
- ストーリー性の強化
- 歴史上の人物を登場人物として活用
- 品質チェックリスト
- フィードバック改善プロセス

**対象:** 新しいWeek/Chapterを作成する方

---

#### [curriculum/WEEK0_QUALITY_STANDARD.md](./curriculum/WEEK0_QUALITY_STANDARD.md)
Week 0カリキュラムの品質基準。

**内容:**
- 合格/不合格の明確な基準
- 自己テスト問題
- 3段階のレベル定義（最低限、基本、高品質）

**対象:** Week 0の品質確認をする方

---

#### [curriculum/06_practical_forecasting_guide.md](./curriculum/06_practical_forecasting_guide.md)
ARIMA/GARCH & GRU予測エンジンの実践的な使い方ガイド。

**内容:**
- forecasting.py（ARIMA/GARCH）の使い方
- gru_forecaster.py（GRU機械学習）の使い方
- 2つのツールの比較
- 実際のトレードへの活かし方
- よくある質問

**対象:** 価格予測ツールを実際に使いたい方

---

#### [curriculum/backup/](./curriculum/backup/)
カリキュラムのバックアップファイル。

**内容:**
- 01_start_and_strategy.md.backup
- 02_rsi.md.backup
- 03_macd.md.backup
- 04_bollinger_bands.md.backup

**対象:** 過去のバージョンを参照したい方

---

## 🔐 API・設定関連

### [MEXC_API_SETUP.md](./MEXC_API_SETUP.md)
MEXC API Key設定の完全ガイド。

**内容:**
- なぜAPI Keyが必要か（2FA問題の解決）
- API Key作成手順
- セキュリティ設定（IPアドレス制限、権限の最小化）
- API使用方法（Python/ccxt）
- ポートフォリオトラッキング実装
- トラブルシューティング

**対象:** MEXC APIを設定したい方、ポートフォリオトラッキングを実装したい方

---

## 📊 分析手法関連

### [ANALYSIS_METHODS.md](./ANALYSIS_METHODS.md)
（プロジェクト全体ガイドを参照）

---

## 🗄️ アーカイブ・参考資料

### archive/

古い資料や参考資料が格納されたディレクトリ。

#### [archive/curriculum_creation_guide.md](./archive/curriculum_creation_guide.md)
教材作成の標準手順（旧版）。

**内容:**
- Week形式とChapter形式の使い分け
- 段階的作成フロー
- 詳細な骨子作成

**対象:** 旧版の教材作成ガイドを参照したい方

---

#### [archive/README_CLAUDE_CODE.md](./archive/README_CLAUDE_CODE.md)
Claude Code統合の初期構想資料。

**対象:** Claude Code統合の初期アイデアを確認したい方

---

#### [archive/samples/](./archive/samples/)
教材作成サンプル。

**内容:**
- week_format_detailed_example.md - Week形式の詳細サンプル
- chapter_format_detailed_example.md - Chapter形式の詳細サンプル

**対象:** 教材作成時のテンプレートとして参照したい方

---

## 📥 ユーザーインポート

### userimported/

ユーザーが提供した資料。

#### [userimported/CLAUDE_CODE_INTEGRATION_SPEC.md](./userimported/CLAUDE_CODE_INTEGRATION_SPEC.md)
Claude Code統合仕様（ユーザー提供）。

**内容:**
- Claude Code SDKの仕様
- 統合要件
- API仕様

**対象:** ユーザー要件を確認したい方

---

## 🗂️ ディレクトリ構造

```
docs/
├── README.md                          ← このファイル
├── DOCS_INDEX.md                      ← 旧インデックス（より詳細な分類）
│
├── プロジェクト全体ガイド
│   ├── GETTING_STARTED.md             ← セットアップ・使い方ガイド
│   ├── ANALYSIS_METHODS.md            ← 分析手法の全体像
│   ├── ROADMAP.md                     ← 開発ロードマップ
│   └── TASKS.md                       ← タスク管理
│
├── カリキュラム関連
│   ├── CURRICULUM_REDESIGN.md         ← カリキュラム再構成計画
│   ├── CURRICULUM_RESTRUCTURE_PLAN.md ← Week 0追加後の整合性確保計画
│   └── curriculum/
│       ├── CURRICULUM_CREATION_MANUAL.md  ← カリキュラム作成マニュアル
│       ├── WEEK0_QUALITY_STANDARD.md      ← Week 0品質基準
│       ├── 06_practical_forecasting_guide.md ← 価格予測ツール実践ガイド
│       └── backup/                         ← カリキュラムバックアップ
│
├── API・設定関連
│   └── MEXC_API_SETUP.md              ← MEXC API設定ガイド
│
├── archive/                           ← アーカイブ・参考資料
│   ├── curriculum_creation_guide.md   ← 教材作成ガイド（旧版）
│   ├── README_CLAUDE_CODE.md          ← Claude Code統合初期構想
│   └── samples/                       ← 教材サンプル
│
└── userimported/                      ← ユーザー提供資料
    └── CLAUDE_CODE_INTEGRATION_SPEC.md ← Claude Code統合仕様
```

---

## 🎯 用途別クイックリンク

### 初めてプロジェクトを使う
1. [GETTING_STARTED.md](./GETTING_STARTED.md) - セットアップ手順
2. [ANALYSIS_METHODS.md](./ANALYSIS_METHODS.md) - 分析手法の概要
3. [curriculum/06_practical_forecasting_guide.md](./curriculum/06_practical_forecasting_guide.md) - 予測ツールの使い方

### カリキュラムを学習したい
1. [CURRICULUM_REDESIGN.md](./CURRICULUM_REDESIGN.md) - カリキュラムの全体像
2. [curriculum/WEEK0_QUALITY_STANDARD.md](./curriculum/WEEK0_QUALITY_STANDARD.md) - Week 0から始める

### カリキュラムを作成したい
1. [curriculum/CURRICULUM_CREATION_MANUAL.md](./curriculum/CURRICULUM_CREATION_MANUAL.md) - 作成マニュアル
2. [archive/samples/](./archive/samples/) - サンプルを参照
3. [CURRICULUM_RESTRUCTURE_PLAN.md](./CURRICULUM_RESTRUCTURE_PLAN.md) - 整合性確保

### API連携・ポートフォリオトラッキング
1. [MEXC_API_SETUP.md](./MEXC_API_SETUP.md) - API設定ガイド
2. [CURRICULUM_REDESIGN.md](./CURRICULUM_REDESIGN.md) - ポートフォリオトラッキング実装計画

### プロジェクト開発に参加したい
1. [ROADMAP.md](./ROADMAP.md) - 開発ロードマップ
2. [TASKS.md](./TASKS.md) - 現在のタスク
3. [DOCS_INDEX.md](./DOCS_INDEX.md) - 設計書・実装ガイド

---

## 📝 カテゴリ分類の理由

### プロジェクト全体ガイド
プロジェクト全体に関わる基本的なドキュメント。初めて使う方、全体像を把握したい方向け。

### カリキュラム関連
100円→1000円チャレンジの教材に関するドキュメント。学習者、教材作成者向け。

### API・設定関連
外部API（MEXC）との連携、設定に関するドキュメント。実践者向け。

### 分析手法関連
データ分析、予測ツールの使い方に関するドキュメント。分析者向け。

### アーカイブ・参考資料
古い資料や参考資料。過去のバージョンを参照したい方、歴史を知りたい方向け。

### ユーザーインポート
ユーザーが提供した資料。要件確認、仕様理解向け。

---

## ⚠️ 注意事項

### archiveについて
`docs/archive/` には古い資料が保存されています。最新情報は必ず `docs/` 直下のファイルを参照してください。

### 更新ルール
- ドキュメント更新時は、このREADME.mdも更新する
- 新規ドキュメント追加時は、適切なカテゴリに分類して追記
- 古くなったドキュメントは `archive/` に移動

### 迷ったら
このREADME.mdに戻って全体像を確認してください。カテゴリ別の分類で、目的のドキュメントがすぐに見つかるはずです。

---

**最終更新**: 2025-11-02
**作成者**: Claude Code (with tatut)
