"""
GRU-based Cryptocurrency Price Forecaster

Research: "High-Frequency Cryptocurrency Price Forecasting Using Machine Learning Models" (MDPI, 2024)
Achieves MAPE = 0.09%, RMSE = 77.17 (vs ARIMA: MAPE = 2.15%, RMSE = 1,234)

24倍の精度向上を実現
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')


class GRUModel(nn.Module):
    """GRU Neural Network Model"""

    def __init__(self, input_size=5, hidden_size=50, num_layers=2, dropout=0.2):
        """
        Args:
            input_size: 入力次元（例: open, high, low, close, volume = 5）
            hidden_size: 隠れ層の次元数
            num_layers: GRU層の数
            dropout: ドロップアウト率（過学習防止）
        """
        super(GRUModel, self).__init__()

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
        """
        Forward pass

        Args:
            x: (batch_size, sequence_length, input_size)

        Returns:
            out: (batch_size, 1)
        """
        # GRU forward
        out, _ = self.gru(x)

        # Take the last time step
        out = out[:, -1, :]

        # Fully connected layer
        out = self.fc(out)

        return out


class TimeSeriesDataset(Dataset):
    """時系列データセット"""

    def __init__(self, X, y):
        """
        Args:
            X: (num_samples, sequence_length, input_size)
            y: (num_samples, 1)
        """
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class GRUForecastingEngine:
    """GRU予測エンジン"""

    def __init__(self, lookback=60, forecast_horizon=7, hidden_size=50, num_layers=2):
        """
        Args:
            lookback: 過去何日分のデータを使うか（デフォルト: 60日）
            forecast_horizon: 何日先を予測するか（デフォルト: 7日）
            hidden_size: GRUの隠れ層次元
            num_layers: GRU層の数
        """
        self.lookback = lookback
        self.forecast_horizon = forecast_horizon
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print(f"🔧 GRU Forecasting Engine initialized")
        print(f"   Device: {self.device}")
        print(f"   Lookback: {lookback} days")
        print(f"   Forecast horizon: {forecast_horizon} days")

    def prepare_data(self, df: pd.DataFrame, train_ratio=0.8):
        """
        時系列データを学習用に変換

        Args:
            df: 価格データ（columns: open, high, low, close, volume）
            train_ratio: 訓練データの割合

        Returns:
            train_loader, val_loader, test_data
        """
        print("\n📊 Preparing data...")

        # 必要なカラムを抽出
        data = df[['open', 'high', 'low', 'close', 'volume']].values

        # 正規化（0-1の範囲に）
        data_normalized = self.scaler.fit_transform(data)

        # シーケンスとターゲットを作成
        X, y = [], []
        for i in range(len(data_normalized) - self.lookback - self.forecast_horizon + 1):
            # 過去lookback日分のデータ
            X.append(data_normalized[i:i + self.lookback])

            # forecast_horizon日後の終値（正規化済み）
            target_idx = i + self.lookback + self.forecast_horizon - 1
            y.append(data_normalized[target_idx, 3])  # close価格のインデックスは3

        X = np.array(X)
        y = np.array(y).reshape(-1, 1)

        print(f"   Total samples: {len(X)}")
        print(f"   Input shape: {X.shape}")
        print(f"   Target shape: {y.shape}")

        # 訓練/検証/テスト分割
        train_size = int(len(X) * train_ratio)
        val_size = int(len(X) * 0.1)

        X_train, y_train = X[:train_size], y[:train_size]
        X_val, y_val = X[train_size:train_size + val_size], y[train_size:train_size + val_size]
        X_test, y_test = X[train_size + val_size:], y[train_size + val_size:]

        print(f"   Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

        # DataLoaderを作成
        train_dataset = TimeSeriesDataset(X_train, y_train)
        val_dataset = TimeSeriesDataset(X_val, y_val)

        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

        return train_loader, val_loader, (X_test, y_test)

    def train(self, train_loader, val_loader, epochs=100, learning_rate=0.001):
        """
        モデル訓練

        Args:
            train_loader: 訓練データローダー
            val_loader: 検証データローダー
            epochs: エポック数
            learning_rate: 学習率
        """
        print(f"\n🚀 Training GRU model...")
        print(f"   Epochs: {epochs}")
        print(f"   Learning rate: {learning_rate}")

        # モデル初期化
        input_size = 5  # open, high, low, close, volume
        self.model = GRUModel(
            input_size=input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers
        ).to(self.device)

        # オプティマイザーと損失関数
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        # Early Stopping用
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0

        # 訓練ループ
        for epoch in range(epochs):
            # 訓練モード
            self.model.train()
            train_loss = 0.0

            for X_batch, y_batch in train_loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)

                # Forward pass
                outputs = self.model(X_batch)
                loss = criterion(outputs, y_batch)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            train_loss /= len(train_loader)

            # 検証モード
            self.model.eval()
            val_loss = 0.0

            with torch.no_grad():
                for X_batch, y_batch in val_loader:
                    X_batch = X_batch.to(self.device)
                    y_batch = y_batch.to(self.device)

                    outputs = self.model(X_batch)
                    loss = criterion(outputs, y_batch)

                    val_loss += loss.item()

            val_loss /= len(val_loader)

            # エポックごとの結果表示
            if (epoch + 1) % 10 == 0:
                print(f"   Epoch [{epoch + 1}/{epochs}] - Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")

            # Early Stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # 最良モデルを保存
                torch.save(self.model.state_dict(), 'best_gru_model.pth')
            else:
                patience_counter += 1

            if patience_counter >= patience:
                print(f"   Early stopping at epoch {epoch + 1}")
                break

        # 最良モデルをロード
        self.model.load_state_dict(torch.load('best_gru_model.pth', weights_only=True))
        print(f"\n✅ Training completed! Best val loss: {best_val_loss:.6f}")

    def evaluate(self, test_data):
        """
        テストデータで評価

        Args:
            test_data: (X_test, y_test)

        Returns:
            metrics: dict
        """
        print(f"\n📈 Evaluating model...")

        X_test, y_test = test_data

        self.model.eval()
        with torch.no_grad():
            X_test_tensor = torch.FloatTensor(X_test).to(self.device)
            predictions = self.model(X_test_tensor).cpu().numpy()

        # 逆正規化
        # predictionsとy_testを元のスケールに戻す
        predictions_denorm = self._denormalize_price(predictions)
        y_test_denorm = self._denormalize_price(y_test)

        # 評価指標
        mse = np.mean((predictions_denorm - y_test_denorm) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions_denorm - y_test_denorm))
        mape = np.mean(np.abs((predictions_denorm - y_test_denorm) / y_test_denorm)) * 100

        metrics = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }

        print(f"   RMSE: {rmse:.2f}")
        print(f"   MAE: {mae:.2f}")
        print(f"   MAPE: {mape:.2f}%")

        return metrics

    def forecast(self, df: pd.DataFrame, periods=7):
        """
        予測実行

        Args:
            df: 最新データ
            periods: 予測期間（デフォルト: 7日）

        Returns:
            dict: {
                'forecast': [予測値リスト],
                'current_price': 現在価格,
                'forecast_change': 変化率
            }
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        print(f"\n🔮 Forecasting next {periods} days...")

        # 最新のlookback日分のデータを取得
        recent_data = df[['open', 'high', 'low', 'close', 'volume']].tail(self.lookback).values

        # 正規化
        recent_data_normalized = self.scaler.transform(recent_data)

        # 予測
        forecasts = []
        current_input = recent_data_normalized.copy()

        self.model.eval()
        with torch.no_grad():
            for _ in range(periods):
                # 入力を準備
                X = torch.FloatTensor(current_input).unsqueeze(0).to(self.device)

                # 予測
                pred = self.model(X).cpu().numpy()[0, 0]
                forecasts.append(pred)

                # 次の入力を準備（予測値を使う）
                # 簡易版: closeだけ予測値に置き換え、他は最後の値を使う
                next_row = current_input[-1].copy()
                next_row[3] = pred  # close価格のインデックスは3

                # ウィンドウをスライド
                current_input = np.vstack([current_input[1:], next_row])

        # 逆正規化
        forecasts_denorm = self._denormalize_price(np.array(forecasts).reshape(-1, 1))

        current_price = df['close'].iloc[-1]
        final_forecast = forecasts_denorm[-1][0]
        forecast_change = ((final_forecast - current_price) / current_price) * 100

        print(f"   Current price: ${current_price:,.2f}")
        print(f"   Forecast ({periods}d): ${final_forecast:,.2f}")
        print(f"   Change: {forecast_change:+.2f}%")

        return {
            'forecast': forecasts_denorm.flatten().tolist(),
            'current_price': float(current_price),
            'forecast_price': float(final_forecast),
            'forecast_change': float(forecast_change)
        }

    def _denormalize_price(self, normalized_value):
        """
        正規化された価格を元のスケールに戻す

        Args:
            normalized_value: 正規化された値

        Returns:
            元のスケールの値
        """
        # closeの列だけを逆変換
        # scalerは5次元で学習しているので、ダミーを作る
        dummy = np.zeros((len(normalized_value), 5))
        dummy[:, 3] = normalized_value.flatten()  # closeのインデックス

        denormalized = self.scaler.inverse_transform(dummy)
        return denormalized[:, 3].reshape(-1, 1)


def main():
    """テスト実行"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    from src.data.timeseries_storage import TimeSeriesStorage

    storage = TimeSeriesStorage()
    engine = GRUForecastingEngine(lookback=60, forecast_horizon=7)

    # BTCの1日足データを読み込み
    df = storage.load_price_data('BTC', '1d')

    if df.empty or len(df) < 100:
        print("❌ BTCのデータが不足しています（最低100日分必要）")
        return

    print("=" * 80)
    print("GRU Forecasting Engine Test")
    print("=" * 80)

    # データ準備
    train_loader, val_loader, test_data = engine.prepare_data(df, train_ratio=0.8)

    # 訓練
    engine.train(train_loader, val_loader, epochs=100, learning_rate=0.001)

    # 評価
    metrics = engine.evaluate(test_data)

    # 予測
    forecast_result = engine.forecast(df, periods=7)

    print("\n" + "=" * 80)
    print("Forecast Results")
    print("=" * 80)
    for i, price in enumerate(forecast_result['forecast'], 1):
        print(f"  Day {i}: ${price:,.2f}")

    print("\n" + "=" * 80)
    print(f"✅ GRU実装完了！MAPE: {metrics['mape']:.2f}%（目標: <0.5%）")
    print("=" * 80)


if __name__ == '__main__':
    main()
