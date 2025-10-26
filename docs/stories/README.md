# 📖 技術習得ストーリー（Chapter形式）

技術の発明背景と原理を物語で学ぶ教材

## 🎯 このフォルダの目的

**Who**: 技術の「なぜ」「どうやって」を深く理解したい学習者

**What**: 技術の発明背景、数式の意味、実装方法、使い方を物語で学ぶ

**How**: 発明者の物語を追体験し、試行錯誤のプロセスから本質を理解

---

## 📚 Chapter一覧

| Chapter | タイトル | 発明者/技術 | 対応Week | 状態 |
|---------|---------|------------|----------|------|
| [1. 投資戦略の誕生](./01_investment_strategy.md) | ユウタ式スイングトレード | 戦略確立 | [Week 1](../../curriculum/week1_basics_v2.md) | ✅ 完成 |
| [2. RSIの発明](./02_rsi_invention.md) | 過熱を数値化した男 | J. Welles Wilder Jr. (1978) | Week 2 | ✅ 完成 |
| [3. MACDの誕生](./03_macd_invention.md) | トレンドを見える化 | Gerald Appel (1970s) | Week 2 | ✅ 完成 |
| [4. Bollinger Bandsの発明](./04_bollinger_bands_invention.md) | リスクを可視化 | John Bollinger (1980s) | Week 2 | ✅ 完成 |
| [5. ARIMA/GARCHの発見](./05_arima_garch_discovery.md) | 未来を予測する数学 | Box & Jenkins (1970), Engle (1982) | Week 3 | ✅ 完成 |
| [6. 統合分析システム](./06_integrated_analysis.md) | 全てを統合する | - | Week 3 | ✅ 完成 |

---

## 🔗 実践カリキュラム（Week形式）との関係

各Chapterで学んだ技術を**実際の取引で使う**には、対応するWeekを参照してください。

**例**:
- Chapter 2（RSI）を読んだ → Week 2でRSIを使った実際の取引を体験
- Week 1で失敗した → Chapter 1-2でなぜ失敗したか理解

詳しくは [カリキュラム作成ガイド - 使い分け](../curriculum_creation_guide.md#week形式とchapter形式の使い分け) を参照

---

## 📊 各Chapterの構成（12シーン）

### 【ストーリーパート】発明者の物語（Scene 1-5）

#### Scene 1: 時代背景と発明者の登場
具体的な時代・場所、発明者のプロフィール

#### Scene 2: 発明者の悩み・問題意識
何度も失敗し、解決策を模索

#### Scene 3: 着想の瞬間
専門知識を応用、アナロジー思考

#### Scene 4: 数式の誕生（試行錯誤）
Step 1 → Step 2 → ... → 完成

#### Scene 5: 出版・世への広まり
歴史的インパクト、現代への影響

---

### 【実装パート】現代での実装（Scene 6-9）

#### Scene 6: Pythonでの実装
シンプルな関数、コメントで各ステップ説明

#### Scene 7: 実データでの検証
Week 1の失敗例などで検証、納得感

#### Scene 8: 応用的な使い方
3つの使い方、初心者へのアドバイス

#### Scene 9: 限界と弱点
正直に弱点を伝える、どんな場面で失敗するか

---

### 【統合パート】ユウタ式での活用（Scene 10-11）

#### Scene 10: ユウタ式戦略への組み込み
エントリー/イグジット判断、使わない場面

#### Scene 11: 実装コード（完全版）
プロダクションレベル、docstring・型ヒント完備

---

### 【まとめパート】振り返りと次へ（Scene 12）

#### Scene 12: エピローグ
教訓、まとめボックス、Next Chapter

---

## 🧑‍🏫 各Chapterの詳細

### Chapter 1: 投資戦略の誕生

**学べること**:
- 仮想通貨取引の本質（3つの戦い）
- スイングトレードの選択理由
- ユウタ式スイングトレード戦略
- トリプル確認（ファンダ×テクニカル×センチメント）

**発明**: ユウタとミコが確立した独自戦略

**実践**: [Week 1](../../curriculum/week1_basics_v2.md) - 実際の取引で戦略を適用

---

### Chapter 2: RSIの発明

**学べること**:
- J. Welles Wilder Jr. の物語（1978年）
- 機械工学から株価分析への応用
- RSI数式の導出プロセス
- 買われすぎ/売られすぎ判定

**発明**: RSI = 100 - (100 / (1 + RS))

**実践**: Week 2（予定） - RSIを使った銘柄選定

---

### Chapter 3: MACDの誕生

**学べること**:
- Gerald Appel の着想（1970年代）
- 移動平均線の限界と改善
- MACD, Signal, Histogramの意味
- トレンドの方向と強さの検出

**発明**: MACD = EMA(12) - EMA(26)

**実践**: Week 2（予定） - MACDでトレンド判断

---

### Chapter 4: Bollinger Bandsの発明

**学べること**:
- John Bollinger の発見（1980年代）
- 統計学（標準偏差）の応用
- ボラティリティの可視化
- バンドウォーク、スクイーズの検出

**発明**: Upper/Lower = MA ± (2 × σ)

**実践**: Week 2（予定） - BBでリスク評価

---

### Chapter 5: ARIMA/GARCHの発見

**学べること**:
- Box & Jenkins のARIMA（1970年）
- Robert Engle のGARCH（1982年、ノーベル賞）
- 時系列予測の数学
- ボラティリティクラスタリング

**発明**:
- ARIMA(p,d,q): 価格予測
- GARCH(p,q): ボラティリティ予測

**実践**: Week 3（予定） - 短期価格予測

---

### Chapter 6: 統合分析システム

**学べること**:
- 全技術の統合方法
- 重み付けスコアリング
- 統合判断エンジンの設計
- BUY/SELL/HOLDの推奨ロジック

**発明**: Technical 40% + Forecast 30% + Fundamental 30%

**実践**: Week 3（予定） - 統合システムで取引

---

## 📝 作成ガイドライン

Chapter形式の教材を作成する際は、[カリキュラム作成ガイド](../curriculum_creation_guide.md#chapter形式の作成手順) を参照してください。

**重要ポイント**:
- ✅ ストーリーの臨場感（具体的な時代・場所）
- ✅ 数式の必然性（Step-by-stepの導出）
- ✅ 正直さ（弱点を隠さない）
- ✅ 実装コードが動作する
- ✅ 5,000-8,000文字

---

## 🔬 技術マップ

```
投資戦略（Chapter 1）
    ↓
├─ テクニカル分析
│   ├─ RSI（Chapter 2）: 買われすぎ/売られすぎ
│   ├─ MACD（Chapter 3）: トレンド方向
│   └─ Bollinger Bands（Chapter 4）: ボラティリティ
│
├─ 予測モデル
│   └─ ARIMA/GARCH（Chapter 5）: 価格/ボラティリティ予測
│
└─ 統合システム（Chapter 6）
    → 全てを組み合わせて総合判断
```

---

## 🔄 推奨学習順序

### パターン1: 順番に読む（理解優先型）
Chapter 1 → 2 → 3 → 4 → 5 → 6

**メリット**: 体系的に理解できる

---

### パターン2: Week と交互（ハイブリッド型・推奨）
- Week 1（実践） → Chapter 1-2（理解）
- Week 2（実践） → Chapter 3-4（理解）
- Week 3（実践） → Chapter 5-6（理解）

**メリット**: 実践と理解を交互に繰り返すので、定着しやすい

---

### パターン3: 興味のあるChapterから（自由型）
気になる技術から読む

**例**:
- RSIを使いたい → Chapter 2
- 価格予測したい → Chapter 5

---

## 💡 読み方のコツ

### 初回: ストーリーを楽しむ
- Scene 1-5を読む（発明者の物語）
- なぜこの技術が生まれたか理解
- 数式の必然性を感じる

### 2回目: 実装を試す
- Scene 6-11を読む（Pythonコード）
- 実際にコードを実行
- 自分のデータで検証

### 3回目: 実践で使う
- Scene 10-11を読む（ユウタ式への組み込み）
- Weekで実際の取引に適用
- 成功/失敗を振り返る

---

**関連リンク**:
- 実践カリキュラム: [curriculum/](../../curriculum/)
- カリキュラム作成ガイド: [../curriculum_creation_guide.md](../curriculum_creation_guide.md)
- 詳細サンプル: [../samples/chapter_format_detailed_example.md](../samples/chapter_format_detailed_example.md)
- プロジェクトREADME: [../../README.md](../../README.md)
