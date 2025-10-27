# 🗺️ 実装ロードマップ（詳細版）

**作成日**: 2025-10-27
**対象**: Phase 2-4の残りタスク
**目標**: 本質的な価格決定要因を分析する高度なシステムの完成

---

## 📊 現在の進捗状況（2025-10-27時点）

### ✅ Phase 1: データインフラ構築（100%完了）

| タスク | 状態 | ファイル | 備考 |
|--------|------|---------|------|
| Parquet保存システム | ✅ 完了 | `src/data/timeseries_storage.py` | 89%圧縮達成 |
| 差分更新機能 | ✅ 完了 | `src/data/timeseries_manager.py` | 新データのみ取得 |
| ニュース保存システム | ✅ 完了 | `src/tools/news_fetcher.py` | Markdown保存 |
| メタデータDB | ✅ 完了 | `src/data/advanced_database.py` | SQLite |

**成果物**:
- 5銘柄のデータ（BTC, ETH, XRP, DOGE, SHIB）
- Parquetファイル容量: 77.9KB（1050データポイント）
- ニュースMarkdownファイル: 銘柄別フォルダ管理

---

### ⏳ Phase 2: テクニカル分析エンジン（80%完了）

#### ✅ 完了済み（2.1 基本指標）

| 指標 | 状態 | ファイル | 実装日 |
|------|------|---------|--------|
| RSI | ✅ | `src/analysis/indicators/` | 既存 |
| MACD | ✅ | `src/analysis/indicators/` | 既存 |
| Bollinger Bands | ✅ | `src/analysis/indicators/` | 既存 |
| ATR | ✅ | `src/analysis/indicators/atr.py` | 既存 |
| OBV | ✅ | `src/analysis/indicators/obv.py` | 既存 |
| Stochastic | ✅ | `src/analysis/indicators/stochastic.py` | 既存 |

#### ✅ 完了済み（2.2 時系列分析）

| モデル | 状態 | ファイル | 実装日 |
|--------|------|---------|--------|
| ARIMA | ✅ | `src/analysis/forecasting.py` | 2025-10-27 |
| GARCH | ✅ | `src/analysis/forecasting.py` | 2025-10-27 |
| 自動パラメータ選択 | ✅ | `auto_select_arima_order()` | 2025-10-27 |
| リスク分類 | ✅ | `_classify_risk()` | 2025-10-27 |

**機能**:
- 7日間の価格予測（95%信頼区間付き）
- ボラティリティ予測
- Streamlitダッシュボードに統合済み

#### ❌ 未実装（2.3 機械学習モデル）

| タスク | 優先度 | 見積時間 | 必要スキル |
|--------|--------|---------|-----------|
| GRU/LSTMモデル構築 | 高 | 3-5日 | PyTorch/TensorFlow |
| 学習データ準備 | 高 | 1日 | pandas, numpy |
| モデル訓練 | 高 | 1-2日 | GPU推奨 |
| バックテスト | 中 | 1-2日 | 統計学 |
| モデル評価・比較 | 中 | 1日 | RMSE, MAE |

**実装方針**:
```python
# src/analysis/ml_forecasting.py（新規作成）
class MLForecaster:
    """機械学習による価格予測"""

    def __init__(self, model_type='lstm'):
        # LSTM or GRU
        self.model = self._build_model(model_type)

    def prepare_data(self, df, lookback=60):
        """時系列データを学習用に変換"""
        # 60日分の履歴 → 次の1-7日を予測

    def train(self, df, epochs=100):
        """モデル訓練"""

    def forecast(self, df, periods=7):
        """予測実行"""
        return {
            'forecast': [...],
            'confidence': [...],
            'model_metrics': {...}
        }
```

**期待される精度**:
- ARIMA/GARCH: RMSE 2-5%
- LSTM/GRU: RMSE 1.5-3%（研究論文より）

---

### ❌ Phase 3: 有機的分析エンジン（0%完了）

#### 3.1 LLM統合（優先度: 最高）

| タスク | 見積時間 | 依存関係 | 備考 |
|--------|---------|---------|------|
| OpenAI/Anthropic API設定 | 0.5日 | - | API Key取得 |
| プロンプト設計 | 1-2日 | - | 6カテゴリー評価用 |
| 有機的スコアラー実装 | 2-3日 | プロンプト | `OrganicScorer` クラス |
| 理由付けシステム | 1-2日 | スコアラー | Markdown形式で出力 |

**実装ファイル**: `src/analysis/organic_scorer.py`（新規作成）

**実装方針**:
```python
class OrganicScorer:
    """有機的分析エンジン（LLM使用）"""

    def __init__(self, api_type='anthropic'):
        self.client = self._init_client(api_type)

    def score_news(self, news: dict, symbol: str, price_data: pd.DataFrame):
        """
        6カテゴリーで評価

        Returns:
            {
                'fundamental_impact': {
                    'score': 0.8,
                    'reasoning': 'ETF承認により機関投資家の参入が期待される...'
                },
                'technical_impact': {...},
                'economic_impact': {...},
                'regulatory_impact': {...},
                'sentiment_impact': {...},
                'external_shock': {...},
                'final_score': 0.78,
                'explanation': '# 総合評価\n\n...'
            }
        """

        # プロンプト構築
        prompt = self._build_prompt(news, symbol, price_data)

        # LLMに分析依頼
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # 結果をパース
        return self._parse_response(response)

    def _build_prompt(self, news, symbol, price_data):
        """
        詳細なプロンプトを生成

        含める情報:
        - ニュース本文
        - 過去30日の価格動向（統計量）
        - 現在のテクニカル指標（RSI, MACD, etc）
        - 評価基準（6カテゴリーの説明）
        """
        return f"""
あなたは仮想通貨アナリストです。以下のニュースが{symbol}の価格に与える影響を6つの観点から評価してください。

【ニュース】
タイトル: {news['title']}
本文: {news['content']}
公開日: {news['published_date']}

【現在の{symbol}の状況】
- 現在価格: ${price_data['close'].iloc[-1]:,.2f}
- 30日間リターン: {price_data['close'].pct_change(30).iloc[-1]*100:.2f}%
- RSI(14): {self.calculate_rsi(price_data):.2f}
- ボラティリティ: {price_data['close'].pct_change().std()*100:.2f}%

【評価基準】
以下の6カテゴリーでスコア（0.0-1.0）と理由を記載してください：

1. **ファンダメンタルズ影響** (fundamental_impact)
   - ブロックチェーンの信頼性、採用率、実用性への影響

2. **技術的影響** (technical_impact)
   - ハッシュレート、開発活動、アップグレードへの影響

3. **経済的影響** (economic_impact)
   - 需給バランス、流動性、機関投資家への影響

4. **規制的影響** (regulatory_impact)
   - 政府規制、ETF承認、法律への影響

5. **センチメント影響** (sentiment_impact)
   - SNS、世論、投資家心理への影響

6. **外部ショック** (external_shock)
   - ハッキング、倒産、著名人発言などの突発的影響

【出力形式（JSON）】
{{
  "fundamental_impact": {{"score": 0.8, "reasoning": "..."}},
  "technical_impact": {{"score": 0.5, "reasoning": "..."}},
  "economic_impact": {{"score": 0.9, "reasoning": "..."}},
  "regulatory_impact": {{"score": 0.95, "reasoning": "..."}},
  "sentiment_impact": {{"score": 0.85, "reasoning": "..."}},
  "external_shock": {{"score": 0.0, "reasoning": "..."}},
  "final_score": 0.78,
  "explanation": "# 総合評価\\n\\n..."
}}
"""
```

**コスト見積もり**:
- 1ニュース分析: 約1000トークン（入力）+ 1000トークン（出力）= 2000トークン
- Claude 3.5 Sonnet: $3/MTok（入力）+ $15/MTok（出力）
- **1ニュースあたり約$0.018（約2.7円）**
- 100ニュース分析で約$1.8（270円）

---

#### 3.2 センチメント分析（優先度: 中）

| タスク | 見積時間 | 備考 |
|--------|---------|------|
| FinBERT実装 | 2-3日 | Hugging Face Transformers |
| BART MNLI実装 | 1-2日 | Zero-shot classification |
| 精度検証 | 1日 | テストデータ作成 |
| Streamlit統合 | 1日 | UI追加 |

**実装ファイル**: `src/analysis/sentiment_analyzer.py`（新規作成）

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class SentimentAnalyzer:
    """FinBERT/BART MNLI によるセンチメント分析"""

    def __init__(self):
        # FinBERT（金融特化）
        self.finbert_tokenizer = AutoTokenizer.from_pretrained(
            "ProsusAI/finbert"
        )
        self.finbert_model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )

        # BART MNLI（Bullish/Bearish判定）
        self.bart_tokenizer = AutoTokenizer.from_pretrained(
            "facebook/bart-large-mnli"
        )
        self.bart_model = AutoModelForSequenceClassification.from_pretrained(
            "facebook/bart-large-mnli"
        )

    def analyze_finbert(self, text: str):
        """
        FinBERTでセンチメント分析

        Returns:
            {
                'label': 'positive' | 'negative' | 'neutral',
                'scores': {'positive': 0.85, 'negative': 0.05, 'neutral': 0.10},
                'confidence': 0.85
            }
        """
        inputs = self.finbert_tokenizer(text, return_tensors="pt",
                                        truncation=True, max_length=512)
        outputs = self.finbert_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        scores = {
            'positive': probs[0][2].item(),
            'negative': probs[0][0].item(),
            'neutral': probs[0][1].item()
        }

        label = max(scores, key=scores.get)
        confidence = scores[label]

        return {
            'label': label,
            'scores': scores,
            'confidence': confidence
        }

    def analyze_bart_mnli(self, text: str):
        """
        BART MNLIでBullish/Bearish判定

        Returns:
            {
                'label': 'bullish' | 'bearish',
                'confidence': 0.92
            }
        """
        # Zero-shot classification
        hypothesis_bullish = "This news is bullish for cryptocurrency prices."
        hypothesis_bearish = "This news is bearish for cryptocurrency prices."

        # 実装省略（BART MNLI による分類）

        return {
            'label': 'bullish' if bullish_score > bearish_score else 'bearish',
            'confidence': max(bullish_score, bearish_score)
        }
```

**期待される精度**:
- キーワードマッチング: 60%
- FinBERT: **85-92%**（研究論文より）

---

#### 3.3 価格決定要因の体系的整理（優先度: 高）

**タスク**: 6カテゴリー評価フレームワークの実装

**実装ファイル**: `src/analysis/factor_framework.py`（新規作成）

```python
class PriceFactorFramework:
    """価格決定要因の体系的フレームワーク"""

    CATEGORIES = {
        'fundamental': {
            'name': 'ファンダメンタルズ要因',
            'factors': [
                'ブロックチェーンの信頼性',
                'ネットワークの採用率',
                '実用性（決済、DeFi、NFT等）',
                '供給量（固定 vs 動的）',
                '発行スケジュール（半減期等）'
            ],
            'weight': 0.25
        },
        'technical': {
            'name': '技術要因',
            'factors': [
                '計算能力（ハッシュレート）',
                'ネットワーク参加者数',
                '開発活動（GitHubコミット数）',
                'アップグレード予定',
                'セキュリティ監査'
            ],
            'weight': 0.15
        },
        'economic': {
            'name': '経済要因',
            'factors': [
                '需要と供給のバランス',
                '流動性（取引量）',
                '生産コスト（マイニングコスト）',
                '機関投資家の参入',
                '他資産との相関'
            ],
            'weight': 0.20
        },
        'regulatory': {
            'name': '規制要因',
            'factors': [
                '政府の規制方針',
                'ETF承認状況',
                '税制',
                '取引所ライセンス',
                '法定通貨認定'
            ],
            'weight': 0.20
        },
        'sentiment': {
            'name': '市場センチメント要因',
            'factors': [
                'ニュースの内容',
                'SNSの盛り上がり',
                'インフルエンサーの発言',
                'Google検索トレンド',
                'Fear & Greed Index'
            ],
            'weight': 0.15
        },
        'external_shock': {
            'name': '外部ショック要因',
            'factors': [
                'ハッキング事件',
                '取引所の倒産',
                '著名人の発言',
                '地政学リスク',
                'マクロ経済（金利、インフレ）'
            ],
            'weight': 0.05
        }
    }

    def calculate_weighted_score(self, category_scores: dict) -> float:
        """
        各カテゴリーのスコアを重み付けして総合スコアを計算

        Args:
            category_scores: {
                'fundamental': 0.8,
                'technical': 0.6,
                'economic': 0.9,
                'regulatory': 0.95,
                'sentiment': 0.85,
                'external_shock': 0.0
            }

        Returns:
            weighted_score (0.0-1.0)
        """
        total = 0.0
        for category, score in category_scores.items():
            weight = self.CATEGORIES[category]['weight']
            total += score * weight

        return total
```

---

### ⏳ Phase 4: 統合とUI（30%完了）

#### ✅ 完了済み

| タスク | 状態 | ファイル |
|--------|------|---------|
| Streamlit基本UI | ✅ | `src/tools/parquet_dashboard.py` |
| 価格チャート表示 | ✅ | Plotly統合 |
| テクニカル指標表示 | ✅ | RSI, MACD, BB |
| ニュース表示 | ✅ | Markdown読込 |
| ARIMA/GARCH予測表示 | ✅ | 信頼区間付き |

#### ❌ 未実装（4.1 統合スコアリングエンジン）

| タスク | 見積時間 | 優先度 | 依存関係 |
|--------|---------|--------|---------|
| IntegratedScoringEngine実装 | 2-3日 | 最高 | Phase 3完了 |
| スコア統合ロジック | 1-2日 | 最高 | - |
| 推奨アクション生成 | 1日 | 高 | 統合ロジック |
| バックテスト | 2-3日 | 中 | 過去データ |

**実装ファイル**: `src/analysis/integrated_engine.py`（新規作成）

```python
class IntegratedScoringEngine:
    """統合スコアリングエンジン"""

    def __init__(self):
        self.organic_scorer = OrganicScorer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.forecaster = ForecastingEngine()
        self.ml_forecaster = MLForecaster()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.factor_framework = PriceFactorFramework()

    def score_comprehensive(self, symbol: str, news: dict = None) -> dict:
        """
        包括的スコアリング

        Returns:
            {
                'organic_analysis': {
                    'fundamental': {'score': 0.8, 'reasoning': '...'},
                    'technical': {'score': 0.6, 'reasoning': '...'},
                    'economic': {'score': 0.9, 'reasoning': '...'},
                    'regulatory': {'score': 0.95, 'reasoning': '...'},
                    'sentiment': {'score': 0.85, 'reasoning': '...'},
                    'external_shock': {'score': 0.0, 'reasoning': '...'},
                    'weighted_score': 0.78
                },
                'mathematical_analysis': {
                    'technical_indicators': {
                        'rsi': 45.2,
                        'macd': {'value': 120.5, 'signal': 'buy'},
                        'bollinger': {'position': 'middle', 'squeeze': False}
                    },
                    'forecasts': {
                        'arima_1d': 68000,
                        'arima_7d': 70000,
                        'lstm_1d': 68500,
                        'lstm_7d': 71000
                    },
                    'volatility': {
                        'current': 0.023,
                        'forecast_7d': 0.031,
                        'risk_level': '中程度'
                    },
                    'sentiment': {
                        'finbert': {'label': 'positive', 'confidence': 0.92},
                        'bart_mnli': {'label': 'bullish', 'confidence': 0.88}
                    }
                },
                'final_score': 0.78,
                'recommendation': 'BUY' | 'SELL' | 'HOLD',
                'confidence': 0.85,
                'explanation': '# 総合分析レポート\n\n...'
            }
        """

        # 1. 価格データ取得
        storage = TimeSeriesStorage()
        price_data = storage.load_price_data(symbol, '1d')

        # 2. 有機的分析（ニュースがある場合のみ）
        organic = None
        if news:
            organic = self.organic_scorer.score_news(news, symbol, price_data)

        # 3. テクニカル指標
        technical = self.technical_analyzer.analyze(price_data)

        # 4. 時系列予測（ARIMA/GARCH）
        arima_forecast = self.forecaster.combined_forecast(price_data, periods=7)

        # 5. 機械学習予測（LSTM）
        lstm_forecast = self.ml_forecaster.forecast(price_data, periods=7)

        # 6. センチメント分析（ニュースがある場合）
        sentiment = None
        if news:
            sentiment = self.sentiment_analyzer.analyze_finbert(news['content'])

        # 7. 統合
        final = self._integrate_all(
            organic, technical, arima_forecast, lstm_forecast, sentiment
        )

        return final

    def _integrate_all(self, organic, technical, arima, lstm, sentiment):
        """全分析結果を統合して最終スコアと推奨を生成"""

        # スコア計算ロジック
        scores = []

        # 有機的分析スコア（0.4の重み）
        if organic:
            organic_score = organic['weighted_score']
            scores.append(organic_score * 0.4)

        # テクニカル分析スコア（0.3の重み）
        technical_score = self._calculate_technical_score(technical)
        scores.append(technical_score * 0.3)

        # 予測スコア（0.2の重み）
        forecast_score = self._calculate_forecast_score(arima, lstm)
        scores.append(forecast_score * 0.2)

        # センチメントスコア（0.1の重み）
        if sentiment:
            sentiment_score = sentiment['scores']['positive']
            scores.append(sentiment_score * 0.1)

        final_score = sum(scores)

        # 推奨アクション
        recommendation = self._generate_recommendation(
            final_score, technical, arima
        )

        return {
            'final_score': final_score,
            'recommendation': recommendation,
            'confidence': self._calculate_confidence(organic, technical, sentiment),
            'explanation': self._generate_explanation(
                organic, technical, arima, lstm, sentiment,
                final_score, recommendation
            )
        }

    def _generate_recommendation(self, score, technical, forecast):
        """
        推奨アクション生成

        ルール:
        - final_score > 0.7 かつ RSI < 70 → BUY
        - final_score < 0.3 かつ RSI > 30 → SELL
        - それ以外 → HOLD
        """
        rsi = technical['rsi']
        macd_signal = technical['macd']['signal']
        forecast_trend = forecast['price_forecast']['forecast'][-1] > forecast['current_price']

        if score > 0.7 and rsi < 70 and forecast_trend:
            return 'BUY'
        elif score < 0.3 and rsi > 30 and not forecast_trend:
            return 'SELL'
        else:
            return 'HOLD'
```

---

#### ❌ 未実装（4.2 Streamlit UI拡張）

| タスク | 見積時間 | 優先度 |
|--------|---------|--------|
| 統合スコア表示セクション | 1日 | 高 |
| 推奨アクション表示 | 0.5日 | 高 |
| 6カテゴリー詳細表示 | 1日 | 中 |
| バックテスト結果表示 | 1日 | 低 |
| リアルタイム更新 | 2日 | 低 |

---

## 🎯 優先順位付けと実装順序

### 最優先（Week 1-2）

1. **有機的分析エンジン（LLM統合）** - Phase 3.1
   - 理由: これが最も価値の高い機能（「なぜ」を説明できる）
   - 見積: 5-7日
   - ファイル: `src/analysis/organic_scorer.py`

2. **統合スコアリングエンジン** - Phase 4.1
   - 理由: 全機能を統合する核心部分
   - 見積: 3-4日
   - ファイル: `src/analysis/integrated_engine.py`

3. **Streamlit UI拡張** - Phase 4.2
   - 理由: 統合スコアを可視化
   - 見積: 2-3日
   - ファイル: `src/tools/parquet_dashboard.py`（拡張）

**Week 1-2 合計**: 10-14日

---

### 高優先度（Week 3-4）

4. **FinBERTセンチメント分析** - Phase 3.2
   - 理由: 精度向上（60% → 85-92%）
   - 見積: 3-4日
   - ファイル: `src/analysis/sentiment_analyzer.py`

5. **バックテスト機能** - Phase 4.1
   - 理由: 推奨アクションの精度検証
   - 見積: 2-3日
   - ファイル: `src/analysis/backtester.py`

**Week 3-4 合計**: 5-7日

---

### 中優先度（Week 5-6）

6. **GRU/LSTMモデル** - Phase 2.3
   - 理由: 予測精度向上（2-5% → 1.5-3%）
   - 見積: 6-8日
   - ファイル: `src/analysis/ml_forecasting.py`

**Week 5-6 合計**: 6-8日

---

### 低優先度（Week 7+）

7. **リアルタイム更新UI**
8. **バックテスト結果の詳細可視化**
9. **API化（FastAPI）**

---

## 📈 期待される成果

### スコアリング精度

| 指標 | 現状 | 改善後（予測） |
|------|------|---------------|
| 価格予測精度（RMSE） | 不明 | ARIMA: 2-5%, LSTM: 1.5-3% |
| センチメント精度 | 60% | FinBERT: 85-92% |
| 説明可能性 | なし | 6カテゴリー詳細説明 |
| 理由付け | なし | 各要因ごとの詳細理由 |

### システム性能

| 指標 | 現状 | 目標 |
|------|------|------|
| 1銘柄の分析時間 | 2秒 | 5-10秒（LLM含む） |
| 分析コスト | 無料 | 1銘柄約$0.02（2.7円） |
| UIレスポンス | 0.1秒 | 0.1秒（維持） |

---

## 🛠️ 必要なリソース

### ライブラリ追加

```txt
# requirements.txt に追加

# Phase 2.3: 機械学習
torch>=2.0.0
tensorflow>=2.13.0  # または PyTorchのみ

# Phase 3.2: センチメント分析
transformers>=4.30.0
sentencepiece>=0.1.99

# Phase 3.1: LLM統合
anthropic>=0.18.0
openai>=1.0.0

# Phase 4: バックテスト
backtrader>=1.9.76  # オプション
```

### API Key

- Anthropic API Key（Claude 3.5 Sonnet用）
- OpenAI API Key（GPT-4用、オプション）

### 計算リソース

- GPU（LSTM訓練用、オプション）
  - Google Colab無料版でも可
  - ローカルならCUDA対応GPU推奨

---

## 📝 実装時の注意点

### 1. LLM利用のコスト管理

```python
# キャッシュ機構を実装
class CachedOrganicScorer(OrganicScorer):
    def __init__(self):
        super().__init__()
        self.cache = {}  # {news_hash: score_result}

    def score_news(self, news, symbol, price_data):
        # ニュースのハッシュ値を計算
        news_hash = self._hash_news(news)

        # キャッシュにあれば返す
        if news_hash in self.cache:
            return self.cache[news_hash]

        # なければLLMで分析
        result = super().score_news(news, symbol, price_data)

        # キャッシュに保存
        self.cache[news_hash] = result

        return result
```

### 2. エラーハンドリング

```python
# LLM APIが失敗した場合のフォールバック
try:
    organic_score = self.organic_scorer.score_news(news, symbol, price_data)
except Exception as e:
    logger.warning(f"LLM分析失敗: {e}")
    # 簡易スコアリングにフォールバック
    organic_score = self._simple_keyword_scoring(news)
```

### 3. テストデータの作成

```python
# src/analysis/test_data/
# - positive_news.json
# - negative_news.json
# - neutral_news.json

# 各ニュースに対して期待されるスコアを定義
# → 精度検証に使用
```

---

## 🎬 次のアクション

### 即座に開始すべきタスク

1. **Anthropic API Keyの取得**
   ```bash
   # https://console.anthropic.com/
   # API Keyを取得して環境変数に設定
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

2. **OrganicScorer実装開始**
   ```bash
   touch src/analysis/organic_scorer.py
   ```

3. **プロンプト設計ドキュメント作成**
   ```bash
   mkdir docs/prompts
   touch docs/prompts/organic_analysis_prompt.md
   ```

---

**作成者**: Claude Code
**最終更新**: 2025-10-27
