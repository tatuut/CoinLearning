# 📚 プロジェクトドキュメント

**最終更新**: 2025-11-03

このディレクトリには、Grass Coin Traderプロジェクトの**すべてのドキュメント**が格納されています。

---

## 📋 このディレクトリの構造

```
docs/
├── README.md                        # ← このファイル（ドキュメント全体のマスター）
├── プロジェクト全体ガイド
│   ├── GETTING_STARTED.md           # セットアップ・使い方
│   ├── ROADMAP.md                   # 開発ロードマップ
│   └── ANALYSIS_METHODS.md          # 分析手法一覧
├── API・設定ガイド
│   └── MEXC_API_SETUP.md            # MEXC API設定
├── 教材作成関連
│   └── curriculum/                  # 教材作成マニュアル
│       ├── CURRICULUM_CREATION_MANUAL.md
│       ├── WEEK0_QUALITY_STANDARD.md
│       ├── analysis_report.md
│       └── 06_practical_forecasting_guide.md
├── アーカイブ
│   └── archive/                     # 古いドキュメント
└── ユーザー提供資料
    └── userimported/                # ユーザー要件・仕様
```

---

## 🎯 まず読むべきファイル

### 初めての方

1. **[GETTING_STARTED.md](./GETTING_STARTED.md)** - セットアップから基本的な使い方まで
2. **[../curriculum/README.md](../curriculum/README.md)** - カリキュラム全体の説明
3. **[../curriculum/LEARNING_PATH.md](../curriculum/LEARNING_PATH.md)** - 学習の進め方

### 開発者・貢献者

1. **[ROADMAP.md](./ROADMAP.md)** - プロジェクト開発の現在地と次のステップ
2. **[curriculum/CURRICULUM_CREATION_MANUAL.md](./curriculum/CURRICULUM_CREATION_MANUAL.md)** - 教材作成の品質基準

---

## 📖 ドキュメントカテゴリ

### 1. プロジェクト全体ガイド

#### [GETTING_STARTED.md](./GETTING_STARTED.md)
**何をするファイル**: プロジェクトのセットアップと基本的な使い方

**内容**:
- 環境準備とインストール
- データ収集の実行方法
- Streamlitダッシュボードの起動
- トラブルシューティング

**いつ読む**: プロジェクトを初めて使うとき

---

#### [ROADMAP.md](./ROADMAP.md)
**何をするファイル**: プロジェクト開発の進捗状況と計画

**内容**:
- Phase 1: データ収集基盤構築（✅ 完了）
- Phase 2: ダッシュボード統合（✅ 完了）
- Phase 3: Claude Code統合（🔄 進行中）
- Phase 4: 高度な分析機能（📝 未着手）
- Phase 5: 実践・教材完成（📝 未着手）

**いつ読む**: プロジェクトの全体像を把握したいとき

---

#### [ANALYSIS_METHODS.md](./ANALYSIS_METHODS.md)
**何をするファイル**: 利用可能な分析手法の全体像

**内容**:
- テクニカル指標（RSI, MACD, Bollinger Bands, ATR, OBV, Stochastic）
- 統計分析（相関分析、ボラティリティ）
- 時系列予測（ARIMA, GRU）
- ニュース分析
- ダッシュボードからの使い方

**いつ読む**: 分析手法を理解したいとき

---

### 2. API・設定ガイド

#### [MEXC_API_SETUP.md](./MEXC_API_SETUP.md)
**何をするファイル**: MEXC API Key設定の完全ガイド

**内容**:
- なぜAPI Keyが必要か（2FA問題の解決）
- API Key作成手順
- セキュリティ設定（IPアドレス制限、権限の最小化）
- API使用方法（Python/ccxt）
- ポートフォリオトラッキング実装
- トラブルシューティング

**いつ読む**: MEXC APIを設定したいとき

---

### 3. 教材作成関連

#### [curriculum/](./curriculum/) ディレクトリ

教材作成に関するドキュメントが格納されています。

##### [curriculum/CURRICULUM_CREATION_MANUAL.md](./curriculum/CURRICULUM_CREATION_MANUAL.md)
**何をするファイル**: カリキュラム作成の品質基準とプロセス

**内容**:
- 構造化された教材作成プロセス（plan → thought → draft → document）
- ストーリー構造の基本パターン
- 回想シーンの7ステップ構造
- 技術的説明の3段階アプローチ
- 反芻パターン
- Week 2以降の形式（理論と実践の統合）

**いつ読む**: 新しいWeek/Chapterを作成するとき

---

##### [curriculum/WEEK0_QUALITY_STANDARD.md](./curriculum/WEEK0_QUALITY_STANDARD.md)
**何をするファイル**: Week 0カリキュラムの品質基準

**内容**:
- 合格/不合格の明確な基準
- 自己テスト問題
- 3段階のレベル定義（最低限、基本、高品質）

**いつ読む**: Week 0の品質確認をするとき

---

##### [curriculum/06_practical_forecasting_guide.md](./curriculum/06_practical_forecasting_guide.md)
**何をするファイル**: ARIMA/GARCH & GRU予測エンジンの実践的な使い方

**内容**:
- forecasting.py（ARIMA/GARCH）の使い方
- gru_forecaster.py（GRU機械学習）の使い方
- 2つのツールの比較
- 実際のトレードへの活かし方

**いつ読む**: 価格予測ツールを実際に使いたいとき

---

##### [curriculum/analysis_report.md](./curriculum/analysis_report.md)
**何をするファイル**: Week 0カリキュラムの分析レポート

**内容**:
- Week 0の構造分析
- ストーリーテリングパターンの抽出
- 改善点の提案

**いつ読む**: Week 0の構造を理解したいとき

---

### 4. アーカイブ・参考資料

#### [archive/](./archive/) ディレクトリ

古い資料や参考資料が格納されています。

**内容**:
- CURRICULUM_REDESIGN.md（カリキュラム再構成計画）
- CURRICULUM_RESTRUCTURE_PLAN.md（Week 0追加後の整合性確保計画）
- DOCS_INDEX.md（旧インデックス）
- TASKS.md（タスク管理）
- curriculum_creation_guide.md（教材作成ガイド旧版）
- README_CLAUDE_CODE.md（Claude Code統合初期構想）
- samples/（教材サンプル）

**いつ見る**: 過去のバージョンや初期構想を参照したいとき

---

### 5. ユーザー提供資料

#### [userimported/](./userimported/) ディレクトリ

ユーザーが提供した資料。

**内容**:
- CLAUDE_CODE_INTEGRATION_SPEC.md（Claude Code統合仕様）

**いつ見る**: ユーザー要件を確認したいとき

---

## 🔗 カリキュラムとの連携

**このdocs/ディレクトリは「作り方」を定義し、curriculum/ディレクトリは「学び方」を定義します。**

```
docs/                           # 「作り方」のドキュメント
├── curriculum/                 # 教材の「作り方」
│   └── CURRICULUM_CREATION_MANUAL.md
    ↓ 品質基準に従って作成
curriculum/                     # 「学び方」のドキュメント
├── README.md                   # カリキュラム全体のマスター
├── LEARNING_PATH.md            # 学習の進め方
├── CONCEPT_TREE.md             # 習得状況の管理
└── textbook/                   # 実際の教材
    ├── 00_foundations.md
    └── 01_first_purchase/
```

### 重要なリンク

- **[../curriculum/README.md](../curriculum/README.md)** - カリキュラム全体の説明
- **[../curriculum/ROADMAP_TO_REALITY.md](../curriculum/ROADMAP_TO_REALITY.md)** - 100円→10000円への現実的なロードマップ
- **[../curriculum/LEARNING_PATH.md](../curriculum/LEARNING_PATH.md)** - 学習全体の地図
- **[../curriculum/CONCEPT_TREE.md](../curriculum/CONCEPT_TREE.md)** - 概念チェックリスト

---

## 🎯 用途別ガイド

### プロジェクトを初めて使う

1. **[GETTING_STARTED.md](./GETTING_STARTED.md)** でセットアップ
2. **[../curriculum/textbook/00_foundations.md](../curriculum/textbook/00_foundations.md)** でWeek 0を学習
3. **[ANALYSIS_METHODS.md](./ANALYSIS_METHODS.md)** で分析手法を確認

### カリキュラムを学習したい

1. **[../curriculum/README.md](../curriculum/README.md)** で全体像を把握
2. **[../curriculum/ROADMAP_TO_REALITY.md](../curriculum/ROADMAP_TO_REALITY.md)** で現実的な道筋を理解
3. **[../curriculum/LEARNING_PATH.md](../curriculum/LEARNING_PATH.md)** で学習計画を確認
4. **[../curriculum/textbook/](../curriculum/textbook/)** で教材を読む

### カリキュラムを作成したい

1. **[curriculum/CURRICULUM_CREATION_MANUAL.md](./curriculum/CURRICULUM_CREATION_MANUAL.md)** で作成マニュアルを読む
2. **[curriculum/WEEK0_QUALITY_STANDARD.md](./curriculum/WEEK0_QUALITY_STANDARD.md)** で品質基準を確認
3. **[curriculum/analysis_report.md](./curriculum/analysis_report.md)** でWeek 0の構造を理解

### API連携・ポートフォリオトラッキング

1. **[MEXC_API_SETUP.md](./MEXC_API_SETUP.md)** でAPI設定

### プロジェクト開発に参加したい

1. **[ROADMAP.md](./ROADMAP.md)** で開発ロードマップを確認
2. **[GETTING_STARTED.md](./GETTING_STARTED.md)** で開発環境をセットアップ

---

## 📝 ドキュメント管理ルール

### 新規ドキュメント追加時

1. 適切なカテゴリに配置
2. このREADME.mdに追記
3. 必要に応じて上位ディレクトリのREADME.mdにもリンク追加

### ドキュメント更新時

1. 最終更新日を記載
2. 変更内容が大きい場合はgitコミットメッセージに詳細を記載

### 古くなったドキュメント

1. `archive/` ディレクトリに移動
2. このREADME.mdから削除（archive/への言及は残す）

---

## ⚠️ 注意事項

### このREADME.mdの役割

このファイルは**プロジェクトドキュメント全体のマスターファイル**です。

- すべてのドキュメントへのリンクを提供
- カテゴリ別に整理
- 「何をするファイルか」「いつ読むか」を明確化

### curriculum/との違い

- **docs/**: プロジェクト全体、開発、教材「作成」のドキュメント
- **curriculum/**: 学習者向け、教材「本体」

### 迷ったら

このREADME.mdに戻って全体像を確認してください。カテゴリ別の分類で、目的のドキュメントがすぐに見つかるはずです。

---

**最終更新**: 2025-11-03
**作成者**: Claude Code（with tatut）

**次に読むファイル**: [GETTING_STARTED.md](./GETTING_STARTED.md)（初めての方）または [../curriculum/README.md](../curriculum/README.md)（学習者）
