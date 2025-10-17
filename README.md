# 草コイントレーダー - 100円→1000円への道

AIと一緒に学ぶ草コイン取引システム

## このシステムでできること

1. 市場分析（自動）- 3つの戦略で買いシグナル検出
2. 取引記録 - 全取引をデータベースに保存
3. 学習カリキュラム - Week 1-4のストーリー形式
4. AIと対話できる分析レポート（NEW!）

## クイックスタート

```bash
pip install requests numpy
python main.py
```

## AIと対話する分析レポートの使い方

### ステップ1: レポート生成
```bash
python analysis/report_generator.py --symbol BTCUSDT
```

### ステップ2: あなたの分析を追記
生成されたMarkdownファイルに考えを書く

### ステップ3: Claude Codeに見せる
「analysis/reports/xxx.md を読んで、私の分析にフィードバックをください」

### ステップ4: ClaudeがWebSearchで調査してフィードバック追記

## 戦略

1. モメンタム戦略 - 上昇トレンドを捉える
2. 出来高急増戦略 - 急激な出来高増加を検出
3. ブレイクアウト戦略 - ボリンジャーバンド突破を検出

Generated with Claude Code
