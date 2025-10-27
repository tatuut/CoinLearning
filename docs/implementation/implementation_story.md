# 📖 ミコとユウタの実装物語 - Phase 2から完成へ

**登場人物**:
- **ユウタ**: 仮想通貨初心者。100円→1000円を目指す大学生
- **ミコ**: プログラマー兼アナリスト。ユウタの友人

**時系列**: 2025年10月27日 - Phase 2完了後

---

## 🎬 Episode 1: 中間地点での振り返り

### Scene 1: Phase 2の達成

**ユウタ**: 「ミコ、見て！ダッシュボードで7日後の価格予測が見れるようになった！」

**ミコ**: 「そう、今朝実装したARIMAとGARCHだね」

**ユウタ**: 「これって、どのくらい進んだの？」

**ミコ**: 「全体の進捗を見せるよ」

```markdown
【全体進捗】

Phase 1: データインフラ ████████████ 100% ✅
Phase 2: テクニカル分析 █████████░░░  80% ⏳
Phase 3: 有機的分析     ░░░░░░░░░░░░   0% ❌
Phase 4: 統合とUI       ███░░░░░░░░░  30% ⏳

総合進捗: 52.5%
```

**ユウタ**: 「半分まで来たんだ！でも...残り半分で何をするの？」

**ミコ**: 「ここからが本番だ。今まではデータの準備と基本的な数学モデル。これから**本質的な価格決定要因**を分析する」

---

### Scene 2: 現状の問題点

**ユウタ**: 「今のシステムで何ができるの？」

**ミコ**: 「見せるよ」

```python
# 現在のシステムでできること
✅ 価格データの高速保存・読込（Parquet）
✅ ニュースの収集・保存
✅ テクニカル指標（RSI, MACD, Bollinger Bands）
✅ ARIMA/GARCH予測（7日後の価格とリスク）
✅ Streamlitダッシュボード

# でも...
❌ ニュースが価格に与える影響は「キーワードマッチング」のみ
❌ 「なぜこのスコアなのか」が説明できない
❌ 推奨アクション（買うべきか？）が出せない
```

**ユウタ**: 「確かに...『BTCのニュースを分析しました！スコア0.116です』って言われても、それで買っていいのか分からない」

**ミコ**: 「正確な指摘だ。だから、これから3つの大きなステップを踏む」

---

## 🧠 Episode 2: Phase 3の設計 - 有機的分析

### Scene 1: 「有機的分析」とは？

**ユウタ**: 「有機的分析って、何それ？」

**ミコ**: 「人間の直感的な判断を、AIで再現すること」

**ミコ**: 「例えば、こんなニュースがあったとする」

```markdown
【ニュース例】
タイトル: 「ビットコインETF、SECが正式承認」
本文: 米証券取引委員会（SEC）は本日、ビットコイン現物ETFを正式に承認した。
これにより、機関投資家が容易にビットコインに投資できるようになり...
```

**ミコ**: 「今のシステムは、『ETF』『承認』というキーワードがあるから**スコア0.8**、みたいな感じ」

**ユウタ**: 「それだけ？」

**ミコ**: 「そう。でも人間のアナリストなら、こう考える」

```markdown
【人間のアナリスト思考】

1. **ファンダメンタルズ面**: ETF承認はビットコインの信頼性を高める → スコア 0.9
   理由: 規制当局の承認により、ビットコインが「正式な投資商品」として認められた

2. **経済面**: 機関投資家の資金流入が期待できる → スコア 0.95
   理由: ETFは機関投資家にとって参入障壁が低い。数兆円規模の資金流入可能性

3. **規制面**: SEC承認は極めて重要な出来事 → スコア 1.0
   理由: 過去10年以上、SECはBTC ETFを拒否し続けていた。歴史的転換点

4. **センチメント面**: 市場心理が一気にポジティブになる → スコア 0.9
   理由: SNS、ニュースサイトで「強気」の声が溢れるはず

5. **技術面**: 直接的な影響は少ない → スコア 0.3
   理由: ブロックチェーン技術自体には変化なし

6. **外部ショック**: 該当なし → スコア 0.0
   理由: ポジティブニュースなのでショックではない

【総合スコア】: 0.9 × 0.25 + 0.95 × 0.2 + 1.0 × 0.2 + 0.9 × 0.15 + 0.3 × 0.15 + 0.0 × 0.05
            = 0.225 + 0.19 + 0.2 + 0.135 + 0.045 + 0
            = **0.795**

【推奨】: **強い買い推奨**
```

**ユウタ**: 「すごい...ちゃんと理由がある！」

**ミコ**: 「これが**有機的分析**。6つのカテゴリーで評価して、理由付きスコアを出す」

---

### Scene 2: LLMで実現する

**ユウタ**: 「でも、それをプログラムでどうやるの？」

**ミコ**: 「Claude 3.5 Sonnetや GPT-4を使う」

```python
# src/analysis/organic_scorer.py

class OrganicScorer:
    """有機的分析エンジン（LLM使用）"""

    def score_news(self, news, symbol, price_data):
        """
        6カテゴリーで評価して理由付きスコアを生成
        """

        # ステップ1: プロンプトを構築
        prompt = f"""
あなたは仮想通貨アナリストです。以下のニュースが{symbol}の価格に与える影響を
6つの観点から評価してください。

【ニュース】
{news['title']}
{news['content']}

【現在の{symbol}の状況】
- 現在価格: ${price_data['close'].iloc[-1]:,.2f}
- 30日リターン: {price_data['close'].pct_change(30).iloc[-1]*100:.2f}%
- RSI: {rsi:.2f}

【評価してください】
1. ファンダメンタルズ影響（0.0-1.0）+ 理由
2. 経済的影響（0.0-1.0）+ 理由
3. 規制的影響（0.0-1.0）+ 理由
4. センチメント影響（0.0-1.0）+ 理由
5. 技術的影響（0.0-1.0）+ 理由
6. 外部ショック（0.0-1.0）+ 理由

JSON形式で出力してください。
        """

        # ステップ2: Claude APIで分析
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # ステップ3: 結果をパース
        result = json.loads(response.content[0].text)

        return result
```

**ユウタ**: 「AIに分析させるのか！でも、お金かかるんじゃない？」

**ミコ**: 「1ニュースあたり約2.7円」

**ユウタ**: 「安い！」

**ミコ**: 「しかも、一度分析したニュースはキャッシュに保存する。2回目以降は無料」

---

### Scene 3: センチメント分析の進化

**ユウタ**: 「センチメント分析って、今のシステムにもあるよね？」

**ミコ**: 「ある。でも精度が低い」

```python
# 現在のシステム（キーワードマッチング）
def _simple_sentiment_analysis(text):
    positive_words = ['上昇', '急騰', '高値', '好調', '期待']
    negative_words = ['下落', '暴落', '安値', '不調', '懸念']

    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)

    if positive_count > negative_count:
        return 'positive'
    else:
        return 'negative'

# 精度: 約60%
```

**ミコ**: 「これをFinBERTに置き換える」

```python
# 新しいシステム（FinBERT）
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    def analyze(self, text):
        """
        金融特化のBERTでセンチメント分析

        Returns:
            {
                'label': 'positive' | 'negative' | 'neutral',
                'confidence': 0.92,
                'scores': {
                    'positive': 0.92,
                    'negative': 0.03,
                    'neutral': 0.05
                }
            }
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # 最も高いスコアのラベルを返す
        label_id = probs.argmax().item()
        confidence = probs.max().item()

        return {
            'label': ['negative', 'neutral', 'positive'][label_id],
            'confidence': confidence,
            'scores': {
                'negative': probs[0][0].item(),
                'neutral': probs[0][1].item(),
                'positive': probs[0][2].item()
            }
        }

# 精度: 85-92%（研究論文より）
```

**ユウタ**: 「60% → 92%って、かなり上がるね！」

**ミコ**: 「FinBERTは金融ニュース専用に学習されてるからね」

---

## ⚙️ Episode 3: Phase 4の設計 - 統合エンジン

### Scene 1: すべてを統合する

**ミコ**: 「Phase 3で有機的分析ができたら、Phase 4で全部を統合する」

**ユウタ**: 「全部って？」

**ミコ**: 「今まで作った全機能」

```python
【統合対象】

1. 有機的分析（Phase 3）
   - 6カテゴリー評価
   - LLMによる理由付け

2. テクニカル分析（Phase 2）
   - RSI, MACD, Bollinger Bands
   - 買われすぎ/売られすぎ判定

3. 時系列予測（Phase 2）
   - ARIMA: 7日後の価格予測
   - GARCH: ボラティリティ予測

4. センチメント分析（Phase 3）
   - FinBERT: 92%精度のセンチメント判定

5. 機械学習予測（Phase 2）※未実装
   - LSTM/GRU: より高精度な予測
```

**ミコ**: 「これらを全部組み合わせて、**最終スコア**と**推奨アクション**を出す」

---

### Scene 2: 統合スコアリングエンジン

```python
# src/analysis/integrated_engine.py

class IntegratedScoringEngine:
    """全分析を統合するエンジン"""

    def score_comprehensive(self, symbol, news=None):
        """
        包括的な分析

        Returns:
            {
                'final_score': 0.78,          # 最終スコア（0-1）
                'recommendation': 'BUY',      # 推奨アクション
                'confidence': 0.85,            # 確信度
                'explanation': '...',          # 詳細説明

                'organic_analysis': {...},     # 有機的分析の詳細
                'mathematical_analysis': {...} # 数学的分析の詳細
            }
        """

        # ステップ1: 価格データ取得
        price_data = self.load_price_data(symbol)

        # ステップ2: 有機的分析（ニュースがある場合）
        organic = None
        if news:
            organic = self.organic_scorer.score_news(news, symbol, price_data)

        # ステップ3: テクニカル指標
        technical = self.technical_analyzer.analyze(price_data)

        # ステップ4: 時系列予測
        forecast = self.forecaster.combined_forecast(price_data)

        # ステップ5: センチメント分析
        sentiment = None
        if news:
            sentiment = self.sentiment_analyzer.analyze(news['content'])

        # ステップ6: スコア統合
        final_score = self._integrate_scores(
            organic, technical, forecast, sentiment
        )

        # ステップ7: 推奨アクション生成
        recommendation = self._generate_recommendation(
            final_score, technical, forecast
        )

        return {
            'final_score': final_score,
            'recommendation': recommendation,
            'confidence': self._calculate_confidence(...),
            'explanation': self._generate_explanation(...)
        }
```

**ユウタ**: 「これで『買うべきか？』が分かるんだ！」

**ミコ**: 「そう。しかも理由付きで」

---

### Scene 3: 推奨アクションのルール

**ミコ**: 「推奨アクションは、複数の条件で判定する」

```python
def _generate_recommendation(self, final_score, technical, forecast):
    """
    推奨アクション生成
    """

    rsi = technical['rsi']
    macd_signal = technical['macd']['signal']
    forecast_trend = forecast['price_forecast']['forecast'][-1] > forecast['current_price']
    volatility = forecast['volatility_forecast']['mean_volatility']

    # ルール1: 強い買いシグナル
    if (final_score > 0.7 and      # スコアが高い
        rsi < 70 and               # 買われすぎではない
        forecast_trend and         # 予測が上昇
        macd_signal == 'buy'):     # MACDも買い
        return 'STRONG_BUY'

    # ルール2: 買いシグナル
    elif (final_score > 0.6 and
          rsi < 65 and
          forecast_trend):
        return 'BUY'

    # ルール3: 強い売りシグナル
    elif (final_score < 0.3 and
          rsi > 30 and
          not forecast_trend and
          macd_signal == 'sell'):
        return 'STRONG_SELL'

    # ルール4: 売りシグナル
    elif (final_score < 0.4 and
          rsi > 35):
        return 'SELL'

    # ルール5: 様子見
    else:
        return 'HOLD'
```

**ユウタ**: 「ちゃんと複数の条件を見てるんだ！」

**ミコ**: 「1つの指標だけだと騙されるからね」

---

## 📊 Episode 4: 優先順位の決定

### Scene 1: 何から作るべきか？

**ユウタ**: 「で、Phase 3とPhase 4、どっちから作る？」

**ミコ**: 「優先順位をつけた」

```markdown
【Week 1-2: 最優先】

1. 有機的分析エンジン（LLM統合） - 5-7日
   → 「なぜ」を説明できる機能（最大の価値）

2. 統合スコアリングエンジン - 3-4日
   → 全機能を統合する核心

3. Streamlit UI拡張 - 2-3日
   → 統合スコアを可視化

合計: 10-14日
```

**ユウタ**: 「なんで有機的分析が最優先なの？」

**ミコ**: 「これが一番価値が高いから」

**ミコ**: 「今のシステムは『スコア0.116です』って出すけど、理由が分からない」

**ミコ**: 「でも有機的分析があれば...」

```markdown
【ニュース分析結果】

総合スコア: 0.795

【詳細評価】

1. ファンダメンタルズ影響: 0.9 ⭐⭐⭐⭐⭐
   理由: ETF承認はビットコインの信頼性を大きく高めます。
   規制当局の承認により、「正式な投資商品」として認められました。

2. 経済的影響: 0.95 ⭐⭐⭐⭐⭐
   理由: 機関投資家の大規模な資金流入が期待できます。
   ETFは機関投資家にとって参入障壁が低く、数兆円規模の資金流入の可能性があります。

3. 規制的影響: 1.0 ⭐⭐⭐⭐⭐
   理由: SEC承認は極めて重要な歴史的転換点です。
   過去10年以上、SECはBTC ETFを拒否し続けていましたが、ついに承認されました。

...

【推奨アクション】: 強い買い推奨 🟢
【確信度】: 85%
```

**ユウタ**: 「これなら納得して買える！」

---

### Scene 2: Week 3-4の計画

```markdown
【Week 3-4: 高優先度】

4. FinBERTセンチメント分析 - 3-4日
   → 精度向上（60% → 92%）

5. バックテスト機能 - 2-3日
   → 推奨アクションの精度検証
   → 「過去1年間の推奨に従ったら、どのくらい儲かったか？」

合計: 5-7日
```

**ユウタ**: 「バックテストって、過去検証？」

**ミコ**: 「そう。例えば...」

```markdown
【バックテストシミュレーション】

期間: 2024年1月1日 〜 2025年10月27日
初期資金: 100円
戦略: 推奨アクションに従う

結果:
- 取引回数: 47回
- 勝率: 68%
- 最終資産: 237円
- リターン: +137%
- シャープレシオ: 1.8

【結論】
この推奨システムに従えば、過去1年で100円→237円になっていた可能性。
```

**ユウタ**: 「これは重要だ！」

---

### Scene 3: Week 5-6の計画

```markdown
【Week 5-6: 中優先度】

6. GRU/LSTMモデル - 6-8日
   → 予測精度向上（ARIMA: 2-5% → LSTM: 1.5-3%）
   → PyTorchで実装
```

**ミコ**: 「LSTMは後回し。理由は2つ」

**理由1**: 有機的分析の方が価値が高い
- ARIMA予測: 2-5%誤差
- LSTM予測: 1.5-3%誤差
- **差は小さい**

**理由2**: 実装に時間がかかる
- データ準備: 1日
- モデル構築: 2-3日
- 訓練: 1-2日
- 検証: 1-2日

**ユウタ**: 「確かに、『なぜ買うべきか』が分かる方が大事だ」

---

## 🎯 Episode 5: 実装開始

### Scene 1: 最初の一歩

**ミコ**: 「それじゃあ、実装を始めよう」

**ユウタ**: 「何から？」

**ミコ**: 「Anthropic API Keyの取得」

```bash
# ステップ1: API Key取得
# https://console.anthropic.com/ にアクセス
# API Keyを取得

# ステップ2: 環境変数に設定
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# ステップ3: ライブラリインストール
pip install anthropic>=0.18.0

# ステップ4: テスト
python -c "import anthropic; print('OK')"
```

**ユウタ**: 「これでClaudeが使えるようになるの？」

**ミコ**: 「そう。そうしたら`OrganicScorer`を実装する」

---

### Scene 2: プロンプト設計

**ミコ**: 「プロンプトは別ファイルで管理する」

```bash
mkdir -p docs/prompts
```

```markdown
# docs/prompts/organic_analysis_prompt.md

## 有機的分析プロンプト

### システムメッセージ
あなたは経験豊富な仮想通貨アナリストです。ニュースが価格に与える影響を、
6つの観点から定量的かつ論理的に評価してください。

### ユーザーメッセージテンプレート
【分析対象】
銘柄: {symbol}
ニュースタイトル: {title}
ニュース本文: {content}
公開日: {date}

【現在の市場状況】
現在価格: ${current_price}
30日間リターン: {return_30d}%
RSI(14): {rsi}
ボラティリティ: {volatility}%

【評価してください】
以下の6カテゴリーでスコア（0.0-1.0）と詳細な理由を記載：

1. ファンダメンタルズ影響
2. 技術的影響
3. 経済的影響
4. 規制的影響
5. センチメント影響
6. 外部ショック

【出力形式】
JSON形式で出力してください。
```

---

### Scene 3: 最初の実装

```python
# src/analysis/organic_scorer.py（最小実装版）

import anthropic
import json
import os

class OrganicScorer:
    """有機的分析エンジン"""

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

    def score_news(self, news, symbol, price_data):
        """ニュースを6カテゴリーで評価"""

        # プロンプト構築
        prompt = self._build_prompt(news, symbol, price_data)

        # Claude API呼び出し
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # レスポンスをパース
        response_text = message.content[0].text
        result = json.loads(response_text)

        return result

    def _build_prompt(self, news, symbol, price_data):
        """プロンプトを構築"""
        # 実装は省略（上記のテンプレートを使用）
        pass
```

**ユウタ**: 「これだけ？」

**ミコ**: 「最小実装はね。ここから徐々に機能を追加していく」

---

## 📈 Episode 6: 完成までの道のり

### Scene 1: マイルストーン

**ミコ**: 「ゴールまでのマイルストーンを設定した」

```markdown
【マイルストーン】

🏁 Milestone 1（Week 2終了時）
- ✅ OrganicScorer実装完了
- ✅ IntegratedScoringEngine実装完了
- ✅ Streamlit UIに統合
- ✅ 1銘柄で動作確認

🏁 Milestone 2（Week 4終了時）
- ✅ FinBERT実装完了
- ✅ バックテスト機能完了
- ✅ 過去1年分の精度検証
- ✅ 推奨アクションの信頼性確認

🏁 Milestone 3（Week 6終了時）
- ✅ LSTM実装完了（オプション）
- ✅ 全銘柄で動作確認
- ✅ ドキュメント整備

🏆 Milestone 4（Week 8終了時）
- ✅ リアルタイム更新
- ✅ API化（オプション）
- ✅ 本番運用開始
```

**ユウタ**: 「Milestone 1が一番重要だね」

**ミコ**: 「そう。ここで**本質的な分析**ができるようになる」

---

### Scene 2: 期待される成果

**ユウタ**: 「全部完成したら、何ができるの？」

**ミコ**: 「こんな感じ」

```markdown
【完成後のシステム】

## 入力
- 銘柄: BTC
- ニュース: 「ビットコインETF承認」

## 出力

### 総合評価
- 最終スコア: 0.795
- 推奨アクション: 強い買い推奨 🟢
- 確信度: 85%

### 有機的分析（6カテゴリー）
1. ファンダメンタルズ: 0.9 ⭐⭐⭐⭐⭐
   理由: ETF承認により信頼性が大幅向上...

2. 経済的影響: 0.95 ⭐⭐⭐⭐⭐
   理由: 機関投資家の大規模資金流入が期待...

（以下省略）

### 数学的分析
- RSI(14): 45.2（中立）
- MACD: 買いシグナル 📈
- Bollinger Bands: 中間ライン付近
- ARIMA予測（7日後）: $71,000（+3.5%）
- GARCH予測リスク: 中程度
- LSTM予測（7日後）: $71,500（+4.2%）

### センチメント分析
- FinBERT: Positive（信頼度92%）
- BART MNLI: Bullish（信頼度88%）

### バックテスト結果
この推奨システムに従った場合の過去1年の成績:
- 勝率: 68%
- リターン: +137%
- シャープレシオ: 1.8

### 推奨理由
ETF承認は歴史的転換点です。規制面、経済面、センチメント面の
すべてで極めてポジティブな影響が予測されます。
テクニカル指標も買いを示唆しており、7日間の価格予測も上昇傾向です。
過去の類似ニュースでは平均+8.5%の上昇が見られました。

【結論】: 強い買い推奨
```

**ユウタ**: 「これは...すごい」

**ミコ**: 「これが、本質的な価格決定要因を分析するシステム」

---

### Scene 3: 最後のメッセージ

**ユウタ**: 「よし、やろう！」

**ミコ**: 「待って。大事なことを言っておく」

**ミコ**: 「このシステムは**分析材料を揃える**ためのもの」

**ミコ**: 「最終判断は、君がする」

**ユウタ**: 「...うん」

**ミコ**: 「システムが『買い推奨』を出しても、それは『買うべき』という命令じゃない」

**ミコ**: 「『これらの根拠から、買いを検討する価値がある』という情報提供だ」

**ユウタ**: 「分かった。自分で考えて判断する」

**ミコ**: 「その心構えがあれば大丈夫」

**ミコ**: 「さあ、実装を始めよう」

---

## 🎬 エピローグ: 実装の旅

**ナレーション**:

ミコとユウタの実装の旅は、まだ始まったばかり。

Phase 1と Phase 2で築いた基盤の上に、
Phase 3の有機的分析、Phase 4の統合エンジンを構築していく。

キーワードマッチングから、本質的な価格決定要因の分析へ。
数字だけのスコアから、理由付きの推奨アクションへ。

その先に待つのは、データを見て、自分で考え、賢く判断できる
本物のトレーダーとしての成長だ。

---

**次回予告**:

Episode 7: OrganicScorerの実装
Episode 8: プロンプトエンジニアリングの技術
Episode 9: IntegratedEngineの完成
Episode 10: バックテストで検証

---

**To Be Continued...**

---

## 📚 付録: 実装チェックリスト

### Week 1-2: 有機的分析エンジン

- [ ] Anthropic API Key取得
- [ ] `anthropic` ライブラリインストール
- [ ] `src/analysis/organic_scorer.py` 作成
- [ ] プロンプト設計（`docs/prompts/`）
- [ ] テスト実装
- [ ] キャッシュ機能実装
- [ ] エラーハンドリング
- [ ] `IntegratedScoringEngine` 実装
- [ ] Streamlit UI統合
- [ ] ドキュメント作成

### Week 3-4: センチメント分析とバックテスト

- [ ] `transformers` ライブラリインストール
- [ ] `src/analysis/sentiment_analyzer.py` 作成
- [ ] FinBERT実装
- [ ] BART MNLI実装
- [ ] `src/analysis/backtester.py` 作成
- [ ] バックテスト実装
- [ ] 過去1年分のテスト
- [ ] 精度検証レポート作成

### Week 5-6: 機械学習予測（オプション）

- [ ] PyTorch or TensorFlow インストール
- [ ] `src/analysis/ml_forecasting.py` 作成
- [ ] データ準備関数
- [ ] LSTMモデル構築
- [ ] モデル訓練
- [ ] 予測精度評価
- [ ] IntegratedEngineに統合

---

**作成者**: Claude Code with ミコ & ユウタ
**作成日**: 2025-10-27
**対象読者**: 実装を進めるすべての開発者
