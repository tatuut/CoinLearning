# データマネジメント × Advanced Dashboard 統合計画

## 👥 登場人物
- **アキラ博士** 🧑‍🔬: システムアーキテクト、何でも知ってる
- **タカシ** 🤔: 初心者トレーダー、よく分かってない

---

## 📋 現状確認（対話形式）

### タカシの質問

**タカシ**: 「ねえ博士、今のシステムって1分足でデータ取得してるんだよね？」

**アキラ博士**: 「その通り！Data Managementページで`MinuteDataCollector`が1分足（1m）データをBinance APIから取得してる」

**タカシ**: 「じゃあ、そのデータをAdvanced Dashboardで4時間足とか日足に変換して表示できるの？」

**アキラ博士**: 「❌ それが**できない**んだ。今は誤解されやすいけど、実はこうなってる：」

### 現状の仕組み

```
📊 データの流れ

Data Management (新規):
  ├─ MinuteDataCollector → Binance API
  ├─ 1分足データ取得 (BTC_1m.parquet)
  └─ Parquet保存 ✅

Advanced Dashboard (既存):
  ├─ 既に保存されている 4h/1d データを表示
  ├─ BTC_4h.parquet, BTC_1d.parquet
  └─ MEXC APIから取得されたもの
```

**タカシ**: 「え、じゃあ別々のAPIから別々のデータ取ってるってこと？」

**アキラ博士**: 「そう！ここがポイント：」

| データソース | API | 時間足 | 用途 |
|------------|-----|--------|------|
| MinuteDataCollector | Binance | 1m | 短期分析用 |
| 既存データ | MEXC | 4h, 1d | 長期分析用 |

**タカシ**: 「じゃあ、1分足から4時間足に変換する機能は？」

**アキラ博士**: 「❌ 実装されてない。でも**実装できる**！pandasの`resample()`で簡単にできるよ」

### データ保存形式について

**タカシ**: 「データはちゃんと保存されてるの？Parquetってやつ？」

**アキラ博士**: 「✅ 完璧に保存されてるよ！」

```python
sample/data/timeseries/prices/
├── BTC_1m.parquet   # 1,520件（1日分）✅
├── BTC_4h.parquet   # 既存データ
├── BTC_1d.parquet   # 既存データ
├── ETH_1m.parquet   # 10,080件（7日分）✅
├── SOL_1m.parquet   # 10,080件（7日分）✅
└── ...
```

**Parquetの利点:**
- 圧縮効率が高い（CSV比で1/10以下）
- 読み込みが超高速
- カラム単位でアクセス可能
- pandas完全対応

### 差分取得について

**タカシ**: 「毎回全部取り直すの？それとも新しいデータだけ取る？」

**アキラ博士**: 「✅ 差分取得に対応してる！賢いでしょ？」

```python
# MinuteDataCollectorの仕組み

初回実行:
  → 最終タイムスタンプなし
  → 指定日数分を全取得（例: 7日分）
  → BTC_1m.parquet に保存

2回目以降:
  → 最終タイムスタンプ取得（例: 2025-10-29 12:50:00）
  → その時刻以降のみ取得（例: 79分間分）
  → 既存ファイルに追記（上書きではなく追加）
```

**実際のコード:**
```python
def collect_data(self, symbol: str, days: int = None):
    last_timestamp = self.get_latest_timestamp(symbol)

    if last_timestamp is None:
        # 初回: 全取得
        return self.collect_initial_data(symbol, days)
    else:
        # 2回目以降: 差分のみ
        return self.collect_incremental_data(symbol)
```

**タカシ**: 「なるほど！じゃあAPIの無駄遣いしないんだね」

**アキラ博士**: 「その通り！Binance APIは制限があるから、差分だけ取るのが効率的だよ」

---

## 🎯 統合内容（何を実装するか）

**タカシ**: 「じゃあ具体的に何を作るの？」

**アキラ博士**: 「今回は**シンプルな統合**だけ！難しくないよ：」

### プランA: シンプル統合（今回実装）

**タカシ**: 「1分足データを表示できるようにする」

**アキラ博士**: 「正解！具体的には：」

#### 1. 時間足選択に1m追加

**現状のコード:**
```python
# ui/pages/03_Advanced_Dashboard.py

# 保存されているファイルから自動検出
intervals = sorted(set([f['interval'] for f in files if f['symbol'] == selected_symbol]))

# ドロップダウンに表示
selected_interval = st.sidebar.selectbox("時間足", intervals)
```

**タカシ**: 「これって変更いらないってこと？」

**アキラ博士**: 「✅ その通り！既に自動検出してるから、1mファイルがあれば勝手に表示される！」

```
現在のドロップダウン:
  BTC: [4h, 1d]

実装後:
  BTC: [1m, 4h, 1d]  ← 1m追加！
  ETH: [1m, 4h, 1d]
  SOL: [1m]          ← 新規！
```

#### 2. デフォルト表示期間を調整

**タカシ**: 「1分足って1日で1,440件もあるの？重くならない？」

**アキラ博士**: 「良い質問！だからデフォルト表示件数を調整する：」

**問題**:
- 1日 = 1,440件（1分 × 60分 × 24時間）
- 7日 = 10,080件 ← 多すぎてブラウザが重い

**対策コード**:
```python
# 時間足に応じたデフォルト表示期間を設定
default_limits = {
    '1m': 500,   # 約8時間分（500分 ≈ 8.3時間）
    '5m': 300,   # 約25時間分
    '1h': 168,   # 1週間分
    '4h': 180,   # 30日分
    '1d': 100,   # 100日分
}

# 選択された時間足に応じてデフォルト値を設定
default_limit = default_limits.get(selected_interval, 100)

limit = st.sidebar.slider(
    "表示期間（直近N件）",
    10,
    2000,  # 最大値を拡大
    default_limit,
    help="チャートに表示するデータの件数を選択"
)
```

### 3. MEXC API更新機能の調整

**問題点**: Data Managementで取得した1mデータはBinance APIから取得しているが、Advanced DashboardはMEXC APIを想定

**対策**: 1分足選択時は「最新データ取得」ボタンを非表示にする

```python
# 更新ボタン（1分足以外のみ表示）
if selected_interval != '1m':
    if st.sidebar.button("🔄 最新データ取得", key="update_data"):
        with st.spinner(f"{selected_symbol}の最新データを取得中..."):
            success, message = fetch_latest_data(selected_symbol)
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)
else:
    st.sidebar.info("ℹ️ 1分足データの更新は「Data Management」ページで行ってください")
```

### 4. テクニカル指標の計算時間最適化

**問題点**: 1分足データでRSI/MACD計算に時間がかかる可能性

**対策**:
- データ件数が多い場合は計算済みキャッシュを使用
- 表示期間のみを計算対象にする（全データではなく）

```python
# 直近N件に制限してから指標計算
df = df.tail(limit)
df = calculate_indicators(df, storage)
```

（既に実装済み - 変更不要）

---

## 💡 ユーザーからの重要な指摘

**タカシ**: 「というか、最初から1分足で全データ取得すればよくない？で、表示時に好きな時間足に変換すればいいじゃん！」

**アキラ博士**: 「🎯 **完璧な指摘だ！** その通り！」

### 新しい方針（修正版）

```
旧方式（非効率）:
  ├─ MEXC API  → 4h データ取得
  ├─ MEXC API  → 1d データ取得
  └─ Binance API → 1m データ取得

新方式（効率的）:
  └─ Binance API → 1m データ取得
       ↓ resample変換
       ├─ 5m に変換
       ├─ 15m に変換
       ├─ 1h に変換
       ├─ 4h に変換
       └─ 1d に変換
```

**利点:**
- ✅ APIリクエストが1種類だけ
- ✅ データの一貫性（同じソース）
- ✅ 柔軟性（任意の時間足に変換可能）
- ✅ ストレージ効率（1mファイルのみ保存）

---

## 🔧 実装手順（修正版）

### Phase 1: 基本統合（5分）
1. ✅ デフォルト表示期間を時間足に応じて調整
2. ✅ スライダーの最大値を2000に拡大

### Phase 2: UI改善（3分）
1. ✅ 1分足選択時の説明テキスト追加
2. ✅ MEXC API更新ボタンの表示制御

### Phase 3: テスト（2分）
1. ✅ BTC 1mデータの表示確認
2. ✅ ETH 1mデータの表示確認
3. ✅ SOL 1mデータの表示確認
4. ✅ ローソク足チャート確認
5. ✅ RSI/MACD計算確認

---

## ⚠️ 制約事項

### データ取得について
- **1分足データの取得**: Data Managementページで実行
- **4h/1dデータの取得**: Advanced Dashboardページで実行
- 理由: 異なるAPI（Binance vs MEXC）を使用しているため

### 表示パフォーマンス
- 1分足で2000件表示時、ブラウザ描画に1-2秒かかる可能性あり
- 推奨: 500-1000件程度に制限

### 予測機能
- ARIMA/GARCH予測は1d（日足）データ推奨
- 1分足での予測は計算時間が長く、精度も低い
- **対策**: 1分足選択時は予測機能を非表示にする

---

## 📊 期待される結果

### Before（現状）
```
Advanced Dashboard:
├── BTC (4h, 1d)
├── ETH (4h, 1d)
├── DOGE (4h, 1d)
└── SHIB (4h, 1d)
```

### After（統合後）
```
Advanced Dashboard:
├── BTC (1m, 4h, 1d)  ← 1m追加！
├── ETH (1m, 4h, 1d)  ← 1m追加！
├── SOL (1m)          ← 新規追加！
├── DOGE (4h, 1d)
└── SHIB (4h, 1d)
```

---

## 🚀 実装コード変更箇所

### 変更ファイル
- `ui/pages/03_Advanced_Dashboard.py` のみ（約20行の変更）

### 変更箇所まとめ
1. **デフォルト表示期間の調整** (835-845行目付近)
2. **スライダー最大値の変更** (843行目)
3. **MEXC API更新ボタンの表示制御** (848-856行目)
4. **1分足向け説明の追加** (857-858行目)
5. **予測機能の表示制御** (922-923行目)

---

## ✅ 承認後の作業

1. [ ] 上記5箇所のコード修正
2. [ ] 動作テスト（BTC/ETH/SOL 1mデータ表示）
3. [ ] gitコミット
4. [ ] ユーザーに結果報告

---

## 💬 確認事項

**この計画で問題ありませんか？**

もし以下の点について変更希望があればお知らせください：
- デフォルト表示期間（現在: 1m=500件、約8時間分）
- 1分足での予測機能の扱い（現在: 非表示）
- その他の要望

承認いただければ、すぐに実装を開始します！
