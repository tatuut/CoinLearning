"""
技術指標プラグインシステム

このディレクトリに新しい指標ファイルを追加すると、
自動的に分析システムに統合されます。

各指標ファイルは以下の形式で定義：

```python
def calculate(df, **params):
    \"\"\"
    指標を計算する関数

    Args:
        df: pandas DataFrame（OHLCV データ）
        **params: 指標固有のパラメータ

    Returns:
        計算結果（Series または DataFrame）
    \"\"\"
    # 計算ロジック
    return result

# メタデータ
INDICATOR_NAME = "指標名"
INDICATOR_DESCRIPTION = "指標の説明"
DEFAULT_PARAMS = {"param1": value1, "param2": value2}
```
"""

import os
import importlib
import inspect


def load_all_indicators():
    """
    このディレクトリ内の全指標を自動的にロード

    Returns:
        dict: {指標ID: 指標情報}
    """
    indicators = {}

    # このディレクトリのパス
    current_dir = os.path.dirname(__file__)

    # 全Pythonファイルをスキャン
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # .py を削除

            try:
                # モジュールをインポート
                module = importlib.import_module(f'analysis.indicators.{module_name}')

                # calculate関数が存在するか確認
                if hasattr(module, 'calculate'):
                    indicators[module_name] = {
                        'name': getattr(module, 'INDICATOR_NAME', module_name),
                        'description': getattr(module, 'INDICATOR_DESCRIPTION', ''),
                        'default_params': getattr(module, 'DEFAULT_PARAMS', {}),
                        'calculate': module.calculate,
                        'module': module
                    }
            except Exception as e:
                print(f"⚠️ 指標 {module_name} のロード失敗: {e}")

    return indicators


def get_indicator_list():
    """
    利用可能な指標の一覧を取得

    Returns:
        list: [(指標ID, 指標名, 説明)]
    """
    indicators = load_all_indicators()
    return [(id, info['name'], info['description'])
            for id, info in indicators.items()]


def calculate_indicator(indicator_id: str, df, **params):
    """
    指定された指標を計算

    Args:
        indicator_id: 指標ID（ファイル名）
        df: pandas DataFrame
        **params: 指標のパラメータ

    Returns:
        計算結果
    """
    indicators = load_all_indicators()

    if indicator_id not in indicators:
        raise ValueError(f"指標 '{indicator_id}' が見つかりません")

    indicator = indicators[indicator_id]

    # デフォルトパラメータとマージ
    final_params = indicator['default_params'].copy()
    final_params.update(params)

    # 計算実行
    return indicator['calculate'](df, **final_params)
