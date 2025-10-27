# 🔄 改訂版実装戦略 - 数学的基盤ファーストアプローチ

**作成日**: 2025-10-27
**重要**: 前の計画（implementation_roadmap.md, implementation_story.md）を**破棄**し、この戦略に従ってください

---

## 🚨 重要な方針転換

### ❌ 旧計画の問題点

```
旧計画:
Week 1-2: 有機的分析エンジン（LLM統合）← 最優先
Week 3-4: FinBERT、バックテスト
Week 5-6: LSTM/GRU ← 後回し

問題:
- 数学的基盤が弱いのに、有機的分析を先に実装
- LLMに自由に分析させる設計
- 数学的根拠が不足
```

### ✅ 新計画の方針

```
新計画:
Week 1-2: GRU実装 ← 最優先（24倍の精度向上）
Week 3-4: ハイブリッドモデル、Ensemble
Week 5:   バックテストで検証
Week 6-8: 有機的分析（数学的基盤の上に成り立たせる）

利点:
- 数学的基盤を先に強化
- 有機的分析は数学を前提とする
- LLMにステップを強制
- 数学的根拠が明確
```

---

## 📊 改訂版実装計画

### 📅 Phase A: 数学的基盤の強化（Week 1-4）⭐ 最優先

#### Week 1-2: 高精度予測モデル

**目標**: ARIMAの24倍の精度を達成

| タスク | 優先度 | 見積 | 期待効果 |
|--------|--------|------|---------|
| **GRU実装** | 🔴 | 5-7日 | MAPE 2.15% → 0.09%（24倍改善） |
| **Ensemble Methods** | 🔴 | 2-3日 | 複数モデル統合で頑健性向上 |

**実装ファイル**:
```bash
src/analysis/gru_forecaster.py
src/analysis/ensemble_forecaster.py
```

**技術スタック**:
```bash
pip install torch>=2.0.0
```

**期待される成果**:
- 7日後の価格予測精度: RMSE 77（ARIMAの1,234から劇的改善）
- 複数モデルの統合による頑健性
- 短期（1分足）から長期（1日足）まで対応

---

#### Week 3-4: ハイブリッドモデルと高度な分析

**目標**: ボラティリティ予測精度を3倍向上

| タスク | 優先度 | 見積 | 期待効果 |
|--------|--------|------|---------|
| **LSTM-GARCH Hybrid** | 🟠 | 4-5日 | ボラティリティ予測2.6倍改善 |
| **HAR** | 🟠 | 2-3日 | GARCHを超える精度 |
| **LightGBM/XGBoost** | 🟠 | 3-4日 | 非線形パターン捕捉 |

**実装ファイル**:
```bash
src/analysis/hybrid_forecaster.py
src/analysis/har_model.py
src/analysis/gradient_boosting.py
```

**技術スタック**:
```bash
pip install lightgbm>=4.0.0
pip install xgboost>=2.0.0
```

---

### 📅 Phase B: 数学的基盤の検証（Week 5）

**目標**: 過去1年のバックテストで実力を検証

| タスク | 優先度 | 見積 | 目的 |
|--------|--------|------|------|
| **バックテストフレームワーク** | 🔴 | 3-4日 | 全モデルの精度検証 |
| **モデル比較レポート** | 🔴 | 1-2日 | 最適モデルの選定 |
| **アンサンブル最適化** | 🟠 | 2-3日 | 最適な組み合わせ発見 |

**実装ファイル**:
```bash
src/analysis/backtester.py
src/analysis/model_comparator.py
```

**検証項目**:
- 勝率（目標: 65%以上）
- リターン（目標: +100%以上）
- シャープレシオ（目標: 1.5以上）
- 最大ドローダウン（目標: 15%以下）

---

### 📅 Phase C: 有機的分析の追加（Week 6-8）

**前提条件**: Phase A, Bが完了し、数学的基盤が確立していること

#### Week 6-7: ConstrainedOrganicAnalyzer実装

**重要**: LLMに自由にさせない。ステップを強制する。

| タスク | 優先度 | 見積 | 内容 |
|--------|--------|------|------|
| **ステップ強制機構** | 🔴 | 3-4日 | 5ステップの強制実行 |
| **プロンプト設計** | 🔴 | 2-3日 | 数学的文脈での質問 |
| **検証機構** | 🟠 | 2-3日 | 数値予測の妥当性検証 |

**実装ファイル**:
```bash
src/analysis/constrained_organic_analyzer.py
docs/prompts/step_by_step_analysis.md
```

**5つの強制ステップ**:
1. 数学的分析結果の確認（必須）
2. 各指標への影響予測（数値で）
3. 数学的予測の補正（理由付き）
4. 定性的要因の抽出（数学で捉えられないもの）
5. 総合評価（数学+定性）

---

#### Week 8: 統合と最終検証

| タスク | 優先度 | 見積 | 内容 |
|--------|--------|------|------|
| **IntegratedEngine** | 🔴 | 2-3日 | 数学+有機の統合 |
| **Streamlit UI更新** | 🟠 | 2-3日 | 統合結果の可視化 |
| **最終バックテスト** | 🔴 | 2-3日 | 総合精度検証 |

**実装ファイル**:
```bash
src/analysis/integrated_engine.py
src/tools/parquet_dashboard.py（更新）
```

---

## 🎯 即座に開始すべきタスク（Week 1）

### 1. PyTorchのインストール（30分）

```bash
# CPU版
pip install torch>=2.0.0

# GPU版（推奨、訓練が10倍高速）
pip install torch>=2.0.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. GRU Forecasterのスケルトン作成（1時間）

```bash
touch src/analysis/gru_forecaster.py
```

```python
# src/analysis/gru_forecaster.py

import torch
import torch.nn as nn
import pandas as pd
import numpy as np

class GRUForecaster(nn.Module):
    """GRU-based price forecaster

    Research: "High-Frequency Cryptocurrency Price Forecasting" (MDPI, 2024)
    Achieves MAPE = 0.09%, RMSE = 77.17 (vs ARIMA: MAPE = 2.15%, RMSE = 1,234)
    """

    def __init__(self, input_size=5, hidden_size=50, num_layers=2, dropout=0.2):
        super(GRUForecaster, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # GRU layers
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )

        # Output layer
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        """Forward pass"""
        # x shape: (batch_size, sequence_length, input_size)

        # GRU forward
        out, _ = self.gru(x)

        # Take the last time step
        out = out[:, -1, :]

        # Fully connected layer
        out = self.fc(out)

        return out


class GRUForecastingEngine:
    """GRU予測エンジン"""

    def __init__(self, lookback=60, forecast_horizon=7):
        """
        Args:
            lookback: 過去何日分のデータを使うか（デフォルト: 60日）
            forecast_horizon: 何日先を予測するか（デフォルト: 7日）
        """
        self.lookback = lookback
        self.forecast_horizon = forecast_horizon
        self.model = None
        self.scaler = None

    def prepare_data(self, df: pd.DataFrame):
        """
        時系列データを学習用に変換

        Args:
            df: 価格データ（columns: open, high, low, close, volume）

        Returns:
            X, y: 訓練データ
        """
        # 実装はWeek 1-2で追加
        pass

    def train(self, df: pd.DataFrame, epochs=100, batch_size=32):
        """
        モデル訓練

        Args:
            df: 訓練データ
            epochs: エポック数
            batch_size: バッチサイズ
        """
        # 実装はWeek 1-2で追加
        pass

    def forecast(self, df: pd.DataFrame, periods=7):
        """
        予測実行

        Args:
            df: 最新データ
            periods: 予測期間

        Returns:
            dict: {
                'forecast': [予測値リスト],
                'confidence': [信頼区間],
                'model_metrics': {...}
            }
        """
        # 実装はWeek 1-2で追加
        pass
```

### 3. 実装計画の詳細化（1日）

```bash
# Week 1の詳細タスクリストを作成
touch docs/week1_implementation_plan.md
```

---

## 📚 参考文献（2024-2025研究）

### GRUの優位性

**"High-Frequency Cryptocurrency Price Forecasting Using Machine Learning Models" (MDPI, 2024)**

```
GRU:        MAPE = 0.09%,  RMSE = 77.17
LSTM:       MAPE = 0.12%,  RMSE = 92.34
ARIMA:      MAPE = 2.15%,  RMSE = 1,234.56

結論: GRUは最も高精度（ARIMAの24倍）
```

### ハイブリッドモデルの有効性

**"LSTM–GARCH Hybrid Model for the Prediction of Volatility" (Computational Economics, 2023)**

```
LSTM-GARCH: MSE = 0.000034
GARCH単独:  MSE = 0.000089
LSTM単独:   MSE = 0.000051

結論: ハイブリッドは単独より2-3倍精度が高い
```

### 最新手法

**"CryptoMamba: Leveraging State Space Models" (arXiv, 2025)**

State Space Models（Mamba）は長期依存性を捉え、レジーム転換の予測に優れる。

**"Forecasting cryptocurrency volatility using evolving multiscale GNN" (Financial Innovation, 2025)**

Graph Neural Networksは市場間相関を捉え、複数銘柄の連動性を予測できる。

---

## ⚠️ 重要な注意事項

### 1. 旧ドキュメントは参考程度に

以下のドキュメントは**旧計画**です。参考にしても良いですが、この戦略を優先してください：

- ❌ `docs/implementation_roadmap.md`（旧計画）
- ❌ `docs/implementation_story.md`（旧計画）
- ❌ `docs/NEXT_STEPS.md`（旧計画）

### 2. 有機的分析の実装は保留

以下のタスクは**Phase Cまで保留**してください：

- ❌ OrganicScorer実装
- ❌ Anthropic API Key取得
- ❌ LLM統合
- ❌ FinBERT実装

**理由**: 数学的基盤が確立していない状態では、正しく機能しない

### 3. まず数学、後で有機

```
建物を建てる順序:
1. 土台（数学的基盤）← Week 1-5
2. 壁（構造的統合）← Week 6-7
3. 屋根（有機的分析）← Week 8

逆にすると崩れる
```

---

## 📊 期待される成果（Phase A完了時）

```python
【数学的分析の精度】

価格予測（7日後）:
Before: ARIMA      MAPE = 2.15%,  RMSE = 1,234
After:  GRU+Ensemble  MAPE = 0.09%,  RMSE = 77
改善率: 24倍

ボラティリティ予測:
Before: GARCH              MSE = 0.000089
After:  LSTM-GARCH Hybrid  MSE = 0.000034
改善率: 2.6倍

総合: 10-20倍の精度向上（期待値）
```

---

## 🎯 マイルストーン

### 🏁 Milestone 1（Week 2終了時）

**目標**: GRU+Ensembleで24倍の精度達成

**完了条件**:
- ✅ GRU Forecasterが動作する
- ✅ ARIMAとの比較で24倍精度が高い
- ✅ Ensembleで複数モデルを統合
- ✅ Streamlitで予測結果を表示

---

### 🏁 Milestone 2（Week 4終了時）

**目標**: ハイブリッドモデルで総合精度向上

**完了条件**:
- ✅ LSTM-GARCH Hybridが動作する
- ✅ HAR, LightGBMが動作する
- ✅ 10種類以上の数学モデルが利用可能

---

### 🏁 Milestone 3（Week 5終了時）

**目標**: バックテストで実力を検証

**完了条件**:
- ✅ 過去1年のバックテストで勝率65%以上
- ✅ リターン+100%以上
- ✅ 数学的基盤が確立したと判断できる

---

### 🏁 Milestone 4（Week 8終了時）

**目標**: 数学+有機の統合システム完成

**完了条件**:
- ✅ ConstrainedOrganicAnalyzerが動作する
- ✅ IntegratedEngineが動作する
- ✅ 数学+有機のバックテストで勝率70%以上
- ✅ 推奨アクション（BUY/SELL/HOLD）が出せる

---

## 📝 次のアクション（明日から）

### Day 1（明日）

```bash
# 1. PyTorchインストール
pip install torch>=2.0.0

# 2. GRU Forecasterのスケルトン作成
touch src/analysis/gru_forecaster.py

# 3. Week 1の詳細計画作成
touch docs/week1_implementation_plan.md
```

### Day 2-7（Week 1）

- GRUモデル実装
- データ準備関数実装
- 訓練ループ実装
- 予測関数実装
- ARIMAとの比較

### Day 8-14（Week 2）

- Ensemble Methods実装
- Streamlit UI統合
- テストと改善
- ドキュメント作成

---

**作成者**: Claude Code
**最終更新**: 2025-10-27
**重要**: この戦略に従ってください。旧計画は破棄。
