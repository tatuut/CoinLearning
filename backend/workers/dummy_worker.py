"""Phase 2: ダミーワーカー（Claude Code実行をシミュレート - Redis不要版）"""
import time
from backend.api.job_manager import job_manager

def dummy_job(symbol: str, job_id: str = None):
    """Claude Code実行をシミュレート（3ステップ、計5秒）"""

    def log(msg):
        """ログ出力＋SQLite蓄積"""
        print(f"[DUMMY] {msg}")

        # SQLiteに追記
        if job_id:
            job_manager.add_log(job_id, msg)

    try:
        # ステータスを「started」に更新
        if job_id:
            job_manager.update_status(job_id, "started")

        log(f"🚀 Job started for {symbol}")

        # Step 1: WebSearch シミュレート
        log("⏳ Step 1/3: Simulating WebSearch...")
        time.sleep(2)
        log("✅ Step 1 done: Found 5 articles")

        # Step 2: Analysis シミュレート
        log("⏳ Step 2/3: Simulating analysis...")
        time.sleep(2)
        log("✅ Step 2 done: Average sentiment +0.45")

        # Step 3: DB Save シミュレート
        log("⏳ Step 3/3: Simulating DB save...")
        time.sleep(1)
        log("✅ Step 3 done: Saved to database")

        log("🎉 Completed!")

        result = {
            "success": True,
            "symbol": symbol,
            "news_count": 5,
            "avg_sentiment": 0.45
        }

        # ステータスを「finished」に更新
        if job_id:
            job_manager.update_status(job_id, "finished", result)

        return result

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        log(error_msg)

        # ステータスを「failed」に更新
        if job_id:
            job_manager.update_status(job_id, "failed", {"error": str(e)})

        raise
