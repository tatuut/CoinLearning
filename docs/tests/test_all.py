"""
システム全体の動作テスト

各モジュールが正常に動作するか確認
"""

import sys
import os
import io

# UTF-8出力設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """必要なモジュールがインポートできるか確認"""
    print("=" * 80)
    print("📦 モジュールインポートテスト")
    print("=" * 80)
    print()

    modules = [
        ('config.exchange_api', 'MEXCAPI'),
        ('data.advanced_database', 'AdvancedDatabase'),
        ('data.timeseries_storage', 'TimeSeriesStorage'),
        ('analysis.correlation_analyzer', 'CorrelationAnalyzer'),
        ('analysis.indicators', 'load_all_indicators'),
    ]

    failed = []

    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"✗ {module_name}.{class_name}: {e}")
            failed.append((module_name, class_name, e))

    print()

    if failed:
        print(f"⚠️ {len(failed)}個のモジュールでエラー")
        return False
    else:
        print(f"✅ 全{len(modules)}個のモジュールが正常")
        return True


def test_database_connection():
    """データベース接続テスト"""
    print("=" * 80)
    print("🗄️ データベース接続テスト")
    print("=" * 80)
    print()

    try:
        from data.advanced_database import AdvancedDatabase

        db = AdvancedDatabase()

        # テーブル存在確認
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"✓ データベース接続成功")
        print(f"✓ テーブル数: {len(tables)}")
        print(f"  主要テーブル:")
        for table in ['price_history_detailed', 'news', 'market_stats_detailed']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"    - {table}: {count}行")

        db.close()
        print()
        return True

    except Exception as e:
        print(f"✗ データベースエラー: {e}")
        print()
        return False


def test_parquet_storage():
    """Parquetストレージテスト"""
    print("=" * 80)
    print("📊 Parquetストレージテスト")
    print("=" * 80)
    print()

    try:
        from data.timeseries_storage import TimeSeriesStorage
        import os

        storage = TimeSeriesStorage()

        # 保存ディレクトリ確認
        prices_dir = os.path.join(storage.data_dir, 'prices')

        if not os.path.exists(prices_dir):
            print(f"⚠️ ディレクトリが存在しません: {prices_dir}")
            print()
            return False

        # ファイル数カウント
        files = [f for f in os.listdir(prices_dir) if f.endswith('.parquet')]

        print(f"✓ Parquetディレクトリ: {prices_dir}")
        print(f"✓ ファイル数: {len(files)}")

        if files:
            print(f"  ファイル一覧:")
            for f in sorted(files)[:10]:  # 最初の10個
                filepath = os.path.join(prices_dir, f)
                size = os.path.getsize(filepath)
                print(f"    - {f} ({size/1024:.1f} KB)")

            # 1つ読み込んでみる
            test_file = files[0]
            symbol, interval = test_file.replace('.parquet', '').split('_')
            df = storage.load_price_data(symbol, interval)

            if df is not None:
                print(f"\n  読み込みテスト: {test_file}")
                print(f"    - 行数: {len(df)}")
                print(f"    - 列: {', '.join(df.columns)}")
                print(f"    - 期間: {df.index[0]} ～ {df.index[-1]}")

        print()
        return True

    except Exception as e:
        print(f"✗ Parquetストレージエラー: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_indicators_plugin():
    """指標プラグインシステムテスト"""
    print("=" * 80)
    print("🔌 指標プラグインシステムテスト")
    print("=" * 80)
    print()

    try:
        from analysis.indicators import load_all_indicators, get_indicator_list

        # 指標をロード
        indicators = load_all_indicators()

        print(f"✓ ロードされた指標数: {len(indicators)}")
        print()

        if indicators:
            print("利用可能な指標:")
            for indicator_id, info in indicators.items():
                print(f"  - {info['name']} ({indicator_id})")
                print(f"    {info['description']}")
                print(f"    パラメータ: {info['default_params']}")
                print()

            # 実際に計算してみる
            from data.timeseries_storage import TimeSeriesStorage
            storage = TimeSeriesStorage()

            # BTCデータで計算テスト
            df = storage.load_price_data('BTC', '1d')

            if df is not None and not df.empty:
                print("計算テスト（BTC 1d）:")
                for indicator_id, info in indicators.items():
                    try:
                        result = info['calculate'](df, **info['default_params'])
                        print(f"  ✓ {info['name']}: 計算成功")
                    except Exception as e:
                        print(f"  ✗ {info['name']}: {e}")
                print()

        print()
        return True

    except Exception as e:
        print(f"✗ プラグインシステムエラー: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_api_connection():
    """API接続テスト"""
    print("=" * 80)
    print("🌐 MEXC API接続テスト")
    print("=" * 80)
    print()

    try:
        from config.exchange_api import MEXCAPI

        api = MEXCAPI()

        # 価格取得テスト
        price = api.get_price("BTCUSDT")
        print(f"✓ BTC価格取得: ${price:,.2f}")

        # 24h統計テスト
        stats = api.get_24h_stats("BTCUSDT")
        print(f"✓ 24h統計取得: 変動率 {stats.get('price_change_percent', 0):+.2f}%")

        print()
        return True

    except Exception as e:
        print(f"✗ API接続エラー: {e}")
        print()
        return False


def main():
    """全テスト実行"""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "システム統合テスト" + " " * 35 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    tests = [
        ("モジュールインポート", test_imports),
        ("データベース接続", test_database_connection),
        ("Parquetストレージ", test_parquet_storage),
        ("指標プラグイン", test_indicators_plugin),
        ("API接続", test_api_connection),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ テスト '{name}' でエラー: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 結果サマリー
    print()
    print("=" * 80)
    print("📊 テスト結果サマリー")
    print("=" * 80)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 合格" if result else "❌ 不合格"
        print(f"{status}: {name}")

    print()
    print(f"合計: {passed}/{total} テスト合格")

    if passed == total:
        print()
        print("🎉 全テスト合格！システムは正常に動作しています。")
    else:
        print()
        print("⚠️ 一部のテストが失敗しました。上記のエラーを確認してください。")

    print()


if __name__ == '__main__':
    main()
