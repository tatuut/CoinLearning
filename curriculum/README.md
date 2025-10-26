# 📚 実践カリキュラム（Week形式）

100円→1000円を実際に達成するための実践教材

## 🎯 このフォルダの目的

**Who**: 実際に手を動かして100円→1000円を達成したい実践者

**What**: ツールの使い方、具体的な手順、トラブルシューティングを物語で学ぶ

**How**: ユウタと一緒に、実際の取引を追体験しながらスキルを習得

---

## 📖 Week一覧

| Week | タイトル | 目標資金 | 対応Chapter | 主な内容 | 状態 |
|------|---------|---------|------------|---------|------|
| [Week 1](./week1_basics.md) | 100円チャレンジ開始 | 100円→110円 | [Chapter 1](./stories/01_investment_strategy.md) | 取引所登録、初取引（SHIB失敗→DOGE成功） | ✅ 完成 |
| Week 2 | テクニカル分析の実践 | 110円→150円 | [Chapter 2-4](./stories/) | RSI, MACD, Bollinger Bands実践 | 📝 予定 |
| Week 3 | ニュース分析と統合判断 | 150円→300円 | [Chapter 5-6](./stories/) | 感情分析、ARIMA/GARCH、統合システム | 📝 予定 |
| Week 4 | システム化と振り返り | 300円→1000円 | - | 自動化、ポートフォリオ、総まとめ | 📝 予定 |

---

## 🔗 技術ストーリー（Chapter形式）との関係

各Weekで使うツールや技術の**背景・原理**を学ぶには、対応するChapterを参照してください。

**学習パターン**:
- **実践優先型**: Week 1 → Chapter 1-2 → Week 2 → Chapter 3-4 ...（初心者向け）
- **理解優先型**: Chapter 1-6 → Week 1-4（中級者向け）
- **ハイブリッド型**: Week → Chapter → Week → Chapter ...（推奨）

詳しくは [カリキュラム作成ガイド - 使い分け](../docs/meta/curriculum_creation_guide.md#week形式とchapter形式の使い分け) を参照

---

## 📊 各Weekの構成（6パート）

### Part 1: ストーリー導入（1000文字）
- ユウタの現状と課題
- 新しいツール・概念の紹介
- 今週の目標設定

### Part 2: ツール・概念の説明（2000文字）
- なぜ必要か
- 何ができるか
- 基本的な使い方

### Part 3: 実践パート1 - 失敗（2000文字）
- ユウタが実際に試す
- 最初の失敗
- 原因分析

### Part 4: 実践パート2 - 成功（2000文字）
- 改善して再挑戦
- ツールを使いこなす
- 成功体験

### Part 5: あなたの実践ガイド（2000文字）
- 超詳細な手順（コピペで実行可能）
- トラブルシューティング
- チェックリスト

### Part 6: まとめと振り返り（1000文字）
- 学んだことリスト
- 次のWeekへの予告
- ユウタからのメッセージ

---

## 🛠️ 使用するツール

### Week 1
- `market_scanner.py`: 全銘柄スキャン
- `crypto_analyst.py`: 個別銘柄分析
- MEXC取引所

### Week 2（予定）
- `data/timeseries_manager.py`: 1分足データ管理
- `tools/technical_indicators.py`: RSI, MACD, BB計算
- チャート分析

### Week 3（予定）
- `data/news_manager.py`: ニュース全文保存
- `analysis/sentiment_analyzer.py`: 感情分析
- `analysis/forecasting.py`: ARIMA/GARCH予測

### Week 4（予定）
- `analysis/integrated_engine.py`: 統合分析
- 自動化スクリプト
- ポートフォリオ管理

---

## 📝 作成ガイドライン

Week形式の教材を作成する際は、[カリキュラム作成ガイド](../docs/meta/curriculum_creation_guide.md#week形式の作成手順) を参照してください。

**重要ポイント**:
- ✅ 超詳細な手順（初心者でも迷わない）
- ✅ 失敗→改善のサイクル
- ✅ 実際に動くコマンド例
- ✅ チェックリスト必須
- ✅ 10,000文字以上

---

## 🔄 次のステップ

1. **Week 1を実践** → 100円で実際に取引してみる
2. **Chapter 1-2を読む** → なぜ成功/失敗したか理解
3. **Week 2を実践** → テクニカル分析を使って取引
4. **Chapter 3-4を読む** → RSI/MACD/BBの原理を理解

---

**関連リンク**:
- 技術ストーリー: [stories/](./stories/)
- カリキュラム作成ガイド: [docs/meta/curriculum_creation_guide.md](../docs/meta/curriculum_creation_guide.md)
- プロジェクトREADME: [../README.md](../README.md)
