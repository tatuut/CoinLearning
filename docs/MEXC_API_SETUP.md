# 🔐 MEXC API Key設定ガイド

**最終更新**: 2025-11-01

このガイドでは、MEXC APIを使用してスマホ2FAなしでリアルタイム取引・資産管理を行う方法を説明します。

---

## 🎯 なぜAPI Keyが必要？

### 問題点

❌ **毎回のスマホ2FA認証**
- ログインのたびにスマホで確認
- 時間がかかる（30秒~1分）
- リアルタイム性を損なう

### 解決策

✅ **API Key使用**
- 2FA不要
- プログラムから直接アクセス
- リアルタイム取引可能
- 自動化可能

**プロトレーダーはみんなAPI Keyを使っています**

---

## 📋 API Key作成手順

### ステップ1: MEXCにログイン

1. [MEXC公式サイト](https://www.mexc.com/)にアクセス
2. アカウントにログイン（最後の2FA認証）

### ステップ2: API管理ページへ移動

1. 右上のアカウントアイコンをクリック
2. **「API管理」** を選択

または、直接URL:
```
https://www.mexc.com/ja-JP/usercenter/api-manage
```

### ステップ3: API Key作成

1. **「APIキーを作成」** ボタンをクリック

2. **セキュリティ認証**（これが最後の2FA）
   - Google Authenticatorコード入力
   - メール認証コード入力

3. **API設定**

   #### 推奨設定（セキュリティ重視）

   | 設定項目 | 推奨値 | 説明 |
   |---------|--------|------|
   | **API名** | `grass-coin-trader` | 識別用の名前 |
   | **取引権限** | ✅ 有効 | 売買に必要 |
   | **読み取り専用** | ❌ 無効 | 取引もする場合 |
   | **出金権限** | ❌ **絶対に無効** | セキュリティのため |
   | **IPアドレス制限** | ✅ 有効 | 自宅IPのみ許可 |

4. **API KeyとSecretをコピー**

   ⚠️ **重要**: Secret Keyは二度と表示されません！
   - API Key: `mx0vgl...`（公開可）
   - Secret Key: `xxxxxxxx`（絶対に秘密）

   **すぐに安全な場所に保存してください**

---

## 🔒 セキュリティ設定

### 1. IPアドレス制限（推奨）

**自宅IPアドレスの確認方法**:

```bash
# Windowsの場合
curl ifconfig.me

# または
https://www.whatismyip.com/
```

**MEXC設定**:
1. API管理画面で「IPアドレス制限を編集」
2. 自宅IPアドレスを追加
3. 保存

**メリット**:
- 他の場所からのアクセスを防ぐ
- APIが漏洩しても安全

### 2. 権限の最小化

**最小限の権限のみ付与**:

| 用途 | 必要な権限 |
|------|-----------|
| ポートフォリオ確認のみ | 読み取り専用 |
| 手動売買 | 取引権限 |
| 自動売買ボット | 取引権限 |
| **出金** | ❌ **絶対に不要** |

### 3. 環境変数に保存（推奨）

**Windowsの場合**:

```powershell
# PowerShellで実行
[System.Environment]::SetEnvironmentVariable('MEXC_API_KEY', 'mx0vgl...', 'User')
[System.Environment]::SetEnvironmentVariable('MEXC_API_SECRET', 'xxxxxxxx', 'User')
```

**確認**:
```powershell
echo $env:MEXC_API_KEY
```

**または `.env` ファイル使用**:

```bash
# .env ファイル作成
MEXC_API_KEY=mx0vgl...
MEXC_API_SECRET=xxxxxxxx
```

⚠️ **注意**: `.env`を`.gitignore`に追加！

```bash
# .gitignore
.env
```

---

## 💻 API使用方法

### Python（ccxt使用）

#### インストール

```bash
pip install ccxt python-dotenv
```

#### サンプルコード

```python
import ccxt
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# MEXC接続
exchange = ccxt.mexc({
    'apiKey': os.getenv('MEXC_API_KEY'),
    'secret': os.getenv('MEXC_API_SECRET'),
})

# 保有資産取得（2FAなし！）
balance = exchange.fetch_balance()
print(balance)

# 取引履歴取得
trades = exchange.fetch_my_trades('BTC/USDT', limit=10)
print(trades)

# 注文（慎重に！）
# order = exchange.create_market_buy_order('BTC/USDT', 0.001)
```

---

## 🧪 テスト方法

### 1. API接続テスト

```python
# test_mexc_api.py
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

try:
    exchange = ccxt.mexc({
        'apiKey': os.getenv('MEXC_API_KEY'),
        'secret': os.getenv('MEXC_API_SECRET'),
    })

    # 接続テスト
    balance = exchange.fetch_balance()
    print("✅ API接続成功！")
    print(f"総資産: {balance['total']}")

except Exception as e:
    print(f"❌ エラー: {e}")
```

実行:
```bash
python test_mexc_api.py
```

### 2. ポートフォリオ確認テスト

```python
# 保有銘柄と数量を表示
for currency, amount in balance['total'].items():
    if amount > 0:
        print(f"{currency}: {amount}")
```

---

## ⚠️ トラブルシューティング

### エラー1: `Invalid API Key`

**原因**:
- API Keyが間違っている
- 環境変数が正しく設定されていない

**対処法**:
```python
# 直接確認
print(os.getenv('MEXC_API_KEY'))
```

### エラー2: `IP not whitelisted`

**原因**:
- IPアドレス制限が有効で、現在のIPが許可されていない

**対処法**:
1. 現在のIPを確認: `curl ifconfig.me`
2. MEXC API管理画面でIPを追加

### エラー3: `Insufficient permissions`

**原因**:
- API Keyに必要な権限がない

**対処法**:
- API管理画面で権限を確認・追加

---

## 📊 ポートフォリオトラッキング実装

### 自動監視スクリプト

```python
# src/portfolio/tracker.py
import ccxt
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

class PortfolioTracker:
    def __init__(self):
        self.exchange = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY'),
            'secret': os.getenv('MEXC_API_SECRET'),
        })

    def fetch_holdings(self):
        """保有資産を取得"""
        balance = self.exchange.fetch_balance()
        holdings = []

        for currency, amount in balance['total'].items():
            if amount > 0:
                # USDTに対する価格取得
                try:
                    ticker = self.exchange.fetch_ticker(f'{currency}/USDT')
                    price = ticker['last']
                    value = amount * price
                except:
                    price = 1 if currency == 'USDT' else 0
                    value = amount

                holdings.append({
                    'currency': currency,
                    'amount': amount,
                    'price_usdt': price,
                    'value_usdt': value,
                })

        return holdings

    def save_snapshot(self):
        """スナップショット保存"""
        timestamp = datetime.now()
        holdings = self.fetch_holdings()

        df = pd.DataFrame(holdings)
        df['timestamp'] = timestamp

        # 保存
        filename = f"data/portfolio/snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.parquet"
        df.to_parquet(filename)

        print(f"✅ 保存: {filename}")

    def start_monitoring(self, interval_seconds=60):
        """定期監視開始"""
        print(f"⏱️  監視開始（{interval_seconds}秒ごと）")
        while True:
            try:
                self.save_snapshot()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\n⏹️  監視停止")
                break
            except Exception as e:
                print(f"❌ エラー: {e}")
                time.sleep(interval_seconds)

if __name__ == '__main__':
    tracker = PortfolioTracker()
    tracker.start_monitoring(interval_seconds=60)  # 1分ごと
```

### 実行方法

```bash
# バックグラウンドで実行
python src/portfolio/tracker.py &
```

---

## 🎯 次のステップ

1. ✅ API Key作成完了
2. ✅ テストスクリプト実行成功
3. [ ] ポートフォリオトラッキング開始
4. [ ] Streamlit UIにポートフォリオ表示追加
5. [ ] Claude解説生成機能実装

---

## 📚 参考リンク

- [MEXC API公式ドキュメント](https://mexcdevelop.github.io/apidocs/spot_v3_en/)
- [ccxt公式ドキュメント](https://docs.ccxt.com/)
- [MEXC API GitHub](https://github.com/mxcdevelop)

---

**最終更新**: 2025-11-01
**作成者**: Claude Code（with tatut）
