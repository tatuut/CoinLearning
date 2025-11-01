# 02. RSI - 買われすぎ・売られすぎを数値化

## 実践ガイド

**Week 2で詳しく学びます**

RSIを使った取引の実践方法：
- RSI < 30: 売られすぎ → 買いのチャンス
- RSI > 70: 買われすぎ → 買わない
- 具体的な使い方は、以下の技術解説を読んでから Week 2で実践します

---

## 技術解説 - RSIの発明

# 📖 Story Chapter 2: RSIの発明 - 「過熱」を数値化した男

## Scene 1: 1978年、ニューオーリンズ

**ミコ**: 「ユウタ、1978年にタイムスリップするぞ」

**ユウタ**: 「は？」

**ミコ**: 「RSI（Relative Strength Index）を発明した男、J・ウェルズ・ワイルダー・ジュニアの話だ」

---

### 【回想シーン: ワイルダーの悩み】

**場所**: ルイジアナ州ニューオーリンズ、自宅の書斎

**ワイルダー** (45歳、機械エンジニア出身のトレーダー):
「くそっ...また負けた」

*チャートを睨みつける。商品先物（大豆）のチャートだ。*

**ワイルダー**: 「価格が急騰してるから買った。そしたら翌日暴落...」

**ワイルダー**: 「なぜだ？なぜ俺が買った瞬間に下がる？」

*机の上には数ヶ月分のトレード記録。ほとんどが赤字。*

**ワイルダー**: 「...待てよ」

**ワイルダー**: 「急騰してる時に買ったから負けたんじゃないか？」

**ワイルダー**: 「つまり、『買われすぎ』の時に買ってしまった？」

---

## Scene 2: エンジニアの着想

**ワイルダー**: 「機械工学で考えろ...」

**ワイルダー**: 「エンジンの回転数が『正常範囲』を超えたら、オーバーヒートする」

**ワイルダー**: 「株価も同じじゃないのか？」

```markdown
【ワイルダーのノート】

仮説:
価格には「正常範囲」がある
→ 範囲を超えて上昇 = 過熱（買われすぎ）
→ 範囲を超えて下落 = 冷却（売られすぎ）

問題:
「正常範囲」をどう定義する？

エンジン: 回転数（RPM）で測定可能
株価: ？？？
```

**ワイルダー**: 「価格そのものじゃダメだ...」

**ワイルダー**: 「$10から$20に上がるのと、$100から$110に上がるのは、意味が違う」

**ワイルダー**: 「必要なのは...**相対的な強さ**だ」

---

## Scene 3: 数式の誕生

**ワイルダー**: （ペンを走らせる）

```markdown
【思考プロセス】

Step 1: 上昇と下落を分離
- 上昇幅 = 今日の終値 - 昨日の終値（正の時のみ）
- 下落幅 = 昨日の終値 - 今日の終値（負の時のみ）

Step 2: 平均を取る
- 平均上昇幅 = 過去14日間の上昇幅の平均
- 平均下落幅 = 過去14日間の下落幅の平均

Step 3: 比率を計算
- RS (Relative Strength) = 平均上昇幅 / 平均下落幅

問題: RSは0～∞の範囲。見づらい...

Step 4: 0-100に正規化
- RSI = 100 - (100 / (1 + RS))

→ これだ！
```

**ワイルダー**: 「できた...」

**ワイルダー**: （震える手で過去のチャートにRSIを計算）

**ワイルダー**: 「...70を超えてる時に買って、全部負けてる」

**ワイルダー**: 「30を下回ってる時に買ってたら...全部勝ってる！」

**ワイルダー**: 「これだ！**これが答えだ！**」

---

## Scene 4: 1978年6月、伝説の出版

**ナレーション**:
1978年6月、ワイルダーは自費出版で『New Concepts in Technical Trading Systems』を発表。

その中で、RSIは世界で初めて紹介された。

**本の中の一節**:
> "RSIは0から100の範囲で動く。70を超えたら買われすぎ、30を下回ったら売られすぎを示す。"

**ナレーション**:
この本は、テクニカル分析の歴史を変えた。

RSIは瞬く間に世界中のトレーダーに広まり、今日でも最も使われる指標の一つとなっている。

---

## Scene 5: 現代、ユウタとミコ

**ユウタ**: 「...すげえ」

**ミコ**: 「ワイルダーは、何度も負けて、悩んで、この数式にたどり着いた」

**ユウタ**: 「機械工学の知識を使ったのか」

**ミコ**: 「そう。『正常範囲』という概念を、株価に応用した」

**ミコ**: 「じゃあ、実際にやってみるぞ」

---

## Scene 6: RSIの実装

**ミコ**: 「Pythonで書くとこうなる」

```python
def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    RSI（Relative Strength Index）を計算

    Args:
        prices: 終値のSeries
        period: 期間（デフォルト14日）

    Returns:
        RSIのSeries（0-100）
    """
    # Step 1: 日次変動を計算
    delta = prices.diff()

    # Step 2: 上昇と下落に分離
    gain = delta.where(delta > 0, 0)  # 上昇分のみ
    loss = -delta.where(delta < 0, 0)  # 下落分のみ（正の値に）

    # Step 3: 平均を計算（ワイルダーの移動平均）
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Step 4: RS（Relative Strength）を計算
    rs = avg_gain / avg_loss

    # Step 5: RSI（0-100に正規化）
    rsi = 100 - (100 / (1 + rs))

    return rsi
```

**ユウタ**: 「これだけ？」

**ミコ**: 「これだけだ。シンプルだろ？」

---

## Scene 7: SHIBでの検証

**ミコ**: 「じゃあ、Week 1で負けたSHIBで確認してみよう」

```python
# SHIBの価格データ取得
shib_df = timeseries_manager.get_data('SHIB')

# RSI計算
shib_df['rsi'] = calculate_rsi(shib_df['close'])

# ユウタが買った日
buy_date = '2025-10-18 15:30'

print(f"購入日のRSI: {shib_df.loc[buy_date, 'rsi']:.1f}")
```

**出力**:
```
購入日のRSI: 68.3
```

**ユウタ**: 「68.3...」

**ミコ**: 「70に近い。『買われすぎ』の領域だ」

**ユウタ**: 「だから、買った後に下がったのか...」

**ミコ**: 「次に、DOGEを見てみよう」

```python
# DOGEの価格データ取得
doge_df = timeseries_manager.get_data('DOGE')
doge_df['rsi'] = calculate_rsi(doge_df['close'])

buy_date = '2025-10-18 20:00'
print(f"購入日のRSI: {doge_df.loc[buy_date, 'rsi']:.1f}")
```

**出力**:
```
購入日のRSI: 42.8
```

**ユウタ**: 「42.8...」

**ミコ**: 「『中立』の領域。買われすぎでも、売られすぎでもない」

**ユウタ**: 「だから、勝てたのか！」

---

## Scene 8: RSIの3つの使い方

**ミコ**: 「RSIには、3つの基本的な使い方がある」

```markdown
【RSIの3つの使い方】

## 1. 買われすぎ/売られすぎ判定
- RSI > 70: 買われすぎ → 売りシグナル（または買わない）
- RSI < 30: 売られすぎ → 買いシグナル

## 2. ダイバージェンス（逆行現象）
価格: 高値更新
RSI: 高値更新せず → 弱気ダイバージェンス（下落の予兆）

価格: 安値更新
RSI: 安値更新せず → 強気ダイバージェンス（上昇の予兆）

## 3. トレンド確認
強い上昇トレンド: RSIが40-80の範囲で推移
強い下降トレンド: RSIが20-60の範囲で推移
```

**ユウタ**: 「70/30だけじゃないのか」

**ミコ**: 「そう。でも、最初は70/30だけで十分」

---

## Scene 9: RSIの弱点

**ミコ**: 「ただし、RSIには弱点がある」

**ユウタ**: 「なに？」

**ミコ**: 「**強いトレンド相場では役に立たない**」

```markdown
【RSIの弱点】

## 問題1: トレンド相場での誤シグナル
強い上昇トレンド:
- RSI > 70が長期間続く
- 「買われすぎ」だが、まだ上がる
- 売ると機会損失

強い下降トレンド:
- RSI < 30が長期間続く
- 「売られすぎ」だが、まだ下がる
- 買うと損失

## 問題2: レンジ相場専用
RSIは「往復する相場」で最も有効
一方向に動く相場では機能しない

## 問題3: 期間の選択
14日: ワイルダーの標準
7日: 短期トレード向け（敏感）
21日: 長期トレード向け（鈍感）

→ どれが正解？
```

**ユウタ**: 「じゃあ、どう使えばいいの？」

**ミコ**: 「**他の指標と組み合わせる**」

---

## Scene 10: ユウタ式での使い方

**ミコ**: 「俺たちの戦略『ユウタ式スイングトレード』では、こう使う」

```markdown
【ユウタ式でのRSI活用法】

## エントリー判断
✅ RSI < 30: 売られすぎ → 反発狙いで買い検討
✅ RSI 30-50: 中立 → トレンド確認後、買い検討
❌ RSI > 70: 買われすぎ → 買わない（待つ）

## イグジット判断
✅ RSI > 70: 過熱 → 利確検討
✅ RSI < 30（買い後）: 弱すぎ → 損切り検討

## 使わない場面
- ニュースで大きく動いた直後（ファンダ優先）
- 強いトレンドが明確な時（トレンドフォロー優先）

## 組み合わせ
RSI単体では判断しない
→ 必ず「ニュース」「トレンド」「出来高」も確認
```

**ユウタ**: 「あくまで『補助』なんだな」

**ミコ**: 「そう。RSIは**フィルター**だ」

**ミコ**: 「『明らかに買われすぎ』を避けるためのツール」

---

## Scene 11: 実装コード

**ミコ**: 「じゃあ、実際のコードに組み込もう」

```python
# tools/technical_indicators.py

import pandas as pd
import numpy as np


class TechnicalIndicators:
    """テクニカル指標計算クラス"""

    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        RSI（Relative Strength Index）

        発明者: J. Welles Wilder Jr. (1978)
        用途: 買われすぎ/売られすぎ判定

        Args:
            prices: 終値のSeries
            period: 期間（デフォルト14）

        Returns:
            RSI (0-100)
        """
        delta = prices.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def interpret_rsi(rsi_value: float) -> dict:
        """
        RSI値を解釈

        Args:
            rsi_value: RSI値（0-100）

        Returns:
            {
                'status': 'oversold' | 'neutral' | 'overbought',
                'signal': 'buy' | 'hold' | 'sell',
                'strength': 0.0-1.0,
                'description': '説明文'
            }
        """
        if rsi_value < 30:
            return {
                'status': 'oversold',
                'signal': 'buy',
                'strength': (30 - rsi_value) / 30,  # 0に近いほど強い
                'description': f'売られすぎ（RSI={rsi_value:.1f}）。反発の可能性あり。'
            }
        elif rsi_value > 70:
            return {
                'status': 'overbought',
                'signal': 'sell',
                'strength': (rsi_value - 70) / 30,  # 100に近いほど強い
                'description': f'買われすぎ（RSI={rsi_value:.1f}）。調整の可能性あり。'
            }
        else:
            return {
                'status': 'neutral',
                'signal': 'hold',
                'strength': 1 - abs(rsi_value - 50) / 20,  # 50に近いほど中立
                'description': f'中立（RSI={rsi_value:.1f}）。トレンド確認が必要。'
            }

    @staticmethod
    def detect_divergence(prices: pd.Series, rsi: pd.Series, window: int = 20) -> dict:
        """
        ダイバージェンス検出

        Args:
            prices: 価格Series
            rsi: RSI Series
            window: 検出期間

        Returns:
            {
                'type': 'bullish' | 'bearish' | 'none',
                'strength': 0.0-1.0,
                'description': '説明文'
            }
        """
        # 直近の高値・安値を検出
        recent_prices = prices.tail(window)
        recent_rsi = rsi.tail(window)

        price_high = recent_prices.max()
        price_low = recent_prices.min()
        rsi_high = recent_rsi.max()
        rsi_low = recent_rsi.min()

        # 最新値
        current_price = recent_prices.iloc[-1]
        current_rsi = recent_rsi.iloc[-1]

        # 強気ダイバージェンス（価格下落、RSI上昇）
        if current_price <= price_low * 1.05 and current_rsi > rsi_low * 1.1:
            return {
                'type': 'bullish',
                'strength': (current_rsi - rsi_low) / rsi_low,
                'description': '強気ダイバージェンス検出。価格は安値付近だがRSIは上昇。反転の可能性。'
            }

        # 弱気ダイバージェンス（価格上昇、RSI下落）
        if current_price >= price_high * 0.95 and current_rsi < rsi_high * 0.9:
            return {
                'type': 'bearish',
                'strength': (rsi_high - current_rsi) / rsi_high,
                'description': '弱気ダイバージェンス検出。価格は高値付近だがRSIは下落。調整の可能性。'
            }

        return {
            'type': 'none',
            'strength': 0.0,
            'description': 'ダイバージェンスなし。'
        }
```

**ユウタ**: 「これで、RSIが使えるようになった！」

**ミコ**: 「まだ一つだけだ。次はもっと強力な武器を手に入れる」

---

## Scene 12: エピローグ

**ユウタ**: 「ワイルダーって天才だな」

**ミコ**: 「天才じゃない。**何度も負けて、考え抜いた人**だ」

**ユウタ**: 「俺たちと同じか」

**ミコ**: 「そう。俺たちも、同じように武器を手に入れていく」

**ミコ**: 「次は...『トレンドの方向』を教えてくれる武器だ」

---

## 📝 Chapter 2 まとめ

### RSI（Relative Strength Index）

```markdown
【発明】
- 発明者: J. Welles Wilder Jr.
- 発表: 1978年6月
- 動機: 「買われすぎ/売られすぎ」を数値化したい

【計算式】
RSI = 100 - (100 / (1 + RS))
RS = 平均上昇幅 / 平均下落幅（14日間）

【解釈】
- RSI > 70: 買われすぎ
- RSI < 30: 売られすぎ
- RSI 30-70: 中立

【使い方（ユウタ式）】
- エントリー: RSI < 30で反発狙い
- イグジット: RSI > 70で利確検討
- フィルター: RSI > 70では買わない

【弱点】
- 強いトレンド相場では誤シグナル
- 単体では不十分（他指標と組み合わせ）
```

### 実装完了

✅ `tools/technical_indicators.py`
- `rsi()`: RSI計算
- `interpret_rsi()`: RSI解釈
- `detect_divergence()`: ダイバージェンス検出

---

---

## 🛠️ 実践で使う

RSIを実際の取引で活用する方法：
- **Week 2: テクニカル分析の実践**（作成予定） - RSIを使った銘柄選定と売買タイミング判断
  - RSI < 30 で反発狙い
  - RSI > 70 では買わない（フィルター）
  - ダイバージェンス検出

現状の参考：
- **[Week 1](../week1_basics.md#関連する技術ストーリーchapter形式)** - Week 1でRSIの重要性を体験

---

**Next Chapter**: [Chapter 3: MACDの誕生 - トレンドを「見える化」した男](./03_macd_invention.md)

---

## 📖 次へ

次のファイル: **[03. MACD - トレンドを見える化](./03_macd.md)**

