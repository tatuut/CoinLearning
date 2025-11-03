# 📚 Grass Coin Trader ドキュメント索引

**最終更新**: 2025-10-28

このファイルは`docs/`ディレクトリ内の全ドキュメントを網羅的に整理した索引です。

---

## 📖 目次

1. [教材作成ガイド（meta/）](#教材作成ガイドmeta)
2. [設計書（design/）](#設計書design)
3. [実装ガイド（implementation/）](#実装ガイドimplementation)
4. [使い方ガイド（guides/）](#使い方ガイドguides)
5. [ユーザーインポート（userimported/）](#ユーザーインポートuserimported)
6. [テストドキュメント（tests/）](#テストドキュメントtests)

---

## 📚 教材作成ガイド（meta/）

### `curriculum_creation_guide.md` ⭐最重要
**目的**: 高品質な教材を段階的に作成するための標準手順書

**内容**:
- **Week形式**: 実践的ツール習得教材（10,000文字以上/Week）
  - 対象: 100円→1000円を実際に達成したい実践者
  - 5ステップ作成フロー
  - 詳細な骨子作成 → 各Part執筆 → 統合レビュー

- **Chapter形式**: 技術習得ストーリー（5,000-8,000文字/Chapter）
  - 対象: 技術の「なぜ」「どうやって」を深く理解したい学習者
  - 6ステップ作成フロー
  - 12シーン構成（発明の背景 → 数式 → 実装 → 使い方）

**使い方**:
- 新しい教材を作る前に必読
- Week形式とChapter形式の使い分け基準を確認
- 段階的作成で質を担保

**関連ファイル**:
- `samples/week_format_detailed_example.md` - Week形式の詳細サンプル
- `samples/chapter_format_detailed_example.md` - Chapter形式の詳細サンプル

---

### `samples/week_format_detailed_example.md`
**目的**: Week形式教材の具体例

**内容**:
- Week 1のフルサンプル（10,000文字超）
- ストーリー導入 → ツール説明 → 実践 → トラブルシューティング → 振り返り
- ユウタとミコの会話形式
- 実際のコマンド例、エラー対処法を含む

**使い方**: 新規Week作成時のテンプレートとして参照

---

### `samples/chapter_format_detailed_example.md`
**目的**: Chapter形式教材の具体例

**内容**:
- RSI発明の物語形式（5,000-8,000文字）
- 12シーン構成の実例
- 数式の導出 → Python実装 → 使い方
- ストーリーと技術解説のバランス

**使い方**: 新規Chapter作成時のテンプレートとして参照

---

## 🎨 設計書（design/）

### `ai_automation_architecture_story_v2.md`
**目的**: Claude Code SDK統合の全体構想（改訂版）

**内容**:
- Scene 1-8: 初期構想（手動実行 → 自動化への道）
- Scene 9: **Claude Agent SDK発見**（重要な転換点）
- Scene 10-15: Agent SDK統合計画
  - WebSearch + 感情分析 + DB保存の自動化
  - リアルタイムログ表示
  - Streamlit UI連携

**アーキテクチャ**:
```
Streamlit UI
    ↓
FastAPI (Python) - BackgroundTasks
    ↓
Node.js Express - Claude Agent SDK
    ↓
Claude API (Agentic実行)
    ↓
custom MCP tools (save_news_to_db)
    ↓
SQLite (crypto_data.db)
```

**使い方**: Phase 3実装の全体像を理解するために必読

---

### `REVISED_STRATEGY_STORY.md`
**目的**: プロジェクト戦略の見直し

**内容**:
- 当初の戦略の問題点
- 新戦略への転換理由
- 実践重視 vs 理論重視のバランス

**使い方**: プロジェクトの方向性を確認する際に参照

---

### `system_redesign_proposal.md`
**目的**: システム全体の再設計提案

**内容**:
- 現状の課題分析
- 新アーキテクチャ提案
- 移行計画

**使い方**: システム全体を見直す際に参照

---

## 🛠️ 実装ガイド（implementation/）

### `phase2_phase3_implementation_plan.md` ⭐最重要（最新）
**目的**: Phase 2/3の詳細実装計画とストーリー

**Phase 2内容**:
- FastAPI + BackgroundTasks + SQLite
- ジョブ管理システム（jobs.db）
- リアルタイムログ取得API
- ダミーワーカー実装

**Phase 3内容**:
- Node.js + Claude Agent SDK統合
- WebSearch + 感情分析 + DB保存
- custom MCP tools実装
- Streamlit UI連携

**実装状況**:
- ✅ Phase 2完了
- 🔄 Phase 3実装中（DBパスエラー修正中）

**使い方**: 現在の実装状況と次のステップを確認

---

### `implementation_roadmap.md`
**目的**: 全体実装ロードマップ

**内容**:
- Phase 1: データ収集基盤
- Phase 2: バックグラウンド実行基盤
- Phase 3: Claude Code SDK統合
- Phase 4-6: 高度な分析・運用

**使い方**: プロジェクト全体の進捗を把握

---

### `implementation_story.md`
**目的**: 実装の経緯をストーリー形式で記録

**内容**:
- なぜこの実装方法を選んだか
- 試行錯誤の記録
- 学んだこと

**使い方**: 実装の背景理解、将来の参考資料

---

### `NEXT_STEPS.md`
**目的**: 次にやるべきことのリスト

**内容**:
- 短期タスク（今週中）
- 中期タスク（今月中）
- 長期タスク（3ヶ月以内）

**使い方**: 作業優先順位の確認

---

## 📘 使い方ガイド（guides/）

### `analysis_workflow.md`
**目的**: 分析ワークフローの標準手順

**内容**:
- データ収集 → 前処理 → 分析 → 可視化の流れ
- 各ステップで使うツール
- トラブルシューティング

**使い方**: 分析作業の手順書として使用

---

### `data_collection_guide.md`
**目的**: データ収集の具体的手順

**内容**:
- APIの使い方
- データ形式
- 保存方法
- エラー対処

**使い方**: データ収集時の参考書

---

### `mathematical_foundation_first.md`
**目的**: 数学的基礎の学習ガイド

**内容**:
- 微分・積分の基礎
- 統計学の基礎
- 線形代数
- 金融数学への応用

**使い方**: 技術指標の理解を深めるための基礎学習

---

### `parquet_explained.md`
**目的**: Parquetフォーマットの解説

**内容**:
- Parquetとは何か
- なぜParquetを使うのか
- 使い方
- 最適化Tips

**使い方**: データ保存形式の選択理由を理解

---

## 📥 ユーザーインポート（userimported/）

### `CLAUDE_CODE_INTEGRATION_SPEC.md`
**目的**: ユーザーが提供したClaude Code統合仕様

**内容**:
- Claude Code SDKの仕様
- 統合要件
- API仕様

**使い方**: ユーザー要件の確認、実装時の参照

---

## 🧪 テストドキュメント（tests/）

### `README.md`
**目的**: テスト方針とテストケース

**内容**:
- テスト戦略
- テストケース一覧
- テスト実行方法

**使い方**: テスト実施時の手順書

---

## 🗂️ ディレクトリ構造

```
docs/
├── DOCS_INDEX.md          ← このファイル
├── README.md              ← docsディレクトリの概要
│
├── meta/                  ← 教材作成のメタ情報
│   ├── curriculum_creation_guide.md  ⭐教材作成の標準手順
│   └── samples/
│       ├── week_format_detailed_example.md
│       └── chapter_format_detailed_example.md
│
├── design/                ← システム設計書
│   ├── ai_automation_architecture_story_v2.md  ⭐Claude Agent SDK統合構想
│   ├── REVISED_STRATEGY_STORY.md
│   └── system_redesign_proposal.md
│
├── implementation/        ← 実装ガイド・計画
│   ├── phase2_phase3_implementation_plan.md  ⭐Phase 2/3実装計画
│   ├── implementation_roadmap.md
│   ├── implementation_story.md
│   └── NEXT_STEPS.md
│
├── guides/                ← 使い方ガイド
│   ├── analysis_workflow.md
│   ├── data_collection_guide.md
│   ├── mathematical_foundation_first.md
│   └── parquet_explained.md
│
├── userimported/          ← ユーザー提供資料
│   └── CLAUDE_CODE_INTEGRATION_SPEC.md
│
├── tests/                 ← テストドキュメント
│   └── README.md
│
└── archive/               ← 古い資料（説明省略）
    └── ...
```

---

## 🎯 用途別クイックリンク

### 教材を作りたい
1. `meta/curriculum_creation_guide.md` を読む
2. Week形式 or Chapter形式を選択
3. `samples/` のサンプルを参考に作成

### 実装を進めたい
1. `implementation/phase2_phase3_implementation_plan.md` で現状確認
2. `implementation/NEXT_STEPS.md` で次タスク確認
3. `implementation/implementation_roadmap.md` で全体像把握

### アーキテクチャを理解したい
1. `design/ai_automation_architecture_story_v2.md` で全体構想理解
2. `implementation/phase2_phase3_implementation_plan.md` で詳細確認

### 分析方法を知りたい
1. `guides/analysis_workflow.md` でワークフロー確認
2. `guides/data_collection_guide.md` でデータ収集
3. `guides/mathematical_foundation_first.md` で理論学習

---

## ⚠️ 注意事項

### archiveについて
`docs/archive/` には古い資料が保存されています。
最新情報は必ず `docs/` 直下の各ディレクトリを参照してください。

### 更新ルール
- ドキュメント更新時は、このファイルも更新する
- 新規ドキュメント追加時は、適切なカテゴリに分類して追記
- 古くなったドキュメントは `archive/` に移動

---

## 📝 最後に

このプロジェクトは教材作成と実装が並行して進んでいます。

**現在の優先順位**:
1. Phase 3実装完了（Claude Agent SDK統合）
2. Week 1教材のブラッシュアップ
3. Chapter形式教材の作成

迷ったら、このファイルに戻って全体像を確認してください。
