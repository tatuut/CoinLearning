# 🎯 次にやること（優先順位付き）

**最終更新**: 2025-10-27
**現在の進捗**: 52.5%（Phase 1: 100%, Phase 2: 80%, Phase 3: 0%, Phase 4: 30%）

---

## 🚀 即座に開始すべきタスク（Week 1-2）

### 1. Anthropic API Keyの取得（30分）

```bash
# ステップ1: https://console.anthropic.com/ にアクセス
# ステップ2: API Keyを取得
# ステップ3: 環境変数に設定
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# ステップ4: ライブラリインストール
pip install anthropic>=0.18.0

# ステップ5: テスト
python -c "import anthropic; print('OK')"
```

---

### 2. OrganicScorer実装（5-7日）⭐ 最重要

**優先度**: 🔴 最高
**理由**: 「なぜ買うべきか」を説明できる機能（最大の価値）

#### ファイル作成

```bash
# 実装ファイル
touch src/analysis/organic_scorer.py

# プロンプト設計ドキュメント
mkdir -p docs/prompts
touch docs/prompts/organic_analysis_prompt.md

# テストファイル
touch src/analysis/test_organic_scorer.py
```

#### 実装順序

1. **Day 1-2**: プロンプト設計
   - 6カテゴリー評価の詳細定義
   - JSON出力フォーマット設計
   - テストケース作成

2. **Day 3-4**: OrganicScorerクラス実装
   - 基本的なClaude API呼び出し
   - プロンプト構築ロジック
   - レスポンスパース処理

3. **Day 5-6**: 機能拡張
   - キャッシュ機能実装
   - エラーハンドリング
   - リトライロジック

4. **Day 7**: テストと改善
   - 複数ニュースでテスト
   - プロンプト改善
   - ドキュメント作成

**参考**: `docs/implementation_roadmap.md` のPhase 3.1セクション

---

### 3. IntegratedScoringEngine実装（3-4日）

**優先度**: 🔴 最高
**理由**: 全機能を統合する核心部分

#### ファイル作成

```bash
touch src/analysis/integrated_engine.py
touch src/analysis/test_integrated_engine.py
```

#### 実装内容

```python
# 統合対象
1. 有機的分析（OrganicScorer）← 新規
2. テクニカル分析（既存）
3. ARIMA/GARCH予測（既存）
4. センチメント分析（既存の簡易版）

# 出力
- final_score: 0.0-1.0
- recommendation: 'BUY' | 'SELL' | 'HOLD'
- confidence: 0.0-1.0
- explanation: Markdown形式の詳細説明
```

**参考**: `docs/implementation_roadmap.md` のPhase 4.1セクション

---

### 4. Streamlit UI拡張（2-3日）

**優先度**: 🟠 高
**理由**: 統合スコアを可視化

#### 追加セクション

```python
# src/tools/parquet_dashboard.py に追加

def show_integrated_analysis(df, symbol, news=None):
    """統合分析セクション"""

    st.subheader("🎯 統合分析（Integrated Scoring）")

    if st.button("🔍 包括的分析を実行"):
        with st.spinner("分析中...（30-60秒かかります）"):
            engine = IntegratedScoringEngine()
            result = engine.score_comprehensive(symbol, news)

            # 最終スコア表示
            st.metric("最終スコア", f"{result['final_score']:.3f}")
            st.metric("推奨アクション", result['recommendation'])
            st.metric("確信度", f"{result['confidence']*100:.1f}%")

            # 詳細説明
            st.markdown(result['explanation'])

            # 有機的分析の詳細
            with st.expander("📊 有機的分析の詳細"):
                # 6カテゴリーのスコアと理由を表示
                ...

            # 数学的分析の詳細
            with st.expander("🔢 数学的分析の詳細"):
                # テクニカル指標、予測結果を表示
                ...
```

---

## 📅 Week 3-4: 高優先度タスク

### 5. FinBERTセンチメント分析（3-4日）

**優先度**: 🟠 高
**理由**: 精度向上（60% → 85-92%）

```bash
# ライブラリインストール
pip install transformers>=4.30.0 torch>=2.0.0

# ファイル作成
touch src/analysis/sentiment_analyzer.py
```

**実装内容**:
- FinBERT（金融特化BERT）
- BART MNLI（Bullish/Bearish判定）
- 既存の簡易センチメント分析との比較

---

### 6. バックテスト機能（2-3日）

**優先度**: 🟠 高
**理由**: 推奨アクションの精度検証

```bash
touch src/analysis/backtester.py
```

**実装内容**:
```python
class Backtester:
    def backtest(self, symbol, start_date, end_date, initial_capital=100):
        """
        過去の推奨に従ったシミュレーション

        Returns:
            {
                'trades': 47,
                'win_rate': 0.68,
                'final_capital': 237,
                'return': 1.37,
                'sharpe_ratio': 1.8
            }
        """
```

---

## 📅 Week 5-6: 中優先度タスク

### 7. LSTM/GRUモデル（6-8日）

**優先度**: 🟡 中
**理由**: 予測精度向上（ARIMA: 2-5% → LSTM: 1.5-3%）

```bash
# ライブラリインストール
pip install torch>=2.0.0
# または
pip install tensorflow>=2.13.0

# ファイル作成
touch src/analysis/ml_forecasting.py
```

**なぜ後回し？**
- 有機的分析の方が価値が高い（理由説明ができる）
- 予測精度の改善幅が小さい（2-5% → 1.5-3%）
- 実装に時間がかかる（6-8日）

---

## 📋 実装チェックリスト

### ✅ 完了済み（Phase 1-2）

- [x] Parquet保存システム
- [x] 差分更新機能
- [x] ニュース保存システム
- [x] RSI/MACD/Bollinger Bands
- [x] ARIMA/GARCH予測
- [x] Streamlit基本UI

### 🔄 進行中（Phase 3-4）

Week 1-2:
- [ ] Anthropic API Key取得
- [ ] OrganicScorer実装
- [ ] IntegratedScoringEngine実装
- [ ] Streamlit UI拡張

Week 3-4:
- [ ] FinBERT実装
- [ ] バックテスト機能

Week 5-6:
- [ ] LSTMモデル（オプション）

---

## 🎯 マイルストーン

### 🏁 Milestone 1（Week 2終了時）

**目標**: 本質的な価格決定要因を分析できるシステム

**完了条件**:
- ✅ OrganicScorerが動作する
- ✅ IntegratedEngineが動作する
- ✅ Streamlitで統合分析を表示できる
- ✅ 1銘柄（BTC）で動作確認

**デモ**:
```bash
# ダッシュボード起動
python -m streamlit run src/tools/parquet_dashboard.py

# 「🔍 包括的分析を実行」ボタンをクリック
# → 30-60秒で結果が表示される
# → 最終スコア、推奨アクション、6カテゴリーの詳細理由が見れる
```

---

### 🏁 Milestone 2（Week 4終了時）

**目標**: 高精度センチメント分析とバックテスト

**完了条件**:
- ✅ FinBERTが動作する
- ✅ バックテストが動作する
- ✅ 過去1年の精度検証完了
- ✅ 推奨アクションの信頼性確認

---

### 🏁 Milestone 3（Week 6終了時）

**目標**: 機械学習予測の統合（オプション）

**完了条件**:
- ✅ LSTMモデルが動作する
- ✅ 予測精度がARIMAより高い
- ✅ IntegratedEngineに統合

---

## 💡 開発のヒント

### プロンプトエンジニアリング

**良いプロンプトの条件**:
1. 明確な役割定義（「あなたは仮想通貨アナリストです」）
2. 具体的な評価基準（6カテゴリーの詳細説明）
3. 出力フォーマットの指定（JSON）
4. 例示（Few-shot learning）

**コツ**:
- プロンプトは別ファイル（`docs/prompts/`）で管理
- バージョン管理して改善履歴を残す
- テストケースで精度を確認

---

### エラーハンドリング

```python
# LLM APIは失敗することがある
try:
    result = organic_scorer.score_news(news, symbol, price_data)
except anthropic.APIError as e:
    logger.error(f"Claude API エラー: {e}")
    # フォールバック: 簡易スコアリング
    result = simple_keyword_scoring(news)
except Exception as e:
    logger.error(f"予期しないエラー: {e}")
    result = None
```

---

### コスト管理

```python
# キャッシュ機能を必ず実装
class CachedOrganicScorer:
    def __init__(self):
        self.cache = {}  # {news_hash: result}

    def score_news(self, news, symbol, price_data):
        news_hash = hashlib.md5(
            f"{news['title']}{news['content']}".encode()
        ).hexdigest()

        if news_hash in self.cache:
            return self.cache[news_hash]

        # LLM API呼び出し
        result = super().score_news(news, symbol, price_data)

        # キャッシュに保存
        self.cache[news_hash] = result

        return result
```

**コスト見積もり**:
- 1ニュース: 約2.7円
- 100ニュース: 約270円
- キャッシュがあれば2回目以降無料

---

## 📚 参考ドキュメント

- **詳細な実装計画**: `docs/implementation_roadmap.md`
- **ストーリー形式の解説**: `docs/implementation_story.md`
- **システム設計**: `docs/system_redesign_proposal.md`
- **プロジェクト構造**: `PROJECT_STRUCTURE.md`

---

## 🤝 サポート

質問や問題があれば、以下を確認:

1. **実装ロードマップ**: 技術的な詳細
2. **実装ストーリー**: 物語形式で理解
3. **既存コード**: `src/analysis/forecasting.py` を参考

---

**作成者**: Claude Code
**最終更新**: 2025-10-27

**次のアクション**: Anthropic API Keyを取得して、OrganicScorerの実装を開始！
