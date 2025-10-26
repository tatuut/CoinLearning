# 🔬 数学的分析 + 有機的分析の2層アーキテクチャ

**設計原則**: 数学が基礎、有機的分析はその上に構築される

---

## 🎯 基本思想

### 誤った設計（旧案）
```
❌ LLMで有機的分析（主） → 数学的分析（従）

問題点:
- AIが主観的に判断してしまう
- 数学的根拠が弱い
- 「なぜこのスコア？」が説明できない
- コストが高い（全てLLM）
```

### 正しい設計（新案）
```
✅ 数学的分析（基礎・必須） → Claude Code有機的分析（補完）

メリット:
- 数学的根拠が明確
- 客観的なベースラインがある
- Claude Codeは「数学では捉えきれない要素」のみ評価
- コストが低い（数学は無料）
```

---

## 📊 2層構造の詳細

### Layer 1: 数学的分析エンジン（客観的事実）

**目的**: 数値データから客観的スコアを算出

```python
class MathematicalAnalysisEngine:
    """数学的分析エンジン（Layer 1）"""

    def analyze(self, symbol: str, price_data: pd.DataFrame) -> dict:
        """
        客観的な数学的分析

        Returns:
            {
                'technical_score': 0.65,     # テクニカル指標から算出
                'forecast_score': 0.72,      # 予測モデルから算出
                'volatility_score': 0.55,    # リスク評価
                'momentum_score': 0.80,      # モメンタム評価
                'base_score': 0.68,          # 総合スコア（加重平均）
                'details': {
                    'rsi': 45.2,
                    'macd': {'signal': 'buy', 'strength': 0.7},
                    'arima_forecast_7d': 71000,
                    'current_price': 68000,
                    'forecast_return_7d': 0.044,  # +4.4%
                    'volatility': 0.023,
                    'risk_level': '中程度'
                }
            }
        """

        # 1. テクニカル指標スコア
        technical = self._calculate_technical_score(price_data)

        # 2. 予測モデルスコア
        forecast = self._calculate_forecast_score(price_data)

        # 3. ボラティリティスコア
        volatility = self._calculate_volatility_score(price_data)

        # 4. モメンタムスコア
        momentum = self._calculate_momentum_score(price_data)

        # 5. 基本スコア（加重平均）
        base_score = (
            technical['score'] * 0.35 +
            forecast['score'] * 0.35 +
            volatility['score'] * 0.15 +
            momentum['score'] * 0.15
        )

        return {
            'technical_score': technical['score'],
            'forecast_score': forecast['score'],
            'volatility_score': volatility['score'],
            'momentum_score': momentum['score'],
            'base_score': base_score,
            'details': {**technical['details'], **forecast['details']}
        }

    def _calculate_technical_score(self, df):
        """テクニカル指標からスコア算出"""

        rsi = self._calculate_rsi(df)
        macd = self._calculate_macd(df)
        bb = self._calculate_bollinger(df)

        # スコアリングルール
        score = 0.0

        # RSI: 30-70が理想（買われすぎ/売られすぎでない）
        if 30 < rsi < 70:
            score += 0.4 * (1 - abs(rsi - 50) / 20)  # 50に近いほど高得点
        elif rsi < 30:
            score += 0.6  # 売られすぎ → 反発期待
        else:  # rsi > 70
            score += 0.2  # 買われすぎ → 注意

        # MACD: 買いシグナルで高得点
        if macd['signal'] == 'buy':
            score += 0.4 * macd['strength']
        elif macd['signal'] == 'sell':
            score += 0.1

        # Bollinger Bands: ミドルライン付近で安定
        if bb['position'] == 'middle':
            score += 0.2
        elif bb['position'] == 'lower':
            score += 0.3  # 下限付近 → 反発期待
        else:  # upper
            score += 0.1  # 上限付近 → 過熱感

        return {
            'score': min(score, 1.0),
            'details': {
                'rsi': rsi,
                'macd': macd,
                'bollinger': bb
            }
        }

    def _calculate_forecast_score(self, df):
        """予測モデルからスコア算出"""

        from src.analysis.forecasting import ForecastingEngine
        engine = ForecastingEngine()

        result = engine.combined_forecast(df, periods=7)

        if not result['price_forecast']['success']:
            return {'score': 0.5, 'details': {}}

        current_price = result['current_price']
        forecast_price = result['price_forecast']['forecast'][-1]
        forecast_return = (forecast_price - current_price) / current_price

        # スコアリングルール
        # 予測リターンが高いほど高得点
        if forecast_return > 0.1:  # +10%以上
            score = 0.9
        elif forecast_return > 0.05:  # +5-10%
            score = 0.8
        elif forecast_return > 0:  # +0-5%
            score = 0.6 + forecast_return * 8  # 線形補間
        elif forecast_return > -0.05:  # -0 to -5%
            score = 0.4 + forecast_return * 4
        else:  # -5%以下
            score = 0.1

        return {
            'score': score,
            'details': {
                'current_price': current_price,
                'forecast_price_7d': forecast_price,
                'forecast_return_7d': forecast_return
            }
        }

    def _calculate_volatility_score(self, df):
        """ボラティリティからリスクスコア算出"""

        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * 100  # パーセント表示

        # スコアリングルール
        # 低ボラティリティ = 高スコア（安全）
        if volatility < 1.5:
            score = 0.9
        elif volatility < 3.0:
            score = 0.7
        elif volatility < 5.0:
            score = 0.5
        elif volatility < 10.0:
            score = 0.3
        else:
            score = 0.1

        return {
            'score': score,
            'details': {
                'volatility': volatility,
                'risk_level': self._classify_risk(volatility)
            }
        }

    def _calculate_momentum_score(self, df):
        """モメンタムスコア算出"""

        # 短期・中期・長期リターン
        returns_7d = df['close'].pct_change(7).iloc[-1]
        returns_30d = df['close'].pct_change(30).iloc[-1]
        returns_90d = df['close'].pct_change(90).iloc[-1]

        # スコアリングルール
        # 全期間でプラスなら高得点
        score = 0.0

        if returns_7d > 0:
            score += 0.3
        if returns_30d > 0:
            score += 0.4
        if returns_90d > 0:
            score += 0.3

        # ボーナス: 加速トレンド（短期 > 中期 > 長期）
        if returns_7d > returns_30d > returns_90d:
            score += 0.2

        return {
            'score': min(score, 1.0),
            'details': {
                'returns_7d': returns_7d,
                'returns_30d': returns_30d,
                'returns_90d': returns_90d
            }
        }
```

---

### Layer 2: Claude Code有機的分析（文脈理解）

**目的**: 数学では捉えきれない要素を評価してスコアを調整

```python
class OrganicAnalysisRules:
    """Claude Code用の有機的分析ルール"""

    # Claude Codeが必ずチェックする項目
    MANDATORY_CHECKS = [
        "ニュースの文脈理解",
        "規制の影響評価",
        "市場心理の推測",
        "歴史的パターンとの比較",
        "外部ショックの可能性"
    ]

    # スコア調整範囲（数学的スコアから±0.2まで）
    MAX_ADJUSTMENT = 0.2

    @staticmethod
    def get_analysis_prompt(math_analysis: dict, news: dict, symbol: str) -> str:
        """
        Claude Code用の分析プロンプト

        重要: Claude Codeに「思考の型」を強制する
        """

        return f"""
# 有機的分析タスク

あなたは仮想通貨プロトレーダーのアシスタントです。
数学的分析の結果を基に、「数学では捉えきれない要素」を評価してください。

---

## 【数学的分析結果】（客観的事実）

### 基本スコア: {math_analysis['base_score']:.3f}

#### 内訳:
- テクニカルスコア: {math_analysis['technical_score']:.3f}
- 予測スコア: {math_analysis['forecast_score']:.3f}
- ボラティリティスコア: {math_analysis['volatility_score']:.3f}
- モメンタムスコア: {math_analysis['momentum_score']:.3f}

#### 詳細データ:
- RSI(14): {math_analysis['details']['rsi']:.2f}
- MACD: {math_analysis['details']['macd']['signal']} (強度: {math_analysis['details']['macd']['strength']:.2f})
- 7日後予測価格: ${math_analysis['details']['forecast_price_7d']:,.2f}
- 予測リターン: {math_analysis['details']['forecast_return_7d']*100:+.2f}%
- ボラティリティ: {math_analysis['details']['volatility']:.2f}%
- リスクレベル: {math_analysis['details']['risk_level']}

---

## 【ニュース情報】

銘柄: {symbol}
タイトル: {news['title']}
本文: {news['content']}
公開日: {news['published_date']}
出典: {news['source']}

---

## 【あなたのタスク】

以下の5項目を**必ず順番に**評価してください。

### 1. ニュースの文脈理解
- このニュースは{symbol}の価格に対して本質的にポジティブ/ネガティブ/中立？
- なぜそう判断するか？（3文以内）
- 影響度: -1.0（非常にネガティブ）〜 +1.0（非常にポジティブ）

### 2. 規制の影響評価
- このニュースは規制面でどのような影響があるか？
- 政府・SEC・取引所などの動きは？
- 影響度: -1.0 〜 +1.0

### 3. 市場心理の推測
- このニュースを見た投資家はどう反応するか？
- SNS・メディアでの盛り上がりは？
- 影響度: -1.0 〜 +1.0

### 4. 歴史的パターンとの比較
- 過去に類似のニュースがあったか？
- その時の価格変動はどうだったか？
- 今回も同じパターンが予想されるか？
- 影響度: -1.0 〜 +1.0

### 5. 外部ショックの可能性
- このニュースは突発的なショックか？
- ハッキング・倒産・著名人発言など
- 影響度: -1.0 〜 +1.0

---

## 【スコア調整ルール】

- 数学的基本スコア: {math_analysis['base_score']:.3f}
- 調整可能範囲: ±0.2（つまり {math_analysis['base_score']-0.2:.3f} 〜 {math_analysis['base_score']+0.2:.3f}）
- 5項目の影響度を平均して調整値を算出
- 調整後の最終スコア = 基本スコア + 調整値

---

## 【出力フォーマット】（JSON）

{{
  "context_analysis": {{
    "sentiment": "positive" | "negative" | "neutral",
    "reasoning": "...",
    "impact": 0.8
  }},
  "regulatory_analysis": {{
    "reasoning": "...",
    "impact": 0.6
  }},
  "market_psychology": {{
    "reasoning": "...",
    "impact": 0.9
  }},
  "historical_pattern": {{
    "reasoning": "...",
    "similar_cases": ["事例1", "事例2"],
    "impact": 0.7
  }},
  "external_shock": {{
    "reasoning": "...",
    "is_shock": false,
    "impact": 0.0
  }},
  "adjustment_value": 0.15,
  "final_score": 0.83,
  "recommendation": "BUY" | "SELL" | "HOLD",
  "confidence": 0.85,
  "summary": "3-5文で総合評価"
}}

**重要**:
- 必ず5項目すべてを評価すること
- 各項目で「reasoning」を必ず記述すること
- adjustment_valueは必ず±0.2以内に収めること
- JSONのみを出力すること（他の文章は不要）
"""
```

---

## 🔄 統合フロー

```python
class TwoLayerScoringEngine:
    """2層スコアリングエンジン"""

    def __init__(self):
        self.math_engine = MathematicalAnalysisEngine()
        self.organic_rules = OrganicAnalysisRules()

    def score_comprehensive(self, symbol: str, news: dict = None) -> dict:
        """
        包括的スコアリング

        フロー:
        1. 数学的分析（必須・無料）
        2. ニュースがあれば有機的分析（オプション・有料）
        3. 統合して最終判断
        """

        # Step 1: 数学的分析（Layer 1）
        storage = TimeSeriesStorage()
        price_data = storage.load_price_data(symbol, '1d')

        math_analysis = self.math_engine.analyze(symbol, price_data)

        # Step 2: 有機的分析（Layer 2）- ニュースがある場合のみ
        organic_analysis = None
        if news:
            prompt = self.organic_rules.get_analysis_prompt(
                math_analysis, news, symbol
            )

            # Claude Codeに分析を依頼
            organic_analysis = self._call_claude_code(prompt)

            # スコア調整の妥当性チェック
            if abs(organic_analysis['adjustment_value']) > self.organic_rules.MAX_ADJUSTMENT:
                logger.warning(f"調整値が範囲外: {organic_analysis['adjustment_value']}")
                organic_analysis['adjustment_value'] = np.clip(
                    organic_analysis['adjustment_value'],
                    -self.organic_rules.MAX_ADJUSTMENT,
                    self.organic_rules.MAX_ADJUSTMENT
                )

            final_score = math_analysis['base_score'] + organic_analysis['adjustment_value']
        else:
            # ニュースがない場合は数学的スコアのみ
            final_score = math_analysis['base_score']

        # Step 3: 推奨アクション生成
        recommendation = self._generate_recommendation(
            final_score,
            math_analysis,
            organic_analysis
        )

        return {
            'final_score': final_score,
            'recommendation': recommendation['action'],
            'confidence': recommendation['confidence'],
            'math_analysis': math_analysis,
            'organic_analysis': organic_analysis,
            'explanation': self._generate_explanation(
                math_analysis, organic_analysis, final_score, recommendation
            )
        }

    def _generate_recommendation(self, score, math, organic):
        """
        推奨アクション生成

        ルール:
        - 数学的条件とスコアの両方をチェック
        - 単一のスコアだけで判断しない
        """

        rsi = math['details']['rsi']
        macd_signal = math['details']['macd']['signal']
        forecast_trend = math['details']['forecast_return_7d'] > 0
        volatility = math['details']['volatility']

        # 基本判定
        if (score > 0.75 and
            rsi < 70 and
            forecast_trend and
            macd_signal == 'buy' and
            volatility < 5.0):
            action = 'STRONG_BUY'
            confidence = 0.9

        elif (score > 0.65 and
              rsi < 65 and
              forecast_trend):
            action = 'BUY'
            confidence = 0.75

        elif (score < 0.35 and
              rsi > 30 and
              not forecast_trend and
              macd_signal == 'sell'):
            action = 'STRONG_SELL'
            confidence = 0.9

        elif (score < 0.45 and
              rsi > 35):
            action = 'SELL'
            confidence = 0.75

        else:
            action = 'HOLD'
            confidence = 0.6

        # 有機的分析がある場合、信頼度を調整
        if organic:
            confidence = (confidence + organic['confidence']) / 2

        return {
            'action': action,
            'confidence': confidence
        }

    def _generate_explanation(self, math, organic, final_score, recommendation):
        """詳細な説明を生成"""

        explanation = f"""
# 総合分析レポート

## 最終判断
- **最終スコア**: {final_score:.3f}
- **推奨アクション**: {recommendation['action']}
- **確信度**: {recommendation['confidence']*100:.1f}%

---

## Layer 1: 数学的分析（客観的事実）

### 基本スコア: {math['base_score']:.3f}

#### 内訳:
- **テクニカル分析**: {math['technical_score']:.3f}
  - RSI(14): {math['details']['rsi']:.2f} → {'買われすぎ' if math['details']['rsi'] > 70 else '売られすぎ' if math['details']['rsi'] < 30 else '中立'}
  - MACD: {math['details']['macd']['signal'].upper()}シグナル

- **予測分析**: {math['forecast_score']:.3f}
  - 7日後予測価格: ${math['details']['forecast_price_7d']:,.2f}
  - 予測リターン: {math['details']['forecast_return_7d']*100:+.2f}%

- **リスク分析**: {math['volatility_score']:.3f}
  - ボラティリティ: {math['details']['volatility']:.2f}%/日
  - リスクレベル: {math['details']['risk_level']}

- **モメンタム分析**: {math['momentum_score']:.3f}
  - 7日リターン: {math['details']['returns_7d']*100:+.2f}%
  - 30日リターン: {math['details']['returns_30d']*100:+.2f}%

---
"""

        if organic:
            explanation += f"""
## Layer 2: 有機的分析（文脈理解）

### スコア調整: {organic['adjustment_value']:+.3f}

#### 評価項目:

1. **ニュースの文脈**: {organic['context_analysis']['sentiment'].upper()}
   - 影響度: {organic['context_analysis']['impact']:+.2f}
   - 理由: {organic['context_analysis']['reasoning']}

2. **規制の影響**:
   - 影響度: {organic['regulatory_analysis']['impact']:+.2f}
   - 理由: {organic['regulatory_analysis']['reasoning']}

3. **市場心理**:
   - 影響度: {organic['market_psychology']['impact']:+.2f}
   - 理由: {organic['market_psychology']['reasoning']}

4. **歴史的パターン**:
   - 影響度: {organic['historical_pattern']['impact']:+.2f}
   - 理由: {organic['historical_pattern']['reasoning']}
   - 類似事例: {', '.join(organic['historical_pattern']['similar_cases'])}

5. **外部ショック**:
   - 影響度: {organic['external_shock']['impact']:+.2f}
   - 理由: {organic['external_shock']['reasoning']}

### 総合評価:
{organic['summary']}

---
"""

        explanation += f"""
## 結論

数学的分析{' と有機的分析' if organic else ''}の結果、**{recommendation['action']}**を推奨します。

**理由**:
- 数学的根拠: 基本スコア {math['base_score']:.3f}（テクニカル・予測・リスク・モメンタムの総合評価）
"""

        if organic:
            explanation += f"- 文脈的根拠: 調整値 {organic['adjustment_value']:+.3f}（ニュース分析による補正）\n"

        explanation += f"""
**注意**: この分析は過去データと現在の情報に基づいています。実際の投資判断は自己責任で行ってください。
"""

        return explanation
```

---

## 🎯 実装の優先順位

### Phase 1: 数学的分析エンジンの完成（Week 1-2）

**最優先** - これがなければ何も始まらない

```bash
# タスク
1. MathematicalAnalysisEngine実装
   - _calculate_technical_score()
   - _calculate_forecast_score()
   - _calculate_volatility_score()
   - _calculate_momentum_score()

2. スコアリングルールの検証
   - 過去データでバックテスト
   - スコアと実際のリターンの相関確認

3. ドキュメント化
   - 各スコアの計算ロジック
   - 重み付けの根拠
```

**見積時間**: 5-7日

---

### Phase 2: Claude Code有機的分析の統合（Week 3-4）

**高優先** - プロの視点を追加

```bash
# タスク
1. OrganicAnalysisRules実装
   - プロンプト設計
   - 強制チェック項目の定義

2. TwoLayerScoringEngine実装
   - 2層統合ロジック
   - スコア調整の妥当性チェック

3. テストと改善
   - 複数ニュースでテスト
   - プロンプトの改善
```

**見積時間**: 5-7日

---

## 📊 期待される成果

### 数学的分析のみ（ニュースなし）
```
入力: BTC
出力:
- 基本スコア: 0.68
- 推奨アクション: BUY
- 根拠: テクニカル0.65, 予測0.72, リスク0.55, モメンタム0.80
```

### 数学 + 有機的分析（ニュースあり）
```
入力: BTC + ニュース「ETF承認」
出力:
- 数学的スコア: 0.68
- 有機的調整: +0.15
- 最終スコア: 0.83
- 推奨アクション: STRONG_BUY
- 根拠:
  - 数学的根拠（客観）: RSI中立, MACD買い, 予測+4.4%
  - 文脈的根拠（主観）: 規制承認は歴史的転換点, 類似事例で平均+8%上昇
```

---

## 💡 なぜこの設計か？

### プロトレーダーの思考プロセス

**普通のトレーダー（数学のみ）**:
```
RSI: 45 → 中立
MACD: 買いシグナル
予測: +4%

→ BUY判断
```

**プロトレーダー（数学 + 文脈）**:
```
RSI: 45 → 中立
MACD: 買いシグナル
予測: +4%

しかし...
- ETF承認は10年越しの歴史的出来事
- 過去の類似事例（2017年CME先物承認）では+30%上昇
- SNSで「強気」の声が圧倒的
- 機関投資家の参入で数兆円規模の資金流入可能性

→ STRONG_BUY判断（数学的スコア0.68 → 最終スコア0.83）
```

**違い**: プロは**数学では見えない文脈**を読む

---

## 📝 実装チェックリスト

### Week 1-2: 数学的分析エンジン

- [ ] `src/analysis/mathematical_engine.py` 作成
- [ ] テクニカルスコア実装
- [ ] 予測スコア実装
- [ ] ボラティリティスコア実装
- [ ] モメンタムスコア実装
- [ ] バックテストで検証
- [ ] スコアリングルールの文書化

### Week 3-4: 2層統合

- [ ] `src/analysis/two_layer_engine.py` 作成
- [ ] OrganicAnalysisRules実装
- [ ] Claude Code用プロンプト設計
- [ ] スコア調整ロジック実装
- [ ] 推奨アクション生成実装
- [ ] Streamlit UI統合
- [ ] テストと改善

---

**作成者**: Claude Code
**作成日**: 2025-10-27
