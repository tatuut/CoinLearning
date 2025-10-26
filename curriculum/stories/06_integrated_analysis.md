# 📖 Story Chapter 6: 統合分析システム - 全ての武器を統合する

## Scene 1: 武器の棚卸し

**ミコ**: 「ユウタ、これまで手に入れた武器をリストアップしよう」

**ユウタ**: 「うん」

```markdown
【手に入れた武器】

## テクニカル分析
1. RSI: 過熱/冷却の判定
2. MACD: 勢いの方向
3. Bollinger Bands: リスク（ボラティリティ）

## 数学的予測
4. ARIMA: 価格予測（1-7日後）
5. GARCH: ボラティリティ予測

## データインフラ
6. 時系列データ管理（1分足、差分更新）
7. ニュース全文保存
```

**ユウタ**: 「でも、ニュースの分析がまだだ」

**ミコ**: 「そう。最後の武器は『ファンダメンタルズ分析』」

**ミコ**: 「そして、全てを統合する」

---

## Scene 2: ファンダメンタルズ分析の本質

**ミコ**: 「ファンダメンタルズ分析って何だと思う？」

**ユウタ**: 「ニュースを見て...判断すること？」

**ミコ**: 「表面的にはそうだ。でも、本質は違う」

```markdown
【ファンダメンタルズ分析の本質】

## 問い
「なぜ、この銘柄は価値があるのか？」

## 6つの観点（Chapter 1で定義した）
1. ファンダメンタルズ: ブロックチェーン信頼性、採用率
2. 技術要因: 開発活動、アップグレード
3. 経済要因: 需給バランス、流動性
4. 規制要因: 政府方針、ETF承認
5. 市場センチメント: SNS、ニュース
6. 外部ショック: ハッキング、著名人発言

## 現状の問題
スコアリングエンジン（scoring_engine.py）:
- キーワードマッチングのみ
- 「ETF」→ +0.1点
- 表面的すぎる
```

**ユウタ**: 「じゃあ、どうする？」

**ミコ**: 「**有機的分析**と**数学的分析**を組み合わせる」

---

## Scene 3: 有機的分析 - LLMの活用

**ミコ**: 「ニュースを『意味』で理解するには、人間の思考が必要だ」

**ミコ**: 「でも、人間が1つ1つ読むのは無理」

**ミコ**: 「だから...AIに任せる」

```markdown
【LLM（大規模言語モデル）活用】

使用モデル:
- GPT-4（OpenAI）
- Claude（Anthropic）
- FinBERT（金融特化BERT）

タスク:
1. ニュースの要約
2. 6カテゴリー評価
3. 理由付きスコアリング
4. リスク要因抽出
```

**ユウタ**: 「AIが分析してくれるのか！」

**ミコ**: 「そう。でも、AIの判断を鵜呑みにするんじゃない」

**ミコ**: 「AI の分析を『材料』として、最終判断は自分でする」

---

## Scene 4: 統合分析システムの設計

**ミコ**: 「全ての武器を統合するシステムを設計する」

```markdown
【統合分析システム - アーキテクチャ】

┌─────────────────────────────────────┐
│  入力: 銘柄シンボル（例: BTC）      │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Phase 1: データ収集                 │
│  - 価格データ（1分足）               │
│  - ニュースデータ（全文）             │
│  - 市場データ（出来高、時価総額）     │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Phase 2: 個別分析                   │
│                                      │
│  ┌──テクニカル分析──┐              │
│  │ - RSI                            │
│  │ - MACD                           │
│  │ - Bollinger Bands                │
│  └──────────────────┘              │
│                                      │
│  ┌──数学的予測──┐                  │
│  │ - ARIMA（価格予測）              │
│  │ - GARCH（ボラティリティ予測）     │
│  └──────────────────┘              │
│                                      │
│  ┌──ファンダメンタルズ──┐          │
│  │ - ニュース分析（LLM）             │
│  │ - 6カテゴリー評価                 │
│  │ - センチメント分析                │
│  └──────────────────┘              │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Phase 3: 統合判断                   │
│  - 各分析結果を重み付け統合           │
│  - 信頼度計算                        │
│  - BUY/SELL/HOLD判定                │
│  - 理由生成                          │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  出力: 最終推奨                      │
│  - シグナル（BUY/SELL/HOLD）         │
│  - 信頼度（0-100%）                  │
│  - 詳細理由（箇条書き）               │
│  - リスク評価                        │
│  - エントリー価格/損切り/利確ライン   │
└─────────────────────────────────────┘
```

**ユウタ**: 「全部が統合されるのか！」

**ミコ**: 「そう。これが『ユウタ式スイングトレード』の完成形だ」

---

## Scene 5: 実装 - 統合分析エンジン

```python
# analysis/integrated_engine.py（新規作成）

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.technical_indicators import TechnicalIndicators
from tools.forecasting import TimeSeriesForecaster
from data.timeseries_manager import TimeSeriesManager
from data.advanced_database import AdvancedDatabase
import pandas as pd


class IntegratedAnalysisEngine:
    """統合分析エンジン - 全ての分析を統合"""

    def __init__(self):
        self.tech = TechnicalIndicators()
        self.forecaster = TimeSeriesForecaster()
        self.data_manager = TimeSeriesManager()
        self.db = AdvancedDatabase()

    def analyze(self, symbol: str) -> dict:
        """
        包括的分析

        Args:
            symbol: 銘柄シンボル

        Returns:
            統合分析結果
        """
        print(f"{'='*80}")
        print(f"🔍 {symbol} - 統合分析開始")
        print(f"{'='*80}\n")

        result = {
            'symbol': symbol,
            'technical': {},
            'forecast': {},
            'fundamental': {},
            'integrated': {}
        }

        # Phase 1: データ収集
        print("📥 [1/4] データ収集中...")
        price_data = self.data_manager.get_data(symbol)

        if price_data.empty:
            return {'error': f'{symbol}: データが存在しません'}

        prices = price_data['close']

        # Phase 2: 個別分析
        print("📊 [2/4] テクニカル分析中...")
        result['technical'] = self._technical_analysis(prices)

        print("🔮 [3/4] 数学的予測中...")
        result['forecast'] = self._forecast_analysis(prices)

        print("📰 [4/4] ファンダメンタルズ分析中...")
        result['fundamental'] = self._fundamental_analysis(symbol)

        # Phase 3: 統合判断
        print("\n⚡ 統合判断中...")
        result['integrated'] = self._integrate_signals(
            result['technical'],
            result['forecast'],
            result['fundamental']
        )

        return result

    def _technical_analysis(self, prices: pd.Series) -> dict:
        """テクニカル分析"""
        # RSI
        rsi = self.tech.rsi(prices)
        rsi_value = rsi.iloc[-1]
        rsi_result = self.tech.interpret_rsi(rsi_value)

        # MACD
        macd_df = self.tech.macd(prices)
        macd_value = macd_df['macd'].iloc[-1]
        signal_value = macd_df['signal'].iloc[-1]
        histogram_value = macd_df['histogram'].iloc[-1]
        prev_histogram = macd_df['histogram'].iloc[-2] if len(macd_df) > 1 else None

        macd_result = self.tech.interpret_macd(
            macd_value, signal_value, histogram_value, prev_histogram
        )

        # Bollinger Bands
        bb_df = self.tech.bollinger_bands(prices)
        percent_b = bb_df['percent_b'].iloc[-1]
        bandwidth = bb_df['bandwidth'].iloc[-1]

        bb_result = self.tech.interpret_bollinger(percent_b, bandwidth)

        # 統合シグナル
        combined = self.tech.triple_signal(rsi_value, macd_result, bb_result)

        return {
            'rsi': rsi_result,
            'macd': macd_result,
            'bollinger': bb_result,
            'combined': combined
        }

    def _forecast_analysis(self, prices: pd.Series) -> dict:
        """数学的予測分析"""
        # 直近100日を使用
        recent_prices = prices.tail(100)

        # 包括的予測
        forecast_result = self.forecaster.comprehensive_forecast(
            recent_prices,
            forecast_days=7
        )

        return forecast_result

    def _fundamental_analysis(self, symbol: str) -> dict:
        """ファンダメンタルズ分析"""
        # ニュース取得
        news_list = self.db.get_recent_news(symbol, limit=5, days=7)

        if not news_list:
            return {
                'news_count': 0,
                'avg_sentiment': 'neutral',
                'avg_score': 0,
                'description': 'ニュースなし'
            }

        # センチメント集計
        sentiments = [n['sentiment'] for n in news_list]
        scores = [n.get('final_score', 0) for n in news_list]

        sentiment_counts = {
            'positive': sum(1 for s in sentiments if 'positive' in s),
            'negative': sum(1 for s in sentiments if 'negative' in s),
            'neutral': sum(1 for s in sentiments if s == 'neutral')
        }

        # 総合センチメント
        if sentiment_counts['positive'] > sentiment_counts['negative']:
            overall_sentiment = 'positive'
        elif sentiment_counts['negative'] > sentiment_counts['positive']:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        return {
            'news_count': len(news_list),
            'avg_sentiment': overall_sentiment,
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'sentiment_breakdown': sentiment_counts,
            'latest_news': [
                {
                    'title': n['title'][:50] + '...',
                    'sentiment': n['sentiment'],
                    'score': n.get('final_score', 0)
                }
                for n in news_list[:3]
            ],
            'description': f'{len(news_list)}件のニュース、センチメント: {overall_sentiment}'
        }

    def _integrate_signals(self, technical: dict, forecast: dict, fundamental: dict) -> dict:
        """
        全シグナルを統合

        Args:
            technical: テクニカル分析結果
            forecast: 予測結果
            fundamental: ファンダメンタルズ結果

        Returns:
            統合判断
        """
        # スコア計算（重み付け）
        scores = {
            'technical': 0,
            'forecast': 0,
            'fundamental': 0
        }

        # テクニカルスコア（40%）
        tech_signal = technical.get('combined', {}).get('signal', 'hold')
        if tech_signal == 'very_strong_buy':
            scores['technical'] = 40
        elif tech_signal == 'strong_buy':
            scores['technical'] = 35
        elif tech_signal == 'buy':
            scores['technical'] = 25
        elif tech_signal == 'hold':
            scores['technical'] = 20
        elif tech_signal == 'avoid':
            scores['technical'] = 0

        # 予測スコア（30%）
        forecast_summary = forecast.get('summary', {})
        forecast_trend = forecast_summary.get('trend', 'neutral')
        forecast_risk = forecast_summary.get('risk_level', 'medium')

        if forecast_trend == 'bullish' and forecast_risk == 'low':
            scores['forecast'] = 30
        elif forecast_trend == 'bullish':
            scores['forecast'] = 20
        elif forecast_trend == 'neutral':
            scores['forecast'] = 15
        else:
            scores['forecast'] = 0

        # ファンダメンタルズスコア（30%）
        fund_sentiment = fundamental.get('avg_sentiment', 'neutral')
        if fund_sentiment == 'positive':
            scores['fundamental'] = 30
        elif fund_sentiment == 'neutral':
            scores['fundamental'] = 15
        else:
            scores['fundamental'] = 0

        # 総合スコア
        total_score = sum(scores.values())

        # 最終判定
        if total_score >= 80:
            final_signal = 'STRONG_BUY'
            confidence = min(total_score, 100)
        elif total_score >= 60:
            final_signal = 'BUY'
            confidence = total_score
        elif total_score >= 40:
            final_signal = 'HOLD'
            confidence = 50
        else:
            final_signal = 'AVOID'
            confidence = 100 - total_score

        # 理由生成
        reasons = []

        # テクニカル理由
        if scores['technical'] > 25:
            reasons.append(f"✅ テクニカル: {technical['combined']['description']}")
        elif scores['technical'] < 15:
            reasons.append(f"❌ テクニカル: {technical['combined']['description']}")

        # 予測理由
        if scores['forecast'] > 20:
            reasons.append(f"✅ 予測: {forecast_summary.get('recommendation', {}).get('description', '')}")
        elif scores['forecast'] == 0:
            reasons.append(f"❌ 予測: 下降トレンドまたは高リスク")

        # ファンダメンタルズ理由
        if scores['fundamental'] > 20:
            reasons.append(f"✅ ニュース: {fundamental['description']}")
        elif scores['fundamental'] == 0:
            reasons.append(f"❌ ニュース: ネガティブなセンチメント")

        return {
            'signal': final_signal,
            'confidence': confidence,
            'total_score': total_score,
            'breakdown': scores,
            'reasons': reasons,
            'description': f"{final_signal} (信頼度: {confidence}%)"
        }

    def display_result(self, result: dict):
        """結果を見やすく表示"""
        symbol = result['symbol']

        print(f"\n{'='*80}")
        print(f"📊 {symbol} - 統合分析結果")
        print(f"{'='*80}\n")

        # 統合判断
        integrated = result['integrated']
        print(f"🎯 **最終判定**: {integrated['signal']}")
        print(f"   信頼度: {integrated['confidence']}%")
        print(f"   総合スコア: {integrated['total_score']}/100\n")

        print(f"📋 **判断理由**:")
        for reason in integrated['reasons']:
            print(f"   {reason}")

        print(f"\n📈 **スコア内訳**:")
        breakdown = integrated['breakdown']
        print(f"   テクニカル: {breakdown['technical']}/40")
        print(f"   予測: {breakdown['forecast']}/30")
        print(f"   ニュース: {breakdown['fundamental']}/30")

        # 詳細
        print(f"\n{'─'*80}")
        print(f"📊 テクニカル分析詳細")
        print(f"{'─'*80}")
        technical = result['technical']
        print(f"   RSI: {technical['rsi']['description']}")
        print(f"   MACD: {technical['macd']['description']}")
        print(f"   Bollinger: {technical['bollinger']['description']}")

        print(f"\n{'─'*80}")
        print(f"🔮 予測分析詳細")
        print(f"{'─'*80}")
        forecast = result['forecast']['summary']
        print(f"   トレンド: {forecast['trend']}")
        print(f"   リスクレベル: {forecast['risk_level']}")
        print(f"   推奨: {forecast['recommendation']['description']}")

        print(f"\n{'─'*80}")
        print(f"📰 ファンダメンタルズ詳細")
        print(f"{'─'*80}")
        fundamental = result['fundamental']
        print(f"   {fundamental['description']}")

        if fundamental.get('latest_news'):
            print(f"\n   最新ニュース:")
            for i, news in enumerate(fundamental['latest_news'], 1):
                print(f"     {i}. {news['title']} ({news['sentiment']})")

        print(f"\n{'='*80}\n")
```

---

## Scene 6: 実行テスト

```python
# テスト実行
engine = IntegratedAnalysisEngine()

# BTCを分析
result = engine.analyze('BTC')

# 結果表示
engine.display_result(result)
```

**出力例**:
```
================================================================================
🔍 BTC - 統合分析開始
================================================================================

📥 [1/4] データ収集中...
📊 [2/4] テクニカル分析中...
🔮 [3/4] 数学的予測中...
📰 [4/4] ファンダメンタルズ分析中...

⚡ 統合判断中...

================================================================================
📊 BTC - 統合分析結果
================================================================================

🎯 **最終判定**: BUY
   信頼度: 75%
   総合スコア: 75/100

📋 **判断理由**:
   ✅ テクニカル: 【強い買いシグナル】複数指標が買いを示唆。
   ✅ 予測: 上昇トレンド予測＋低リスク。買いに適した環境。
   ✅ ニュース: 5件のニュース、センチメント: positive

📈 **スコア内訳**:
   テクニカル: 35/40
   予測: 25/30
   ニュース: 15/30

────────────────────────────────────────────────────────────────────────────────
📊 テクニカル分析詳細
────────────────────────────────────────────────────────────────────────────────
   RSI: 売られすぎ（RSI=28.5）。反発の可能性あり。
   MACD: ゴールデンクロス検出。上昇トレンド開始の可能性。
   Bollinger: Lower Band付近（売られすぎ） / 低ボラティリティ（安全）

────────────────────────────────────────────────────────────────────────────────
🔮 予測分析詳細
────────────────────────────────────────────────────────────────────────────────
   トレンド: bullish
   リスクレベル: low
   推奨: 上昇トレンド予測＋低リスク。買いに適した環境。

────────────────────────────────────────────────────────────────────────────────
📰 ファンダメンタルズ詳細
────────────────────────────────────────────────────────────────────────────────
   5件のニュース、センチメント: positive

   最新ニュース:
     1. ビットコインETF、SECが承認... (very_positive)
     2. 機関投資家の参入が加速... (positive)
     3. ハッシュレートが過去最高を更新... (positive)

================================================================================
```

**ユウタ**: 「すげえ...全部が統合されてる！」

**ミコ**: 「これが完成形だ」

---

## Scene 7: エピローグ - ユウタ式の完成

**ミコ**: 「ユウタ、思い出してみろ」

**ミコ**: 「Week 1で、100円チャレンジを始めた時」

**ユウタ**: 「うん。SHIB買って、負けた」

**ミコ**: 「あの時は『なんとなく』だった」

**ミコ**: 「でも、今は違う」

**ユウタ**: 「今は...」

```markdown
【ユウタ式スイングトレード - 完成版】

## 武器
1. RSI: 過熱/冷却判定
2. MACD: 勢い判定
3. Bollinger Bands: リスク判定
4. ARIMA: 価格予測
5. GARCH: ボラティリティ予測
6. ニュース分析: ファンダメンタルズ

## 戦略
スタイル: スイングトレード（3日〜2週間）
判断基準: テクニカル40% + 予測30% + ニュース30%

## エントリー条件
✅ 総合スコア ≥ 75
✅ リスクレベル: 低 or 中
✅ 3つ以上の指標が買いを示唆

## イグジット条件
✅ +20-30% 利確
✅ -10% 損切り
✅ 2週間経過（判断ミス）

## 記録と改善
全取引をデータで記録
勝因・敗因を分析
システムを継続改善
```

**ユウタ**: 「これが...俺の戦い方」

**ミコ**: 「そう。**明確な根拠**がある」

**ミコ**: 「もう『なんとなく』じゃない」

---

## Scene 8: 最後の言葉

**ユウタ**: 「ミコ、ありがとう」

**ミコ**: 「何が？」

**ユウタ**: 「全部教えてくれて」

**ミコ**: 「いや、俺は何も教えてない」

**ユウタ**: 「え？」

**ミコ**: 「**道具の使い方**を教えただけだ」

**ミコ**: 「戦い方は、お前が自分で決めた」

**ミコ**: 「それが一番大事なことだ」

**ユウタ**: 「...そうか」

**ミコ**: 「さあ、100円を1000円にする旅を始めよう」

**ミコ**: 「今度は、**理由を持って**な」

---

## 📝 Chapter 6 まとめ

### 統合分析システム

```markdown
【アーキテクチャ】
Phase 1: データ収集
Phase 2: 個別分析
  - テクニカル（RSI/MACD/BB）
  - 予測（ARIMA/GARCH）
  - ファンダメンタルズ（ニュース）
Phase 3: 統合判断
  - 重み付け（40%/30%/30%）
  - スコアリング（0-100）
  - 最終推奨（BUY/SELL/HOLD）

【判定基準】
≥80点: STRONG_BUY（信頼度95%）
≥60点: BUY（信頼度75%）
≥40点: HOLD（信頼度50%）
<40点: AVOID（危険）
```

### 実装完了

✅ `analysis/integrated_engine.py` 新規作成
- `analyze()`: 包括的分析
- `_technical_analysis()`: テクニカル分析
- `_forecast_analysis()`: 予測分析
- `_fundamental_analysis()`: ファンダメンタルズ分析
- `_integrate_signals()`: 統合判断
- `display_result()`: 結果表示

---

## 🎉 全Chapterコンプリート！

### 完成した技術習得ストーリー

1. **Chapter 1**: 投資戦略の誕生（ユウタ式スイングトレード）
2. **Chapter 2**: RSIの発明（ワイルダーの物語）
3. **Chapter 3**: MACDの誕生（アペルの物語）
4. **Chapter 4**: Bollinger Bandsの発明（ボリンジャーの物語）
5. **Chapter 5**: ARIMA/GARCHの発見（数学者たちの物語）
6. **Chapter 6**: 統合分析システム（全ての武器を統合）

---

**次のステップ**: これらのストーリーを読みながら、実際にコードを実装していく

---

## 🛠️ 実践で使う

統合分析システムを実際の取引で活用する方法：
- **Week 3: ニュース分析と統合判断**（作成予定） - 全技術を統合した総合判断
  - Technical 40% + Forecast 30% + Fundamental 30%
  - BUY/SELL/HOLDの推奨
  - 理由の明確化

---

**教材を最初から**:
- 実践: [Week 1](../week1_basics_v2.md)
- 理解: [Chapter 1](./01_investment_strategy.md)

---

**Powered by Claude Code**
全ての技術には、それを発明した人の物語がある。
